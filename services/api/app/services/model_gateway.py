import uuid

from app.core.config import Settings
from app.schemas.model import ModelErrorCode, ModelGenerationRequest
from app.services.model_circuit_breaker import CircuitBreaker
from app.services.model_client import ModelClient
from app.services.model_errors import ModelError
from app.services.model_response_policy import validate_response


class ModelGateway:
    def __init__(self, settings: Settings, client: ModelClient, breaker: CircuitBreaker):
        self.settings, self.client, self.breaker = settings, client, breaker

    async def generate(self, request: ModelGenerationRequest, request_id: str | None = None):
        request_id = request_id or str(uuid.uuid4())
        last_error: ModelError | None = None
        paths: list[tuple[str, str, str | None, str | None]] = []
        if await self.breaker.allow():
            paths.append(
                (
                    "primary",
                    self.settings.model_primary_url,
                    self.settings.model_primary_name,
                    self.settings.model_primary_api_key.get_secret_value()
                    if self.settings.model_primary_api_key
                    else None,
                )
            )
        else:
            last_error = ModelError(ModelErrorCode.CIRCUIT_OPEN, "Primary circuit is open")
        if self.settings.model_stable_adapter_enabled:
            paths.append(
                (
                    "stable_adapter",
                    self.settings.model_primary_url,
                    self.settings.model_stable_name,
                    self.settings.model_primary_api_key.get_secret_value()
                    if self.settings.model_primary_api_key
                    else None,
                )
            )
        if self.settings.model_fallback_enabled:
            paths.append(
                (
                    "fallback_server",
                    self.settings.model_fallback_url,
                    self.settings.model_fallback_name,
                    self.settings.model_fallback_api_key.get_secret_value()
                    if self.settings.model_fallback_api_key
                    else None,
                )
            )
        for index, (kind, url, model, key) in enumerate(paths):
            try:
                result = await self.client.generate(
                    request, base_url=url, api_key=key, model=model, request_id=request_id
                )
                policy = validate_response(result.content, request.messages[-1].content)
                if not policy.accepted:
                    last_error = ModelError(ModelErrorCode.POLICY_REJECTED, policy.reason or "Policy rejected")
                    continue
                if kind == "primary":
                    await self.breaker.success()
                result.fallback_used = index > 0 or kind != "primary"
                result.fallback_reason = last_error.code.value if result.fallback_used and last_error else None
                return result
            except ModelError as exc:
                last_error = exc
                if kind == "primary":
                    await self.breaker.failure()
                continue
        raise last_error or ModelError(ModelErrorCode.UNAVAILABLE, "No model path is configured")
