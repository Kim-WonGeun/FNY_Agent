from __future__ import annotations

from app.schemas import WeeklyReportInput, WeeklyReportResult, WeeklyThreadSummary
from app.weekly_report_builder import empty_section_items, executive_summary, report_metadata, section_blocks
from app.weekly_report_items import analyze_weekly_line


class RuleBasedWeeklyReportAnalyzer:
    """메일 묶음에서 주간보고 초안을 만드는 룰 기반 분석기."""

    def analyze(self, payload: WeeklyReportInput) -> WeeklyReportResult:
        section_items = empty_section_items()
        threads: list[WeeklyThreadSummary] = []
        excluded_count = 0

        for line in payload.emails:
            analyzed_line = analyze_weekly_line(line)
            if analyzed_line is None:
                excluded_count += 1
                continue

            section_items[analyzed_line.section].append(analyzed_line.item)
            threads.append(analyzed_line.thread)

        n = len(payload.emails)
        business_count = len(threads)
        executive = executive_summary(n, business_count, excluded_count)
        model_name, prompt_version = report_metadata(payload.prompt)
        highlights, risks, pending, next_plans = section_blocks(section_items)

        return WeeklyReportResult(
            executive_summary=executive,
            highlights=highlights,
            risks_blockers=risks,
            pending_decisions=pending,
            next_week_suggestions=next_plans,
            thread_summaries=threads[:40],
            model_name=model_name,
            prompt_version=prompt_version,
        )


def analyze_weekly_report(payload: WeeklyReportInput) -> WeeklyReportResult:
    return RuleBasedWeeklyReportAnalyzer().analyze(payload)
