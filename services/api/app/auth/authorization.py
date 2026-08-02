from uuid import UUID

from fastapi import Depends, Request

from app.auth.dependencies import get_current_user
from app.auth.permissions import Permission, role_has_permission
from app.auth.roles import ClassroomRole
from app.core.errors import APIError


def require_classroom_permission(permission: Permission):
    async def dependency(classroom_id: UUID, request: Request, user=Depends(get_current_user)):
        membership = await request.app.state.users.membership(user.internal_user_id, classroom_id)
        if not membership or membership["status"] != "active":
            raise APIError(403, "MEMBERSHIP_REQUIRED", "Active classroom membership is required.")
        role = ClassroomRole(membership["role"])
        if not role_has_permission(role, permission):
            raise APIError(403, "FORBIDDEN", "You do not have permission to perform this action.")
        return user

    return dependency
