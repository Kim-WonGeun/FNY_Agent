from __future__ import annotations

import unittest

from app.prompt_metadata import prompt_version, result_metadata
from app.schemas import PromptTemplate


class PromptMetadataTest(unittest.TestCase):
    def test_prompt_version_uses_default_without_prompt(self) -> None:
        self.assertEqual(prompt_version(None, "rule-v1"), "rule-v1")

    def test_prompt_version_uses_prompt_code_and_version(self) -> None:
        prompt = PromptTemplate(prompt_code="email-analysis", version=7, model_name="test-model")

        self.assertEqual(prompt_version(prompt, "rule-v1"), "email-analysis-v7")

    def test_result_metadata_uses_prompt_model_when_present(self) -> None:
        prompt = PromptTemplate(prompt_code="weekly", version=2, model_name="test-model")

        self.assertEqual(result_metadata(None, "default-model", "default-v1"), ("default-model", "default-v1"))
        self.assertEqual(result_metadata(prompt, "default-model", "default-v1"), ("test-model", "weekly-v2"))
