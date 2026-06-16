from __future__ import annotations

from app.schemas import EmailCategory, PriorityLevel, PriorityReasonCode, UrgencyLevel
from app.text_utils import contains_any


REASON_LABELS: dict[PriorityReasonCode, str] = {
    PriorityReasonCode.urgent_keyword: "긴급 표현",
    PriorityReasonCode.needs_reply: "회신 요청",
    PriorityReasonCode.has_deadline: "일정 또는 마감 표현",
    PriorityReasonCode.approval_required: "승인 필요 표현",
    PriorityReasonCode.finance_related: "재무 관련 표현",
    PriorityReasonCode.meeting_related: "회의 또는 일정 표현",
    PriorityReasonCode.customer_or_contract: "고객/계약 영향",
    PriorityReasonCode.no_strong_signal: "강한 업무 신호 없음",
}


def priority_reason_codes(
    urgency: UrgencyLevel,
    needs_reply: bool,
    has_deadline: bool,
    email_category: EmailCategory,
    haystack: str,
) -> list[PriorityReasonCode]:
    codes: list[PriorityReasonCode] = []
    if urgency in (UrgencyLevel.critical, UrgencyLevel.high):
        codes.append(PriorityReasonCode.urgent_keyword)
    if needs_reply:
        codes.append(PriorityReasonCode.needs_reply)
    if has_deadline:
        codes.append(PriorityReasonCode.has_deadline)
    if contains_any(haystack, ("승인", "approve", "approval")):
        codes.append(PriorityReasonCode.approval_required)
    if email_category == EmailCategory.finance:
        codes.append(PriorityReasonCode.finance_related)
    if email_category == EmailCategory.meeting:
        codes.append(PriorityReasonCode.meeting_related)
    if contains_any(haystack, ("고객", "장애", "계약", "customer", "incident", "contract")):
        codes.append(PriorityReasonCode.customer_or_contract)
    if not codes:
        codes.append(PriorityReasonCode.no_strong_signal)
    return codes


def reasoning_text(
    reason_codes: list[PriorityReasonCode],
    urgency: UrgencyLevel,
    priority: PriorityLevel,
) -> str:
    labels = [REASON_LABELS.get(code, code.value) for code in reason_codes]
    return f"{', '.join(labels)}을 근거로 {priority.value} 우선순위와 {urgency.value} 긴급도로 판단했습니다."
