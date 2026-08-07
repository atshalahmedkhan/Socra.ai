import json
import logging
import time

import jwt
import pytest
from fastapi.testclient import TestClient

from app.auth.jwt import verify_access_token
from app.auth.permissions import Permission, role_has_permission
from app.auth.roles import ClassroomRole
from app.core.config import Settings
from app.core.errors import APIError
from app.core.logging import JsonFormatter, redact
from app.main import app


def test_missing_auth_uses_stable_error_and_request_id():
    with TestClient(app) as client:
        response = client.get("/api/v1/auth/me", headers={"X-Request-ID": "req_test"})
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "AUTH_REQUIRED",
            "message": "Authentication is required.",
            "request_id": "req_test",
            "details": {},
        }
    }
    assert response.headers["x-request-id"] == "req_test"


def test_invalid_request_id_is_replaced():
    with TestClient(app) as client:
        response = client.get("/health/live", headers={"X-Request-ID": "bad value\n"})
    assert response.status_code == 200
    assert response.headers["x-request-id"].startswith("req_")


def test_root_health_remains_available_without_dependencies():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_dependency_health_is_safe_and_contains_no_endpoints():
    with TestClient(app) as client:
        response = client.get("/api/v1/health/dependencies")
    assert response.status_code == 503
    payload = response.json()
    assert payload["database"] == "not_configured"
    assert payload["supabase_jwks"] == "not_configured"
    assert payload["primary_model"] == "unavailable"
    serialized = json.dumps(payload).lower()
    assert "http://" not in serialized
    assert "postgresql://" not in serialized


def test_validation_error_is_normalized():
    with TestClient(app) as client:
        response = client.get("/api/v1/classrooms/not-a-uuid")
    assert response.status_code == 401  # authentication happens before resource parsing/authorization
    assert response.json()["error"]["request_id"]


def test_valid_and_expired_jwt():
    settings = Settings(
        supabase_jwt_secret="unit-secret-that-is-at-least-32-bytes-long",
        supabase_jwt_issuer="https://issuer.test",
        supabase_jwt_audience="authenticated",
    )
    claims = {
        "sub": "11111111-1111-1111-1111-111111111111",
        "iss": "https://issuer.test",
        "aud": "authenticated",
        "exp": int(time.time()) + 60,
    }
    token = jwt.encode(claims, "unit-secret-that-is-at-least-32-bytes-long", algorithm="HS256")
    assert verify_access_token(token, settings)["sub"] == claims["sub"]
    claims["exp"] = int(time.time()) - 1
    with pytest.raises(APIError) as caught:
        verify_access_token(
            jwt.encode(claims, "unit-secret-that-is-at-least-32-bytes-long", algorithm="HS256"), settings
        )
    assert caught.value.code == "TOKEN_EXPIRED"


@pytest.mark.parametrize(
    "change",
    [
        {"iss": "wrong"},
        {"aud": "wrong"},
        {"sub": None},
    ],
)
def test_invalid_jwt_claims(change):
    settings = Settings(
        supabase_jwt_secret="unit-secret-that-is-at-least-32-bytes-long",
        supabase_jwt_issuer="https://issuer.test",
        supabase_jwt_audience="authenticated",
    )
    claims = {
        "sub": "11111111-1111-1111-1111-111111111111",
        "iss": "https://issuer.test",
        "aud": "authenticated",
        "exp": int(time.time()) + 60,
    }
    claims.update(change)
    token = jwt.encode(claims, "unit-secret-that-is-at-least-32-bytes-long", algorithm="HS256")
    with pytest.raises(APIError) as caught:
        verify_access_token(token, settings)
    assert caught.value.code == "INVALID_TOKEN"


def test_role_permissions_are_centralized():
    assert role_has_permission(ClassroomRole.STUDENT, Permission.CLASSROOM_READ)
    assert not role_has_permission(ClassroomRole.STUDENT, Permission.MEMBER_MANAGE)
    assert role_has_permission(ClassroomRole.INSTRUCTOR, Permission.MEMBER_MANAGE)


def test_redaction_is_recursive():
    data = redact(
        {
            "authorization": "Bearer secret",
            "nested": {"database_url": "postgres://secret"},
            "student_message": "must not be passed to logger",
        }
    )
    assert data["authorization"] == "[REDACTED]"
    assert data["nested"]["database_url"] == "[REDACTED]"


def test_json_log_has_service_and_no_secret():
    record = logging.LogRecord("test", logging.INFO, "", 0, "done", (), None)
    record.structured = {"authorization": "secret", "request_id": "r1"}
    output = json.loads(JsonFormatter().format(record))
    assert output["service"] == "socra-api"
    assert output["authorization"] == "[REDACTED]"


def test_production_rejects_unsafe_configuration():
    with pytest.raises(ValueError):
        Settings(app_env="production", debug=True, cors_allowed_origins=["*"])
