import hmac
import uuid
from contextlib import asynccontextmanager

import asyncpg
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import dependency_router, root_router
from app.api.health import router as health_router
from app.api.v1.router import router as v1_router
from app.auth.dependencies import get_current_user
from app.core.config import get_settings
from app.core.errors import APIError
from app.core.exception_handlers import install_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.repositories.model_request_repository import ModelRequestRepository
from app.repositories.user_repository import UserRepository
from app.schemas.model import ModelGenerationRequest
from app.services.model_circuit_breaker import CircuitBreaker
from app.services.model_client import ModelClient
from app.services.model_errors import ModelError
from app.services.model_gateway import ModelGateway
from app.services.model_usage import safely_record

CONTROLLED_ERROR = "Socra cannot generate the next question right now. Your message has been saved. Please try again."


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings)
    pool = None
    if settings.database_url:
        try:
            pool = await asyncpg.create_pool(
                settings.database_url.get_secret_value(),
                min_size=1,
                max_size=5,
            )
        except Exception:
            raise RuntimeError("Database connection failed; verify the redacted DATABASE_URL configuration.") from None
    client = ModelClient(settings)
    app.state.settings = settings
    app.state.db_pool = pool
    app.state.model_client = client
    app.state.gateway = ModelGateway(
        settings,
        client,
        CircuitBreaker(
            settings.model_circuit_breaker_failure_threshold,
            settings.model_circuit_breaker_reset_seconds,
        ),
    )
    app.state.model_requests = ModelRequestRepository(pool)
    app.state.users = UserRepository(pool)
    yield
    await client.close()
    if pool:
        await pool.close()


app = FastAPI(title="Socra API", version="0.1.0", lifespan=lifespan)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)
install_exception_handlers(app)
app.include_router(health_router)
app.include_router(root_router)
app.include_router(dependency_router)
app.include_router(v1_router, prefix=get_settings().api_v1_prefix)


@app.post("/api/v1/model/generate")
async def generate(body: ModelGenerationRequest, request: Request, user=Depends(get_current_user)):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    repo = request.app.state.model_requests
    settings = request.app.state.settings
    await safely_record(
        repo.create_pending,
        request_id=request_id,
        session_id=body.session_id,
        provider_endpoint=settings.model_primary_url,
        model_name=settings.model_primary_name,
        model_version=settings.model_version,
        prompt_version=settings.prompt_version,
    )
    try:
        result = await request.app.state.gateway.generate(body, request_id)
        await safely_record(
            repo.finish,
            request_id,
            status="succeeded",
            model_name=result.model_name,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            total_tokens=result.total_tokens,
            total_latency_ms=result.total_latency_ms,
            retry_count=result.retry_count,
            fallback_used=result.fallback_used,
            fallback_reason=result.fallback_reason,
            provider_endpoint=result.provider_endpoint,
        )
        return result
    except ModelError as exc:
        await safely_record(
            repo.finish,
            request_id,
            status="failed",
            model_name=settings.model_primary_name,
            error_code=exc.code.value,
        )
        status = 504 if exc.code.value == "MODEL_TIMEOUT" else 503
        raise APIError(status, exc.code.value, CONTROLLED_ERROR) from None


@app.post("/api/v1/internal/model/smoke-test")
async def internal_smoke(request: Request):
    settings = request.app.state.settings
    if settings.environment not in {"development", "test"} or not settings.internal_routes_enabled:
        raise HTTPException(404, "Not found")
    if not settings.internal_service_token:
        raise HTTPException(404, "Not found")
    supplied = request.headers.get("x-internal-token", "")
    expected = settings.internal_service_token.get_secret_value()
    if not hmac.compare_digest(supplied, expected):
        raise HTTPException(401, "Unauthorized")
    body = ModelGenerationRequest(
        messages=[
            {"role": "system", "content": "You are Socra. Ask one concise guiding question."},
            {"role": "user", "content": "Help me reason about preorder traversal."},
        ],
        max_output_tokens=64,
    )
    result = await request.app.state.gateway.generate(body)
    return {
        "status": "ok",
        "model": result.model_name,
        "latency_ms": result.total_latency_ms,
        "total_tokens": result.total_tokens,
        "fallback_used": result.fallback_used,
    }
