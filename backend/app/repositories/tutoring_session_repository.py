from datetime import UTC, datetime
from uuid import UUID, uuid4

import asyncpg

from app.schemas.remediation import (
    HintLevel,
    MessageRole,
    SessionMessage,
    SessionStatus,
    TutoringSessionResponse,
)


class TutoringSessionRepository:
    """Repository for managing tutoring sessions and message history."""

    def __init__(self, pool: asyncpg.Pool | None = None):
        self.pool = pool
        self._memory_sessions: dict[UUID, dict] = {}
        self._memory_messages: dict[UUID, list[dict]] = {}

    async def create_session(
        self,
        classroom_id: UUID,
        student_id: UUID,
        learning_objective: str | None = None,
    ) -> TutoringSessionResponse:
        now = datetime.now(UTC)
        if not self.pool:
            session_id = uuid4()
            record = {
                "id": session_id,
                "classroom_id": classroom_id,
                "student_id": student_id,
                "learning_objective": learning_objective,
                "status": SessionStatus.ACTIVE,
                "hints_used": 0,
                "attempts": 0,
                "started_at": now,
                "ended_at": None,
                "created_at": now,
                "updated_at": now,
            }
            self._memory_sessions[session_id] = record
            self._memory_messages[session_id] = []
            return TutoringSessionResponse(**record)

        row = await self.pool.fetchrow(
            """
            insert into public.tutoring_sessions
                (classroom_id, student_id, learning_objective, status, hints_used, attempts, started_at)
            values ($1, $2, $3, 'active', 0, 0, now())
            returning id, classroom_id, student_id, learning_objective, status,
                      hints_used, attempts, started_at, ended_at, created_at, updated_at
            """,
            classroom_id,
            student_id,
            learning_objective,
        )
        return TutoringSessionResponse(
            id=row["id"],
            classroom_id=row["classroom_id"],
            student_id=row["student_id"],
            learning_objective=row["learning_objective"],
            status=SessionStatus(row["status"]),
            hints_used=row["hints_used"],
            attempts=row["attempts"],
            started_at=row["started_at"],
            ended_at=row["ended_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def get_session(self, session_id: UUID) -> TutoringSessionResponse | None:
        if not self.pool:
            data = self._memory_sessions.get(session_id)
            return TutoringSessionResponse(**data) if data else None

        row = await self.pool.fetchrow(
            """
            select id, classroom_id, student_id, learning_objective, status,
                   hints_used, attempts, started_at, ended_at, created_at, updated_at
            from public.tutoring_sessions
            where id = $1
            """,
            session_id,
        )
        if not row:
            return None

        return TutoringSessionResponse(
            id=row["id"],
            classroom_id=row["classroom_id"],
            student_id=row["student_id"],
            learning_objective=row["learning_objective"],
            status=SessionStatus(row["status"]),
            hints_used=row["hints_used"],
            attempts=row["attempts"],
            started_at=row["started_at"],
            ended_at=row["ended_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def update_session_stats(
        self,
        session_id: UUID,
        hints_used: int,
        attempts: int,
        status: SessionStatus = SessionStatus.ACTIVE,
    ) -> None:
        now = datetime.now(UTC)
        if not self.pool:
            if session_id in self._memory_sessions:
                self._memory_sessions[session_id]["hints_used"] = hints_used
                self._memory_sessions[session_id]["attempts"] = attempts
                self._memory_sessions[session_id]["status"] = status
                self._memory_sessions[session_id]["updated_at"] = now
            return

        await self.pool.execute(
            """
            update public.tutoring_sessions
            set hints_used = $2, attempts = $3, status = $4, updated_at = now()
            where id = $1
            """,
            session_id,
            hints_used,
            attempts,
            status.value,
        )

    async def end_session(
        self,
        session_id: UUID,
        status: SessionStatus = SessionStatus.COMPLETED,
    ) -> TutoringSessionResponse | None:
        now = datetime.now(UTC)
        if not self.pool:
            if session_id in self._memory_sessions:
                self._memory_sessions[session_id]["status"] = status
                self._memory_sessions[session_id]["ended_at"] = now
                self._memory_sessions[session_id]["updated_at"] = now
                return TutoringSessionResponse(**self._memory_sessions[session_id])
            return None

        row = await self.pool.fetchrow(
            """
            update public.tutoring_sessions
            set status = $2, ended_at = now(), updated_at = now()
            where id = $1
            returning id, classroom_id, student_id, learning_objective, status,
                      hints_used, attempts, started_at, ended_at, created_at, updated_at
            """,
            session_id,
            status.value,
        )
        if not row:
            return None

        return TutoringSessionResponse(
            id=row["id"],
            classroom_id=row["classroom_id"],
            student_id=row["student_id"],
            learning_objective=row["learning_objective"],
            status=SessionStatus(row["status"]),
            hints_used=row["hints_used"],
            attempts=row["attempts"],
            started_at=row["started_at"],
            ended_at=row["ended_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def add_message(
        self,
        session_id: UUID,
        role: MessageRole,
        content: str,
        sequence_number: int,
        hint_level: HintLevel | None = None,
        author_user_id: UUID | None = None,
    ) -> SessionMessage:
        now = datetime.now(UTC)
        hint_val = int(hint_level) if hint_level is not None else None

        if not self.pool:
            msg_id = uuid4()
            msg = {
                "id": msg_id,
                "session_id": session_id,
                "author_user_id": author_user_id,
                "role": role,
                "content": content,
                "sequence_number": sequence_number,
                "hint_level": hint_level,
                "created_at": now,
            }
            if session_id not in self._memory_messages:
                self._memory_messages[session_id] = []
            self._memory_messages[session_id].append(msg)
            return SessionMessage(**msg)

        row = await self.pool.fetchrow(
            """
            insert into public.messages
                (session_id, author_user_id, role, content, sequence_number, hint_level, created_at)
            values ($1, $2, $3, $4, $5, $6, now())
            returning id, session_id, author_user_id, role, content, sequence_number, hint_level, created_at
            """,
            session_id,
            author_user_id,
            role.value,
            content,
            sequence_number,
            hint_val,
        )
        return SessionMessage(
            id=row["id"],
            session_id=row["session_id"],
            author_user_id=row["author_user_id"],
            role=MessageRole(row["role"]),
            content=row["content"],
            sequence_number=row["sequence_number"],
            hint_level=HintLevel(row["hint_level"]) if row["hint_level"] is not None else None,
            created_at=row["created_at"],
        )

    async def get_messages(self, session_id: UUID) -> list[SessionMessage]:
        if not self.pool:
            messages = self._memory_messages.get(session_id, [])
            return [SessionMessage(**m) for m in sorted(messages, key=lambda x: x["sequence_number"])]

        rows = await self.pool.fetch(
            """
            select id, session_id, author_user_id, role, content, sequence_number, hint_level, created_at
            from public.messages
            where session_id = $1
            order by sequence_number asc
            """,
            session_id,
        )
        return [
            SessionMessage(
                id=r["id"],
                session_id=r["session_id"],
                author_user_id=r["author_user_id"],
                role=MessageRole(r["role"]),
                content=r["content"],
                sequence_number=r["sequence_number"],
                hint_level=HintLevel(r["hint_level"]) if r["hint_level"] is not None else None,
                created_at=r["created_at"],
            )
            for r in rows
        ]
