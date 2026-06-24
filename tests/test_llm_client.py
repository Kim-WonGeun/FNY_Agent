from __future__ import annotations

import unittest

from app.exceptions import LLMConfigurationError
from app.llm_client import MissingLLMClient


class MissingLLMClientTest(unittest.TestCase):
    def test_complete_json_raises_configuration_error(self) -> None:
        with self.assertRaisesRegex(LLMConfigurationError, "not configured"):
            MissingLLMClient().complete_json("prompt", "test-model")
