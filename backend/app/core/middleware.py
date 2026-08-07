import logging
import re
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware

from app.core.request_context import request_id_context

logger = logging.getLogger("socra.request")
SAFE_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        supplied = request.headers.get("x-request-id", "")
        request_id = supplied if SAFE_ID.fullmatch(supplied) else f"req_{uuid.uuid4().hex}"
        request.state.request_id = request_id
        token = request_id_context.set(request_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            latency = round((time.perf_counter() - started) * 1000)
            logger.info(
                "request_complete",
                extra={
                    "structured": {
                        "request_id": request_id,
                        "method": request.method,
                        "route": request.url.path,
                        "status_code": locals().get("response").status_code if "response" in locals() else 500,
                        "latency_ms": latency,
                    }
                },
            )
            request_id_context.reset(token)
        response.headers["X-Request-ID"] = request_id
        return response
