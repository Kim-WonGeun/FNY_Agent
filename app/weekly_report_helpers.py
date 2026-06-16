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


def clean_report_text(text: str, limit: int = 180) -> str:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    cleaned = cleaned.replace("&nbsp;", " ")
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit].rstrip() + "..."
