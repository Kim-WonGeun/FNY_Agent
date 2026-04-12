# 룰 기반 메일 분석기 (LLM 이전 단계)
# - 제목+본문에서 키워드로 긴급도, 회신 필요, 마감/일정 힌트만 판단

from __future__ import annotations

import re
from dataclasses import dataclass

from app.models import ActionItem, AnalysisResult, EmailCategory, EmailInput, PriorityLevel, UrgencyLevel


@dataclass(frozen=True)
class _KeywordSet:
    """언어별 키워드 묶음 (확장 시 여기만 추가)"""

    urgent: tuple[str, ...]
    reply: tuple[str, ...]
    deadline_hint: tuple[str, ...]
    meeting: tuple[str, ...]
    report: tuple[str, ...]
    finance: tuple[str, ...]
    request: tuple[str, ...]


_KO = _KeywordSet(
    urgent=("긴급", "즉시", "asap", "오늘까지", "당일", "마감", "데드라인"),
    reply=("회신", "답장", "답변", "확인 부탁", "검토 부탁", "연락", "reply"),
    deadline_hint=("마감", "까지", "내일", "모레", "회의", "일정", "deadline", "due"),
    meeting=("회의", "미팅", "일정", "캘린더", "참석"),
    report=("보고", "보고서", "공유", "회고", "update"),
    finance=("세금계산서", "계산서", "정산", "결제", "입금", "재무"),
    request=("요청", "부탁", "확인", "검토", "전달"),
)

_EN = _KeywordSet(
    urgent=("urgent", "asap", "immediately", "today", "eod", "deadline"),
    reply=("reply", "please confirm", "get back", "respond", "let me know"),
    deadline_hint=("deadline", "due", "by ", "meeting", "tomorrow", "schedule"),
    meeting=("meeting", "schedule", "calendar", "attend", "invite"),
    report=("report", "weekly", "update", "retrospective", "share"),
    finance=("invoice", "payment", "tax", "settlement", "finance"),
    request=("request", "please", "confirm", "review", "check"),
)


def _normalize(text: str) -> str:
    """검색용으로 소문자 + 공백 정리"""
    return re.sub(r"\s+", " ", text.strip().lower())


def _contains_any(haystack: str, needles: tuple[str, ...]) -> bool:
    return any(n in haystack for n in needles)


def _pick_keywords(language: str) -> _KeywordSet:
    if language == "en":
        return _EN
        
    return _KO


def _score_urgency(haystack: str, ks: _KeywordSet) -> UrgencyLevel:
    """키워드 강도에 따라 긴급도 결정 (단순 우선순위)"""
    if _contains_any(haystack, ("긴급", "urgent", "critical", "즉시", "immediately")):
        return UrgencyLevel.critical
    if _contains_any(haystack, ks.urgent):
        return UrgencyLevel.high
    if _contains_any(haystack, ks.deadline_hint):
        return UrgencyLevel.medium
        
    return UrgencyLevel.low


def _urgency_score(urgency: UrgencyLevel, needs_reply: bool, has_deadline: bool) -> float:
    base = {
        UrgencyLevel.critical: 95.0,
        UrgencyLevel.high: 82.0,
        UrgencyLevel.medium: 62.0,
        UrgencyLevel.low: 28.0,
    }[urgency]

    if needs_reply:
        base += 6.0
    if has_deadline:
        base += 8.0

    return min(base, 100.0)


def _importance_score(haystack: str, ks: _KeywordSet, urgency: UrgencyLevel, needs_reply: bool) -> float:
    score = 45.0

    if urgency in (UrgencyLevel.critical, UrgencyLevel.high):
        score += 24.0
    elif urgency == UrgencyLevel.medium:
        score += 12.0

    if needs_reply:
        score += 16.0
    if _contains_any(haystack, ks.request):
        score += 8.0
    if _contains_any(haystack, ks.finance):
        score += 10.0

    return min(score, 100.0)


def _priority_level(urgency_score: float, importance_score: float, needs_reply: bool) -> PriorityLevel:
    combined = (urgency_score * 0.55) + (importance_score * 0.45)

    if combined >= 86 or (urgency_score >= 90 and needs_reply):
        return PriorityLevel.p1
    if combined >= 68:
        return PriorityLevel.p2
    if combined >= 45:
        return PriorityLevel.p3

    return PriorityLevel.p4


