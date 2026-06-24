from __future__ import annotations

from typing import Protocol

from app.exceptions import LLMConfigurationError


class LLMClient(Protocol):
    def complete_json(self, prompt: str, model: str) -> str:
        ...


class MissingLLMClient:
    def complete_json(self, prompt: str, model: str) -> str:
        raise LLMConfigurationError("LLM client is not configured.")
