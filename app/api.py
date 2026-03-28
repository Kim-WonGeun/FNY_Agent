from fastapi import FastAPI

from app.analyzer import analyze_email
from app.models import AnalysisResult, EmailInput

app = FastAPI(title="Mail Agent", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalysisResult)
def analyze(payload: EmailInput) -> AnalysisResult:
    return analyze_email(payload)