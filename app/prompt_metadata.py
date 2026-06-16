from __future__ import annotations

from typing import Optional

from app.schemas import PromptTemplate


def prompt_version(prompt: Optional[PromptTemplate], default_prompt_version: str) -> str:
    if prompt:
        return f"{prompt.prompt_code}-v{prompt.version}"
    return default_prompt_version


def result_metadata(
    prompt: Optional[PromptTemplate],
    default_model_name: str,
    default_prompt_version: str,
) -> tuple[str, str]:
    if prompt:
        return prompt.model_name, prompt_version(prompt, default_prompt_version)
    return default_model_name, default_prompt_version
