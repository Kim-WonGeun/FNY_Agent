from __future__ import annotations

from app.email_actions import suggested_action_text, user_task_summary
from app.email_decisions import confidence_score, requires_action
from app.email_deadlines import deadline_text, time_sensitivity
from app.email_reasoning import priority_reason_codes
from app.keywords import pick_keywords
from app.schemas import EmailInput
from app.scoring import category, importance_score, priority_level, score_urgency, urgency_score
from app.signals import EmailAnalysisSignals
from app.text_utils import contains_any, normalize


def analyze_signals(email: EmailInput) -> EmailAnalysisSignals:
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
    rendered_time_sensitivity = time_sensitivity(urgency, has_deadline, combined)
    rendered_deadline_text = deadline_text(combined, has_deadline)
    rendered_requires_action = requires_action(email_category, needs_reply, has_deadline)
    rendered_user_task_summary = user_task_summary(email_category, needs_reply, has_deadline, suggested_action)
    reason_codes = priority_reason_codes(urgency, needs_reply, has_deadline, email_category, combined)
    rendered_confidence_score = confidence_score(urgency, needs_reply, has_deadline)

    return EmailAnalysisSignals(
        haystack=combined,
        urgency=urgency,
        category=email_category,
        priority=priority,
        importance_score=importance_score_value,
        urgency_score=urgency_score_value,
        confidence_score=rendered_confidence_score,
        needs_reply=needs_reply,
        has_deadline=has_deadline,
        deadline_text=rendered_deadline_text,
        time_sensitivity=rendered_time_sensitivity,
        requires_action=rendered_requires_action,
        user_task_summary=rendered_user_task_summary,
        priority_reason_codes=reason_codes,
        suggested_action=suggested_action,
    )
