from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Mapping, Optional

from app.exceptions import LLMConfigurationError


class AnalyzerMode(str, Enum):
    rule_based = "rule_based"
    llm = "llm"


@dataclass(frozen=True)
class AgentSettings:
    email_analyzer_mode: AnalyzerMode = AnalyzerMode.rule_based
    weekly_report_analyzer_mode: AnalyzerMode = AnalyzerMode.rule_based
    openai_model: str = "gpt-5.4-mini"
    openai_api_key: str = ""


def _read_mode(values: Mapping[str, str], name: str, default: AnalyzerMode) -> AnalyzerMode:
    raw = values.get(name, default.value).strip().lower().replace("-", "_")
    try:
        return AnalyzerMode(raw)
    except ValueError as exc:
        allowed = ", ".join(mode.value for mode in AnalyzerMode)
        raise LLMConfigurationError(f"{name} must be one of: {allowed}.") from exc


def load_settings(env_file: Optional[Path] = None) -> AgentSettings:
    values = _load_env_values(env_file)
    return AgentSettings(
        email_analyzer_mode=_read_mode(values, "FNY_AGENT_EMAIL_ANALYZER", AnalyzerMode.rule_based),
        weekly_report_analyzer_mode=_read_mode(values, "FNY_AGENT_WEEKLY_REPORT_ANALYZER", AnalyzerMode.rule_based),
        openai_model=values.get("OPENAI_MODEL", "gpt-5.4-mini").strip() or "gpt-5.4-mini",
        openai_api_key=values.get("OPENAI_API_KEY", "").strip(),
    )


def _load_env_values(env_file: Optional[Path]) -> dict[str, str]:
    values = _parse_env_file(env_file or _default_env_file())
    values.update(os.environ)
    return values


def _default_env_file() -> Path:
    return Path(__file__).resolve().parents[1] / ".env"


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        values[key] = _strip_env_value(value.strip())
    return values


def _strip_env_value(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value
