from __future__ import annotations

import re
from typing import Callable, Iterable, Optional, TypeVar


T = TypeVar("T")


def clean_text(value: str, limit: Optional[int] = None) -> str:
    cleaned = re.sub(r"[\u200b-\u200f\ufeff]", "", value or "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:limit] if limit else cleaned


def clean_list(values: Iterable[str], limit: int) -> list[str]:
    cleaned = [clean_text(value, 500) for value in values]
    return list(dict.fromkeys(value for value in cleaned if value))[:limit]


def dedupe_by(values: Iterable[T], key: Callable[[T], str]) -> list[T]:
    result: list[T] = []
    seen: set[str] = set()
    for value in values:
        marker = key(value)
        if not marker or marker in seen:
            continue
        seen.add(marker)
        result.append(value)
    return result
