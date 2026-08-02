from uuid import UUID

from fastapi import APIRouter, Depends

from app.auth.authorization import require_classroom_permission
from app.auth.dependencies import get_current_user
from app.auth.permissions import Permission
from app.core.errors import not_implemented

router = APIRouter()


async def unavailable():
    raise not_implemented("This API contract")


@router.api_route("/classrooms", methods=["GET", "POST"], dependencies=[Depends(get_current_user)])
async def classrooms():
    return await unavailable()


@router.api_route(
    "/classrooms/{classroom_id}",
    methods=["GET"],
    dependencies=[Depends(require_classroom_permission(Permission.CLASSROOM_READ))],
)
async def classroom_read(classroom_id: UUID):
    return await unavailable()


@router.api_route(
    "/classrooms/{classroom_id}",
    methods=["PATCH", "DELETE"],
    dependencies=[Depends(require_classroom_permission(Permission.CLASSROOM_UPDATE))],
)
async def classroom_write(classroom_id: UUID):
    return await unavailable()


@router.api_route(
    "/classrooms/{classroom_id}/members",
    methods=["GET"],
    dependencies=[Depends(require_classroom_permission(Permission.MEMBER_READ))],
)
async def members_read(classroom_id: UUID):
    return await unavailable()


@router.api_route(
    "/classrooms/{classroom_id}/members",
    methods=["POST"],
    dependencies=[Depends(require_classroom_permission(Permission.MEMBER_MANAGE))],
)
async def members_create(classroom_id: UUID):
    return await unavailable()


@router.api_route(
    "/classrooms/{classroom_id}/members/{member_id}",
    methods=["PATCH", "DELETE"],
    dependencies=[Depends(require_classroom_permission(Permission.MEMBER_MANAGE))],
)
async def members_write(classroom_id: UUID, member_id: UUID):
    return await unavailable()


@router.api_route(
    "/classrooms/{classroom_id}/materials",
    methods=["GET"],
    dependencies=[Depends(require_classroom_permission(Permission.MATERIAL_READ))],
)
async def materials_read(classroom_id: UUID):
    return await unavailable()


@router.api_route(
    "/classrooms/{classroom_id}/materials",
    methods=["POST"],
    dependencies=[Depends(require_classroom_permission(Permission.MATERIAL_CREATE))],
)
async def materials_create(classroom_id: UUID):
    return await unavailable()


for path, methods in (
    ("/materials/{material_id}", ["GET", "DELETE"]),
    ("/materials/{material_id}/status", ["GET"]),
    ("/tutoring-sessions", ["POST"]),
    ("/tutoring-sessions/{session_id}", ["GET"]),
    ("/tutoring-sessions/{session_id}/end", ["POST"]),
    ("/tutoring-sessions/{session_id}/messages", ["GET", "POST"]),
    ("/messages/{message_id}/feedback", ["POST"]),
    ("/tutoring-sessions/{session_id}/feedback", ["GET"]),
    ("/research/participant-status", ["GET"]),
    ("/research/consent", ["POST"]),
    ("/research/withdraw", ["POST"]),
):
    router.add_api_route(path, unavailable, methods=methods, dependencies=[Depends(get_current_user)])
