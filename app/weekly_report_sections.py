from __future__ import annotations

import re

from app.text_utils import normalize
from app.weekly_report_helpers import clean_report_text

LOW_SIGNAL_PATTERNS = (
    "채용",
    "공고",
    "recruit",
    "hiring",
    "job",
    "developer",
    "engineer",
    "linkedin",
    "saramin",
    "잡코리아",
    "광고",
    "프로모션",
    "할인",
    "coupon",
    "discount",
    "newsletter",
    "unsubscribe",
)

SECTION_SIGNALS: dict[str, tuple[str, ...]] = {
    "ISSUE": ("장애", "오류", "실패", "보안", "리스크", "지연", "긴급", "incident", "error", "failure"),
    "PENDING_DECISION": ("확인", "승인", "검토", "회신", "요청", "결정", "정산", "계약", "approval", "review", "reply"),
    "NEXT_PLAN": ("다음 주", "차주", "예정", "계획", "준비", "next week", "plan"),
    "HIGHLIGHT": ("완료", "공유", "개선", "반영", "진행", "배포", "성과", "released", "completed"),
}


def is_low_signal_report_mail(text: str) -> bool:
    normalized = normalize(text)
    return any(pattern.lower() in normalized for pattern in LOW_SIGNAL_PATTERNS)


def classify_report_section(text: str) -> str:
    normalized = normalize(text)
    for section in ("ISSUE", "PENDING_DECISION", "NEXT_PLAN", "HIGHLIGHT"):
        if any(signal.lower() in normalized for signal in SECTION_SIGNALS[section]):
            return section
    return "PROGRESS"


def split_report_sentences(text: str) -> list[str]:
    candidates = re.split(r"\n+|(?<=[.!?。])\s+|(?<=다\.)\s+", text or "")
    return [clean_report_text(candidate, 180) for candidate in candidates if clean_report_text(candidate, 180)]


def evidence_sentence(text: str, section: str) -> str:
    sentences = split_report_sentences(text)
    signals = SECTION_SIGNALS.get(section, ())
    for sentence in sentences:
        normalized = normalize(sentence)
        if any(signal.lower() in normalized for signal in signals):
            return sentence
    return sentences[0] if sentences else ""


def report_item(subject: str, evidence: str, section: str) -> str:
    subject = clean_report_text(subject, 80) or "관련 메일"
    evidence = clean_report_text(evidence, 160)

    if evidence and evidence != subject:
        return f"{subject}: {evidence}"

    endings = {
        "ISSUE": "관련 이슈를 확인했습니다.",
        "PENDING_DECISION": "관련 확인 및 의사결정이 필요합니다.",
        "NEXT_PLAN": "관련 후속 계획을 준비합니다.",
        "HIGHLIGHT": "관련 진행 내용을 확인했습니다.",
        "PROGRESS": "관련 진행 상황을 정리했습니다.",
    }
    return f"{subject} {endings.get(section, endings['PROGRESS'])}"
