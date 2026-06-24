from __future__ import annotations

from functools import lru_cache

from app.analyzer_contracts import EmailAnalyzer, WeeklyReportAnalyzer
from app.email_analyzer import RuleBasedEmailAnalyzer
from app.llm_analyzer import LLMEmailAnalyzer, LLMWeeklyReportAnalyzer
from app.openai_client import OpenAIResponsesClient
from app.settings import AgentSettings, AnalyzerMode, load_settings
from app.weekly_report import RuleBasedWeeklyReportAnalyzer


def build_email_analyzer(settings: AgentSettings) -> EmailAnalyzer:
    if settings.email_analyzer_mode == AnalyzerMode.llm:
        return LLMEmailAnalyzer(settings, OpenAIResponsesClient(settings))
    return RuleBasedEmailAnalyzer()


def build_weekly_report_analyzer(settings: AgentSettings) -> WeeklyReportAnalyzer:
    if settings.weekly_report_analyzer_mode == AnalyzerMode.llm:
        return LLMWeeklyReportAnalyzer(settings, OpenAIResponsesClient(settings))
    return RuleBasedWeeklyReportAnalyzer()


@lru_cache(maxsize=1)
def get_settings() -> AgentSettings:
    return load_settings()


@lru_cache(maxsize=1)
def get_email_analyzer() -> EmailAnalyzer:
    return build_email_analyzer(get_settings())


@lru_cache(maxsize=1)
def get_weekly_report_analyzer() -> WeeklyReportAnalyzer:
    return build_weekly_report_analyzer(get_settings())


def reset_provider_cache() -> None:
    get_settings.cache_clear()
    get_email_analyzer.cache_clear()
    get_weekly_report_analyzer.cache_clear()
