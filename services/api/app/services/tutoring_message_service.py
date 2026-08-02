from dataclasses import dataclass
from uuid import UUID

from app.repositories.message_repository import MessageRepository
from app.repositories.model_request_repository import ModelRequestRepository
from app.schemas.model import ChatMessage, ModelGenerationRequest
from app.services.model_errors import ModelError


@dataclass(frozen=True)
class TutoringMessageResult:
    student_message_id: UUID
    assistant_message_id: UUID
    assistant_status: str
    assistant_content: str
    duplicate: bool


class TutoringMessageService:
    def __init__(self, messages: MessageRepository, model_requests: ModelRequestRepository, gateway, settings):
        self.messages = messages
        self.model_requests = model_requests
        self.gateway = gateway
        self.settings = settings

    async def send(
        self, *, session_id: UUID, student_id: UUID, content: str,
        client_request_id: str, request_id: str,
    ) -> TutoringMessageResult:
        pair = await self.messages.create_student_and_pending_assistant(
            session_id=session_id, student_id=student_id, content=content,
            client_request_id=client_request_id,
        )
        if pair.duplicate:
            rows = await self.messages.get_pair(pair.student_id, pair.assistant_id)
            assistant = next(row for row in rows if row["id"] == pair.assistant_id)
            return TutoringMessageResult(
                pair.student_id, pair.assistant_id, assistant["status"],
                assistant["content"], True,
            )
        provider_endpoint = "mock" if self.settings.model_provider == "mock" else self.settings.model_primary_url
        provider_route = "mock" if self.settings.model_provider == "mock" else "primary"
        model_name = "deterministic-mock" if self.settings.model_provider == "mock" else self.settings.model_primary_name
        model_version = "mock-v1" if self.settings.model_provider == "mock" else self.settings.model_version

        await self.model_requests.create_pending(
            request_id=request_id,
            session_id=str(session_id),
            provider_endpoint=provider_endpoint,
            provider_route=provider_route,
            model_name=model_name,
            model_version=model_version,
            prompt_version=self.settings.prompt_version,
            student_message_id=str(pair.student_id),
            assistant_message_id=str(pair.assistant_id),
        )
        request = ModelGenerationRequest(session_id=str(session_id), messages=[ChatMessage(role="user", content=content)])
        try:
            result = await self.gateway.generate(request, request_id)
        except ModelError as exc:
            await self.messages.fail_assistant(pair.assistant_id)
            await self.model_requests.finish(
                request_id,
                status="failed",
                model_name=model_name,
                error_code=exc.code.value,
                provider_endpoint=provider_endpoint,
                provider_route=provider_route,
            )
            raise
        await self.messages.complete_assistant(pair.assistant_id, result.content)
        await self.model_requests.finish(
            request_id,
            status="completed",
            model_name=result.model_name,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            total_tokens=result.total_tokens,
            total_latency_ms=result.total_latency_ms,
            retry_count=result.retry_count,
            fallback_used=result.fallback_used,
            fallback_reason=result.fallback_reason,
            provider_endpoint=result.provider_endpoint,
            provider_route=result.provider_route,
        )
        return TutoringMessageResult(
            pair.student_id, pair.assistant_id, "completed", result.content, False
        )
