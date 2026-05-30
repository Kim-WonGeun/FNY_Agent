from __future__ import annotations

import json


class FakeLLMClient:
    def __init__(self, response: dict[str, object]) -> None:
        self.response = response
        self.prompts: list[str] = []
        self.models: list[str] = []

    def complete_json(self, prompt: str, model: str) -> str:
        self.prompts.append(prompt)
        self.models.append(model)
        return json.dumps(self.response)
