from __future__ import annotations

import unittest
from datetime import datetime

from app.schemas import WeeklyEmailLine
from app.weekly_report_items import analyze_weekly_line
from tests.helpers import weekly_report_payload


class WeeklyReportItemsTest(unittest.TestCase):
    def test_analyze_weekly_line_builds_section_item_and_thread(self) -> None:
        line = weekly_report_payload().emails[0]

        analyzed_line = analyze_weekly_line(line)

        self.assertIsNotNone(analyzed_line)
        assert analyzed_line is not None
        self.assertEqual(analyzed_line.section, "PENDING_DECISION")
        self.assertEqual(analyzed_line.item, "고객 계약 검토 관련 확인 및 의사결정이 필요합니다.")
        self.assertEqual(analyzed_line.thread.email_id, "EML_260328_A1B2C3")
        self.assertEqual(analyzed_line.thread.subject, "고객 계약 검토")

    def test_analyze_weekly_line_excludes_low_signal_mail(self) -> None:
        line = WeeklyEmailLine(
            email_id="EML_260328_LOW001",
            subject="채용 공고 안내",
            body_excerpt="newsletter unsubscribe",
            from_email="jobs@test.com",
            received_at=datetime(2026, 3, 28, 9, 0, 0),
        )

        self.assertIsNone(analyze_weekly_line(line))
