from __future__ import annotations

from typing import Optional

from app.llm_contract import (
    LLMClient,
    MissingLLMClient,
    parse_json_model,
    render_email_analysis_prompt,
    render_weekly_report_prompt,
    with_email_llm_metadata,
    with_weekly_llm_metadata,
)
from app.schemas import AnalysisResult, EmailInput, WeeklyReportInput, WeeklyReportResult
from app.settings import AgentSettings


class LLMEmailAnalyzer:
    def __init__(self, settings: AgentSettings, client: Optional[LLMClient] = None) -> None:
        self.settings = settings
        self.client = client or MissingLLMClient()

    def analyze(self, email: EmailInput) -> AnalysisResult:
        prompt = render_email_analysis_prompt(email, self.settings)
        raw_result = self.client.complete_json(prompt, self.settings.openai_model)
        result = parse_json_model(raw_result, AnalysisResult)
        return with_email_llm_metadata(result, email, self.settings)


class LLMWeeklyReportAnalyzer:
    def __init__(self, settings: AgentSettings, client: Optional[LLMClient] = None) -> None:
        self.settings = settings
        self.client = client or MissingLLMClient()

    def analyze(self, payload: WeeklyReportInput) -> WeeklyReportResult:
        prompt = render_weekly_report_prompt(payload, self.settings)
        raw_result = self.client.complete_json(prompt, self.settings.openai_model)
        result = parse_json_model(raw_result, WeeklyReportResult)
        return with_weekly_llm_metadata(result, payload, self.settings)
