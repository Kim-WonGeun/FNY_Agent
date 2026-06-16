from __future__ import annotations

from typing import Optional

from app.prompt_metadata import result_metadata
from app.schemas import PromptTemplate

SECTION_ORDER: tuple[str, ...] = ("HIGHLIGHT", "PROGRESS", "ISSUE", "PENDING_DECISION", "NEXT_PLAN")


def empty_section_items() -> dict[str, list[str]]:
    return {section: [] for section in SECTION_ORDER}


def executive_summary(total_count: int, business_count: int, excluded_count: int) -> str:
    if business_count == 0:
        return f"선택 기간 메일 {total_count}건을 검토했지만 보고서에 반영할 업무성 메일은 확인되지 않았습니다."
    if excluded_count > 0:
        return f"선택 기간 메일 {total_count}건 중 업무성 메일 {business_count}건을 기준으로 보고서 초안을 구성했습니다."
    return f"선택 기간 업무성 메일 {business_count}건을 기준으로 보고서 초안을 구성했습니다."


def report_metadata(prompt: Optional[PromptTemplate]) -> tuple[str, str]:
    return result_metadata(prompt, "weekly-report-agent", "weekly-report-v2")


def section_blocks(
    section_items: dict[str, list[str]],
) -> tuple[list[str], list[str], list[str], list[str]]:
    highlights = (section_items["HIGHLIGHT"] + section_items["PROGRESS"])[:5]
    risks = section_items["ISSUE"][:4]
    pending = section_items["PENDING_DECISION"][:5]
    next_plans = section_items["NEXT_PLAN"][:5]

    if not highlights:
        highlights = ["기간 내 완료 또는 주요 진척으로 분류할 업무성 메일은 확인되지 않았습니다."]
    if not risks:
        risks = ["별도 이슈나 리스크로 공유할 내용은 확인되지 않았습니다."]
    if not pending:
        pending = ["추가 확인이나 의사결정이 필요한 항목은 확인되지 않았습니다."]
    if not next_plans:
        next_plans = ["차주 계획으로 이어질 명확한 후속 일정은 확인되지 않았습니다."]

    return highlights, risks, pending, next_plans
