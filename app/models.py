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


class TimeSensitivity(str, Enum):
    immediate = "IMMEDIATE"
    today = "TODAY"
    this_week = "THIS_WEEK"
    no_deadline = "NO_DEADLINE"


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
class WeeklyEmailLine(BaseModel):
    """주간 집계용 메일 한 줄(본문은 발췌)"""

    email_id: EmailId
    subject: str = Field(default="", description="메일 제목")
    body_excerpt: str = Field(default="", description="본문 발췌")
    from_email: EmailStr = Field(..., description="발신자 이메일")
    received_at: datetime = Field(..., description="수신 시각")


class PromptTemplate(BaseModel):
    """서버 DB에서 관리하는 LLM 프롬프트 섹션"""

    prompt_code: str = Field(default="WEEKLY_REPORT", description="프롬프트 코드")
    version: int = Field(default=1, description="프롬프트 버전")
    model_name: str = Field(default="gpt-5.4-mini", description="사용 모델명")
    role: str = Field(default="", description="Role 섹션")
    policy: str = Field(default="", description="Policy 섹션")
    guide: str = Field(default="", description="Guide 섹션")
    output: str = Field(default="", description="Output 섹션")


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
    priority_reason_codes: list[str] = Field(default_factory=list)
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
