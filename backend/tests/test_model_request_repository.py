import pytest

from app.repositories.model_request_repository import ModelRequestRepository


class Pool:
    def __init__(self):
        self.calls = []

    async def execute(self, query, *args):
        self.calls.append((query, args))


@pytest.mark.asyncio
async def test_pending_and_success_have_no_raw_content():
    pool = Pool()
    repo = ModelRequestRepository(pool)
    await repo.create_pending(
        request_id="r1",
        session_id=None,
        provider_endpoint="http://model",
        model_name="gemma-3-4b-base",
        model_version="v1",
        prompt_version="p1",
    )
    await repo.finish(
        "r1",
        status="succeeded",
        model_name="gemma-3-4b-base",
        prompt_tokens=2,
        completion_tokens=3,
        total_tokens=5,
        total_latency_ms=10,
    )
    combined = repr(pool.calls).lower()
    assert "raw_prompt" not in combined and "response_content" not in combined
    assert len(pool.calls) == 2


@pytest.mark.asyncio
async def test_repository_is_noop_without_database():
    repo = ModelRequestRepository(None)
    await repo.create_pending(
        request_id="r",
        session_id=None,
        provider_endpoint="x",
        model_name="m",
        model_version="v",
        prompt_version="p",
    )
    await repo.finish("r", status="failed", model_name="m", error_code="MODEL_TIMEOUT")
