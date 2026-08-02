# Backend architecture audit

Before this change the repository contained a static Supabase collaboration site and a separate FastAPI model scaffold. FastAPI had health and model routes, `asyncpg` model telemetry, and no product authentication, versioned router, user/classroom tables, request-ID middleware, centralized errors, role definitions, or structured request logging. Existing model services, health routes, Docker topology, and tests were retained.

The browser schema (`chat_messages`, `day_comments`, `phase_statuses`, `chat_perms`) is unrelated to the Socra tutoring product domain and was not repurposed. The new minimal product migration defines `users`, `classrooms`, and `classroom_members`. Tutoring, materials, feedback, and research tables still do not exist; their routes are authenticated contracts returning stable `NOT_IMPLEMENTED`.

Risks/blockers: live Supabase JWT/JWKS and database behavior require credentials; migrations are not applied to a live project; domain repositories remain future work; model runtime is independently blocked by missing Hugging Face access.
