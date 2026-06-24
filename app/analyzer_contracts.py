from __future__ import annotations

from typing import Protocol

from app.schemas import AnalysisResult, EmailInput, WeeklyReportInput, WeeklyReportResult


class EmailAnalyzer(Protocol):
    def analyze(self, email: EmailInput) -> AnalysisResult:
        ...


class WeeklyReportAnalyzer(Protocol):
    def analyze(self, payload: WeeklyReportInput) -> WeeklyReportResult:
        ...
