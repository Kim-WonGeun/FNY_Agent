from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, constr


class Language(str, Enum):
    ko = "ko"
    en = "en"


EmailId = constr(pattern=r"^[A-Z]{3}_\d{6}_[A-Z0-9]{6}$")


class PromptTemplate(BaseModel):
    """서버 DB에서 관리하는 LLM 프롬프트 섹션"""

    prompt_code: str = Field(default="WEEKLY_REPORT", description="프롬프트 코드")
    version: int = Field(default=1, description="프롬프트 버전")
    model_name: str = Field(default="gpt-5.4-mini", description="사용 모델명")
    role: str = Field(default="", description="Role 섹션")
    policy: str = Field(default="", description="Policy 섹션")
    guide: str = Field(default="", description="Guide 섹션")
    output: str = Field(default="", description="Output 섹션")
