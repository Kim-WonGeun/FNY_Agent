from __future__ import annotations

from app.keywords import KeywordSet
from app.schemas import EmailCategory, PriorityLevel, UrgencyLevel
from app.text_utils import contains_any


def score_urgency(haystack: str, keywords: KeywordSet) -> UrgencyLevel:
    if contains_any(haystack, ("긴급", "urgent", "critical", "즉시", "immediately")):
        return UrgencyLevel.critical
    if contains_any(haystack, keywords.urgent):
        return UrgencyLevel.high
    if contains_any(haystack, keywords.deadline_hint):
        return UrgencyLevel.medium
    return UrgencyLevel.low


def urgency_score(urgency: UrgencyLevel, needs_reply: bool, has_deadline: bool) -> float:
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


def importance_score(haystack: str, keywords: KeywordSet, urgency: UrgencyLevel, needs_reply: bool) -> float:
    score = 45.0

    if urgency in (UrgencyLevel.critical, UrgencyLevel.high):
        score += 24.0
    elif urgency == UrgencyLevel.medium:
        score += 12.0

    if needs_reply:
        score += 16.0
    if contains_any(haystack, keywords.request):
        score += 8.0
    if contains_any(haystack, keywords.finance):
        score += 10.0

    return min(score, 100.0)


def priority_level(urgency_score_value: float, importance_score_value: float, needs_reply: bool) -> PriorityLevel:
    combined = (urgency_score_value * 0.55) + (importance_score_value * 0.45)

    if combined >= 86 or (urgency_score_value >= 90 and needs_reply):
        return PriorityLevel.p1
    if combined >= 68:
        return PriorityLevel.p2
    if combined >= 45:
        return PriorityLevel.p3

    return PriorityLevel.p4


def category(haystack: str, keywords: KeywordSet, urgency: UrgencyLevel) -> EmailCategory:
    if urgency == UrgencyLevel.critical:
        return EmailCategory.urgent
    if contains_any(haystack, keywords.finance):
        return EmailCategory.finance
    if contains_any(haystack, keywords.meeting):
        return EmailCategory.meeting
    if contains_any(haystack, keywords.report):
        return EmailCategory.report
    if contains_any(haystack, keywords.request):
        return EmailCategory.request

    return EmailCategory.general
