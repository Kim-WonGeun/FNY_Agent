from __future__ import annotations

from typing import Protocol

from app.exceptions import LLMConfigurationError
from app.prompt_metadata import prompt_version
from app.llm_prompts import render_email_analysis_prompt, render_weekly_report_prompt
from app.llm_response_parser import parse_json_model
from app.schemas import AnalysisResult, EmailInput, WeeklyReportInput, WeeklyReportResult
from app.settings import AgentSettings


class LLMClient(Protocol):
    def complete_json(self, prompt: str, model: str) -> str:
        ...


class MissingLLMClient:
    def complete_json(self, prompt: str, model: str) -> str:
        raise LLMConfigurationError("LLM client is not configured.")


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
