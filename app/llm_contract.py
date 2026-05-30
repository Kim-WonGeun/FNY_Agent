from __future__ import annotations

import json
import re
from typing import Protocol, TypeVar

from pydantic import BaseModel, ValidationError

from app.exceptions import LLMConfigurationError, LLMResponseError
from app.schemas import AnalysisResult, EmailInput, WeeklyReportInput, WeeklyReportResult
from app.settings import AgentSettings


TModel = TypeVar("TModel", bound=BaseModel)


class LLMClient(Protocol):
    def complete_json(self, prompt: str, model: str) -> str:
        ...


class MissingLLMClient:
    def complete_json(self, prompt: str, model: str) -> str:
        raise LLMConfigurationError("LLM client is not configured.")


def render_email_analysis_prompt(email: EmailInput, settings: AgentSettings) -> str:
    template = email.prompt
    sections = [
        "You are FNY's mail intelligence analyzer.",
        "Return only one valid JSON object matching the AnalysisResult schema.",
        "Do not include markdown fences or explanatory prose.",
    ]
    if template:
        sections.extend(
            [
                f"Prompt code: {template.prompt_code}",
                f"Prompt version: {template.version}",
                f"Role:\n{template.role}",
                f"Policy:\n{template.policy}",
                f"Guide:\n{template.guide}",
                f"Output:\n{template.output}",
            ]
        )
    sections.extend(
        [
            f"Model: {settings.openai_model}",
            "Required stable fields include: short_summary, detailed_summary, category, priority_level, "
            "importance_score, urgency_score, confidence_score, needs_reply, has_deadline, "
            "suggested_action, reasoning, action_items.",
            f"AnalysisResult JSON schema:\n{_model_json_schema(AnalysisResult)}",
            f"Email payload:\n{email.model_dump_json()}",
        ]
    )
    return "\n\n".join(section for section in sections if section)


def render_weekly_report_prompt(payload: WeeklyReportInput, settings: AgentSettings) -> str:
    template = payload.prompt
    sections = [
        "You are FNY's weekly mail report analyzer.",
        "Return only one valid JSON object matching the WeeklyReportResult schema.",
        "Do not include markdown fences or explanatory prose.",
    ]
    if template:
        sections.extend(
            [
                f"Prompt code: {template.prompt_code}",
                f"Prompt version: {template.version}",
                f"Role:\n{template.role}",
                f"Policy:\n{template.policy}",
                f"Guide:\n{template.guide}",
                f"Output:\n{template.output}",
            ]
        )
    sections.extend(
        [
            f"Model: {settings.openai_model}",
            "Required stable fields include: executive_summary, highlights, risks_blockers, "
            "pending_decisions, next_week_suggestions, thread_summaries.",
            f"WeeklyReportResult JSON schema:\n{_model_json_schema(WeeklyReportResult)}",
            f"Weekly report payload:\n{payload.model_dump_json()}",
        ]
    )
    return "\n\n".join(section for section in sections if section)


def parse_json_model(raw_text: str, model_type: type[TModel]) -> TModel:
    try:
        json_text = _extract_json_object(raw_text)
        return model_type.model_validate_json(json_text)
    except (ValueError, ValidationError) as exc:
        raise LLMResponseError("LLM response did not match the expected JSON schema.") from exc


def with_email_llm_metadata(result: AnalysisResult, email: EmailInput, settings: AgentSettings) -> AnalysisResult:
    prompt_version = f"{email.prompt.prompt_code}-v{email.prompt.version}" if email.prompt else "email-llm-v1"
    return result.model_copy(update={"model_name": settings.openai_model, "prompt_version": prompt_version})


def with_weekly_llm_metadata(
    result: WeeklyReportResult,
    payload: WeeklyReportInput,
    settings: AgentSettings,
) -> WeeklyReportResult:
    prompt_version = f"{payload.prompt.prompt_code}-v{payload.prompt.version}" if payload.prompt else "weekly-llm-v1"
    return result.model_copy(update={"model_name": settings.openai_model, "prompt_version": prompt_version})


def _extract_json_object(raw_text: str) -> str:
    stripped = raw_text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        stripped = fenced.group(1).strip()

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("LLM response does not contain a JSON object.")
    return stripped[start : end + 1]


def _model_json_schema(model_type: type[BaseModel]) -> str:
    return json.dumps(model_type.model_json_schema(), ensure_ascii=False, sort_keys=True)
