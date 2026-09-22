import time
from uuid import uuid4

import jwt
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.main import app


@pytest.fixture
def auth_headers():
    settings = app.state.settings
    secret = "unit-secret-that-is-at-least-32-bytes-long"
    settings.supabase_jwt_secret = SecretStr(secret)
    settings.supabase_jwt_issuer = "https://issuer.test"
    settings.supabase_jwt_audience = "authenticated"

    user_id = str(uuid4())
    claims = {
        "sub": user_id,
        "iss": "https://issuer.test",
        "aud": "authenticated",
        "exp": int(time.time()) + 3600,
    }
    token = jwt.encode(claims, secret, algorithm="HS256")
    return {"Authorization": f"Bearer {token}", "X-Request-ID": "req_tutoring_test"}



def test_tutoring_session_lifecycle(auth_headers):
    with TestClient(app) as client:
        classroom_id = str(uuid4())

        # 1. Create Session
        resp = client.post(
            "/api/v1/tutoring-sessions",
            headers=auth_headers,
            json={
                "classroom_id": classroom_id,
                "learning_objective": "Master recursion base cases",
            },
        )
        assert resp.status_code == 200, resp.text
        session_data = resp.json()
        session_id = session_data["id"]
        assert session_data["status"] == "active"
        assert session_data["learning_objective"] == "Master recursion base cases"

        # 2. Get Messages (should contain the opening greeting)
        resp = client.get(f"/api/v1/tutoring-sessions/{session_id}/messages", headers=auth_headers)
        assert resp.status_code == 200
        messages = resp.json()
        assert len(messages) == 1
        assert messages[0]["role"] == "assistant"

        # 3. Student sends a message with struggle / confusion
        resp = client.post(
            f"/api/v1/tutoring-sessions/{session_id}/messages",
            headers=auth_headers,
            json={"content": "I am stuck and don't know when the recursive call stops"},
        )
        assert resp.status_code == 200, resp.text
        turn_data = resp.json()
        assert turn_data["session_id"] == session_id
        assert turn_data["diagnostic"]["misconception"] == "frustration_or_stuck"
        assert turn_data["attempts"] == 1
        assert turn_data["assistant_message"]["content"]

        # 4. Student explicitly requests a hint
        resp = client.post(
            f"/api/v1/tutoring-sessions/{session_id}/hint",
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        hint_data = resp.json()
        assert hint_data["hints_used"] == 1
        assert hint_data["hint_level"] >= 1

        # 5. Get Session Summary
        resp = client.get(f"/api/v1/tutoring-sessions/{session_id}/summary", headers=auth_headers)
        assert resp.status_code == 200
        summary = resp.json()
        assert summary["attempts"] == 1
        assert summary["hints_used"] == 1
        assert summary["total_turns"] >= 3

        # 6. End Session
        resp = client.post(
            f"/api/v1/tutoring-sessions/{session_id}/end",
            headers=auth_headers,
            json={"status": "completed"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

        # 7. Messages to closed session should be rejected
        resp = client.post(
            f"/api/v1/tutoring-sessions/{session_id}/messages",
            headers=auth_headers,
            json={"content": "Can I still ask something?"},
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "SESSION_CLOSED"


def test_tutoring_session_not_found(auth_headers):
    with TestClient(app) as client:
        random_id = str(uuid4())
        resp = client.get(f"/api/v1/tutoring-sessions/{random_id}", headers=auth_headers)
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "NOT_FOUND"
