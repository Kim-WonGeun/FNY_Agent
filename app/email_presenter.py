from __future__ import annotations

from app.schemas import (
    ActionItem,
    ActionType,
    EmailCategory,
    EmailInput,
    PriorityLevel,
    PriorityReasonCode,
    UrgencyLevel,
)
from app.text_utils import best_sentence, clean_sentence, contains_any


def short_summary(
    email: EmailInput,
    email_category: EmailCategory,
    needs_reply: bool,
    has_deadline: bool,
    haystack: str,
) -> str:
    topic = _topic_phrase(email, email_category, haystack)
    if needs_reply and has_deadline:
        return f"{topic}에 대해 기한 내 확인과 회신이 필요합니다."
    if needs_reply:
        return f"{topic}에 대한 확인 또는 회신이 필요합니다."
    if has_deadline:
        return f"{topic}에 일정 또는 마감 확인이 필요합니다."
    if email_category == EmailCategory.meeting:
        return f"{topic}과 참석 여부를 확인하면 좋습니다."
    if email_category == EmailCategory.finance:
        return f"{topic} 관련 증빙과 처리 여부를 확인하면 좋습니다."
    return f"{topic}을 확인하면 좋습니다."


def detailed_summary(
    email: EmailInput,
    email_category: EmailCategory,
    needs_reply: bool,
    has_deadline: bool,
    haystack: str,
) -> str:
    body = email.body_text or email.subject
    key_sentence = best_sentence(
        body,
        ("오늘", "내일", "마감", "회신", "승인", "고객", "계약", "정산", "회의", "보고", "검토"),
        _topic_phrase(email, email_category, haystack),
    )
    follow_up_parts: list[str] = []
    if needs_reply:
        follow_up_parts.append("회신 여부")
    if has_deadline:
        follow_up_parts.append("마감 일정")
    if email_category == EmailCategory.finance:
        follow_up_parts.append("증빙 또는 정산 내역")
    if email_category == EmailCategory.meeting:
        follow_up_parts.append("참석 여부와 안건")
    if email_category == EmailCategory.urgent:
        follow_up_parts.append("우선 처리 가능 여부")

    if follow_up_parts:
        return f"{key_sentence}. {', '.join(follow_up_parts)}를 확인해야 합니다."
    return f"{key_sentence}. 필요한 후속 확인이 있는지 검토하면 좋습니다."


def suggested_action_text(
    email_category: EmailCategory,
    needs_reply: bool,
    has_deadline: bool,
    haystack: str,
) -> str:
    if contains_any(haystack, ("승인", "approve", "approval")):
        return "승인 가능 여부와 보완 필요 항목을 회신"
    if needs_reply and has_deadline:
        return "기한 전에 검토 결과를 회신"
    if needs_reply:
        return "요청 내용을 확인하고 회신"
    if email_category == EmailCategory.meeting:
        return "회의 일정과 참석 가능 여부 확인"
    if email_category == EmailCategory.finance:
        return "정산 자료와 증빙 내역 확인"
    if email_category == EmailCategory.report:
        return "보고 자료에 반영할 내용 검토"
    if has_deadline:
        return "메일에 적힌 마감 일정 확인"
    return "필요한 후속 조치가 있는지 확인"


def action_items(
    email_category: EmailCategory,
    needs_reply: bool,
    has_deadline: bool,
    priority: PriorityLevel,
    suggested_action: str,
    haystack: str,
) -> list[ActionItem]:
    items: list[ActionItem] = []
    if contains_any(haystack, ("승인", "approve", "approval")):
        items.append(
            ActionItem(
                action_text="승인 가능 여부와 보완 필요 항목을 정리",
                action_type=ActionType.approve,
                priority_level=priority,
            )
        )
    if needs_reply:
        items.append(
            ActionItem(
                action_text=suggested_action,
                action_type=ActionType.reply,
                priority_level=priority,
            )
        )
    if has_deadline:
        items.append(
            ActionItem(
                action_text="메일에 적힌 일정과 처리 기한 확인",
                action_type=ActionType.schedule,
                priority_level=priority,
            )
        )
    if not items:
        items.append(
            ActionItem(
                action_text=suggested_action,
                action_type=_action_type(email_category, needs_reply),
                priority_level=priority,
            )
        )
    return items


def reasoning_text(
    priority_reason_codes: list[PriorityReasonCode],
    urgency: UrgencyLevel,
    priority: PriorityLevel,
) -> str:
    reason_labels = {
        PriorityReasonCode.urgent_keyword: "긴급 표현",
        PriorityReasonCode.needs_reply: "회신 요청",
        PriorityReasonCode.has_deadline: "일정 또는 마감 표현",
        PriorityReasonCode.approval_required: "승인 필요 표현",
        PriorityReasonCode.finance_related: "재무 관련 표현",
        PriorityReasonCode.meeting_related: "회의 또는 일정 표현",
        PriorityReasonCode.customer_or_contract: "고객/계약 영향",
        PriorityReasonCode.no_strong_signal: "강한 업무 신호 없음",
    }
    labels = [reason_labels.get(code, code.value) for code in priority_reason_codes]
    return f"{', '.join(labels)}을 근거로 {priority.value} 우선순위와 {urgency.value} 긴급도로 판단했습니다."


def user_task_summary(
    email_category: EmailCategory,
    needs_reply: bool,
    has_deadline: bool,
    suggested_action: str,
) -> str:
    if needs_reply and has_deadline:
        return "메일 내용을 확인하고 마감 전에 회신 또는 필요한 조치를 진행해야 합니다."
    if needs_reply:
        return "메일 내용을 확인하고 회신 필요 여부를 판단해야 합니다."
    if has_deadline:
        return "메일에 포함된 일정 또는 마감 정보를 확인해야 합니다."
    if email_category == EmailCategory.meeting:
        return "회의 일정과 참석 필요 여부를 확인해야 합니다."
    return suggested_action or "필요 시 메일 내용을 확인하면 됩니다."


def _topic_phrase(email: EmailInput, email_category: EmailCategory, haystack: str) -> str:
    subject = clean_sentence(email.subject, max_length=60)
    if subject:
        return subject
    if email_category == EmailCategory.finance:
        return "정산 및 재무 확인"
    if email_category == EmailCategory.meeting:
        return "회의 일정 확인"
    if email_category == EmailCategory.report:
        return "보고 자료 확인"
    if email_category == EmailCategory.urgent:
        return "긴급 요청"
    if contains_any(haystack, ("계약", "contract")):
        return "계약 검토"
    if contains_any(haystack, ("고객", "customer")):
        return "고객 요청"
    return "메일 내용"


def _action_type(email_category: EmailCategory, needs_reply: bool) -> ActionType:
    if needs_reply:
        return ActionType.reply
    if email_category == EmailCategory.meeting:
        return ActionType.schedule
    if email_category == EmailCategory.report:
        return ActionType.review
    if email_category == EmailCategory.finance:
        return ActionType.payment
    if email_category == EmailCategory.urgent:
        return ActionType.follow_up

    return ActionType.review
