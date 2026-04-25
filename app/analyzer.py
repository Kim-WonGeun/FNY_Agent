# 룰 기반 메일 분석기 (LLM 이전 단계)
# - 제목+본문에서 키워드로 긴급도, 회신 필요, 마감/일정 힌트만 판단

from __future__ import annotations

import re
from dataclasses import dataclass

from app.models import (
    ActionItem,
    AnalysisResult,
    EmailCategory,
    EmailInput,
    PriorityLevel,
    TimeSensitivity,
    UrgencyLevel,
    WeeklyReportInput,
    WeeklyReportResult,
    WeeklyThreadSummary,
)


@dataclass(frozen=True)
class _KeywordSet:
    """언어별 키워드 묶음 (확장 시 여기만 추가)"""

    urgent: tuple[str, ...]
    reply: tuple[str, ...]
    deadline_hint: tuple[str, ...]
    meeting: tuple[str, ...]
    report: tuple[str, ...]
    finance: tuple[str, ...]
    request: tuple[str, ...]


_KO = _KeywordSet(
    urgent=("긴급", "즉시", "asap", "오늘까지", "당일", "마감", "데드라인"),
    reply=("회신", "답장", "답변", "확인 부탁", "검토 부탁", "연락", "reply"),
    deadline_hint=("마감", "까지", "내일", "모레", "회의", "일정", "deadline", "due"),
    meeting=("회의", "미팅", "일정", "캘린더", "참석"),
    report=("보고", "보고서", "공유", "회고", "update"),
    finance=("세금계산서", "계산서", "정산", "결제", "입금", "재무"),
    request=("요청", "부탁", "확인", "검토", "전달"),
)

_EN = _KeywordSet(
    urgent=("urgent", "asap", "immediately", "today", "eod", "deadline"),
    reply=("reply", "please confirm", "get back", "respond", "let me know"),
    deadline_hint=("deadline", "due", "by ", "meeting", "tomorrow", "schedule"),
    meeting=("meeting", "schedule", "calendar", "attend", "invite"),
    report=("report", "weekly", "update", "retrospective", "share"),
    finance=("invoice", "payment", "tax", "settlement", "finance"),
    request=("request", "please", "confirm", "review", "check"),
)

