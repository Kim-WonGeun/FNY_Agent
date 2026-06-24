from __future__ import annotations

from app.prompt_metadata import prompt_version
from app.schemas import AnalysisResult, EmailInput, WeeklyReportInput, WeeklyReportResult
from app.settings import AgentSettings


def with_email_llm_metadata(result: AnalysisResult, email: EmailInput, settings: AgentSettings) -> AnalysisResult:
    rendered_prompt_version = prompt_version(email.prompt, "email-llm-v1")
    return result.model_copy(update={"model_name": settings.openai_model, "prompt_version": rendered_prompt_version})


def with_weekly_llm_metadata(
    result: WeeklyReportResult,
    payload: WeeklyReportInput,
    settings: AgentSettings,
) -> WeeklyReportResult:
    rendered_prompt_version = prompt_version(payload.prompt, "weekly-llm-v1")
    return result.model_copy(update={"model_name": settings.openai_model, "prompt_version": rendered_prompt_version})
