from enum import StrEnum


class ClassroomRole(StrEnum):
    STUDENT = "student"
    TA = "ta"
    INSTRUCTOR = "instructor"


class SystemRole(StrEnum):
    ADMIN = "admin"
