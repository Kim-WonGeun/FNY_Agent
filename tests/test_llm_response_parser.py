from __future__ import annotations

import unittest

from app.llm_response_parser import extract_json_object, parse_json_model
from app.schemas import AnalysisResult


class LLMResponseParserTest(unittest.TestCase):
    def test_extract_json_object_accepts_fenced_json(self) -> None:
        self.assertEqual(extract_json_object('```json\n{"ok": true}\n```'), '{"ok": true}')

    def test_parse_json_model_validates_schema(self) -> None:
        raw = """
        {
          "email_id": "EML_260328_X9Y8Z7",
          "urgency": "critical",
          "short_summary": "확인과 회신이 필요합니다.",
          "detailed_summary": "긴급 회신 요청입니다.",
          "category": "URGENT",
          "priority_level": "P1",
          "importance_score": 95,
          "urgency_score": 100,
          "confidence_score": 90,
          "needs_reply": true,
          "has_deadline": false,
          "suggested_action": "요청 내용을 확인하고 회신",
          "reasoning": "긴급 표현과 회신 요청이 있습니다.",
          "action_items": []
        }
        """

        result = parse_json_model(raw, AnalysisResult)

        self.assertEqual(result.email_id, "EML_260328_X9Y8Z7")
        self.assertEqual(result.priority_level.value, "P1")
