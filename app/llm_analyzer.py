from __future__ import annotations

from typing import Optional

from app.llm_client import LLMClient, MissingLLMClient
from app.llm_completion import complete_json_model
from app.llm_metadata import with_email_llm_metadata, with_weekly_llm_metadata
from app.llm_prompts import render_email_analysis_prompt, render_weekly_report_prompt
from app.llm_quality import normalize_email_analysis_result, normalize_weekly_report_result
from app.schemas import AnalysisResult, EmailInput, WeeklyReportInput, WeeklyReportResult
from app.settings import AgentSettings


class LLMEmailAnalyzer:
    def __init__(self, settings: AgentSettings, client: Optional[LLMClient] = None) -> None:
        self.settings = settings
        self.client = client or MissingLLMClient()

    def analyze(self, email: EmailInput) -> AnalysisResult:
        prompt = render_email_analysis_prompt(email, self.settings)
        result = complete_json_model(self.client, self.settings, prompt, AnalysisResult)
        return with_email_llm_metadata(normalize_email_analysis_result(result, email), email, self.settings)


class LLMWeeklyReportAnalyzer:
    def __init__(self, settings: AgentSettings, client: Optional[LLMClient] = None) -> None:
        self.settings = settings
        self.client = client or MissingLLMClient()

    def analyze(self, payload: WeeklyReportInput) -> WeeklyReportResult:
        prompt = render_weekly_report_prompt(payload, self.settings)
        result = complete_json_model(self.client, self.settings, prompt, WeeklyReportResult)
        return with_weekly_llm_metadata(normalize_weekly_report_result(result, payload), payload, self.settings)
