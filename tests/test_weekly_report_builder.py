from __future__ import annotations

import unittest

from app.schemas import PromptTemplate
from app.weekly_report_builder import executive_summary, section_blocks
from app.weekly_report_builder import empty_section_items, report_metadata


class WeeklyReportBuilderTest(unittest.TestCase):
    def test_empty_section_items_initializes_known_sections(self) -> None:
        self.assertEqual(
            empty_section_items(),
            {
                "HIGHLIGHT": [],
                "PROGRESS": [],
                "ISSUE": [],
                "PENDING_DECISION": [],
                "NEXT_PLAN": [],
            },
        )

    def test_executive_summary_reflects_business_mail_count(self) -> None:
        self.assertEqual(
            executive_summary(total_count=0, business_count=0, excluded_count=0),
            "선택 기간 메일 0건을 검토했지만 보고서에 반영할 업무성 메일은 확인되지 않았습니다.",
        )
        self.assertEqual(
            executive_summary(total_count=3, business_count=2, excluded_count=1),
            "선택 기간 메일 3건 중 업무성 메일 2건을 기준으로 보고서 초안을 구성했습니다.",
        )
        self.assertEqual(
            executive_summary(total_count=2, business_count=2, excluded_count=0),
            "선택 기간 업무성 메일 2건을 기준으로 보고서 초안을 구성했습니다.",
        )

    def test_section_blocks_apply_limits_and_fallbacks(self) -> None:
        section_items = {
            "HIGHLIGHT": ["완료 1", "완료 2", "완료 3"],
            "PROGRESS": ["진행 1", "진행 2", "진행 3"],
            "ISSUE": [],
            "PENDING_DECISION": ["검토 1"],
            "NEXT_PLAN": [],
        }

        highlights, risks, pending, next_plans = section_blocks(section_items)

        self.assertEqual(highlights, ["완료 1", "완료 2", "완료 3", "진행 1", "진행 2"])
        self.assertEqual(risks, ["별도 이슈나 리스크로 공유할 내용은 확인되지 않았습니다."])
        self.assertEqual(pending, ["검토 1"])
        self.assertEqual(next_plans, ["차주 계획으로 이어질 명확한 후속 일정은 확인되지 않았습니다."])

    def test_report_metadata_uses_prompt_when_present(self) -> None:
        prompt = PromptTemplate(prompt_code="weekly-custom", version=3, model_name="test-model")

        self.assertEqual(report_metadata(None), ("weekly-report-agent", "weekly-report-v2"))
        self.assertEqual(report_metadata(prompt), ("test-model", "weekly-custom-v3"))
