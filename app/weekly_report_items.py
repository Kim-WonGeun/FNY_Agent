from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.schemas import WeeklyEmailLine, WeeklyThreadSummary
from app.weekly_report_helpers import clean_report_text, extract_weekly_keywords
from app.weekly_report_sections import (
    classify_report_section,
    evidence_sentence,
    is_low_signal_report_mail,
    report_item,
)


@dataclass(frozen=True)
class WeeklyReportLineAnalysis:
    section: str
    item: str
    thread: WeeklyThreadSummary


def analyze_weekly_line(line: WeeklyEmailLine) -> Optional[WeeklyReportLineAnalysis]:
    subject = line.subject.strip() if line.subject else "(제목 없음)"
    text = f"{subject}\n{line.body_excerpt}"
    if is_low_signal_report_mail(text):
        return None

    section = classify_report_section(text)
    evidence = evidence_sentence(text, section)
    item = report_item(subject, evidence, section)
    line_keywords = extract_weekly_keywords(text, limit=5)
    one_liner = clean_report_text(evidence, 120) or ", ".join(line_keywords) or item

    return WeeklyReportLineAnalysis(
        section=section,
        item=item,
        thread=WeeklyThreadSummary(
            email_id=str(line.email_id),
            subject=subject,
            one_liner=one_liner,
        ),
    )
