from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import EmailId, Language, PromptTemplate


class WeeklyEmailLine(BaseModel):
    """주간 집계용 메일 한 줄(본문은 발췌)"""

    email_id: EmailId
    subject: str = Field(default="", description="메일 제목")
    body_excerpt: str = Field(default="", description="본문 발췌")
    from_email: EmailStr = Field(..., description="발신자 이메일")
    received_at: datetime = Field(..., description="수신 시각")


class WeeklyReportInput(BaseModel):
    mail_account_id: str = Field(..., max_length=30, description="메일 계정 ID")
    period_start: datetime = Field(..., description="집계 시작(포함)")
    period_end: datetime = Field(..., description="집계 종료(배타)")
    language: Language = Field(default=Language.ko, description="요약 언어")
    prompt: Optional[PromptTemplate] = Field(default=None, description="LLM 프롬프트 템플릿")
    emails: list[WeeklyEmailLine] = Field(default_factory=list, description="포함할 메일 목록")


class WeeklyThreadSummary(BaseModel):
    email_id: str
    subject: str = ""
    one_liner: str = ""


class WeeklyReportResult(BaseModel):
    executive_summary: str = Field(..., max_length=2000)
    highlights: list[str] = Field(default_factory=list)
    risks_blockers: list[str] = Field(default_factory=list)
    pending_decisions: list[str] = Field(default_factory=list)
    next_week_suggestions: list[str] = Field(default_factory=list)
    thread_summaries: list[WeeklyThreadSummary] = Field(default_factory=list)
    model_name: str = Field(default="rule-based-agent-weekly")
    prompt_version: str = Field(default="weekly-rule-v1")
