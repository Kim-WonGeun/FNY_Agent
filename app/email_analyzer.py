from __future__ import annotations

from app.email_result_builder import build_analysis_result
from app.email_rules import analyze_signals
from app.schemas import AnalysisResult, EmailInput


class RuleBasedEmailAnalyzer:
    """LLM 연동 전 단계의 결정적 룰 기반 메일 분석기."""

    def analyze(self, email: EmailInput) -> AnalysisResult:
        signals = analyze_signals(email)
        return build_analysis_result(email, signals)


def analyze_email(email: EmailInput) -> AnalysisResult:
    return RuleBasedEmailAnalyzer().analyze(email)
