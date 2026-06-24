from datetime import datetime, timezone
import unittest

from app.llm_quality import normalize_email_analysis_result, normalize_weekly_report_result
from app.schemas import AnalysisResult, EmailInput, WeeklyEmailLine, WeeklyReportInput, WeeklyReportResult, WeeklyThreadSummary


class LLMQualityTest(unittest.TestCase):
    def test_normalizes_email_identity_deadline_and_duplicate_actions(self):
        email = EmailInput(email_id="EML_260621_A00001", subject="확인 요청", body_text="본문", from_email="a@example.com", received_at=datetime.now(timezone.utc))
        result = AnalysisResult(
            email_id="EML_260621_A00002", urgency="low", short_summary="  ", detailed_summary="상세", category="REQUEST",
            priority_level="P3", importance_score=10, urgency_score=10, confidence_score=90,
            needs_reply=False, has_deadline=False, deadline_at=datetime.now(timezone.utc),
            action_items=[{"action_text":"확인", "action_type":"REVIEW", "priority_level":"P3"}, {"action_text":"확인", "action_type":"REVIEW", "priority_level":"P3"}],
        )
        normalized = normalize_email_analysis_result(result, email)
        self.assertEqual(normalized.email_id, "EML_260621_A00001")
        self.assertEqual(normalized.short_summary, "확인 요청")
        self.assertIsNone(normalized.deadline_at)
        self.assertEqual(len(normalized.action_items), 1)

    def test_removes_hallucinated_weekly_sources_and_duplicates(self):
        line = WeeklyEmailLine(email_id="EML_260621_A00001", subject="완료", body_excerpt="완료", from_email="a@example.com", received_at=datetime.now(timezone.utc))
        payload = WeeklyReportInput(mail_account_id="MAC_1", period_start=datetime.now(timezone.utc), period_end=datetime.now(timezone.utc), emails=[line])
        result = WeeklyReportResult(
            executive_summary=" 요약 ", highlights=["완료", "완료"],
            thread_summaries=[WeeklyThreadSummary(email_id="EML_260621_A00001"), WeeklyThreadSummary(email_id="EML_260621_FAKE01")],
        )
        normalized = normalize_weekly_report_result(result, payload)
        self.assertEqual(normalized.highlights, ["완료"])
        self.assertEqual([item.email_id for item in normalized.thread_summaries], ["EML_260621_A00001"])


if __name__ == "__main__":
    unittest.main()
