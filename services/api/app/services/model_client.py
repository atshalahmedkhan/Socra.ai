import asyncio
import random
import time

import httpx

from app.core.config import Settings
from app.schemas.model import (
    ModelErrorCode,
    ModelGenerationRequest,
    ModelGenerationResult,
)
from app.services.model_errors import ModelError


class ModelClient:
    def __init__(self, settings: Settings, http_client: httpx.AsyncClient | None = None):
        self.settings = settings
        timeout = httpx.Timeout(
            connect=settings.model_connect_timeout_seconds,
            read=settings.model_read_timeout_seconds,
            write=settings.model_write_timeout_seconds,
            pool=settings.model_pool_timeout_seconds,
        )
        self.http = http_client or httpx.AsyncClient(timeout=timeout)
        self._owns_client = http_client is None
        self.semaphore = asyncio.Semaphore(settings.model_max_concurrency)

    async def close(self) -> None:
        if self._owns_client:
            await self.http.aclose()

    async def generate(
        self,
        request: ModelGenerationRequest,
        *,
        base_url: str,
        api_key: str | None,
        model: str,
        request_id: str,
    ) -> ModelGenerationResult:
        started = time.perf_counter()
        retries = 0
        try:
            async with asyncio.timeout(self.settings.model_total_deadline_seconds):
                async with self.semaphore:
                    while True:
                        try:
                            result = await self._attempt(
                                request,
                                base_url=base_url,
                                api_key=api_key,
                                model=model,
                                request_id=request_id,
                            )
                            result.retry_count = retries
                            result.total_latency_ms = round((time.perf_counter() - started) * 1000)
                            return result
                        except ModelError as exc:
                            if not exc.retryable or retries >= self.settings.model_max_retries:
                                raise
                            retries += 1
                            delay = self.settings.model_retry_base_delay_ms / 1000 * (2 ** (retries - 1))
                            await asyncio.sleep(delay * random.uniform(0.8, 1.2))
        except TimeoutError as exc:
            raise ModelError(ModelErrorCode.TIMEOUT, "Model request timed out", retryable=True) from exc
    async def _attempt(self, request, *, base_url, api_key, model, request_id):
        headers = {"Content-Type": "application/json", "X-Request-ID": request_id}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        body = {
            "model": model,
            "messages": [m.model_dump() for m in request.messages],
            "max_tokens": request.max_output_tokens or self.settings.model_max_output_tokens,
            "temperature": request.temperature if request.temperature is not None else self.settings.model_temperature,
            "top_p": request.top_p if request.top_p is not None else self.settings.model_top_p,
        }
        started = time.perf_counter()
        try:
            response = await self.http.post(f"{base_url.rstrip('/')}/v1/chat/completions", headers=headers, json=body)
        except httpx.TimeoutException as exc:
            raise ModelError(ModelErrorCode.TIMEOUT, "Model request timed out", retryable=True) from exc
        except httpx.TransportError as exc:
            raise ModelError(ModelErrorCode.UNAVAILABLE, "Model transport unavailable", retryable=True) from exc
        if response.status_code in (401, 403):
            raise ModelError(ModelErrorCode.AUTHENTICATION_FAILED, "Model authentication failed")
        if response.status_code in (502, 503, 504):
            raise ModelError(ModelErrorCode.UNAVAILABLE, "Model server temporarily unavailable", retryable=True)
        if response.status_code == 404:
            raise ModelError(ModelErrorCode.NOT_LOADED, "Requested model is not loaded")
        if response.status_code >= 400:
            raise ModelError(ModelErrorCode.INVALID_RESPONSE, "Model server rejected request")
        try:
            data = response.json()
            choice = data["choices"][0]
            content = choice["message"]["content"].strip()
            if not content:
                raise ValueError("empty content")
            usage = data.get("usage") or {}
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise ModelError(ModelErrorCode.INVALID_RESPONSE, "Malformed model response") from exc
        elapsed = round((time.perf_counter() - started) * 1000)
        return ModelGenerationResult(
            content=content,
            model_name=data.get("model", model),
            model_version=self.settings.model_version,
            prompt_version=self.settings.prompt_version,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            total_latency_ms=elapsed,
            generation_latency_ms=elapsed,
            provider_endpoint=base_url,
            finish_reason=choice.get("finish_reason"),
        )
