from __future__ import annotations

import unittest

from app.llm_completion import complete_json_model
from app.schemas import AnalysisResult
from app.settings import AgentSettings
from tests.helpers import FakeLLMClient


class LLMCompletionTest(unittest.TestCase):
    def test_completes_prompt_with_configured_model_and_parses_schema(self) -> None:
        client = FakeLLMClient(
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
                "needs_reply": True,
                "has_deadline": False,
                "suggested_action": "요청 내용을 확인하고 회신",
                "reasoning": "긴급 표현과 회신 요청이 있습니다.",
                "action_items": [],
            }
        )

        result = complete_json_model(
            client,
            AgentSettings(openai_model="test-model"),
            "prompt body",
            AnalysisResult,
        )

        self.assertEqual(result.email_id, "EML_260328_X9Y8Z7")
        self.assertEqual(client.models, ["test-model"])
        self.assertEqual(client.prompts, ["prompt body"])


if __name__ == "__main__":
    unittest.main()
