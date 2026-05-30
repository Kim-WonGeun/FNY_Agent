from __future__ import annotations

from dataclasses import dataclass

from app.schemas import EmailCategory, PriorityLevel, PriorityReasonCode, TimeSensitivity, UrgencyLevel


@dataclass(frozen=True)
class EmailAnalysisSignals:
    haystack: str
    urgency: UrgencyLevel
    needs_reply: bool
    has_deadline: bool
    category: EmailCategory
    urgency_score: float
    importance_score: float
    priority: PriorityLevel
    suggested_action: str
    time_sensitivity: TimeSensitivity
    deadline_text: str
    requires_action: bool
    user_task_summary: str
    priority_reason_codes: list[PriorityReasonCode]
    confidence_score: float
