# 룰 기반 메일 분석기 (LLM 이전 단계)
# - 제목+본문에서 키워드로 긴급도, 회신 필요, 마감/일정 힌트만 판단

from __future__ import annotations

import re
from dataclasses import dataclass

from app.models import AnalysisResult, EmailInput, UrgencyLevel


@dataclass(frozen=True)
class _KeywordSet:
    """언어별 키워드 묶음 (확장 시 여기만 추가)"""

    urgent: tuple[str, ...]
    reply: tuple[str, ...]
    deadline_hint: tuple[str, ...]


_KO = _KeywordSet(
    urgent=("긴급", "즉시", "asap", "오늘까지", "당일", "마감", "데드라인"),
    reply=("회신", "답장", "답변", "확인 부탁", "검토 부탁", "연락", "reply"),
    deadline_hint=("마감", "까지", "내일", "모레", "회의", "일정", "deadline", "due"),
)

_EN = _KeywordSet(
    urgent=("urgent", "asap", "immediately", "today", "eod", "deadline"),
    reply=("reply", "please confirm", "get back", "respond", "let me know"),
    deadline_hint=("deadline", "due", "by ", "meeting", "tomorrow", "schedule"),
)


def _normalize(text: str) -> str:
    """검색용으로 소문자 + 공백 정리"""
    return re.sub(r"\s+", " ", text.strip().lower())


def _contains_any(haystack: str, needles: tuple[str, ...]) -> bool:
    return any(n in haystack for n in needles)


def _pick_keywords(language: str) -> _KeywordSet:
    if language == "en":
        return _EN
        
    return _KO


def _score_urgency(haystack: str, ks: _KeywordSet) -> UrgencyLevel:
    """키워드 강도에 따라 긴급도 결정 (단순 우선순위)"""
    if _contains_any(haystack, ("긴급", "urgent", "critical", "즉시", "immediately")):
        return UrgencyLevel.critical
    if _contains_any(haystack, ks.urgent):
        return UrgencyLevel.high
    if _contains_any(haystack, ks.deadline_hint):
        return UrgencyLevel.medium
        
    return UrgencyLevel.low


def analyze_email(email: EmailInput) -> AnalysisResult:
    """
    룰 기반 분석: LLM 없이 키워드로 최소 판단만 수행.
    - deadline_at: 날짜 파싱은 다음 단계(파서 또는 LLM)에서 채움
    """
    combined = _normalize(f"{email.subject}\n{email.body_text}")
    ks = _pick_keywords(email.language.value)

    urgency = _score_urgency(combined, ks)
    needs_reply = _contains_any(combined, ks.reply)
    has_deadline = _contains_any(combined, ks.deadline_hint)

    # 요약: 어떤 신호가 있었는지 한 줄로 (300자 제한 내)
    parts: list[str] = []
    parts.append(f"긴급도: {urgency.value}")

    if needs_reply:
        parts.append("회신/확인 요청 키워드 감지")
    if has_deadline:
        parts.append("일정·마감 관련 키워드 감지")
    if not parts:
        parts.append("특이 키워드 없음")

    summary = " / ".join(parts)


    action_items: list[str] = []

    if needs_reply:
        action_items.append("발신자 요청 확인 후 회신 여부 결정")
    if has_deadline:
        action_items.append("일정·마감 일시 확인 (캘린더 반영 검토)")

    # 룰만 쓸 때는 확신도를 낮게 두는 편이 안전 (0~1)
    confidence = 0.55 if urgency != UrgencyLevel.low or needs_reply or has_deadline else 0.35

    return AnalysisResult(
        email_id=email.email_id,
        urgency=urgency,
        summary=summary,
        needs_reply=needs_reply,
        has_deadline=has_deadline,
        deadline_at=None,
        action_items=action_items,
        confidence=confidence,
    )