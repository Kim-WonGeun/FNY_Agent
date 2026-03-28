from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, constr


# 메일 긴급도 분류를 위한 Enum
# - 분석 결과는 반드시 아래 4가지 값 중 하나만 허용
class UrgencyLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


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


# 메일 분석 응답(출력) 모델
# - Python Agent -> Spring Boot 로 반환되는 결과 스키마
class AnalysisResult(BaseModel):
    email_id: EmailId
    urgency: UrgencyLevel
    summary: str = Field(..., max_length=300, description="분석 요약(최대 300자)")
    needs_reply: bool
    has_deadline: bool
    deadline_at: datetime | None = None
    action_items: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)