from __future__ import annotations

from enum import Enum


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


class ActionType(str, Enum):
    reply = "REPLY"
    review = "REVIEW"
    approve = "APPROVE"
    schedule = "SCHEDULE"
    payment = "PAYMENT"
    follow_up = "FOLLOW_UP"
    archive = "ARCHIVE"


class PriorityReasonCode(str, Enum):
    needs_reply = "NEEDS_REPLY"
    has_deadline = "HAS_DEADLINE"
    urgent_keyword = "URGENT_KEYWORD"
    direct_to_me = "DIRECT_TO_ME"
    important_header = "IMPORTANT_HEADER"
    attachment = "ATTACHMENT"
    finance_related = "FINANCE_RELATED"
    meeting_related = "MEETING_RELATED"
    approval_required = "APPROVAL_REQUIRED"
    customer_or_contract = "CUSTOMER_OR_CONTRACT"
    no_strong_signal = "NO_STRONG_SIGNAL"
