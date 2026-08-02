from uuid import uuid4

import pytest

from app.core.config import Settings
from app.repositories.message_repository import MessagePair
from app.schemas.model import ChatMessage, ModelErrorCode, ModelGenerationRequest
from app.services.deterministic_mock_model import DeterministicMockModelAdapter, MockScenario
from app.services.model_circuit_breaker import CircuitBreaker
from app.services.model_errors import ModelError
from app.services.model_gateway import ModelGateway
from app.services.tutoring_message_service import TutoringMessageService


def gateway(scenario, *, fallback=False):
    settings = Settings(
        model_provider="mock",
        model_mock_scenario=scenario,
        model_fallback_enabled=fallback,
        model_fallback_api_key="test-key" if fallback else None,
    )
    adapter = DeterministicMockModelAdapter(settings, scenario)
    return settings, adapter, ModelGateway(settings, adapter, CircuitBreaker(3, 30))


def request():
    return ModelGenerationRequest(messages=[ChatMessage(role="user", content="Help me reason about recursion")])


@pytest.mark.asyncio
async def test_mock_success():
    _, adapter, model_gateway = gateway(MockScenario.SUCCESS)
    result = await model_gateway.generate(request(), "req-success")
    assert result.provider_route == "mock"
    assert result.provider_endpoint == "mock"
    assert result.prompt_tokens > 0 and result.completion_tokens > 0
    assert adapter.calls == ["primary"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "scenario,code",
    [
        (MockScenario.TIMEOUT, ModelErrorCode.TIMEOUT),
        (MockScenario.NON_RETRYABLE_FAILURE, ModelErrorCode.INVALID_RESPONSE),
        (MockScenario.PRIMARY_AND_FALLBACK_FAILURE, ModelErrorCode.UNAVAILABLE),
    ],
)
async def test_mock_terminal_failures(scenario, code):
    _, _, model_gateway = gateway(scenario, fallback=scenario == MockScenario.PRIMARY_AND_FALLBACK_FAILURE)
    with pytest.raises(ModelError) as caught:
        await model_gateway.generate(request(), "req-fail")
    assert caught.value.code == code


@pytest.mark.asyncio
async def test_mock_retryable_failure_reports_one_retry():
    _, adapter, model_gateway = gateway(MockScenario.RETRYABLE_FAILURE)
    result = await model_gateway.generate(request(), "req-retry")
    assert result.retry_count == 1
    assert adapter.calls == ["primary", "primary"]


@pytest.mark.asyncio
async def test_mock_primary_failure_then_fallback_success():
    _, adapter, model_gateway = gateway(MockScenario.PRIMARY_FAILURE_FALLBACK_SUCCESS, fallback=True)
    result = await model_gateway.generate(request(), "req-fallback")
    assert adapter.calls == ["primary", "fallback"]
    assert result.fallback_used is True
    assert result.fallback_reason == "MODEL_UNAVAILABLE"
    assert result.provider_route == "mock"


class MemoryMessages:
    def __init__(self):
        self.by_key = {}
        self.rows = {}

    async def create_student_and_pending_assistant(self, *, session_id, student_id, content, client_request_id):
        key = (session_id, client_request_id)
        if key in self.by_key:
            student, assistant = self.by_key[key]
            return MessagePair(student, assistant, True)
        student, assistant = uuid4(), uuid4()
        self.by_key[key] = (student, assistant)
        self.rows[student] = {"id": student, "role": "student", "content": content, "status": "completed"}
        self.rows[assistant] = {
            "id": assistant,
            "role": "assistant",
            "content": "Pending response",
            "status": "pending",
        }
        return MessagePair(student, assistant, False)

    async def complete_assistant(self, assistant_id, content):
        self.rows[assistant_id].update(content=content, status="completed")

    async def fail_assistant(self, assistant_id):
        self.rows[assistant_id].update(content="Response unavailable", status="failed")

    async def get_pair(self, student_id, assistant_id):
        return [self.rows[student_id].copy(), self.rows[assistant_id].copy()]


class MemoryModelRequests:
    def __init__(self):
        self.rows = {}

    async def create_pending(self, **data):
        self.rows[data["request_id"]] = {
            **data,
            "status": "pending",
            "latency_ms": None,
            "input_tokens": 0,
            "output_tokens": 0,
            "retry_count": 0,
            "fallback_used": False,
            "fallback_reason": None,
            "error_code": None,
        }

    async def finish(self, request_id, **data):
        row = self.rows[request_id]
        row.update(data)
        row["latency_ms"] = data.get("total_latency_ms")
        row["input_tokens"] = data.get("prompt_tokens", 0)
        row["output_tokens"] = data.get("completion_tokens", 0)


