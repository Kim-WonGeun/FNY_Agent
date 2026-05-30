from __future__ import annotations

import re

from app.keywords import pick_keywords
from app.email_presenter import (
    action_items,
    detailed_summary,
    reasoning_text,
    short_summary,
    suggested_action_text,
    user_task_summary,
)
from app.schemas import (
    AnalysisResult,
    EmailCategory,
    EmailInput,
    PriorityReasonCode,
    TimeSensitivity,
    UrgencyLevel,
)
from app.scoring import category, importance_score, priority_level, score_urgency, urgency_score
from app.signals import EmailAnalysisSignals
from app.text_utils import contains_any, normalize


def _time_sensitivity(urgency: UrgencyLevel, has_deadline: bool, haystack: str) -> TimeSensitivity:
    if urgency == UrgencyLevel.critical or contains_any(haystack, ("즉시", "asap", "immediately", "긴급")):
        return TimeSensitivity.immediate
    if contains_any(haystack, ("오늘", "당일", "today", "eod")):
        return TimeSensitivity.today
    if has_deadline:
        return TimeSensitivity.this_week
    return TimeSensitivity.no_deadline


def _deadline_text(haystack: str, has_deadline: bool) -> str:
    if not has_deadline:
        return ""
    patterns = (
        r"(오늘까지|당일|내일까지|모레까지|이번 주\s*[가-힣]*까지|[0-9]{1,2}월\s*[0-9]{1,2}일\s*까지)",
        r"(by\s+[a-zA-Z]+\s+\d{1,2}|by\s+tomorrow|by\s+today|due\s+[a-zA-Z]+\s+\d{1,2})",
    )
    for pattern in patterns:
        match = re.search(pattern, haystack, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    return "메일에 마감/일정 관련 표현이 있습니다."


def _priority_reason_codes(
    urgency: UrgencyLevel,
    needs_reply: bool,
    has_deadline: bool,
    email_category: EmailCategory,
    haystack: str,
) -> list[PriorityReasonCode]:
    codes: list[PriorityReasonCode] = []
    if urgency in (UrgencyLevel.critical, UrgencyLevel.high):
        codes.append(PriorityReasonCode.urgent_keyword)
    if needs_reply:
        codes.append(PriorityReasonCode.needs_reply)
    if has_deadline:
        codes.append(PriorityReasonCode.has_deadline)
    if contains_any(haystack, ("승인", "approve", "approval")):
        codes.append(PriorityReasonCode.approval_required)
    if email_category == EmailCategory.finance:
        codes.append(PriorityReasonCode.finance_related)
    if email_category == EmailCategory.meeting:
        codes.append(PriorityReasonCode.meeting_related)
    if contains_any(haystack, ("고객", "장애", "계약", "customer", "incident", "contract")):
        codes.append(PriorityReasonCode.customer_or_contract)
    if not codes:
        codes.append(PriorityReasonCode.no_strong_signal)
    return codes


class RuleBasedEmailAnalyzer:
    """LLM 연동 전 단계의 결정적 룰 기반 메일 분석기."""

    def analyze(self, email: EmailInput) -> AnalysisResult:
        signals = _analyze_signals(email)
        rendered_short_summary = short_summary(
            email,
            signals.category,
            signals.needs_reply,
            signals.has_deadline,
            signals.haystack,
        )
        rendered_detailed_summary = detailed_summary(
            email,
            signals.category,
            signals.needs_reply,
            signals.has_deadline,
            signals.haystack,
        )
        rendered_reasoning = reasoning_text(signals.priority_reason_codes, signals.urgency, signals.priority)
        rendered_action_items = action_items(
            signals.category,
            signals.needs_reply,
            signals.has_deadline,
            signals.priority,
            signals.suggested_action,
            signals.haystack,
        )

        model_name = email.prompt.model_name if email.prompt else "rule-based-agent"
        prompt_version = f"{email.prompt.prompt_code}-v{email.prompt.version}" if email.prompt else "rule-v1"

        return AnalysisResult(
            email_id=email.email_id,
            urgency=signals.urgency,
            short_summary=rendered_short_summary,
            detailed_summary=rendered_detailed_summary,
            category=signals.category,
            priority_level=signals.priority,
            importance_score=signals.importance_score,
            urgency_score=signals.urgency_score,
            confidence_score=signals.confidence_score,
            needs_reply=signals.needs_reply,
            has_deadline=signals.has_deadline,
            deadline_at=None,
            deadline_text=signals.deadline_text,
            time_sensitivity=signals.time_sensitivity,
            requires_action=signals.requires_action,
            user_task_summary=signals.user_task_summary,
            priority_reason_codes=signals.priority_reason_codes,
            suggested_action=signals.suggested_action,
            reasoning=rendered_reasoning,
            action_items=rendered_action_items,
            model_name=model_name,
            prompt_version=prompt_version,
        )


def _analyze_signals(email: EmailInput) -> EmailAnalysisSignals:
    combined = normalize(f"{email.subject}\n{email.body_text}")
    keywords = pick_keywords(email.language.value)

    urgency = score_urgency(combined, keywords)
    needs_reply = contains_any(combined, keywords.reply)
    has_deadline = contains_any(combined, keywords.deadline_hint)
    email_category = category(combined, keywords, urgency)
    urgency_score_value = urgency_score(urgency, needs_reply, has_deadline)
    importance_score_value = importance_score(combined, keywords, urgency, needs_reply)
    priority = priority_level(urgency_score_value, importance_score_value, needs_reply)
    suggested_action = suggested_action_text(email_category, needs_reply, has_deadline, combined)
    time_sensitivity = _time_sensitivity(urgency, has_deadline, combined)
    deadline_text = _deadline_text(combined, has_deadline)
    requires_action = needs_reply or has_deadline or email_category in {
        EmailCategory.urgent,
        EmailCategory.request,
        EmailCategory.meeting,
        EmailCategory.report,
        EmailCategory.finance,
    }
    rendered_user_task_summary = user_task_summary(email_category, needs_reply, has_deadline, suggested_action)
    reason_codes = _priority_reason_codes(urgency, needs_reply, has_deadline, email_category, combined)
    confidence_score = 55.0 if urgency != UrgencyLevel.low or needs_reply or has_deadline else 35.0

    return EmailAnalysisSignals(
        haystack=combined,
        urgency=urgency,
        category=email_category,
        priority=priority,
        importance_score=importance_score_value,
        urgency_score=urgency_score_value,
        confidence_score=confidence_score,
        needs_reply=needs_reply,
        has_deadline=has_deadline,
        deadline_text=deadline_text,
        time_sensitivity=time_sensitivity,
        requires_action=requires_action,
        user_task_summary=rendered_user_task_summary,
        priority_reason_codes=reason_codes,
        suggested_action=suggested_action,
    )


def analyze_email(email: EmailInput) -> AnalysisResult:
    return RuleBasedEmailAnalyzer().analyze(email)
