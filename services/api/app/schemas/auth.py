from uuid import UUID

from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    auth_user_id: UUID
    internal_user_id: UUID
    email: str | None = None
    is_authenticated: bool = True
    is_admin: bool = False
    is_researcher: bool = False


class MeResponse(AuthenticatedUser):
    pass