@pytest.mark.asyncio
async def test_full_message_flow_database_readback_and_idempotency():
    settings, adapter, model_gateway = gateway(MockScenario.SUCCESS)
    messages, telemetry = MemoryMessages(), MemoryModelRequests()
    service = TutoringMessageService(messages, telemetry, model_gateway, settings)
    session_id, student_id = uuid4(), uuid4()
    first = await service.send(
        session_id=session_id,
        student_id=student_id,
        content="Explain recursion",
        client_request_id="frontend-1",
        request_id="request-1",
    )
    read_back = await messages.get_pair(first.student_message_id, first.assistant_message_id)
    assert [row["status"] for row in read_back] == ["completed", "completed"]
    assert read_back[1]["content"] == first.assistant_content
    model_row = telemetry.rows["request-1"]
    assert model_row["provider_route"] == "mock"
    assert model_row["status"] == "completed"
    assert model_row["latency_ms"] == 7
    assert model_row["input_tokens"] > 0 and model_row["output_tokens"] > 0
    duplicate = await service.send(
        session_id=session_id,
        student_id=student_id,
        content="Explain recursion",
        client_request_id="frontend-1",
        request_id="request-2",
    )
    assert duplicate.duplicate is True
    assert duplicate.student_message_id == first.student_message_id
    assert len(messages.rows) == 2
    assert adapter.calls == ["primary"]
    assert "request-2" not in telemetry.rows


@pytest.mark.asyncio
async def test_full_flow_failure_marks_assistant_and_safe_telemetry():
    settings, _, model_gateway = gateway(MockScenario.NON_RETRYABLE_FAILURE)
    messages, telemetry = MemoryMessages(), MemoryModelRequests()
    service = TutoringMessageService(messages, telemetry, model_gateway, settings)
    with pytest.raises(ModelError):
        await service.send(
            session_id=uuid4(),
            student_id=uuid4(),
            content="Fail safely",
            client_request_id="frontend-fail",
            request_id="request-fail",
        )
    assistant = next(row for row in messages.rows.values() if row["role"] == "assistant")
    assert assistant["status"] == "failed"
    assert telemetry.rows["request-fail"]["status"] == "failed"
    assert telemetry.rows["request-fail"]["error_code"] == "MODEL_INVALID_RESPONSE"


@pytest.mark.asyncio
async def test_full_flow_persists_mock_fallback_metadata():
    settings, _, model_gateway = gateway(MockScenario.PRIMARY_FAILURE_FALLBACK_SUCCESS, fallback=True)
    messages, telemetry = MemoryMessages(), MemoryModelRequests()
    service = TutoringMessageService(messages, telemetry, model_gateway, settings)
    result = await service.send(
        session_id=uuid4(),
        student_id=uuid4(),
        content="Use fallback",
        client_request_id="frontend-fallback",
        request_id="request-fallback",
    )
    assert result.assistant_status == "completed"
    row = telemetry.rows["request-fallback"]
    assert row["provider_route"] == "mock"
    assert row["fallback_used"] is True
    assert row["fallback_reason"] == "MODEL_UNAVAILABLE"
    assert row["status"] == "completed"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "scenario,expected_code",
    [
        (MockScenario.TIMEOUT, "MODEL_TIMEOUT"),
        (MockScenario.PRIMARY_AND_FALLBACK_FAILURE, "MODEL_UNAVAILABLE"),
    ],
)
async def test_full_flow_persists_safe_terminal_failures(scenario, expected_code):
    settings, _, model_gateway = gateway(scenario, fallback=scenario == MockScenario.PRIMARY_AND_FALLBACK_FAILURE)
    messages, telemetry = MemoryMessages(), MemoryModelRequests()
    service = TutoringMessageService(messages, telemetry, model_gateway, settings)
    with pytest.raises(ModelError):
        await service.send(
            session_id=uuid4(),
            student_id=uuid4(),
            content="Fail deterministically",
            client_request_id=f"frontend-{scenario}",
            request_id=f"request-{scenario}",
        )
    row = telemetry.rows[f"request-{scenario}"]
    assert row["status"] == "failed"
    assert row["error_code"] == expected_code
    assert row["provider_route"] == "mock"


def test_mock_flow_migration_contract():
    migration = (
        (
            __import__("pathlib").Path(__file__).parents[3]
            / "database/migrations/202608020002_add_mock_flow_and_idempotency.sql"
        )
        .read_text()
        .lower()
    )
    for required in (
        "provider_route",
        "latency_ms",
        "input_tokens",
        "output_tokens",
        "client_request_id",
        "reply_to_message_id",
        "pending",
        "completed",
        "failed",
    ):
        assert required in migration
    assert "messages_session_client_request_uidx" in migration


def test_mock_is_rejected_in_production():
    with pytest.raises(ValueError, match="mock is not allowed"):
        Settings(app_env="production", model_provider="mock")
