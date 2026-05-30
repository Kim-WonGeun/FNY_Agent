from __future__ import annotations

import json
import unittest

from app.exceptions import LLMConfigurationError


class APIErrorHandlingTest(unittest.TestCase):
    def test_create_app_registers_expected_routes(self) -> None:
        from app.api import create_app

        app = create_app()

        self.assertEqual(app.title, "Mail Agent")
        self.assertEqual(
            {route.path for route in app.routes},
            {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc", "/health", "/analyze", "/analyze-weekly"},
        )

    def test_llm_error_handler_returns_machine_readable_error(self) -> None:
        from app.api import handle_llm_error

        response = handle_llm_error(None, LLMConfigurationError("missing key"))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            json.loads(response.body),
            {
                "error": "LLM_CONFIGURATION_ERROR",
                "message": "missing key",
            },
        )
