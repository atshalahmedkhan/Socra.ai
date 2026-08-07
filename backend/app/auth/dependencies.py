from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import verify_access_token
from app.core.errors import APIError
from app.schemas.auth import AuthenticatedUser

bearer = HTTPBearer(auto_error=False)


async def get_optional_user(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if not credentials:
        return None
    if credentials.scheme.lower() != "bearer":
        raise APIError(401, "INVALID_TOKEN", "The authorization header is invalid.")
    claims = verify_access_token(credentials.credentials, request.app.state.settings)
    try:
        auth_id = UUID(claims["sub"])
    except (KeyError, ValueError):
        raise APIError(401, "INVALID_TOKEN", "The access token is invalid.") from None
    record = await request.app.state.users.get_or_create(auth_id, claims.get("email"))
    return AuthenticatedUser(
        auth_user_id=record["auth_user_id"],
        internal_user_id=record["id"],
        email=record["email"],
        is_admin=record["is_admin"],
        is_researcher=record["is_researcher"],
    )


async def get_current_user(user=Depends(get_optional_user)):
    if not user:
        raise APIError(401, "AUTH_REQUIRED", "Authentication is required.")
    return user
