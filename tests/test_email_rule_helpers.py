from __future__ import annotations

import unittest

from app.email_actions import action_items, suggested_action_text, user_task_summary
from app.email_decisions import confidence_score, requires_action
from app.email_deadlines import deadline_text, time_sensitivity
from app.email_reasoning import priority_reason_codes, reasoning_text
from app.email_result_builder import build_analysis_result
from app.email_rules import analyze_signals
from app.schemas import (
    EmailCategory,
    PriorityLevel,
    PriorityReasonCode,
    TimeSensitivity,
    UrgencyLevel,
)
from app.signals import EmailAnalysisSignals
from tests.helpers import urgent_reply_email


class EmailRuleHelperTest(unittest.TestCase):
    def test_analyze_signals_extracts_rule_based_email_signals(self) -> None:
        email = urgent_reply_email()

        signals = analyze_signals(email)

        self.assertEqual(signals.urgency, UrgencyLevel.critical)
        self.assertEqual(signals.priority, PriorityLevel.p1)
        self.assertTrue(signals.needs_reply)
        self.assertFalse(signals.has_deadline)
        self.assertEqual(signals.suggested_action, "요청 내용을 확인하고 회신")
        self.assertEqual(signals.priority_reason_codes, [PriorityReasonCode.urgent_keyword, PriorityReasonCode.needs_reply])

    def test_build_analysis_result_renders_signals(self) -> None:
        email = urgent_reply_email()
        signals = EmailAnalysisSignals(
            haystack="긴급: 오늘 중 회신 확인 부탁드립니다.",
            urgency=UrgencyLevel.critical,
            needs_reply=True,
            has_deadline=False,
            category=EmailCategory.urgent,
            urgency_score=100.0,
            importance_score=93.0,
            priority=PriorityLevel.p1,
            suggested_action="요청 내용을 확인하고 회신",
            time_sensitivity=TimeSensitivity.immediate,
            deadline_text="",
            requires_action=True,
            user_task_summary="메일 내용을 확인하고 회신 필요 여부를 판단해야 합니다.",
            priority_reason_codes=[PriorityReasonCode.urgent_keyword, PriorityReasonCode.needs_reply],
            confidence_score=55.0,
        )

        result = build_analysis_result(email, signals)

        self.assertEqual(result.email_id, email.email_id)
        self.assertEqual(result.priority_level, PriorityLevel.p1)
        self.assertEqual(result.short_summary, "긴급: 오늘 중 회신에 대한 확인 또는 회신이 필요합니다.")
        self.assertEqual(result.action_items[0].action_type.value, "REPLY")
        self.assertEqual(result.model_name, "rule-based-agent")

    def test_email_actions_render_follow_up_work(self) -> None:
        haystack = "승인 요청입니다. 오늘까지 회신 부탁드립니다."

        suggested_action = suggested_action_text(EmailCategory.request, True, True, haystack)
        rendered_items = action_items(
            EmailCategory.request,
            needs_reply=True,
            has_deadline=True,
            priority=PriorityLevel.p1,
            suggested_action=suggested_action,
            haystack=haystack,
        )
        task_summary = user_task_summary(EmailCategory.request, True, True, suggested_action)

        self.assertEqual(suggested_action, "승인 가능 여부와 보완 필요 항목을 회신")
        self.assertEqual([item.action_type.value for item in rendered_items], ["APPROVE", "REPLY", "SCHEDULE"])
        self.assertEqual(task_summary, "메일 내용을 확인하고 마감 전에 회신 또는 필요한 조치를 진행해야 합니다.")

    def test_email_reasoning_renders_priority_reason_codes(self) -> None:
        reason_codes = priority_reason_codes(
            UrgencyLevel.high,
            needs_reply=True,
            has_deadline=True,
            email_category=EmailCategory.meeting,
            haystack="고객 미팅 일정 회신 부탁드립니다.",
        )

        rendered_reasoning = reasoning_text(reason_codes, UrgencyLevel.high, PriorityLevel.p2)

        self.assertEqual(
            reason_codes,
            [
                PriorityReasonCode.urgent_keyword,
                PriorityReasonCode.needs_reply,
                PriorityReasonCode.has_deadline,
                PriorityReasonCode.meeting_related,
                PriorityReasonCode.customer_or_contract,
            ],
        )
        self.assertEqual(
            rendered_reasoning,
            "긴급 표현, 회신 요청, 일정 또는 마감 표현, 회의 또는 일정 표현, 고객/계약 영향을 근거로 P2 우선순위와 high 긴급도로 판단했습니다.",
        )

    def test_email_deadlines_extracts_time_sensitivity_and_text(self) -> None:
        haystack = "자료는 3월 29일 까지 전달 부탁드립니다."

        self.assertEqual(time_sensitivity(UrgencyLevel.medium, True, haystack), TimeSensitivity.this_week)
        self.assertEqual(deadline_text(haystack, True), "3월 29일 까지")
        self.assertEqual(deadline_text(haystack, False), "")
        self.assertEqual(time_sensitivity(UrgencyLevel.critical, False, "asap 확인"), TimeSensitivity.immediate)

    def test_email_decisions_detects_actionability_and_confidence(self) -> None:
        self.assertTrue(requires_action(EmailCategory.request, needs_reply=False, has_deadline=False))
        self.assertTrue(requires_action(EmailCategory.general, needs_reply=True, has_deadline=False))
        self.assertFalse(requires_action(EmailCategory.general, needs_reply=False, has_deadline=False))
        self.assertEqual(confidence_score(UrgencyLevel.low, needs_reply=False, has_deadline=False), 35.0)
        self.assertEqual(confidence_score(UrgencyLevel.low, needs_reply=True, has_deadline=False), 55.0)
