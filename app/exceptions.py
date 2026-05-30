from __future__ import annotations


class LLMError(RuntimeError):
    status_code = 500
    error_code = "LLM_ERROR"


class LLMConfigurationError(LLMError):
    status_code = 503
    error_code = "LLM_CONFIGURATION_ERROR"


class LLMResponseError(LLMError):
    status_code = 502
    error_code = "LLM_RESPONSE_ERROR"
