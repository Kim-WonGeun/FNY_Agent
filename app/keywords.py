from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KeywordSet:
    urgent: tuple[str, ...]
    reply: tuple[str, ...]
    deadline_hint: tuple[str, ...]
    meeting: tuple[str, ...]
    report: tuple[str, ...]
    finance: tuple[str, ...]
    request: tuple[str, ...]


KO_KEYWORDS = KeywordSet(
    urgent=("긴급", "즉시", "asap", "오늘까지", "당일", "마감", "데드라인"),
    reply=("회신", "답장", "답변", "확인 부탁", "검토 부탁", "연락", "reply"),
    deadline_hint=("마감", "까지", "내일", "모레", "회의", "일정", "deadline", "due"),
    meeting=("회의", "미팅", "일정", "캘린더", "참석"),
    report=("보고", "보고서", "공유", "회고", "update"),
    finance=("세금계산서", "계산서", "정산", "결제", "입금", "재무"),
    request=("요청", "부탁", "확인", "검토", "전달"),
)

EN_KEYWORDS = KeywordSet(
    urgent=("urgent", "asap", "immediately", "today", "eod", "deadline"),
    reply=("reply", "please confirm", "get back", "respond", "let me know"),
    deadline_hint=("deadline", "due", "by ", "meeting", "tomorrow", "schedule"),
    meeting=("meeting", "schedule", "calendar", "attend", "invite"),
    report=("report", "weekly", "update", "retrospective", "share"),
    finance=("invoice", "payment", "tax", "settlement", "finance"),
    request=("request", "please", "confirm", "review", "check"),
)

WEEKLY_KEYWORDS = (
    "승인",
    "고객",
    "미팅",
    "정산",
    "세금계산서",
    "배포",
    "QA",
    "계약",
    "장애",
    "보안",
    "예산",
    "릴리즈",
    "파트너",
    "마케팅",
    "데이터",
    "인프라",
    "결제",
    "운영",
    "정책",
    "성과",
    "회의록",
    "일정",
    "검토",
    "확인",
    "요청",
    "보고",
    "공유",
    "권한",
    "알림",
)

WEEKLY_STOPWORDS = {
    "안녕하세요",
    "부탁드립니다",
    "공유드립니다",
    "확인해",
    "주세요",
    "이번",
    "다음",
    "오늘",
    "관련",
    "필요합니다",
    "있습니다",
    "합니다",
}


def pick_keywords(language: str) -> KeywordSet:
    if language == "en":
        return EN_KEYWORDS
    return KO_KEYWORDS
