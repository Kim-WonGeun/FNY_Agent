from __future__ import annotations

from app.email_actions import action_items
from app.email_presenter import detailed_summary, short_summary
from app.email_reasoning import reasoning_text
from app.prompt_metadata import result_metadata
from app.schemas import AnalysisResult, EmailInput
from app.signals import EmailAnalysisSignals


def build_analysis_result(email: EmailInput, signals: EmailAnalysisSignals) -> AnalysisResult:
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

    model_name, rendered_prompt_version = result_metadata(email.prompt, "rule-based-agent", "rule-v1")

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
        prompt_version=rendered_prompt_version,
    )
