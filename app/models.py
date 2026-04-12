from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, constr


# 메일 긴급도 분류를 위한 Enum
# - 분석 결과는 반드시 아래 4가지 값 중 하나만 허용
class UrgencyLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class PriorityLevel(str, Enum):
    p1 = "P1"
    p2 = "P2"
    p3 = "P3"
    p4 = "P4"


class EmailCategory(str, Enum):
    urgent = "URGENT"
    request = "REQUEST"
    meeting = "MEETING"
    report = "REPORT"
    finance = "FINANCE"
    general = "GENERAL"


# 메일 언어 코드 Enum
# - 초기에 ko/en만 허용하여 입력 품질을 통제
class Language(str, Enum):
    ko = "ko"
    en = "en"


# 메일 ID 형식 타입
# - 규칙: PREFIX_YYMMDD_RANDOM6
# - 예시: EML_260324_A1B2C3
EmailId = constr(pattern=r"^[A-Z]{3}_\d{6}_[A-Z0-9]{6}$")


# 메일 분석 요청(입력) 모델
# - Spring Boot -> Python Agent 로 전달되는 payload 스키마
class EmailInput(BaseModel):
    email_id: EmailId = Field(..., description="메일 고유 ID")
    subject: str = Field(default="", description="메일 제목")
    body_text: str = Field(default="", description="메일 본문 텍스트")
    from_email: EmailStr = Field(..., description="발신자 이메일")
    received_at: datetime = Field(..., description="수신 시각(ISO-8601)")
    language: Language = Field(default=Language.ko, description="메일 언어")


class ActionItem(BaseModel):
    action_text: str = Field(..., max_length=500, description="액션 내용")
    action_type: str = Field(default="REVIEW", max_length=50, description="액션 유형")
    priority_level: PriorityLevel = Field(default=PriorityLevel.p3, description="액션 우선순위")
    due_at: Optional[datetime] = Field(default=None, description="액션 마감 시각")


# 메일 분석 응답(출력) 모델
# - Python Agent -> Spring Boot 로 반환되는 결과 스키마
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
    suggested_action: str = Field(default="", max_length=255)
    reasoning: str = Field(default="")
    action_items: List[ActionItem] = Field(default_factory=list)
    model_name: str = Field(default="rule-based-agent")
    prompt_version: str = Field(default="rule-v1")

    @property
    def summary(self) -> str:
        return self.short_summary

    @property
    def confidence(self) -> float:
        return self.confidence_score / 100.0
