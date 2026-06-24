from __future__ import annotations

from app.llm_quality_utils import clean_list, clean_text, dedupe_by
from app.schemas import AnalysisResult, EmailInput, WeeklyReportInput, WeeklyReportResult


def normalize_email_analysis_result(result: AnalysisResult, email: EmailInput) -> AnalysisResult:
    short_summary = clean_text(result.short_summary, 1000) or clean_text(email.subject, 1000) or "메일 내용을 확인해 주세요."
    detailed_summary = clean_text(result.detailed_summary) or short_summary
    action_items = dedupe_by(result.action_items, lambda item: clean_text(item.action_text, 500).lower())[:5]
    deadline_at = result.deadline_at if result.has_deadline else None
    deadline_text = clean_text(result.deadline_text, 255) if result.has_deadline else ""

    return result.model_copy(
        update={
            "email_id": email.email_id,
            "short_summary": short_summary,
            "detailed_summary": detailed_summary,
            "deadline_at": deadline_at,
            "deadline_text": deadline_text,
            "suggested_action": clean_text(result.suggested_action, 255),
            "reasoning": clean_text(result.reasoning),
            "user_task_summary": clean_text(result.user_task_summary, 1000),
            "action_items": action_items,
            "priority_reason_codes": list(dict.fromkeys(result.priority_reason_codes)),
        }
    )


def normalize_weekly_report_result(result: WeeklyReportResult, payload: WeeklyReportInput) -> WeeklyReportResult:
    allowed_ids = {str(email.email_id) for email in payload.emails}
    threads = [thread for thread in result.thread_summaries if str(thread.email_id) in allowed_ids]
    threads = dedupe_by(threads, lambda thread: str(thread.email_id))[:40]

    return result.model_copy(
        update={
            "executive_summary": clean_text(result.executive_summary, 2000)
            or f"선택 기간 메일 {len(payload.emails)}건을 기준으로 보고서 초안을 구성했습니다.",
            "highlights": clean_list(result.highlights, 5),
            "risks_blockers": clean_list(result.risks_blockers, 4),
            "pending_decisions": clean_list(result.pending_decisions, 5),
            "next_week_suggestions": clean_list(result.next_week_suggestions, 5),
            "thread_summaries": threads,
        }
    )
