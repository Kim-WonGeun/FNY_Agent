from fastapi import FastAPI

from app.analyzer import analyze_email, analyze_weekly_report
from app.models import AnalysisResult, EmailInput, WeeklyReportInput, WeeklyReportResult

app = FastAPI(title="Mail Agent", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalysisResult)
def analyze(payload: EmailInput) -> AnalysisResult:
    return analyze_email(payload)


@app.post("/analyze-weekly", response_model=WeeklyReportResult)
def analyze_weekly(payload: WeeklyReportInput) -> WeeklyReportResult:
    return analyze_weekly_report(payload)