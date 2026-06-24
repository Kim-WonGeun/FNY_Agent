from __future__ import annotations

import unittest

from app import llm_contract


class LLMContractCompatibilityTest(unittest.TestCase):
    def test_exports_legacy_contract_api(self) -> None:
        self.assertEqual(
            llm_contract.__all__,
            [
                "LLMClient",
                "MissingLLMClient",
                "parse_json_model",
                "render_email_analysis_prompt",
                "render_weekly_report_prompt",
                "with_email_llm_metadata",
                "with_weekly_llm_metadata",
            ],
        )
        for name in llm_contract.__all__:
            self.assertTrue(hasattr(llm_contract, name))
