from __future__ import annotations

import sys
import types
import unittest
from datetime import datetime
from unittest.mock import patch

from app.exceptions import LLMConfigurationError, LLMResponseError
from app.llm_analyzer import LLMEmailAnalyzer, LLMWeeklyReportAnalyzer
from app.llm_contract import parse_json_model, render_email_analysis_prompt, render_weekly_report_prompt
from app.openai_client import OpenAIResponsesClient
from app.schemas import AnalysisResult, EmailInput, Language, WeeklyReportInput
from app.settings import AgentSettings
from tests.helpers import FakeLLMClient


class OpenAIResponsesClientTest(unittest.TestCase):
    def test_requires_api_key(self) -> None:
        client = OpenAIResponsesClient(AgentSettings(openai_api_key=""))

        with self.assertRaisesRegex(LLMConfigurationError, "OPENAI_API_KEY"):
            client.complete_json("prompt", "test-model")

    def test_requires_output_text(self) -> None:
        class FakeResponses:
            def create(self, model: str, input: str) -> object:
                return types.SimpleNamespace(output_text="")

        class FakeOpenAI:
            def __init__(self, api_key: str) -> None:
                self.api_key = api_key
                self.responses = FakeResponses()

        fake_module = types.SimpleNamespace(OpenAI=FakeOpenAI)

        with patch.dict(sys.modules, {"openai": fake_module}):
            client = OpenAIResponsesClient(AgentSettings(openai_api_key="test-key"))
            with self.assertRaisesRegex(LLMResponseError, "output_text"):
                client.complete_json("prompt", "test-model")

    def test_extracts_output_text_from_sdk_response(self) -> None:
        calls: list[dict[str, str]] = []

        class FakeResponses:
            def create(self, model: str, input: str) -> object:
                calls.append({"model": model, "input": input})
                return types.SimpleNamespace(output_text='{"ok": true}')

        class FakeOpenAI:
            def __init__(self, api_key: str) -> None:
                self.api_key = api_key
                self.responses = FakeResponses()

        fake_module = types.SimpleNamespace(OpenAI=FakeOpenAI)

        with patch.dict(sys.modules, {"openai": fake_module}):
            client = OpenAIResponsesClient(AgentSettings(openai_api_key="test-key"))
            result = client.complete_json("prompt", "test-model")

        self.assertEqual(result, '{"ok": true}')
        self.assertEqual(calls, [{"model": "test-model", "input": "prompt"}])


class LLMAnalyzerContractTest(unittest.TestCase):
    def test_email_prompt_includes_payload_and_template(self) -> None:
        email = EmailInput(
            email_id="EML_260328_X9Y8Z7",
            subject="긴급: 오늘 중 회신",
            body_text="확인 부탁드립니다.",
            from_email="boss@test.com",
            received_at=datetime(2026, 3, 28, 9, 0, 0),
            language=Language.ko,
        )

        prompt = render_email_analysis_prompt(email, AgentSettings(openai_model="test-model"))

        self.assertIn("AnalysisResult", prompt)
        self.assertIn("test-model", prompt)
        self.assertIn("긴급: 오늘 중 회신", prompt)
        self.assertIn("EML_260328_X9Y8Z7", prompt)
        self.assertIn("AnalysisResult JSON schema", prompt)
        self.assertIn('"priority_level"', prompt)
        self.assertIn('"action_items"', prompt)

    def test_weekly_report_prompt_includes_json_schema(self) -> None:
        payload = WeeklyReportInput(
            mail_account_id="ACC_260328_A1B2C3",
            period_start=datetime(2026, 3, 23, 0, 0, 0),
            period_end=datetime(2026, 3, 30, 0, 0, 0),
            language=Language.ko,
            emails=[],
        )

        prompt = render_weekly_report_prompt(payload, AgentSettings(openai_model="test-model"))

        self.assertIn("WeeklyReportResult JSON schema", prompt)
        self.assertIn('"executive_summary"', prompt)
        self.assertIn('"thread_summaries"', prompt)
        self.assertIn("ACC_260328_A1B2C3", prompt)

    def test_parse_json_model_accepts_markdown_fenced_json(self) -> None:
        raw = """```json
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
        ```"""

        result = parse_json_model(raw, AnalysisResult)

        self.assertEqual(result.email_id, "EML_260328_X9Y8Z7")
        self.assertEqual(result.priority_level.value, "P1")

    def test_parse_json_model_wraps_invalid_json(self) -> None:
        with self.assertRaisesRegex(LLMResponseError, "expected JSON schema"):
            parse_json_model("not json", AnalysisResult)

    def test_llm_email_analyzer_validates_client_json(self) -> None:
        email = EmailInput(
            email_id="EML_260328_X9Y8Z7",
            subject="긴급: 오늘 중 회신",
            body_text="확인 부탁드립니다.",
            from_email="boss@test.com",
            received_at=datetime(2026, 3, 28, 9, 0, 0),
            language=Language.ko,
        )
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

        result = LLMEmailAnalyzer(AgentSettings(openai_model="test-model"), client).analyze(email)

        self.assertEqual(result.model_name, "test-model")
        self.assertEqual(result.prompt_version, "email-llm-v1")
        self.assertEqual(client.models, ["test-model"])
        self.assertIn("긴급: 오늘 중 회신", client.prompts[0])

    def test_llm_weekly_report_analyzer_validates_client_json(self) -> None:
        payload = WeeklyReportInput(
            mail_account_id="ACC_260328_A1B2C3",
            period_start=datetime(2026, 3, 23, 0, 0, 0),
            period_end=datetime(2026, 3, 30, 0, 0, 0),
            language=Language.ko,
            emails=[],
        )
        client = FakeLLMClient(
            {
                "executive_summary": "선택 기간 메일 0건을 요약했습니다.",
                "highlights": [],
                "risks_blockers": [],
                "pending_decisions": [],
                "next_week_suggestions": [],
                "thread_summaries": [],
            }
        )

        result = LLMWeeklyReportAnalyzer(AgentSettings(openai_model="test-model"), client).analyze(payload)

        self.assertEqual(result.model_name, "test-model")
        self.assertEqual(result.prompt_version, "weekly-llm-v1")
        self.assertEqual(client.models, ["test-model"])
