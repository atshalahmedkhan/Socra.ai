# Deployment

> Phase 1 focuses on a stable **local** development environment. This document
> captures the intended deployment shape; refine it as services mature.

## Environments

| Environment | Purpose |
| --- | --- |
| development | Local + shared dev resources |
| staging | Pre-release verification with production-like config |
| production / pilot | Real usage (pilot cohort) |

Each environment uses **separate** Supabase project, storage bucket, credentials,
model endpoint, logs, and environment variables. See
[secrets-and-environments.md](secrets-and-environments.md).

## Build artifacts

- **Frontend** (`frontend/`): Next.js production build (`npm run build`), deployed
  as a container or to a Node host.
- **Backend** (`backend/`): container built from `backend/Dockerfile`,
  served with `uvicorn`/`gunicorn`.
- **Model server** (`model/server/`): vLLM container on a GPU host,
  reachable only from the backend, authenticated via `MODEL_SERVER_API_KEY`.

## Secrets in CI/CD

- Store deployment secrets in **GitHub repository secrets** (or the platform's
  secret manager) — never in the repo.
- CI runs lint, typecheck, tests, and Gitleaks before any deploy.

## Local (Docker Compose)

```bash
docker compose up --build
```

This is a development scaffold (`docker-compose.yml`). It runs the API
service. The model server is GPU-bound and typically run separately.

## Rollout checklist (per environment)

- [ ] Environment variables set and validated at startup.
- [ ] Database migrations applied (`backend/database/migrations/`).
- [ ] RLS policies applied (`backend/database/policies/`).
- [ ] Model server reachable from backend, and only from backend.
- [ ] Frontend bundle verified to contain no backend secrets.
- [ ] Logs shipped to per-environment sink; no tokens/keys logged.
