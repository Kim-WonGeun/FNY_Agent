from __future__ import annotations

import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.exceptions import LLMResponseError


TModel = TypeVar("TModel", bound=BaseModel)


def parse_json_model(raw_text: str, model_type: type[TModel]) -> TModel:
    try:
        json_text = extract_json_object(raw_text)
        return model_type.model_validate_json(json_text)
    except (ValueError, ValidationError) as exc:
        raise LLMResponseError("LLM response did not match the expected JSON schema.") from exc


def extract_json_object(raw_text: str) -> str:
    stripped = raw_text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        stripped = fenced.group(1).strip()

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("LLM response does not contain a JSON object.")
    return stripped[start : end + 1]
