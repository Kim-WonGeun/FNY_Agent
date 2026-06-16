from __future__ import annotations

import unittest

from app.analyzer import analyze_email, analyze_weekly_report
from app.email_analyzer import RuleBasedEmailAnalyzer
from app.providers import get_email_analyzer, get_weekly_report_analyzer
from app.weekly_report import RuleBasedWeeklyReportAnalyzer
from tests.helpers import low_signal_report_email, urgent_reply_email, weekly_report_payload


class AnalyzeEmailTest(unittest.TestCase):
    def test_urgent_reply_email_returns_p1_actionable_result(self) -> None:
        email = urgent_reply_email()

        result = analyze_email(email)

        self.assertEqual(result.urgency.value, "critical")
        self.assertEqual(result.priority_level.value, "P1")
        self.assertTrue(result.needs_reply)
        self.assertTrue(result.requires_action)
        self.assertEqual(result.suggested_action, "요청 내용을 확인하고 회신")
        self.assertEqual([code.value for code in result.priority_reason_codes], ["URGENT_KEYWORD", "NEEDS_REPLY"])
        self.assertEqual(result.action_items[0].action_type.value, "REPLY")

    def test_rule_based_email_analyzer_matches_function_api(self) -> None:
        email = urgent_reply_email()

        function_result = analyze_email(email)
        class_result = RuleBasedEmailAnalyzer().analyze(email)

        self.assertEqual(class_result.model_dump(), function_result.model_dump())

    def test_default_email_provider_implements_analyze_contract(self) -> None:
        email = urgent_reply_email()

        result = get_email_analyzer().analyze(email)

        self.assertEqual(result.email_id, email.email_id)
        self.assertEqual(result.priority_level.value, "P1")

    def test_low_signal_report_email_keeps_low_priority(self) -> None:
        email = low_signal_report_email()

        result = analyze_email(email)

        self.assertEqual(result.urgency.value, "low")
        self.assertEqual(result.category.value, "REPORT")
        self.assertEqual(result.priority_level.value, "P4")
        self.assertFalse(result.needs_reply)
        self.assertFalse(result.has_deadline)
        self.assertEqual([code.value for code in result.priority_reason_codes], ["NO_STRONG_SIGNAL"])

class AnalyzeWeeklyReportTest(unittest.TestCase):
    def test_weekly_report_builds_structured_summary(self) -> None:
        payload = weekly_report_payload()

        result = analyze_weekly_report(payload)

        self.assertEqual(result.executive_summary, "선택 기간 업무성 메일 1건을 기준으로 보고서 초안을 구성했습니다.")
        self.assertEqual(len(result.thread_summaries), 1)
        self.assertEqual(result.thread_summaries[0].email_id, "EML_260328_A1B2C3")
        self.assertTrue(result.highlights)
        self.assertEqual(result.model_name, "weekly-report-agent")
        self.assertEqual(result.prompt_version, "weekly-report-v2")

    def test_rule_based_weekly_report_analyzer_matches_function_api(self) -> None:
        payload = weekly_report_payload()

        function_result = analyze_weekly_report(payload)
        class_result = RuleBasedWeeklyReportAnalyzer().analyze(payload)

        self.assertEqual(class_result.model_dump(), function_result.model_dump())

    def test_default_weekly_report_provider_implements_analyze_contract(self) -> None:
        payload = weekly_report_payload(with_email=False)

        result = get_weekly_report_analyzer().analyze(payload)

        self.assertEqual(result.executive_summary, "선택 기간 메일 0건을 검토했지만 보고서에 반영할 업무성 메일은 확인되지 않았습니다.")
        self.assertEqual(result.thread_summaries, [])
