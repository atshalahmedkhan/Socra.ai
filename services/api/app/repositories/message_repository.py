from dataclasses import dataclass
from uuid import UUID

import asyncpg


@dataclass(frozen=True)
class MessagePair:
    student_id: UUID
    assistant_id: UUID
    duplicate: bool


class MessageRepository:
    def __init__(self, pool: asyncpg.Pool | None):
        self.pool = pool

    async def create_student_and_pending_assistant(
        self, *, session_id: UUID, student_id: UUID, content: str, client_request_id: str
    ) -> MessagePair:
        if not self.pool:
            raise RuntimeError("Database is required for message persistence")
        async with self.pool.acquire() as connection, connection.transaction():
            await connection.execute("select pg_advisory_xact_lock(hashtext($1))", str(session_id))
            existing = await connection.fetchrow(
                """select s.id student_id, a.id assistant_id from public.messages s
                   join public.messages a on a.reply_to_message_id=s.id
                   where s.session_id=$1 and s.client_request_id=$2""",
                session_id,
                client_request_id,
            )
            if existing:
                return MessagePair(existing["student_id"], existing["assistant_id"], True)
            sequence = await connection.fetchval(
                "select coalesce(max(sequence_number), -1) + 1 from public.messages where session_id=$1",
                session_id,
            )
            student = await connection.fetchrow(
                """insert into public.messages
                   (session_id, author_user_id, role, content, sequence_number, status, client_request_id)
                   values ($1,$2,'student',$3,$4,'completed',$5) returning id""",
                session_id,
                student_id,
                content,
                sequence,
                client_request_id,
            )
            assistant = await connection.fetchrow(
                """insert into public.messages
                   (session_id, role, content, sequence_number, status, reply_to_message_id)
                   values ($1,'assistant','Pending response',$2,'pending',$3) returning id""",
                session_id,
                sequence + 1,
                student["id"],
            )
            return MessagePair(student["id"], assistant["id"], False)

    async def complete_assistant(self, assistant_id: UUID, content: str) -> None:
        await self.pool.execute(
            "update public.messages set content=$2, status='completed' where id=$1", assistant_id, content
        )

    async def fail_assistant(self, assistant_id: UUID) -> None:
        await self.pool.execute(
            "update public.messages set content='Response unavailable', status='failed' where id=$1", assistant_id
        )

    async def get_pair(self, student_id: UUID, assistant_id: UUID):
        rows = await self.pool.fetch(
            """select id, role, content, status, client_request_id, reply_to_message_id
               from public.messages where id=any($1::uuid[]) order by sequence_number""",
            [student_id, assistant_id],
        )
        return [dict(row) for row in rows]
