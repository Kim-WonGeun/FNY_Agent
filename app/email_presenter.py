from __future__ import annotations

from app.schemas import (
    EmailCategory,
    EmailInput,
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
