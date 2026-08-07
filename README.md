# Socra

A Socratic tutoring platform. Socra guides students through progressive questions and hints instead of giving final answers, powered by a self-hosted, fine-tuned Gemma model.

> **Phase 1 — infrastructure and backend scaffold.** The backend API, authentication, model gateway, and database schema are in place. A live model endpoint, frontend tutoring UI, and domain route implementations are not yet complete. See `docs/phase1-final-gap-audit.md` for the current gap list.

## Architecture

```
frontend/          (Next.js — student browser)
        ↓  HTTPS + Supabase JWT
backend/           (FastAPI — auth, orchestration, model calls)
        ↓  Supabase service-role key
Supabase / PostgreSQL  (Auth · pgvector · Storage)
        ↓  internal Docker network
model/server/      (vLLM — Gemma inference, GPU-only)
```

## Repository layout

| Directory | Contents |
| --- | --- |
| `frontend/` | Next.js student application |
| `backend/` | FastAPI API server + database migrations |
| `model/server/` | vLLM inference server (Gemma, GPU-only) |
| `model/training/` | QLoRA fine-tuning scripts and config |
| `model/benchmarks/` | Benchmark prompts and latency measurement scripts |
| `model/evaluation/` | Evaluation harness and model version results |
| `annotated-data/` | Training, validation, and test datasets (git-ignored content) |
| `docs/` | Architecture, API, authentication, deployment, and audit documentation |
| `legacy/` | Previous research collaboration website (separate Supabase schema) |
| `packages/shared-types/` | TypeScript contract types shared between frontend and backend |
| `.github/workflows/` | CI/CD — frontend lint/test/build, backend ruff/pytest, model infrastructure checks |

## Quick start

### Environment

```bash
cp .env.example .env
# Fill in Supabase credentials, DATABASE_URL, and model server API keys.
# See docs/secrets-and-environments.md for what each variable does.
```

### Backend

```bash
cd backend
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
# GET http://localhost:8000/health → { "status": "ok" }
```

### Frontend

```bash
cd frontend
npm ci
npm run dev
# http://localhost:3000
```

### Model server (requires NVIDIA GPU + Hugging Face access)

```bash
# Accept Gemma terms on Hugging Face, then set HF_TOKEN and MODEL_PRIMARY_API_KEY in .env
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build model-primary
```

### Run tests

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm run test
```

## Database migrations

Apply in filename order against your Supabase project:

```bash
psql "$DATABASE_URL" -f backend/database/migrations/0001_init.sql
psql "$DATABASE_URL" -f backend/database/migrations/202607190001_create_model_requests.sql
psql "$DATABASE_URL" -f backend/database/migrations/202607190002_create_identity_and_classrooms.sql
psql "$DATABASE_URL" -f backend/database/migrations/202608020001_create_phase1_domain_schema.sql
```

## Documentation

| Document | Contents |
| --- | --- |
| `docs/architecture.md` | System overview and component map |
| `docs/backend-architecture.md` | FastAPI layer descriptions |
| `docs/api-routes.md` | All API routes with auth and status |
| `docs/authentication-flow.md` | Supabase JWT flow |
| `docs/authorization-model.md` | Role-permission matrix |
| `docs/model-infrastructure.md` | vLLM topology, fallback, circuit breaker |
| `docs/model-training.md` | QLoRA training process |
| `docs/deployment.md` | Deployment checklist |
| `docs/secrets-and-environments.md` | Secret management rules |
| `docs/development-workflow.md` | Branch and PR conventions |
| `docs/phase1-final-gap-audit.md` | Current Phase 1 gap list |

## Legacy research site

`legacy/` contains the static multi-page collaboration site (calendar, Gantt, chat) that predates the tutoring platform. It uses a separate Supabase schema and a separate Supabase project. See `legacy/README.md`.
