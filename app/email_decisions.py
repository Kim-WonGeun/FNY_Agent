from __future__ import annotations

from app.schemas import EmailCategory, UrgencyLevel


ACTIONABLE_CATEGORIES: frozenset[EmailCategory] = frozenset(
    {
        EmailCategory.urgent,
        EmailCategory.request,
        EmailCategory.meeting,
        EmailCategory.report,
        EmailCategory.finance,
    }
)


def requires_action(email_category: EmailCategory, needs_reply: bool, has_deadline: bool) -> bool:
    return needs_reply or has_deadline or email_category in ACTIONABLE_CATEGORIES


def confidence_score(urgency: UrgencyLevel, needs_reply: bool, has_deadline: bool) -> float:
    if urgency != UrgencyLevel.low or needs_reply or has_deadline:
        return 55.0
    return 35.0
