from __future__ import annotations

import re


TRAILING_POLITE_PHRASES = (
    "부탁드립니다",
    "부탁드려요",
    "감사합니다",
    "주세요",
    "드립니다",
)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def contains_any(haystack: str, needles: tuple[str, ...]) -> bool:
    return any(needle in haystack for needle in needles)


def sentence_candidates(text: str) -> list[str]:
    compact = re.sub(r"\s+", " ", text.strip())
    if not compact:
        return []
    parts = re.split(r"(?<=[.!?。！？])\s+|(?<=[다요죠함임])\.\s*|\n+", compact)
    return [part.strip(" .") for part in parts if part.strip(" .")]


def clean_sentence(text: str, max_length: int = 90) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip(" ."))
    for phrase in TRAILING_POLITE_PHRASES:
        cleaned = re.sub(rf"\s*{phrase}\.?$", "", cleaned)
    cleaned = re.sub(r"(확인|검토|회신|전달|정리|공유|제출)해$", r"\1해야 합니다", cleaned)
    if len(cleaned) <= max_length:
        return cleaned
    return cleaned[:max_length].rstrip() + "..."


def best_sentence(text: str, keywords: tuple[str, ...], fallback: str) -> str:
    sentences = sentence_candidates(text)
    if not sentences:
        return fallback

    normalized_keywords = tuple(keyword.lower() for keyword in keywords)
    scored: list[tuple[int, int, str]] = []
    for index, sentence in enumerate(sentences):
        lowered = sentence.lower()
        score = sum(2 for keyword in normalized_keywords if keyword and keyword in lowered)
        if any(token in lowered for token in ("오늘", "내일", "마감", "회신", "승인", "고객", "계약")):
            score += 1
        scored.append((score, -index, sentence))

    scored.sort(reverse=True)
    return clean_sentence(scored[0][2])
