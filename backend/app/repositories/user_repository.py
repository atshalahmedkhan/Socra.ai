from uuid import UUID

import asyncpg


class UserRepository:
    def __init__(self, pool: asyncpg.Pool | None):
        self.pool = pool

    async def get_or_create(self, auth_user_id: UUID, email: str | None):
        if not self.pool:
            return {
                "id": auth_user_id,
                "auth_user_id": auth_user_id,
                "email": email,
                "is_admin": False,
                "is_researcher": False,
            }
        return await self.pool.fetchrow(
            """insert into public.users(auth_user_id, email) values($1,$2)
               on conflict(auth_user_id) do update set email=coalesce(excluded.email, users.email),
               updated_at=now()
               returning id, auth_user_id, email, is_admin, is_researcher""",
            auth_user_id,
            email,
        )

    async def membership(self, user_id: UUID, classroom_id: UUID):
        if not self.pool:
            return None
        return await self.pool.fetchrow(
            "select id, role, status from public.classroom_members where user_id=$1 and classroom_id=$2",
            user_id,
            classroom_id,
        )
