from __future__ import annotations

from app.schemas import ActionItem, ActionType, EmailCategory, PriorityLevel
from app.text_utils import contains_any


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
