import asyncio

import httpx
import pytest

from app.core.config import Settings
from app.schemas.model import ChatMessage, ModelErrorCode, ModelGenerationRequest
from app.services.model_circuit_breaker import CircuitBreaker, CircuitState
from app.services.model_client import ModelClient
from app.services.model_errors import ModelError
from app.services.model_response_policy import validate_response


def request():
    return ModelGenerationRequest(
        messages=[ChatMessage(role="user", content="Help me reason about preorder traversal")]
    )


@pytest.mark.asyncio
async def test_success_and_usage_parsing():
    def handler(req):
        assert req.headers["x-request-id"] == "r1"
        return httpx.Response(
            200,
            json={
                "model": "socra",
                "choices": [{"message": {"content": "What node is visited first?"}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 4, "completion_tokens": 6, "total_tokens": 10},
            },
        )

    http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    result = await ModelClient(Settings(), http).generate(
        request(), base_url="http://model", api_key="secret", model="socra", request_id="r1"
    )
    assert result.total_tokens == 10
    assert result.content.startswith("What")
    await http.aclose()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status,code,retryable",
    [
        (400, ModelErrorCode.INVALID_RESPONSE, False),
        (401, ModelErrorCode.AUTHENTICATION_FAILED, False),
        (403, ModelErrorCode.AUTHENTICATION_FAILED, False),
        (502, ModelErrorCode.UNAVAILABLE, True),
        (503, ModelErrorCode.UNAVAILABLE, True),
        (504, ModelErrorCode.UNAVAILABLE, True),
    ],
)
async def test_http_errors(status, code, retryable):
    http = httpx.AsyncClient(transport=httpx.MockTransport(lambda req: httpx.Response(status)))
    client = ModelClient(Settings(model_max_retries=0), http)
    with pytest.raises(ModelError) as caught:
        await client.generate(request(), base_url="http://model", api_key=None, model="x", request_id="r")
    assert caught.value.code == code and caught.value.retryable == retryable
    await http.aclose()


@pytest.mark.asyncio
async def test_retry_once():
    calls = 0

    def handler(req):
        nonlocal calls
        calls += 1
        return httpx.Response(
            503 if calls == 1 else 200, json={} if calls == 1 else {"choices": [{"message": {"content": "Question?"}}]}
        )

    http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    result = await ModelClient(Settings(model_retry_base_delay_ms=0), http).generate(
        request(), base_url="http://m", api_key=None, model="x", request_id="r"
    )
    assert calls == 2 and result.retry_count == 1
    await http.aclose()


@pytest.mark.asyncio
async def test_total_deadline_timeout_is_normalized():
    async def handler(req):
        del req
        await asyncio.sleep(0.05)
        return httpx.Response(200, json={"choices": [{"message": {"content": "late"}}]})

    http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client = ModelClient(Settings(model_total_deadline_seconds=0.01, model_max_retries=0), http)
    with pytest.raises(ModelError) as caught:
        await client.generate(request(), base_url="http://model", api_key=None, model="x", request_id="r")
    assert caught.value.code == ModelErrorCode.TIMEOUT
    await http.aclose()


@pytest.mark.asyncio
async def test_circuit_breaker_transitions():
    breaker = CircuitBreaker(2, 0)
    await breaker.failure()
    assert breaker.state == CircuitState.CLOSED
    await breaker.failure()
    assert breaker.state == CircuitState.OPEN
    assert await breaker.allow()
    assert breaker.state == CircuitState.HALF_OPEN
    await breaker.success()
    assert breaker.state == CircuitState.CLOSED


def test_policy_rejects_complete_code():
    result = validate_response("```python\ndef preorder(x):\n  return []\n```", "Give complete code solution")
    assert not result.accepted
