from __future__ import annotations

import json
from typing import Optional

from pydantic import BaseModel

from app.schemas import AnalysisResult, EmailInput, PromptTemplate, WeeklyReportInput, WeeklyReportResult
from app.settings import AgentSettings


def render_email_analysis_prompt(email: EmailInput, settings: AgentSettings) -> str:
    return _render_structured_prompt(
        system_instruction="You are FNY's mail intelligence analyzer.",
        schema_name="AnalysisResult",
        model_type=AnalysisResult,
        required_fields=(
            "Required stable fields include: short_summary, detailed_summary, category, priority_level, "
            "importance_score, urgency_score, confidence_score, needs_reply, has_deadline, "
            "suggested_action, reasoning, action_items."
        ),
        payload_label="Email payload",
        payload_json=email.model_dump_json(),
        template=email.prompt,
        model_name=settings.openai_model,
    )


def render_weekly_report_prompt(payload: WeeklyReportInput, settings: AgentSettings) -> str:
    return _render_structured_prompt(
        system_instruction="You are FNY's weekly mail report analyzer.",
        schema_name="WeeklyReportResult",
        model_type=WeeklyReportResult,
        required_fields=(
            "Required stable fields include: executive_summary, highlights, risks_blockers, "
            "pending_decisions, next_week_suggestions, thread_summaries."
        ),
        payload_label="Weekly report payload",
        payload_json=payload.model_dump_json(),
        template=payload.prompt,
        model_name=settings.openai_model,
    )


def _render_structured_prompt(
    system_instruction: str,
    schema_name: str,
    model_type: type[BaseModel],
    required_fields: str,
    payload_label: str,
    payload_json: str,
    template: Optional[PromptTemplate],
    model_name: str,
) -> str:
    sections = [
        system_instruction,
        f"Return only one valid JSON object matching the {schema_name} schema.",
        "Do not include markdown fences or explanatory prose.",
    ]
    sections.extend(_prompt_template_sections(template))
    sections.extend(
        [
            f"Model: {model_name}",
            required_fields,
            f"{schema_name} JSON schema:\n{_model_json_schema(model_type)}",
            f"{payload_label}:\n{payload_json}",
        ]
    )
    return "\n\n".join(section for section in sections if section)


def _prompt_template_sections(template: Optional[PromptTemplate]) -> list[str]:
    if not template:
        return []
    return [
        f"Prompt code: {template.prompt_code}",
        f"Prompt version: {template.version}",
        f"Role:\n{template.role}",
        f"Policy:\n{template.policy}",
        f"Guide:\n{template.guide}",
        f"Output:\n{template.output}",
    ]


def _model_json_schema(model_type: type[BaseModel]) -> str:
    return json.dumps(model_type.model_json_schema(), ensure_ascii=False, sort_keys=True)
