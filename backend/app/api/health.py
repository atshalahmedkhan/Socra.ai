import asyncio
import time

from fastapi import APIRouter, Request, Response

router = APIRouter(prefix="/health", tags=["health"])
root_router = APIRouter(tags=["health"])
dependency_router = APIRouter(prefix="/api/v1/health", tags=["health"])


@root_router.get("/health")
async def root_live(request: Request):
    return {
        "status": "ok",
        "service": "socra-api",
        "version": request.app.state.settings.service_version,
    }


@router.get("/live")
async def live(request: Request):
    return {"status": "alive", "service": "socra-api", "version": request.app.state.settings.service_version}


async def _model_health(client, url, key, expected, timeout):
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    try:
        async with asyncio.timeout(timeout):
            health, models = await asyncio.gather(
                client.get(f"{url.rstrip('/')}/health", headers=headers),
                client.get(f"{url.rstrip('/')}/v1/models", headers=headers),
            )
        ids = [item.get("id") for item in models.json().get("data", [])]
        return health.status_code == 200 and models.status_code == 200 and expected in ids
    except Exception:
        return False


async def _database_status(request: Request) -> str:
    pool = request.app.state.db_pool
    if not pool:
        return "not_configured"
    try:
        async with asyncio.timeout(request.app.state.settings.model_health_timeout_seconds):
            await pool.fetchval("select 1")
        return "healthy"
    except Exception:
        return "unavailable"


async def _jwks_status(request: Request) -> str:
    settings = request.app.state.settings
    if not settings.supabase_jwks_url:
        return "not_configured"
    try:
        async with asyncio.timeout(settings.model_health_timeout_seconds):
            result = await request.app.state.model_client.http.get(settings.supabase_jwks_url)
        return "healthy" if result.status_code == 200 else "unavailable"
    except Exception:
        return "unavailable"


async def _dependency_states(request: Request) -> dict[str, str]:
    settings = request.app.state.settings
    client = request.app.state.model_client.http
    primary_key = settings.model_primary_api_key.get_secret_value() if settings.model_primary_api_key else None
    database, jwks, primary_ok = await asyncio.gather(
        _database_status(request),
        _jwks_status(request),
        _model_health(
            client,
            settings.model_primary_url,
            primary_key,
            settings.model_primary_name,
            settings.model_health_timeout_seconds,
        ),
    )
    fallback = "not_configured"
    if settings.model_fallback_enabled:
        fallback_key = settings.model_fallback_api_key.get_secret_value() if settings.model_fallback_api_key else None
        fallback_ok = await _model_health(
            client,
            settings.model_fallback_url,
            fallback_key,
            settings.model_fallback_name,
            settings.model_health_timeout_seconds,
        )
        fallback = "healthy" if fallback_ok else "unavailable"
    return {
        "database": database,
        "supabase_jwks": jwks,
        "primary_model": "healthy" if primary_ok else "unavailable",
        "fallback_model": fallback,
    }


@dependency_router.get("/dependencies")
async def dependencies(request: Request, response: Response):
    states = await _dependency_states(request)
    core_available = states["database"] == "healthy" and states["supabase_jwks"] == "healthy"
    if core_available and states["primary_model"] == "healthy":
        status = "healthy"
    elif core_available:
        status = "degraded"
    else:
        status = "unavailable"
        response.status_code = 503
    return {"status": status, **states}


@router.get("/ready")
async def ready(request: Request, response: Response):
    states = await _dependency_states(request)
    primary = states["primary_model"] == "healthy"
    fallback = states["fallback_model"] == "healthy"
    database = states["database"]
    status = "ready" if primary and database == "healthy" else "degraded" if fallback else "unavailable"
    if status == "unavailable":
        response.status_code = 503
    return {"status": status, **states}


@router.get("/model")
async def model_health(request: Request, response: Response):
    if not request.app.state.settings.model_deep_health_enabled:
        response.status_code = 404
        return {"status": "disabled"}
    started = time.perf_counter()
    return {
        "status": "enabled",
        "model": request.app.state.settings.model_primary_name,
        "latency_ms": round((time.perf_counter() - started) * 1000),
    }
