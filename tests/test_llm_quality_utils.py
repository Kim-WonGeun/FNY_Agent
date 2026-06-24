from __future__ import annotations

import unittest

from app.llm_quality_utils import clean_list, clean_text, dedupe_by


class LLMQualityUtilsTest(unittest.TestCase):
    def test_clean_text_removes_invisible_characters_and_whitespace(self) -> None:
        self.assertEqual(clean_text(" \u200b메일\n  요약 "), "메일 요약")

    def test_clean_list_removes_empty_and_duplicate_values(self) -> None:
        self.assertEqual(clean_list([" 완료 ", "완료", "", " 진행 "], 5), ["완료", "진행"])

    def test_dedupe_by_keeps_first_value_for_each_key(self) -> None:
        values = [{"id": "A", "value": 1}, {"id": "A", "value": 2}, {"id": "B", "value": 3}]

        self.assertEqual(dedupe_by(values, lambda item: item["id"]), [values[0], values[2]])
