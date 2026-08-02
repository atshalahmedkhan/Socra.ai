import httpx
from enum import StrEnum

from app.core.config import Settings
from app.schemas.model import ModelErrorCode, ModelGenerationResult
from app.services.model_errors import ModelError


class MockScenario(StrEnum):
    SUCCESS = "success"
    TIMEOUT = "timeout"
    RETRYABLE_FAILURE = "retryable_failure"
    NON_RETRYABLE_FAILURE = "non_retryable_failure"
    PRIMARY_FAILURE_FALLBACK_SUCCESS = "primary_failure_fallback_success"
    PRIMARY_AND_FALLBACK_FAILURE = "primary_and_fallback_failure"


class DeterministicMockModelAdapter:
    """Deterministic test/development adapter. It does not represent Gemma."""

    def __init__(self, settings: Settings, scenario: MockScenario | str = MockScenario.SUCCESS):
        self.settings = settings
        self.scenario = MockScenario(scenario)
        self.calls: list[str] = []
        self.http = httpx.AsyncClient()

    async def close(self) -> None:
        await self.http.aclose()
    async def generate(self, request, *, base_url, api_key, model, request_id):
        del api_key, model, request_id
        route = "fallback" if base_url == self.settings.model_fallback_url else "primary"
        self.calls.append(route)
        if self.scenario == MockScenario.TIMEOUT:
            raise ModelError(ModelErrorCode.TIMEOUT, "Simulated timeout", retryable=True)
        if self.scenario == MockScenario.NON_RETRYABLE_FAILURE:
            raise ModelError(ModelErrorCode.INVALID_RESPONSE, "Simulated permanent failure")
        if self.scenario == MockScenario.PRIMARY_AND_FALLBACK_FAILURE:
            raise ModelError(ModelErrorCode.UNAVAILABLE, "Simulated unavailable route", retryable=True)
        if self.scenario == MockScenario.PRIMARY_FAILURE_FALLBACK_SUCCESS and route == "primary":
            raise ModelError(ModelErrorCode.UNAVAILABLE, "Simulated primary failure", retryable=True)
        retry_count = 1 if self.scenario == MockScenario.RETRYABLE_FAILURE else 0
        if retry_count:
            self.calls.append(route)
        input_tokens = sum(len(message.content.split()) for message in request.messages)
        content = "What part of the problem would you examine first?"
        output_tokens = len(content.split())
        return ModelGenerationResult(
            content=content,
            model_name="deterministic-mock",
            model_version="mock-v1",
            prompt_version=self.settings.prompt_version,
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            total_latency_ms=7 if route == "primary" else 11,
            generation_latency_ms=5,
            fallback_used=route == "fallback",
            fallback_reason="MODEL_UNAVAILABLE" if route == "fallback" else None,
            retry_count=retry_count,
            provider_endpoint="mock",
            provider_route="mock",
            finish_reason="stop",
        )
