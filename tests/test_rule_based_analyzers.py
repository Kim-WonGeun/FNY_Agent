from __future__ import annotations

import unittest
from datetime import datetime

from app.analyzer import analyze_email, analyze_weekly_report
from app.email_analyzer import RuleBasedEmailAnalyzer
from app.providers import get_email_analyzer, get_weekly_report_analyzer
from app.schemas import EmailInput, Language, WeeklyEmailLine, WeeklyReportInput
from app.weekly_report import RuleBasedWeeklyReportAnalyzer


class AnalyzeEmailTest(unittest.TestCase):
    def test_urgent_reply_email_returns_p1_actionable_result(self) -> None:
        email = EmailInput(
            email_id="EML_260328_X9Y8Z7",
            subject="긴급: 오늘 중 회신",
            body_text="확인 부탁드립니다.",
            from_email="boss@test.com",
            received_at=datetime(2026, 3, 28, 9, 0, 0),
            language=Language.ko,
        )

        result = analyze_email(email)

        self.assertEqual(result.urgency.value, "critical")
        self.assertEqual(result.priority_level.value, "P1")
        self.assertTrue(result.needs_reply)
        self.assertTrue(result.requires_action)
        self.assertEqual(result.suggested_action, "요청 내용을 확인하고 회신")
        self.assertEqual([code.value for code in result.priority_reason_codes], ["URGENT_KEYWORD", "NEEDS_REPLY"])
        self.assertEqual(result.action_items[0].action_type.value, "REPLY")

    def test_rule_based_email_analyzer_matches_function_api(self) -> None:
        email = EmailInput(
            email_id="EML_260328_X9Y8Z7",
            subject="긴급: 오늘 중 회신",
            body_text="확인 부탁드립니다.",
            from_email="boss@test.com",
            received_at=datetime(2026, 3, 28, 9, 0, 0),
            language=Language.ko,
        )

        function_result = analyze_email(email)
        class_result = RuleBasedEmailAnalyzer().analyze(email)

        self.assertEqual(class_result.model_dump(), function_result.model_dump())

    def test_default_email_provider_implements_analyze_contract(self) -> None:
        email = EmailInput(
            email_id="EML_260328_X9Y8Z7",
            subject="긴급: 오늘 중 회신",
            body_text="확인 부탁드립니다.",
            from_email="boss@test.com",
            received_at=datetime(2026, 3, 28, 9, 0, 0),
            language=Language.ko,
        )

        result = get_email_analyzer().analyze(email)

        self.assertEqual(result.email_id, email.email_id)
        self.assertEqual(result.priority_level.value, "P1")

    def test_low_signal_report_email_keeps_low_priority(self) -> None:
        email = EmailInput(
            email_id="EML_260328_M3N4P5",
            subject="Weekly update",
            body_text="No action needed. FYI only.",
            from_email="peer@test.com",
            received_at=datetime(2026, 3, 28, 9, 0, 0),
            language=Language.en,
        )

        result = analyze_email(email)

        self.assertEqual(result.urgency.value, "low")
        self.assertEqual(result.category.value, "REPORT")
        self.assertEqual(result.priority_level.value, "P4")
        self.assertFalse(result.needs_reply)
        self.assertFalse(result.has_deadline)
        self.assertEqual([code.value for code in result.priority_reason_codes], ["NO_STRONG_SIGNAL"])


class AnalyzeWeeklyReportTest(unittest.TestCase):
    def test_weekly_report_builds_structured_summary(self) -> None:
        payload = WeeklyReportInput(
            mail_account_id="ACC_260328_A1B2C3",
            period_start=datetime(2026, 3, 23, 0, 0, 0),
            period_end=datetime(2026, 3, 30, 0, 0, 0),
            language=Language.ko,
            emails=[
                WeeklyEmailLine(
                    email_id="EML_260328_A1B2C3",
                    subject="고객 계약 검토",
                    body_excerpt="고객 계약 승인 요청과 정산 확인이 필요합니다.",
                    from_email="sales@test.com",
                    received_at=datetime(2026, 3, 28, 9, 0, 0),
                )
            ],
        )

        result = analyze_weekly_report(payload)

        self.assertEqual(result.executive_summary, "선택 기간 메일 1건을 바탕으로 주간보고 초안을 구성했습니다.")
        self.assertEqual(len(result.thread_summaries), 1)
        self.assertEqual(result.thread_summaries[0].email_id, "EML_260328_A1B2C3")
        self.assertTrue(result.highlights)
        self.assertEqual(result.model_name, "weekly-report-agent")
        self.assertEqual(result.prompt_version, "weekly-report-v1")

    def test_rule_based_weekly_report_analyzer_matches_function_api(self) -> None:
        payload = WeeklyReportInput(
            mail_account_id="ACC_260328_A1B2C3",
            period_start=datetime(2026, 3, 23, 0, 0, 0),
            period_end=datetime(2026, 3, 30, 0, 0, 0),
            language=Language.ko,
            emails=[
                WeeklyEmailLine(
                    email_id="EML_260328_A1B2C3",
                    subject="고객 계약 검토",
                    body_excerpt="고객 계약 승인 요청과 정산 확인이 필요합니다.",
                    from_email="sales@test.com",
                    received_at=datetime(2026, 3, 28, 9, 0, 0),
                )
            ],
        )

        function_result = analyze_weekly_report(payload)
        class_result = RuleBasedWeeklyReportAnalyzer().analyze(payload)

        self.assertEqual(class_result.model_dump(), function_result.model_dump())

    def test_default_weekly_report_provider_implements_analyze_contract(self) -> None:
        payload = WeeklyReportInput(
            mail_account_id="ACC_260328_A1B2C3",
            period_start=datetime(2026, 3, 23, 0, 0, 0),
            period_end=datetime(2026, 3, 30, 0, 0, 0),
            language=Language.ko,
            emails=[],
        )

        result = get_weekly_report_analyzer().analyze(payload)

        self.assertEqual(result.executive_summary, "선택 기간 메일 0건을 바탕으로 주간보고 초안을 구성했습니다.")
        self.assertEqual(result.thread_summaries, [])
