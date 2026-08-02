from enum import StrEnum

from app.auth.roles import ClassroomRole


class Permission(StrEnum):
    CLASSROOM_READ = "classroom:read"
    CLASSROOM_UPDATE = "classroom:update"
    CLASSROOM_DELETE = "classroom:delete"
    MEMBER_READ = "member:read"
    MEMBER_MANAGE = "member:manage"
    MATERIAL_READ = "material:read"
    MATERIAL_CREATE = "material:create"
    MATERIAL_DELETE = "material:delete"
    SESSION_CREATE = "session:create"
    SESSION_READ_OWN = "session:read_own"
    SESSION_READ_AGGREGATE = "session:read_classroom_aggregate"
    MESSAGE_CREATE = "message:create"
    FEEDBACK_CREATE = "feedback:create"
    RESEARCH_READ = "research:read_anonymized"
    SYSTEM_ADMIN = "system:admin"


ROLE_PERMISSIONS = {
    ClassroomRole.STUDENT: {
        Permission.CLASSROOM_READ,
        Permission.MATERIAL_READ,
        Permission.SESSION_CREATE,
        Permission.SESSION_READ_OWN,
        Permission.MESSAGE_CREATE,
        Permission.FEEDBACK_CREATE,
    },
    ClassroomRole.TA: {
        Permission.CLASSROOM_READ,
        Permission.MEMBER_READ,
        Permission.MATERIAL_READ,
        Permission.MATERIAL_CREATE,
        Permission.SESSION_READ_AGGREGATE,
    },
    ClassroomRole.INSTRUCTOR: {
        Permission.CLASSROOM_READ,
        Permission.CLASSROOM_UPDATE,
        Permission.CLASSROOM_DELETE,
        Permission.MEMBER_READ,
        Permission.MEMBER_MANAGE,
        Permission.MATERIAL_READ,
        Permission.MATERIAL_CREATE,
        Permission.MATERIAL_DELETE,
        Permission.SESSION_READ_AGGREGATE,
    },
}


def role_has_permission(role: ClassroomRole, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS[role]
