import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.core.errors import APIError

logger = logging.getLogger(__name__)


def payload(request: Request, code: str, message: str, details=None):
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": getattr(request.state, "request_id", "unknown"),
            "details": details or {},
        }
    }


async def api_error_handler(request: Request, exc: APIError):
    return JSONResponse(payload(request, exc.code, exc.message, exc.details), status_code=exc.status_code)


async def validation_handler(request: Request, exc: RequestValidationError):
    details = [
        {"field": ".".join(map(str, item["loc"])), "message": item["msg"], "type": item["type"]}
        for item in exc.errors()
    ]
    return JSONResponse(
        payload(request, "VALIDATION_ERROR", "The request is invalid.", {"errors": details}), status_code=422
    )


async def http_handler(request: Request, exc: HTTPException):
    codes = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}
    return JSONResponse(
        payload(request, codes.get(exc.status_code, "INVALID_REQUEST"), str(exc.detail)), status_code=exc.status_code
    )


async def unexpected_handler(request: Request, exc: Exception):
    logger.exception("Unhandled request error")
    return JSONResponse(payload(request, "INTERNAL_ERROR", "An unexpected error occurred."), status_code=500)


def install_exception_handlers(app):
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_handler)
    app.add_exception_handler(HTTPException, http_handler)
    app.add_exception_handler(Exception, unexpected_handler)
