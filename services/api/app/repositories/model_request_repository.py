import logging

import asyncpg

logger = logging.getLogger(__name__)


class ModelRequestRepository:
    """Async PostgreSQL telemetry. Payloads cannot contain prompt/response columns."""

    def __init__(self, pool: asyncpg.Pool | None):
        self.pool = pool

    async def create_pending(
        self,
        *,
        request_id: str,
        session_id: str | None,
        provider_endpoint: str,
        model_name: str,
        model_version: str,
        prompt_version: str,
        provider_route: str = "primary",
        student_message_id: str | None = None,
        assistant_message_id: str | None = None,
    ) -> None:
        if not self.pool:
            return
        await self.pool.execute(
            """insert into public.model_requests
               (request_id, session_id, provider_endpoint, model_name, model_version,
                prompt_version, status, provider_route, student_message_id, assistant_message_id)
               values ($1, $2::uuid, $3, $4, $5, $6, 'pending', $7, $8::uuid, $9::uuid)
               on conflict (request_id) do nothing""",
            request_id,
            session_id,
            provider_endpoint,
            model_name,
            model_version,
            prompt_version,
            provider_route,
            student_message_id,
            assistant_message_id,
        )

    async def finish(
        self,
        request_id: str,
        *,
        status: str,
        model_name: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        total_latency_ms: int | None = None,
        retry_count: int = 0,
        fallback_used: bool = False,
        fallback_reason: str | None = None,
        error_code: str | None = None,
        provider_endpoint: str | None = None,
        provider_route: str | None = None,
    ) -> None:
        if not self.pool:
            return
        await self.pool.execute(
            """update public.model_requests set status=$2, model_name=$3,
               prompt_tokens=$4, completion_tokens=$5, total_tokens=$6,
               total_latency_ms=$7, latency_ms=$7, input_tokens=$4, output_tokens=$5,
               retry_count=$8, fallback_used=$9,
               fallback_reason=$10, error_code=$11,
               provider_endpoint=coalesce($12, provider_endpoint),
               provider_route=coalesce($13, provider_route)
               where request_id=$1""",
            request_id,
            status,
            model_name,
            prompt_tokens,
            completion_tokens,
            total_tokens,
            total_latency_ms,
            retry_count,
            fallback_used,
            fallback_reason,
            error_code,
            provider_endpoint,
            provider_route,
        )
