# API routes

All product routes require Bearer authentication. Classroom paths additionally load active membership and the noted permission. Contract routes return `501 NOT_IMPLEMENTED` after authorization until their domain repositories exist.

| Method | Path | Permission | Status |
|---|---|---|---|
| GET | `/api/v1/auth/me` | authenticated | Active |
| POST | `/api/v1/auth/logout` | authenticated | Active; client performs Supabase sign-out |
| GET, POST | `/api/v1/classrooms` | authenticated | Contract |
| GET | `/api/v1/classrooms/{classroom_id}` | classroom:read | Contract |
| PATCH, DELETE | `/api/v1/classrooms/{classroom_id}` | classroom:update | Contract |
| GET | `/api/v1/classrooms/{classroom_id}/members` | member:read | Contract |
| POST, PATCH, DELETE | classroom member paths | member:manage | Contract |
| GET, POST | classroom materials path | material:read/create | Contract |
| GET, DELETE | `/api/v1/materials/{material_id}` | authenticated | Contract |
| GET | `/api/v1/materials/{material_id}/status` | authenticated | Contract |
| POST, GET | tutoring-session paths | authenticated | Contract |
| GET, POST | tutoring messages path | authenticated | Contract |
| POST, GET | feedback paths | authenticated | Contract |
| GET, POST | research status/consent/withdraw | authenticated | Contract |
| POST | `/api/v1/model/generate` | transitional model route | Active; product authorization pending |
| POST | `/api/v1/internal/model/smoke-test` | internal token; development/test only | Active when enabled |
| GET | `/health/live`, `/health/ready`, `/health/model` | public probe | Active |

Contract request/response bodies will be finalized with their domain migrations. They deliberately provide no fake in-memory behavior.
