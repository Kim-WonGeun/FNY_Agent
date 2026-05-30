from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from app.email_analyzer import RuleBasedEmailAnalyzer
from app.exceptions import LLMConfigurationError
from app.llm_analyzer import LLMEmailAnalyzer, LLMWeeklyReportAnalyzer
from app.providers import (
    build_email_analyzer,
    build_weekly_report_analyzer,
    get_email_analyzer,
    get_settings,
    reset_provider_cache,
)
from app.settings import AnalyzerMode, AgentSettings, load_settings
from app.weekly_report import RuleBasedWeeklyReportAnalyzer


class ProviderSettingsTest(unittest.TestCase):
    def tearDown(self) -> None:
        reset_provider_cache()

    def test_default_settings_use_rule_based_analyzers(self) -> None:
        settings = AgentSettings()

        self.assertIsInstance(build_email_analyzer(settings), RuleBasedEmailAnalyzer)
        self.assertIsInstance(build_weekly_report_analyzer(settings), RuleBasedWeeklyReportAnalyzer)

    def test_llm_settings_select_llm_placeholders(self) -> None:
        settings = AgentSettings(
            email_analyzer_mode=AnalyzerMode.llm,
            weekly_report_analyzer_mode=AnalyzerMode.llm,
        )

        self.assertIsInstance(build_email_analyzer(settings), LLMEmailAnalyzer)
        self.assertIsInstance(build_weekly_report_analyzer(settings), LLMWeeklyReportAnalyzer)

    def test_load_settings_reads_environment_modes(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "FNY_AGENT_EMAIL_ANALYZER": "llm",
                "FNY_AGENT_WEEKLY_REPORT_ANALYZER": "llm",
                "OPENAI_MODEL": "test-model",
                "OPENAI_API_KEY": "test-key",
            },
            clear=True,
        ):
            settings = load_settings()

        self.assertEqual(settings.email_analyzer_mode, AnalyzerMode.llm)
        self.assertEqual(settings.weekly_report_analyzer_mode, AnalyzerMode.llm)
        self.assertEqual(settings.openai_model, "test-model")
        self.assertEqual(settings.openai_api_key, "test-key")

    def test_load_settings_rejects_invalid_analyzer_mode(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "FNY_AGENT_EMAIL_ANALYZER": "unknown",
            },
            clear=True,
        ):
            with self.assertRaisesRegex(LLMConfigurationError, "FNY_AGENT_EMAIL_ANALYZER"):
                load_settings()

    def test_load_settings_reads_env_file(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            env_file = Path(tmp_dir) / ".env"
            env_file.write_text(
                "\n".join(
                    [
                        "FNY_AGENT_EMAIL_ANALYZER=llm",
                        "FNY_AGENT_WEEKLY_REPORT_ANALYZER=rule_based",
                        "OPENAI_MODEL='env-file-model'",
                        "OPENAI_API_KEY=env-file-key",
                    ]
                ),
                encoding="utf-8",
            )

            with patch.dict("os.environ", {}, clear=True):
                settings = load_settings(env_file)

        self.assertEqual(settings.email_analyzer_mode, AnalyzerMode.llm)
        self.assertEqual(settings.weekly_report_analyzer_mode, AnalyzerMode.rule_based)
        self.assertEqual(settings.openai_model, "env-file-model")
        self.assertEqual(settings.openai_api_key, "env-file-key")

    def test_environment_values_override_env_file(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            env_file = Path(tmp_dir) / ".env"
            env_file.write_text("OPENAI_MODEL=env-file-model", encoding="utf-8")

            with patch.dict("os.environ", {"OPENAI_MODEL": "process-model"}, clear=True):
                settings = load_settings(env_file)

        self.assertEqual(settings.openai_model, "process-model")

    def test_provider_dependencies_are_cached_until_reset(self) -> None:
        with patch.dict("os.environ", {"OPENAI_MODEL": "first-model"}, clear=True):
            reset_provider_cache()
            first_settings = get_settings()
            first_analyzer = get_email_analyzer()

        with patch.dict("os.environ", {"OPENAI_MODEL": "second-model"}, clear=True):
            second_settings = get_settings()
            second_analyzer = get_email_analyzer()

        self.assertIs(first_settings, second_settings)
        self.assertIs(first_analyzer, second_analyzer)
        self.assertEqual(second_settings.openai_model, "first-model")

        with patch.dict("os.environ", {"OPENAI_MODEL": "second-model"}, clear=True):
            reset_provider_cache()
            refreshed_settings = get_settings()

        self.assertEqual(refreshed_settings.openai_model, "second-model")
