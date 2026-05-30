from __future__ import annotations

import re

from app.keywords import WEEKLY_KEYWORDS, WEEKLY_STOPWORDS
from app.text_utils import normalize


def extract_weekly_keywords(text: str, limit: int = 12) -> list[str]:
    normalized = normalize(text)
    scores: dict[str, int] = {}

    for keyword in WEEKLY_KEYWORDS:
        count = normalized.count(keyword.lower())
        if count > 0:
            scores[keyword] = scores.get(keyword, 0) + count * 3

    for token in re.findall(r"[가-힣A-Za-z0-9]{2,}", text):
        if token in WEEKLY_STOPWORDS:
            continue
        if token.lower() in WEEKLY_STOPWORDS:
            continue
        scores[token] = scores.get(token, 0) + 1

    return [
        keyword
        for keyword, _ in sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def keyword_group(keywords: list[str], candidates: tuple[str, ...], limit: int = 10) -> list[str]:
    selected = [keyword for keyword in keywords if keyword in candidates]
    return selected[:limit]


def report_line(prefix: str, keywords: list[str], fallback: str) -> str:
    selected = keywords[:5]
    if not selected:
        return fallback
    return f"{prefix}: {', '.join(selected)} 관련 내용을 정리했습니다."
