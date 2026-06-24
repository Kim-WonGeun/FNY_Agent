from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from app.analyzer_contracts import EmailAnalyzer, WeeklyReportAnalyzer
from app.exceptions import LLMError
from app.providers import get_email_analyzer, get_weekly_report_analyzer
from app.schemas import AnalysisResult, EmailInput, WeeklyReportInput, WeeklyReportResult


def create_app() -> FastAPI:
    api = FastAPI(title="Mail Agent", version="0.1.0")
    api.add_exception_handler(LLMError, handle_llm_error)
    api.add_api_route("/health", health, methods=["GET"])
    api.add_api_route("/analyze", analyze, methods=["POST"], response_model=AnalysisResult)
    api.add_api_route("/analyze-weekly", analyze_weekly, methods=["POST"], response_model=WeeklyReportResult)
    return api


def handle_llm_error(request: Request, exc: LLMError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": str(exc),
        },
    )


def health() -> dict[str, str]:
    return {"status": "ok"}


def analyze(
    payload: EmailInput,
    analyzer: EmailAnalyzer = Depends(get_email_analyzer),
) -> AnalysisResult:
    return analyzer.analyze(payload)


def analyze_weekly(
    payload: WeeklyReportInput,
    analyzer: WeeklyReportAnalyzer = Depends(get_weekly_report_analyzer),
) -> WeeklyReportResult:
    return analyzer.analyze(payload)


app = create_app()
