from __future__ import annotations

from typing import Any

from app.exceptions import LLMConfigurationError, LLMResponseError
from app.settings import AgentSettings


class OpenAIResponsesClient:
    def __init__(self, settings: AgentSettings) -> None:
        self.settings = settings

    def complete_json(self, prompt: str, model: str) -> str:
        if not self.settings.openai_api_key:
            raise LLMConfigurationError("OPENAI_API_KEY is required when using the LLM analyzer.")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LLMConfigurationError("The openai package is required when using the LLM analyzer.") from exc

        client = OpenAI(api_key=self.settings.openai_api_key)
        response = client.responses.create(
            model=model,
            input=prompt,
        )
        return _extract_output_text(response)


def _extract_output_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    if isinstance(response, dict):
        dict_output_text = response.get("output_text")
        if isinstance(dict_output_text, str) and dict_output_text.strip():
            return dict_output_text

    raise LLMResponseError("OpenAI response did not include output_text.")
