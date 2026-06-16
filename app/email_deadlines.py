from __future__ import annotations

import re

from app.schemas import TimeSensitivity, UrgencyLevel
from app.text_utils import contains_any


def time_sensitivity(urgency: UrgencyLevel, has_deadline: bool, haystack: str) -> TimeSensitivity:
    if urgency == UrgencyLevel.critical or contains_any(haystack, ("즉시", "asap", "immediately", "긴급")):
        return TimeSensitivity.immediate
    if contains_any(haystack, ("오늘", "당일", "today", "eod")):
        return TimeSensitivity.today
    if has_deadline:
        return TimeSensitivity.this_week
    return TimeSensitivity.no_deadline


def deadline_text(haystack: str, has_deadline: bool) -> str:
    if not has_deadline:
        return ""
    patterns = (
        r"(오늘까지|당일|내일까지|모레까지|이번 주\s*[가-힣]*까지|[0-9]{1,2}월\s*[0-9]{1,2}일\s*까지)",
        r"(by\s+[a-zA-Z]+\s+\d{1,2}|by\s+tomorrow|by\s+today|due\s+[a-zA-Z]+\s+\d{1,2})",
    )
    for pattern in patterns:
        match = re.search(pattern, haystack, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    return "메일에 마감/일정 관련 표현이 있습니다."
