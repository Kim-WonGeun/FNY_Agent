from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import EmailId, Language, PromptTemplate
from app.schemas.enums import (
    ActionType,
    EmailCategory,
    PriorityLevel,
    PriorityReasonCode,
    TimeSensitivity,
    UrgencyLevel,
)


class EmailInput(BaseModel):
    email_id: EmailId = Field(..., description="메일 고유 ID")
    subject: str = Field(default="", description="메일 제목")
    body_text: str = Field(default="", description="메일 본문 텍스트")
    from_email: EmailStr = Field(..., description="발신자 이메일")
    received_at: datetime = Field(..., description="수신 시각(ISO-8601)")
    language: Language = Field(default=Language.ko, description="메일 언어")
    prompt: Optional[PromptTemplate] = Field(default=None, description="LLM 프롬프트 템플릿")


class ActionItem(BaseModel):
    action_text: str = Field(..., max_length=500, description="액션 내용")
    action_type: ActionType = Field(default=ActionType.review, description="액션 유형")
    priority_level: PriorityLevel = Field(default=PriorityLevel.p3, description="액션 우선순위")
    due_at: Optional[datetime] = Field(default=None, description="액션 마감 시각")


class AnalysisResult(BaseModel):
    email_id: EmailId
    urgency: UrgencyLevel
    short_summary: str = Field(..., max_length=1000, description="한 줄 요약")
    detailed_summary: str = Field(..., description="상세 요약")
    category: EmailCategory
    priority_level: PriorityLevel
    importance_score: float = Field(ge=0.0, le=100.0)
    urgency_score: float = Field(ge=0.0, le=100.0)
    confidence_score: float = Field(ge=0.0, le=100.0)
    needs_reply: bool
    has_deadline: bool
    deadline_at: Optional[datetime] = None
    deadline_text: str = Field(default="", max_length=255)
    time_sensitivity: TimeSensitivity = Field(default=TimeSensitivity.no_deadline)
    requires_action: bool = False
    user_task_summary: str = Field(default="", max_length=1000)
    priority_reason_codes: list[PriorityReasonCode] = Field(default_factory=list)
    suggested_action: str = Field(default="", max_length=255)
    reasoning: str = Field(default="")
    action_items: list[ActionItem] = Field(default_factory=list)
    model_name: str = Field(default="rule-based-agent")
    prompt_version: str = Field(default="rule-v1")

    @property
    def summary(self) -> str:
        return self.short_summary

    @property
    def confidence(self) -> float:
        return self.confidence_score / 100.0