_WEEKLY_KEYWORDS = (
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

_WEEKLY_STOPWORDS = {
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


def _normalize(text: str) -> str:
    """검색용으로 소문자 + 공백 정리"""
    return re.sub(r"\s+", " ", text.strip().lower())


def _contains_any(haystack: str, needles: tuple[str, ...]) -> bool:
    return any(n in haystack for n in needles)


def _pick_keywords(language: str) -> _KeywordSet:
    if language == "en":
        return _EN
        
    return _KO


def _extract_weekly_keywords(text: str, limit: int = 12) -> list[str]:
    normalized = _normalize(text)
    scores: dict[str, int] = {}

    for keyword in _WEEKLY_KEYWORDS:
        count = normalized.count(keyword.lower())
        if count > 0:
            scores[keyword] = scores.get(keyword, 0) + count * 3

    for token in re.findall(r"[가-힣A-Za-z0-9]{2,}", text):
        if token in _WEEKLY_STOPWORDS:
            continue
        if token.lower() in _WEEKLY_STOPWORDS:
            continue
        scores[token] = scores.get(token, 0) + 1

    return [
        keyword
        for keyword, _ in sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def _keyword_group(keywords: list[str], candidates: tuple[str, ...], limit: int = 10) -> list[str]:
    selected = [keyword for keyword in keywords if keyword in candidates]
    return selected[:limit]


def _report_line(prefix: str, keywords: list[str], fallback: str) -> str:
    selected = keywords[:5]
    if not selected:
        return fallback
    return f"{prefix}: {', '.join(selected)} 관련 내용을 정리했습니다."


def _score_urgency(haystack: str, ks: _KeywordSet) -> UrgencyLevel:
    """키워드 강도에 따라 긴급도 결정 (단순 우선순위)"""
    if _contains_any(haystack, ("긴급", "urgent", "critical", "즉시", "immediately")):
        return UrgencyLevel.critical
    if _contains_any(haystack, ks.urgent):
        return UrgencyLevel.high
    if _contains_any(haystack, ks.deadline_hint):
        return UrgencyLevel.medium
        
    return UrgencyLevel.low


def _urgency_score(urgency: UrgencyLevel, needs_reply: bool, has_deadline: bool) -> float:
    base = {
        UrgencyLevel.critical: 95.0,
        UrgencyLevel.high: 82.0,
        UrgencyLevel.medium: 62.0,
        UrgencyLevel.low: 28.0,
    }[urgency]

    if needs_reply:
        base += 6.0
    if has_deadline:
        base += 8.0

    return min(base, 100.0)


def _importance_score(haystack: str, ks: _KeywordSet, urgency: UrgencyLevel, needs_reply: bool) -> float:
    score = 45.0

    if urgency in (UrgencyLevel.critical, UrgencyLevel.high):
        score += 24.0
    elif urgency == UrgencyLevel.medium:
        score += 12.0

    if needs_reply:
        score += 16.0
    if _contains_any(haystack, ks.request):
        score += 8.0
    if _contains_any(haystack, ks.finance):
        score += 10.0

    return min(score, 100.0)


def _priority_level(urgency_score: float, importance_score: float, needs_reply: bool) -> PriorityLevel:
    combined = (urgency_score * 0.55) + (importance_score * 0.45)

    if combined >= 86 or (urgency_score >= 90 and needs_reply):
        return PriorityLevel.p1
    if combined >= 68:
        return PriorityLevel.p2
    if combined >= 45:
        return PriorityLevel.p3

    return PriorityLevel.p4


def _category(haystack: str, ks: _KeywordSet, urgency: UrgencyLevel) -> EmailCategory:
    if urgency == UrgencyLevel.critical:
        return EmailCategory.urgent
    if _contains_any(haystack, ks.finance):
        return EmailCategory.finance
    if _contains_any(haystack, ks.meeting):
        return EmailCategory.meeting
    if _contains_any(haystack, ks.report):
        return EmailCategory.report
    if _contains_any(haystack, ks.request):
        return EmailCategory.request

    return EmailCategory.general


def _action_type(category: EmailCategory, needs_reply: bool) -> str:
    if needs_reply:
        return "REPLY"
    if category == EmailCategory.meeting:
        return "SCHEDULE"
    if category == EmailCategory.report:
        return "REVIEW"
    if category == EmailCategory.finance:
        return "ARCHIVE"
    if category == EmailCategory.urgent:
        return "ESCALATE"

    return "REVIEW"


def _suggested_action(category: EmailCategory, needs_reply: bool, has_deadline: bool) -> str:
    if needs_reply:
        return "내용 확인 후 회신"
    if category == EmailCategory.meeting:
        return "회의 일정 확인"
    if category == EmailCategory.finance:
        return "재무 증빙 확인"
    if category == EmailCategory.report:
        return "공유 내용 검토"
    if has_deadline:
        return "마감 일정 확인"

    return "필요 시 내용 확인"


def _time_sensitivity(urgency: UrgencyLevel, has_deadline: bool, haystack: str) -> TimeSensitivity:
    if urgency == UrgencyLevel.critical or _contains_any(haystack, ("즉시", "asap", "immediately", "긴급")):
        return TimeSensitivity.immediate
    if _contains_any(haystack, ("오늘", "당일", "today", "eod")):
        return TimeSensitivity.today
    if has_deadline:
        return TimeSensitivity.this_week
    return TimeSensitivity.no_deadline


def _deadline_text(haystack: str, has_deadline: bool) -> str:
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


def _priority_reason_codes(
    urgency: UrgencyLevel,
    needs_reply: bool,
    has_deadline: bool,
    category: EmailCategory,
    haystack: str,
) -> list[str]:
    codes: list[str] = []
    if urgency in (UrgencyLevel.critical, UrgencyLevel.high):
        codes.append("HIGH_URGENCY")
    if needs_reply:
        codes.append("NEEDS_REPLY")
    if has_deadline:
        codes.append("DEADLINE_SIGNAL")
    if category == EmailCategory.urgent:
        codes.append("URGENT_CATEGORY")
    if category == EmailCategory.finance:
        codes.append("FINANCE_RELATED")
    if category == EmailCategory.meeting:
        codes.append("MEETING_RELATED")
    if _contains_any(haystack, ("고객", "장애", "계약", "customer", "incident", "contract")):
        codes.append("BUSINESS_IMPACT")
    if not codes:
        codes.append("NO_STRONG_SIGNAL")
    return codes


def _user_task_summary(category: EmailCategory, needs_reply: bool, has_deadline: bool, suggested_action: str) -> str:
    if needs_reply and has_deadline:
        return "메일 내용을 확인하고 마감 전에 회신 또는 필요한 조치를 진행해야 합니다."
    if needs_reply:
        return "메일 내용을 확인하고 회신 필요 여부를 판단해야 합니다."
    if has_deadline:
        return "메일에 포함된 일정 또는 마감 정보를 확인해야 합니다."
    if category == EmailCategory.meeting:
        return "회의 일정과 참석 필요 여부를 확인해야 합니다."
    return suggested_action or "필요 시 메일 내용을 확인하면 됩니다."


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
    category = _category(combined, ks, urgency)
    urgency_score = _urgency_score(urgency, needs_reply, has_deadline)
    importance_score = _importance_score(combined, ks, urgency, needs_reply)
    priority_level = _priority_level(urgency_score, importance_score, needs_reply)
    suggested_action = _suggested_action(category, needs_reply, has_deadline)
    time_sensitivity = _time_sensitivity(urgency, has_deadline, combined)
    deadline_text = _deadline_text(combined, has_deadline)
    requires_action = needs_reply or has_deadline or category in {
        EmailCategory.urgent,
        EmailCategory.request,
        EmailCategory.meeting,
        EmailCategory.report,
        EmailCategory.finance,
    }
    user_task_summary = _user_task_summary(category, needs_reply, has_deadline, suggested_action)
    priority_reason_codes = _priority_reason_codes(urgency, needs_reply, has_deadline, category, combined)

    parts: list[str] = [f"긴급도 {urgency.value}", f"우선순위 {priority_level.value}"]

    if needs_reply:
        parts.append("회신/확인 요청 키워드 감지")
    if has_deadline:
        parts.append("일정·마감 관련 키워드 감지")
    if not parts:
        parts.append("특이 키워드 없음")

    short_summary = " / ".join(parts)
    detailed_summary = (
        f"제목과 본문에서 {category.value} 성격의 메일로 판단했습니다. "
        f"긴급도 점수는 {urgency_score:.0f}, 중요도 점수는 {importance_score:.0f}입니다."
    )

    action_items: list[ActionItem] = []

    if needs_reply:
        action_items.append(
            ActionItem(
                action_text="발신자 요청 확인 후 회신 여부 결정",
                action_type="REPLY",
                priority_level=priority_level,
            )
        )
    if has_deadline:
        action_items.append(
            ActionItem(
                action_text="일정·마감 일시 확인",
                action_type="SCHEDULE",
                priority_level=priority_level,
            )
        )
    if not action_items:
        action_items.append(
            ActionItem(
                action_text=suggested_action,
                action_type=_action_type(category, needs_reply),
                priority_level=priority_level,
            )
        )

    confidence_score = 55.0 if urgency != UrgencyLevel.low or needs_reply or has_deadline else 35.0

    return AnalysisResult(
        email_id=email.email_id,
        urgency=urgency,
        short_summary=short_summary,
        detailed_summary=detailed_summary,
        category=category,
        priority_level=priority_level,
        importance_score=importance_score,
        urgency_score=urgency_score,
        confidence_score=confidence_score,
        needs_reply=needs_reply,
        has_deadline=has_deadline,
        deadline_at=None,
        deadline_text=deadline_text,
        time_sensitivity=time_sensitivity,
        requires_action=requires_action,
        user_task_summary=user_task_summary,
        priority_reason_codes=priority_reason_codes,
        suggested_action=suggested_action,
        reasoning=" / ".join(parts),
        action_items=action_items,
    )


def analyze_weekly_report(payload: WeeklyReportInput) -> WeeklyReportResult:
    """
    주간보고용: 메일 제목/본문에서 금주실적, 차주계획, 특이사항 초안을 만든다.
    (LLM 연동 전 단계에서도 구조화된 JSON을 반환)
    """
    corpus_parts: list[str] = []
    threads: list[WeeklyThreadSummary] = []

    for line in payload.emails:
        subj = line.subject.strip() if line.subject else "(제목 없음)"
        text = f"{subj}\n{line.body_excerpt}"
        line_keywords = _extract_weekly_keywords(text, limit=6)
        corpus_parts.append(text)
        threads.append(
            WeeklyThreadSummary(
                email_id=str(line.email_id),
                subject=subj,
                one_liner=", ".join(line_keywords),
            )
        )

    keywords = _extract_weekly_keywords("\n".join(corpus_parts), limit=24)
    issue_keywords = _keyword_group(
        keywords,
        ("장애", "보안", "계약", "정산", "세금계산서", "예산", "결제", "인프라"),
    )
    work_keywords = _keyword_group(
        keywords,
        ("승인", "검토", "확인", "요청", "일정", "회의록", "권한", "정책"),
    )
    topic_keywords = _keyword_group(
        keywords,
        ("고객", "미팅", "배포", "QA", "릴리즈", "파트너", "마케팅", "데이터", "운영", "성과", "보고", "공유"),
    )
    n = len(payload.emails)
    executive = f"선택 기간 메일 {n}건을 바탕으로 주간보고 초안을 구성했습니다."

    model_name = payload.prompt.model_name if payload.prompt else "weekly-report-agent"
    prompt_version = f"{payload.prompt.prompt_code}-v{payload.prompt.version}" if payload.prompt else "weekly-report-v1"

    return WeeklyReportResult(
        executive_summary=executive,
        highlights=[
            _report_line("금주실적", topic_keywords or keywords, "금주실적: 선택 기간 메일에서 주요 완료 내용을 추가 확인해 주세요."),
            _report_line("진행사항", work_keywords or keywords, "진행사항: 검토 중인 업무를 메일 원문 기준으로 보강해 주세요."),
        ],
        risks_blockers=[
            _report_line("특이사항", issue_keywords, "특이사항: 별도 이슈로 분류할 키워드가 뚜렷하지 않습니다."),
        ],
        pending_decisions=[
            _report_line("확인필요", work_keywords, "확인필요: 추가 확인이 필요한 항목이 뚜렷하지 않습니다."),
        ],
        next_week_suggestions=[
            _report_line("차주계획", (work_keywords + topic_keywords)[:8], "차주계획: 금주 메일 흐름을 바탕으로 다음 주 계획을 보강해 주세요."),
        ],
        thread_summaries=threads[:40],
        model_name=model_name,
        prompt_version=prompt_version,
    )
