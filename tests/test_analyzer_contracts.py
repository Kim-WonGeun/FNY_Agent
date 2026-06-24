from __future__ import annotations

import unittest

from app.analyzer_contracts import EmailAnalyzer, WeeklyReportAnalyzer
from app.providers import EmailAnalyzer as ProviderEmailAnalyzer
from app.providers import WeeklyReportAnalyzer as ProviderWeeklyReportAnalyzer


class AnalyzerContractsTest(unittest.TestCase):
    def test_provider_keeps_contract_import_compatibility(self) -> None:
        self.assertIs(ProviderEmailAnalyzer, EmailAnalyzer)
        self.assertIs(ProviderWeeklyReportAnalyzer, WeeklyReportAnalyzer)