def _category(haystack: str, ks: _KeywordSet, urgency: UrgencyLevel) -> EmailCategory:
    if urgency == UrgencyLevel.critical:
        return EmailCategory.urgent
    if _contains_any(haystack, ks.finance):
        return EmailCategory.finance
    if _contains_any(haystack, ks.meeting):
        return EmailCategory.meeting
    if _contains_any(haystack, ks.report):
        return EmailCategory.report
    if _contains_any(haystack, ks.request):
        return EmailCategory.request

    return EmailCategory.general


def _action_type(category: EmailCategory, needs_reply: bool) -> str:
    if needs_reply:
        return "REPLY"
    if category == EmailCategory.meeting:
        return "SCHEDULE"
    if category == EmailCategory.report:
        return "REVIEW"
    if category == EmailCategory.finance:
        return "ARCHIVE"
    if category == EmailCategory.urgent:
        return "ESCALATE"

    return "REVIEW"


def _suggested_action(category: EmailCategory, needs_reply: bool, has_deadline: bool) -> str:
    if needs_reply:
        return "내용 확인 후 회신"
    if category == EmailCategory.meeting:
        return "회의 일정 확인"
    if category == EmailCategory.finance:
        return "재무 증빙 확인"
    if category == EmailCategory.report:
        return "공유 내용 검토"
    if has_deadline:
        return "마감 일정 확인"

    return "필요 시 내용 확인"


def analyze_email(email: EmailInput) -> AnalysisResult:
    """
    룰 기반 분석: LLM 없이 키워드로 최소 판단만 수행.
    - deadline_at: 날짜 파싱은 다음 단계(파서 또는 LLM)에서 채움
    """
    combined = _normalize(f"{email.subject}\n{email.body_text}")
    ks = _pick_keywords(email.language.value)

    urgency = _score_urgency(combined, ks)
    needs_reply = _contains_any(combined, ks.reply)
    has_deadline = _contains_any(combined, ks.deadline_hint)
    category = _category(combined, ks, urgency)
    urgency_score = _urgency_score(urgency, needs_reply, has_deadline)
    importance_score = _importance_score(combined, ks, urgency, needs_reply)
    priority_level = _priority_level(urgency_score, importance_score, needs_reply)
    suggested_action = _suggested_action(category, needs_reply, has_deadline)

    parts: list[str] = [f"긴급도 {urgency.value}", f"우선순위 {priority_level.value}"]

    if needs_reply:
        parts.append("회신/확인 요청 키워드 감지")
    if has_deadline:
        parts.append("일정·마감 관련 키워드 감지")
    if not parts:
        parts.append("특이 키워드 없음")

    short_summary = " / ".join(parts)
    detailed_summary = (
        f"제목과 본문에서 {category.value} 성격의 메일로 판단했습니다. "
        f"긴급도 점수는 {urgency_score:.0f}, 중요도 점수는 {importance_score:.0f}입니다."
    )

    action_items: list[ActionItem] = []

    if needs_reply:
        action_items.append(
            ActionItem(
                action_text="발신자 요청 확인 후 회신 여부 결정",
                action_type="REPLY",
                priority_level=priority_level,
            )
        )
    if has_deadline:
        action_items.append(
            ActionItem(
                action_text="일정·마감 일시 확인",
                action_type="SCHEDULE",
                priority_level=priority_level,
            )
        )
    if not action_items:
        action_items.append(
            ActionItem(
                action_text=suggested_action,
                action_type=_action_type(category, needs_reply),
                priority_level=priority_level,
            )
        )

    confidence_score = 55.0 if urgency != UrgencyLevel.low or needs_reply or has_deadline else 35.0

    return AnalysisResult(
        email_id=email.email_id,
        urgency=urgency,
        short_summary=short_summary,
        detailed_summary=detailed_summary,
        category=category,
        priority_level=priority_level,
        importance_score=importance_score,
        urgency_score=urgency_score,
        confidence_score=confidence_score,
        needs_reply=needs_reply,
        has_deadline=has_deadline,
        deadline_at=None,
        suggested_action=suggested_action,
        reasoning=" / ".join(parts),
        action_items=action_items,
    )
