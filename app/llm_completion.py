from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

from app.llm_client import LLMClient
from app.llm_response_parser import parse_json_model
from app.settings import AgentSettings


TModel = TypeVar("TModel", bound=BaseModel)


def complete_json_model(
    client: LLMClient,
    settings: AgentSettings,
    prompt: str,
    model_type: type[TModel],
) -> TModel:
    raw_result = client.complete_json(prompt, settings.openai_model)
    return parse_json_model(raw_result, model_type)
