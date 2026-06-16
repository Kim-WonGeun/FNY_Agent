from __future__ import annotations

import unittest

from app.weekly_report_sections import (
    classify_report_section,
    evidence_sentence,
    is_low_signal_report_mail,
    report_item,
    split_report_sentences,
)


class WeeklyReportSectionsTest(unittest.TestCase):
    def test_classifies_report_sections_by_signal(self) -> None:
        self.assertEqual(classify_report_section("장애 대응이 지연되었습니다."), "ISSUE")
        self.assertEqual(classify_report_section("계약 검토와 승인 요청이 있습니다."), "PENDING_DECISION")
        self.assertEqual(classify_report_section("다음 주 배포 계획을 준비합니다."), "NEXT_PLAN")
        self.assertEqual(classify_report_section("릴리즈가 완료되었습니다."), "HIGHLIGHT")
        self.assertEqual(classify_report_section("운영 현황입니다."), "PROGRESS")

    def test_detects_low_signal_report_mail(self) -> None:
        self.assertTrue(is_low_signal_report_mail("채용 공고 newsletter unsubscribe"))
        self.assertFalse(is_low_signal_report_mail("고객 계약 승인 요청"))

    def test_extracts_evidence_sentence_for_section(self) -> None:
        text = "고객 계약을 공유합니다. 승인 요청이 있습니다."

        self.assertEqual(split_report_sentences(text), ["고객 계약을 공유합니다.", "승인 요청이 있습니다."])
        self.assertEqual(evidence_sentence(text, "PENDING_DECISION"), "고객 계약을 공유합니다.")

    def test_report_item_uses_subject_and_evidence(self) -> None:
        self.assertEqual(
            report_item("고객 계약 검토", "승인 요청이 있습니다.", "PENDING_DECISION"),
            "고객 계약 검토: 승인 요청이 있습니다.",
        )
        self.assertEqual(report_item("고객 계약 검토", "", "PENDING_DECISION"), "고객 계약 검토 관련 확인 및 의사결정이 필요합니다.")
