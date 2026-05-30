from __future__ import annotations

from app.schemas import WeeklyReportInput, WeeklyReportResult, WeeklyThreadSummary
from app.weekly_report_helpers import extract_weekly_keywords, keyword_group, report_line


class RuleBasedWeeklyReportAnalyzer:
    """메일 묶음에서 주간보고 초안을 만드는 룰 기반 분석기."""

    def analyze(self, payload: WeeklyReportInput) -> WeeklyReportResult:
        corpus_parts: list[str] = []
        threads: list[WeeklyThreadSummary] = []

        for line in payload.emails:
            subj = line.subject.strip() if line.subject else "(제목 없음)"
            text = f"{subj}\n{line.body_excerpt}"
            line_keywords = extract_weekly_keywords(text, limit=6)
            corpus_parts.append(text)
            threads.append(
                WeeklyThreadSummary(
                    email_id=str(line.email_id),
                    subject=subj,
                    one_liner=", ".join(line_keywords),
                )
            )

        keywords = extract_weekly_keywords("\n".join(corpus_parts), limit=24)
        issue_keywords = keyword_group(
            keywords,
            ("장애", "보안", "계약", "정산", "세금계산서", "예산", "결제", "인프라"),
        )
        work_keywords = keyword_group(
            keywords,
            ("승인", "검토", "확인", "요청", "일정", "회의록", "권한", "정책"),
        )
        topic_keywords = keyword_group(
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
                report_line("금주실적", topic_keywords or keywords, "금주실적: 선택 기간 메일에서 주요 완료 내용을 추가 확인해 주세요."),
                report_line("진행사항", work_keywords or keywords, "진행사항: 검토 중인 업무를 메일 원문 기준으로 보강해 주세요."),
            ],
            risks_blockers=[
                report_line("특이사항", issue_keywords, "특이사항: 별도 이슈로 분류할 키워드가 뚜렷하지 않습니다."),
            ],
            pending_decisions=[
                report_line("확인필요", work_keywords, "확인필요: 추가 확인이 필요한 항목이 뚜렷하지 않습니다."),
            ],
            next_week_suggestions=[
                report_line("차주계획", (work_keywords + topic_keywords)[:8], "차주계획: 금주 메일 흐름을 바탕으로 다음 주 계획을 보강해 주세요."),
            ],
            thread_summaries=threads[:40],
            model_name=model_name,
            prompt_version=prompt_version,
        )


def analyze_weekly_report(payload: WeeklyReportInput) -> WeeklyReportResult:
    return RuleBasedWeeklyReportAnalyzer().analyze(payload)
