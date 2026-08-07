# Repository Audit

**Audit date:** 2026-08-06
**Auditor:** Read-only structural audit; no implementation changes made.

---

## 1. Executive Summary

Socra is an early-stage Socratic tutoring platform. The vision is to guide students through progressive questions and hints using a self-hosted, fine-tuned Gemma model (via vLLM), backed by a FastAPI API layer and a Next.js frontend, all anchored to a Supabase database.

**What has already been built:** The repository contains a complete backend infrastructure scaffold — FastAPI application with versioned routing, Supabase JWT authentication, a classroom-scoped role/permission system, model gateway with circuit breaker and fallback, async PostgreSQL telemetry, structured redacted logging, request-ID middleware, stable error envelopes, comprehensive configuration validation, and Docker Compose topology for local GPU-backed development. Database migrations for identity, classrooms, model telemetry, and the full Phase 1 domain schema (tutoring sessions, messages, feedback, research participants) are present. CI pipelines pass ruff and pytest. The legacy static research-project site (HTML/JS/CSS pages with Supabase realtime) is retained intact.

**Current phase:** The repository represents approximately Phase 1 infrastructure and backend scaffold, ~20–25% complete toward the full platform. Backend plumbing is solid; no tutoring domain logic is implemented. The frontend is a single placeholder page. The model server has never successfully started. Live Supabase and live model credentials have never been configured or tested.

**Overall condition:** ACCEPTABLE. The infrastructure skeleton is coherent and the security posture is well-considered, but large mandatory gaps remain before Phase 1 can be called complete.

**Biggest remaining gap:** No live model endpoint has ever been started; no domain routes have real implementations; the Next.js frontend has no tutoring UI; and no live integration test has been run against real Supabase or a real Gemma model.

---

## 2. Repository Metadata

| Field | Value |
|---|---|
| Path | `/Users/tejasgovind/Documents/Socra/Socra.ai` |
| Git repository | Yes |
| Current branch | `main` |
| Latest commit | `43525f9` — Merge pull request #4 from `atshalahmedkhan/feat/phase1-backend-integration` |
| Remote | `https://github.com/atshalahmedkhan/Socra.ai.git` |
| Working tree | Clean (nothing to commit) |
| Active remote branches | `main`, `agent/testing-mock-model`, `chore/add-ci-workflow`, `chore/phase1-github-workflow`, `copilot/fix-github-actions-job-analyze-javascript-typescri`, `feat/phase1-backend-integration` |

---

## 3. Repository Tree

```
Socra.ai/
├── README.md                        # Root project README
├── .env.example                     # All environment variables (placeholders)
├── .gitignore
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   ├── feature_request.yml
│   │   └── config.yml
│   ├── pull_request_template.md
│   └── workflows/
│       ├── ci.yml                   # Frontend + backend CI
│       ├── codeql.yml               # GitHub CodeQL scanning
│       └── model-infrastructure.yml # Model infrastructure checks
├── apps/
│   └── web/                         # Next.js 16 frontend
│       ├── app/
│       │   ├── layout.tsx
│       │   ├── page.tsx             # Single placeholder home page
│       │   └── globals.css
│       ├── components/              # Empty (.gitkeep only)
│       ├── features/                # Empty (.gitkeep only)
│       ├── hooks/                   # Empty (.gitkeep only)
│       ├── lib/
│       │   ├── api.ts               # Thin HTTP client (health only)
│       │   └── env.ts
│       ├── types/index.ts
│       ├── tests/
│       │   ├── unit/env.test.ts
│       │   └── e2e/home.spec.ts
│       ├── Dockerfile
│       ├── package.json
│       ├── playwright.config.ts
│       └── vitest.config.ts
├── packages/
│   └── shared-types/
│       └── src/index.ts             # Shared TS contract types (TutorRequest, TutorResponse, etc.)
├── services/
│   ├── api/                         # FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py              # App factory, lifespan, generate endpoint
│   │   │   ├── api/
│   │   │   │   ├── health.py        # /health, /health/live, /health/ready, /health/model
│   │   │   │   └── v1/
│   │   │   │       ├── router.py    # Mounts auth + contracts routers
│   │   │   │       ├── auth.py      # /api/v1/auth/me, /api/v1/auth/logout
│   │   │   │       └── contracts.py # All domain contract routes → 501 NOT_IMPLEMENTED
│   │   │   ├── auth/
│   │   │   │   ├── dependencies.py  # get_current_user / get_optional_user
│   │   │   │   ├── jwt.py           # Supabase JWKS + HS256 verification
│   │   │   │   ├── authorization.py # Classroom permission dependency
│   │   │   │   ├── permissions.py   # Permission enum + role-permission matrix
│   │   │   │   └── roles.py         # ClassroomRole enum
│   │   │   ├── core/
│   │   │   │   ├── config.py        # Pydantic Settings with full validation
│   │   │   │   ├── errors.py        # APIError + not_implemented()
│   │   │   │   ├── exception_handlers.py
│   │   │   │   ├── logging.py       # JSON + console formatters, redaction
│   │   │   │   ├── middleware.py    # RequestContextMiddleware (X-Request-ID)
│   │   │   │   └── request_context.py
│   │   │   ├── database/session.py
│   │   │   ├── models/              # Empty __init__ only
│   │   │   ├── repositories/
│   │   │   │   ├── model_request_repository.py  # Telemetry writes
│   │   │   │   └── user_repository.py           # get_or_create, membership
│   │   │   ├── schemas/
│   │   │   │   ├── auth.py          # AuthenticatedUser, MeResponse
│   │   │   │   ├── common.py        # OperationSuccess
│   │   │   │   ├── errors.py        # ErrorBody, ErrorResponse
│   │   │   │   ├── health.py
│   │   │   │   └── model.py         # ModelGenerationRequest, ChatMessage, etc.
│   │   │   └── services/
│   │   │       ├── model_circuit_breaker.py  # CircuitBreaker (3 failures → open)
│   │   │       ├── model_client.py           # Async httpx client to vLLM
│   │   │       ├── model_errors.py           # ModelError + ModelErrorCode
│   │   │       ├── model_gateway.py          # Primary → stable adapter → fallback orchestration
│   │   │       ├── model_response_policy.py  # Validates response: no full solutions
│   │   │       └── model_usage.py            # safely_record wrapper
│   │   ├── tests/
│   │   │   ├── conftest.py
│   │   │   ├── test_backend_architecture.py   # Auth, JWT, middleware, permissions, logging
│   │   │   ├── test_config.py                 # Settings validation
│   │   │   ├── test_frontend_supabase_env.py
│   │   │   ├── test_health.py                 # Health endpoints
│   │   │   ├── test_model_infrastructure.py   # ModelClient, CircuitBreaker, policy
│   │   │   ├── test_model_request_repository.py
│   │   │   ├── test_phase1_migration.py       # Migration structural checks
│   │   │   └── test_supabase_config.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── requirements-dev.txt
│   ├── model-server/
│   │   ├── Dockerfile               # FROM vllm/vllm-openai:v0.9.2
│   │   ├── start-primary.sh         # vLLM serve entrypoint
│   │   ├── start-fallback.sh
│   │   ├── scripts/
│   │   │   ├── serve.sh             # Alternative serve script
│   │   │   └── validate-adapters.py # Validates LoRA adapter paths at startup
│   │   └── config/server.env.example
│   └── model-training/
│       ├── configs/qlora.yaml       # QLoRA hyperparameters (scaffold only)
│       ├── data/                    # git-ignored dataset directory
│       ├── evaluations/             # Empty (.gitkeep)
│       ├── notebooks/               # Empty (.gitkeep)
│       ├── requirements.txt
│       └── scripts/train_qlora.py   # Scaffold (TODO: implement on GPU)
├── database/
│   ├── migrations/
│   │   ├── 0001_init.sql                        # pgvector, courses, materials, chunks
│   │   ├── 202607190001_create_model_requests.sql
│   │   ├── 202607190002_create_identity_and_classrooms.sql
│   │   └── 202608020001_create_phase1_domain_schema.sql  # Full Phase 1 domain
│   ├── policies/rls.sql             # Placeholder RLS for legacy courses tables
│   └── seed/seed.sql
├── benchmarks/
│   └── prompts/socra-smoke.jsonl    # 10 Socratic tutoring benchmark prompts
├── scripts/
│   ├── README.md
│   ├── benchmark_model.py           # Model benchmark runner (requires live endpoint)
│   ├── check-env.sh
│   ├── check_vllm_metrics.py
│   ├── generate-config.js           # Builds config.js for static site (Vercel)
│   ├── inspect_model_environment.py
│   ├── run_benchmark_matrix.py      # Multi-concurrency benchmark sweep
│   ├── test_model_endpoint.py
│   ├── verify_gemma_access.py
│   └── verify_model_runtime.py
├── infra/                           # Empty placeholder directory
├── docs/                            # 24 documentation files
├── test-results/
│   ├── model-request-persistence.md
│   └── model-runtime-verification.{json,md}
├── docker-compose.yml               # api + model-primary + model-fallback (profile)
├── docker-compose.gpu.yml           # NVIDIA device reservation overlay
├── docker-compose.local.yml         # Local port binding overlay
├── vercel.json
├── package.json                     # Root; generate-config script
├── ruff.toml
│
│ ── Legacy static research site (retained, unrelated to tutoring product):
├── index.html / login.html / calendar.html / gantt.html / chat.html
├── css/style.css
├── js/                              # auth.js, data.js, nav.js, page scripts
├── supabase_schema.sql              # Browser Supabase schema (unrelated product)
├── supabase_fix_grants.sql
├── supabase_clear_test_data.sql
└── example.config.js
```

---

## 4. Architecture Overview

```
┌─────────────────────────┐
│  Legacy static site      │  (retained, unrelated to tutoring product)
│  HTML/JS + Supabase JS   │
└─────────────────────────┘

┌────────────────┐   HTTPS / Bearer token   ┌────────────────────┐
│  Next.js 16    │ ───────────────────────▶ │  FastAPI backend   │
│  apps/web      │  (placeholder page only) │  services/api      │
└────────────────┘                          └────────┬───────────┘
                                                     │ internal Docker network
                                                     │ (never reached in practice)
                                                     ▼
                                         ┌─────────────────────┐
                                         │  vLLM model server  │
                                         │  services/model-    │
                                         │  server (BLOCKED)   │
                                         └─────────────────────┘
                                                     │
                                     ┌───────────────┴──────────────┐
                                     │ Supabase: Auth · PostgreSQL  │
                                     │ (never connected live)       │
                                     └──────────────────────────────┘
```

The intended data flow for a tutoring request:
1. Student signs in via Supabase Auth (Next.js frontend).
2. Frontend sends messages + JWT to FastAPI.
3. FastAPI verifies JWT via Supabase JWKS, resolves internal user, checks classroom membership.
4. FastAPI calls vLLM model server with Socratic prompt.
5. Response is policy-validated and returned to frontend.
6. Model telemetry is persisted to `public.model_requests`.

**Current reality:** Steps 1–5 have never been executed end-to-end. Steps 1 and 4 are completely blocked (no live frontend UI, no live model server). Steps 2–3 pass unit tests with mocked transports.

---

## 5. Directory-by-Directory Review

### `apps/web/`

**Purpose:** Next.js 16 frontend — the student-facing UI for Socratic tutoring.

**Important files:**
- `app/page.tsx` — Single placeholder home page displaying "Phase 1 · Development scaffold" and the instruction to start the backend.
- `lib/api.ts` — Thin API client; only exposes a `health()` call.
- `lib/env.ts` — Reads `NEXT_PUBLIC_*` variables.
- `types/index.ts` — `AppEnv`, `HealthStatus` types only.
- `components/`, `features/`, `hooks/` — All empty (`.gitkeep` only).

**Status:** PARTIAL. Scaffold exists and builds. No tutoring UI, no chat, no session creation, no auth integration with Supabase in the frontend.

---

### `packages/shared-types/`

**Purpose:** TypeScript types shared between frontend and backend API contracts.

**Important files:**
- `src/index.ts` — Defines `ChatRole`, `ChatMessage`, `TutorRequest`, `TutorResponse`, `HealthStatus`.

**Status:** PARTIAL. Types are defined but not consumed by `apps/web` as a workspace dependency. The comment in `types/index.ts` acknowledges this: "Wire that package in as a workspace dependency when the monorepo adds workspace tooling."

---

### `services/api/`

**Purpose:** FastAPI Python backend — authentication, authorization, model orchestration, telemetry.

**Important files:**
- `app/main.py` — App factory with lifespan; creates asyncpg pool, ModelClient, ModelGateway, CircuitBreaker, repositories. Registers two live routes: `POST /api/v1/model/generate` and `POST /api/v1/internal/model/smoke-test`.
- `app/api/health.py` — Four health probes: `/health` (root), `/health/live`, `/health/ready`, `/api/v1/health/dependencies`.
- `app/api/v1/auth.py` — `GET /api/v1/auth/me`, `POST /api/v1/auth/logout` (both active).
- `app/api/v1/contracts.py` — All tutoring/classroom/research domain routes returning `501 NOT_IMPLEMENTED`.
- `app/auth/` — Complete JWT verification (JWKS preferred, HS256 fallback), user sync, classroom membership, permission matrix.
- `app/core/config.py` — 80-variable Pydantic Settings with project-ref cross-validation and strict staging/production enforcement.
- `app/services/` — ModelClient (httpx), ModelGateway (primary → stable adapter → fallback), CircuitBreaker, response policy.
- `app/repositories/` — ModelRequestRepository (telemetry), UserRepository (get_or_create, membership lookup).

**Status:** VERIFIED for infrastructure. PARTIAL for product domain (no tutoring repositories, no domain logic beyond contracts).

---

### `services/model-server/`

**Purpose:** vLLM OpenAI-compatible inference server for the fine-tuned Gemma model.

**Important files:**
- `Dockerfile` — `FROM vllm/vllm-openai:v0.9.2`, copies startup scripts.
- `start-primary.sh` — Validates adapter config, then calls `vllm serve` with env-driven parameters (model, port, API key, max-model-len, GPU utilization).
- `start-fallback.sh` — Similar entrypoint for the fallback process on port 8002.
- `scripts/validate-adapters.py` — Checks LoRA adapter path validity before startup.

**Status:** PARTIAL. Container definition is complete. Has never successfully started — vLLM image download did not complete, `HF_TOKEN` is missing, Gemma access was not established, and no LoRA adapters exist.

---

### `services/model-training/`

**Purpose:** QLoRA fine-tuning pipeline for Gemma (Colab Pro+ or equivalent GPU environment).

**Important files:**
- `configs/qlora.yaml` — Hyperparameter config for `google/gemma-4-E4B-it` with QLoRA settings.
- `scripts/train_qlora.py` — Scaffold only; body is a TODO list with `print("[scaffold] Would train using config: ...")`.
- `data/`, `evaluations/`, `notebooks/` — All empty (git-ignored or `.gitkeep`).

**Status:** PARTIAL. Config exists; actual training code is a scaffold; no data, no trained weights, no evaluation harness.

---

### `database/`

**Purpose:** PostgreSQL schema migrations, RLS policies, and seed data.

**Important files:**
- `migrations/0001_init.sql` — pgvector extension, `courses`, `course_materials`, `material_chunks` tables (legacy; separate from tutoring domain).
- `migrations/202607190001_create_model_requests.sql` — `public.model_requests` telemetry table with all status/timing/fallback columns.
- `migrations/202607190002_create_identity_and_classrooms.sql` — `public.users`, `public.classrooms`, `public.classroom_members`.
- `migrations/202608020001_create_phase1_domain_schema.sql` — `learning_materials`, `tutoring_sessions`, `messages`, `feedback`, `research_participants`, `anonymized_event_logs`, plus FK links back to `model_requests`.
- `policies/rls.sql` — Minimal RLS for the legacy `courses` tables only; the product-domain tables have RLS enabled but no client-side policies (backend service role bypasses RLS).

**Status:** VERIFIED (schema files exist and are structurally sound). PARTIAL (never applied to a live Supabase project; no credentials configured; no live row written).

---

### `benchmarks/`

**Purpose:** Benchmark prompts for smoke-testing and benchmarking the model endpoint.

**Important files:**
- `prompts/socra-smoke.jsonl` — 10 Socratic tutoring prompts covering recursion, tree traversal, binary search, linked lists, hash maps, dynamic programming, graph traversal, debugging, Big-O, and one prompt-injection test.

**Status:** VERIFIED (file exists and contains valid prompts). PARTIAL (never run against a live model; `benchmark_model.py` requires a real endpoint URL and API key).

---

### `scripts/`

**Purpose:** Repository-level helper and benchmark scripts (Python + shell).

**Important files:**
- `benchmark_model.py` — Async model benchmark runner; measures latency and token usage. Requires live endpoint.
- `run_benchmark_matrix.py` — Sweeps concurrency levels; requires live endpoint.
- `test_model_endpoint.py` — Quick sanity check against a vLLM endpoint.
- `verify_gemma_access.py` — Checks HF token and Gemma model access.
- `verify_model_runtime.py` — Checks HF token, model endpoints, API endpoints; recorded FAIL for all three.
- `check_vllm_metrics.py` — Polls vLLM `/metrics` endpoint.
- `inspect_model_environment.py` — Reports GPU/driver environment.
- `generate-config.js` — Builds `config.js` for the legacy static site on Vercel.
- `check-env.sh` — Verifies `.env` file has all keys from `.env.example`.

**Status:** VERIFIED (scripts exist and are syntactically valid). NOT_RUN (all scripts requiring a live model endpoint have never produced results).

---

### `infra/`

**Purpose:** Placeholder for infrastructure-as-code (Terraform, Kubernetes, etc.).

**Status:** MISSING. Only a `README.md` exists. No environment-specific directories, no IaC configs.

---

### `docs/`

**Purpose:** Project documentation (24 files). See Section 14.

**Status:** VERIFIED for content existence. Some documents describe aspirational state not yet implemented.

---

### `test-results/`

**Purpose:** Persistent record of test runs.

**Important files:**
- `model-request-persistence.md` — States "unit-tested, live verification blocked."
- `model-runtime-verification.json` — FAIL for all three checks (HF_TOKEN, model_endpoints, api_endpoints).
- `model-runtime-verification.md` — Same, in markdown.

**Status:** VERIFIED (records exist). The results document confirmed failures, not successes.

---

### Legacy static site (root HTML/JS/CSS)

**Purpose:** A multi-page research-project collaboration site (calendar, Gantt, chat, team overview) with Supabase realtime. Pre-dates the tutoring platform work.

**Files:** `index.html`, `login.html`, `calendar.html`, `gantt.html`, `chat.html`, `project_timeline_gantt_dates.html`, `css/style.css`, `js/`, `supabase_schema.sql`, `supabase_fix_grants.sql`, `supabase_clear_test_data.sql`, `example.config.js`.

**Status:** VERIFIED (fully functional as a static site). Separate from the tutoring product and not integrated with `services/api`.

---

## 6. Important Files

### `.env.example`

**Purpose:** Documents every environment variable required by the system; contains placeholder values only.

**Contains:** 80 variables spanning app config, Supabase (modern and legacy names), database, JWT, model server, vLLM tuning, and benchmark settings.

**Status:** VERIFIED. CI enforces that all required keys are present. Modern key names (`SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY`) are preferred; legacy names (`SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`) remain as compatibility aliases.

---

### `docker-compose.yml`

**Purpose:** Defines the local development stack: `api` service (FastAPI on port 8000), `model-primary` (vLLM on internal port 8001), `model-fallback` (optional profile, internal port 8002). All services share a private internal Docker network (`socra-private`).

**Status:** VERIFIED. The `model-primary` service has a healthcheck. The `model-fallback` service uses the `fallback` Compose profile. The Next.js frontend is not in this file.

---

### `docker-compose.gpu.yml`

**Purpose:** Overlay adding NVIDIA GPU device reservations for `model-primary` and `model-fallback`.

**Status:** VERIFIED.

---

### `docker-compose.local.yml`

**Purpose:** Overlay binding `model-primary` to `127.0.0.1:8001` for local development access.

**Status:** VERIFIED.

---

### `services/api/Dockerfile`

**Purpose:** `python:3.12-slim` image; installs requirements; copies `app/`; runs as non-root user 65532; starts `uvicorn`.

**Status:** VERIFIED. Production-ready baseline (non-root, no `.env` baked in).

---

### `apps/web/Dockerfile`

**Purpose:** Development-only Next.js container; `npm ci` + `npm run dev`.

**Note:** File comment states "Production builds should use a multi-stage build." The current Dockerfile is not production-ready.

**Status:** PARTIAL.

---

### `services/model-server/Dockerfile`

**Purpose:** Extends `vllm/vllm-openai:v0.9.2`; copies `validate-adapters.py`, `start-primary.sh`, `start-fallback.sh`; sets entrypoint to `start-primary.sh`.

**Status:** VERIFIED. Image definition is correct but has never been successfully built (download incomplete per `model-runtime-environment.md`).

---

### `vercel.json`

**Purpose:** Vercel deployment config for the legacy static site; sets headers and rewrites.

**Status:** VERIFIED (present; targets static site deployment, not the Next.js app).

---

### `.github/workflows/ci.yml`

**Purpose:** Runs on push/PR to `main`. Two jobs: `frontend` (npm ci → lint → typecheck → test → build) and `backend` (pip install → ruff check → pytest).

**Status:** VERIFIED. CI passes per recent commits.

---

### `.github/workflows/model-infrastructure.yml`

**Purpose:** Runs on every push/PR. Validates: ruff check, pytest, `python -m compileall`, Docker Compose config dry-run (base + GPU overlay), `.env.example` variable completeness, secret scanning (no HF tokens or model API keys in tracked files).

**Status:** VERIFIED.

---

### `ruff.toml`

**Purpose:** Python linter configuration; `line-length = 120`, targets Python 3.12, enables E/F/I/UP/B rules.

**Status:** VERIFIED.

---

## 7. Benchmark Application

This repository does not contain a traditional benchmark application in the sense of a pinned upstream C/benchmark project. Instead, the "benchmark" for this project is the **model inference quality and latency benchmark**:

| Attribute | Value |
|---|---|
| Benchmark type | LLM inference latency and correctness |
| Benchmark inputs | `benchmarks/prompts/socra-smoke.jsonl` (10 Socratic prompts) |
| Benchmark script | `scripts/benchmark_model.py`, `scripts/run_benchmark_matrix.py` |
| Target model | vLLM serving `google/gemma-3-4b-it` or `google/gemma-4-E4B-it` |
| Latency targets | Health p95 < 500 ms; response p50 < 8 s; p95 < 20 s; error rate < 1% |
| Results | NONE — no live endpoint was available; `docs/model-benchmark-results.md` explicitly states "No model benchmark was run." |

**Status:** PARTIAL. Benchmark infrastructure (inputs, scripts, targets) exists. No benchmark results exist.

---

## 8. Candidate Research

No dedicated candidate-comparison document was found (no `candidates/` directory, no `docs/candidate-comparison.md`, no `docs/benchmark-selection.md`).

The model choice (Gemma) is mentioned in `docs/architecture.md` and `docs/model-training.md` without a documented evaluation of alternatives.

| Item | Status |
|---|---|
| Candidate repository directory | MISSING |
| Documented model selection rationale | MISSING |
| Documented alternative model candidates | MISSING |
| Selected model (Gemma 4 E4B instruction-tuned) | VERIFIED (referenced in code and docs) |

---

## 9. Benchmark Data

| Artifact | Status | Notes |
|---|---|---|
| Benchmark input prompts | VERIFIED | `benchmarks/prompts/socra-smoke.jsonl` (10 prompts) |
| Input checksum | MISSING | No checksum file present |
| Expected output / golden responses | MISSING | Not present in repository |
| Benchmark results | MISSING | `docs/model-benchmark-results.md` explicitly states none were captured |
| `vllm-metrics-sample.txt` | MISSING (content) | File present but states "Not captured" |
| Benchmark result directory | MISSING | `benchmark-results/` is in `.gitignore`, nothing exists |

---

## 10. Docker Architecture

### Base images

| Service | Base image |
|---|---|
| `services/api` | `python:3.12-slim` |
| `apps/web` | `node:22-alpine` (dev only) |
| `services/model-server` | `vllm/vllm-openai:v0.9.2` |

### Network topology

All services connect to `socra-private`, defined as `internal: true`. This means the model server has no external network access. Only the API service exposes a host port (`127.0.0.1:8000:8000`). The model server uses `expose` (container-to-container only), never `ports`.

### Startup sequence

1. `docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build`
2. `model-primary` starts: validates adapters → runs `vllm serve` → healthcheck (`/health`)
3. `api` starts: creates asyncpg pool → creates ModelClient → mounts routes → ready

### GPU support

- NVIDIA GPU reservations via `docker-compose.gpu.yml` (overlay, not default)
- `docker-compose.local.yml` binds model port to localhost for development
- No AMD GPU support documented
- No ARM64 / Apple Silicon support — model server requires NVIDIA CUDA

### ARM64 status

NOT SUPPORTED for production. The vLLM base image (`vllm/vllm-openai`) requires an NVIDIA GPU and is Linux/amd64 only. No Buildx multi-platform configuration exists. No QEMU references found.

### Current Docker status

PARTIAL. The Compose definitions are correct but the model server image download never completed (per `docs/model-runtime-environment.md`). No successful `docker compose up` result is documented.

---

## 11. Script Architecture

### Python scripts (`scripts/`)

| Script | Purpose | Requires live model | Status |
|---|---|---|---|
| `benchmark_model.py` | Single-concurrency latency benchmark against vLLM endpoint | Yes | VERIFIED (code); NOT_RUN (results) |
| `run_benchmark_matrix.py` | Multi-concurrency sweep | Yes | VERIFIED (code); NOT_RUN (results) |
| `test_model_endpoint.py` | Quick endpoint sanity check | Yes | VERIFIED (code); NOT_RUN |
| `verify_gemma_access.py` | Check HF token + Gemma access | Yes (HF) | VERIFIED (code); FAILS (missing token) |
| `verify_model_runtime.py` | Check HF token + model + API endpoints | Yes | VERIFIED (code); FAILS (all three checks) |
| `check_vllm_metrics.py` | Poll vLLM `/metrics` endpoint | Yes | VERIFIED (code); NOT_RUN |
| `inspect_model_environment.py` | Report GPU/driver info | No (local) | VERIFIED (code) |
| `generate-config.js` | Generate `config.js` for legacy static site (Vercel) | No | VERIFIED |
| `check-env.sh` | Verify `.env` completeness | No | VERIFIED |

### Shell scripts (`services/model-server/scripts/` and root)

| Script | Purpose | Status |
|---|---|---|
| `services/model-server/start-primary.sh` | vLLM entrypoint; validates env, launches `vllm serve` | VERIFIED (code); NOT_RUN |
| `services/model-server/start-fallback.sh` | Fallback vLLM entrypoint on port 8002 | VERIFIED (code); NOT_RUN |
| `services/model-server/scripts/serve.sh` | Alternative serve script (slightly different flags) | VERIFIED; potentially redundant with `start-primary.sh` |
| `services/model-server/scripts/validate-adapters.py` | Validates LoRA adapter directory before server start | VERIFIED |

**Note:** `serve.sh` and `start-primary.sh` overlap in purpose. `start-primary.sh` is the Dockerfile entrypoint; `serve.sh` may be a development convenience script. See Section 19 for duplication concerns.

---

## 12. Testing Architecture

### Backend tests (`services/api/tests/`)

| Test file | What it tests | Type |
|---|---|---|
| `test_health.py` | `/health`, `/api/v1/status` | Unit (TestClient, no DB) |
| `test_backend_architecture.py` | Auth, JWT, middleware, permissions, logging, error envelopes | Unit (mocked) |
| `test_config.py` | Settings validation, env aliases, production guards | Unit |
| `test_frontend_supabase_env.py` | Frontend env variable naming conventions | Unit (static) |
| `test_supabase_config.py` | Supabase URL, JWT, JWKS config validation | Unit |
| `test_model_infrastructure.py` | ModelClient, CircuitBreaker, retry, response policy | Unit (httpx.MockTransport) |
| `test_model_request_repository.py` | Repository SQL logic | Unit (fake pool) |
| `test_phase1_migration.py` | Migration file ordering, table presence, RLS statements | Unit (file-level, no DB) |

**Count:** 8 test files. All unit tests with mocked transports or TestClient. No integration tests against live Supabase or vLLM.

**conftest.py:** Explicitly clears all credential environment variables to prevent accidental live connection.

**Status:** IMPLEMENTED (tests exist and CI passes). RESULTS_DOCUMENTED (CI badge on PRs). NOT_VERIFIED_IN_THIS_AUDIT (not re-run).

### Frontend tests (`apps/web/tests/`)

| Test | Type | What it tests |
|---|---|---|
| `tests/unit/env.test.ts` | Vitest unit | Env variables expose defaults |
| `tests/e2e/home.spec.ts` | Playwright E2E | Home page loads, title matches `/Socra/i` |

**Status:** IMPLEMENTED (minimal). E2E test requires a running dev server.

---

## 13. AMD64 / ARM64 Architecture

### AMD64 / x86_64

**Status:** VERIFIED for the API and web containers (`python:3.12-slim`, `node:22-alpine` are multi-platform). The model server is AMD64-only due to NVIDIA CUDA dependency.

### ARM64 / aarch64

**Status:**
- API container (`python:3.12-slim`): would likely run on ARM64 (multi-platform base), but untested.
- Web container (`node:22-alpine`): multi-platform, would run on ARM64.
- Model server (`vllm/vllm-openai`): NOT SUPPORTED on ARM64. vLLM requires NVIDIA CUDA; Apple Silicon or ARM-only hosts cannot run this image.
- No Buildx multi-platform build configuration found.
- No QEMU references found.

**Conclusion:** ARM64 compatibility testing is not supported and not documented. Real ARM64 performance benchmarking is out of scope for this project phase. The model server component architecturally requires an AMD64 NVIDIA GPU host.

---

## 14. Documentation Inventory

| Document | Purpose | Phase described | Matches code? | Status |
|---|---|---|---|---|
| `architecture.md` | System component overview with ASCII diagram | Phase 1 design | YES (describes implemented structure) | Current |
| `backend-architecture.md` | FastAPI layers summary | Phase 1 | YES | Current |
| `backend-architecture-audit.md` | Change log from pre-FastAPI state to current | Phase 1 retrospective | YES | Current |
| `api-routes.md` | Route table with auth and status | Phase 1 | YES | Current |
| `authentication-flow.md` | JWT + Supabase auth sequence diagram | Phase 1 | YES | Current |
| `authorization-model.md` | Role-permission matrix table | Phase 1 | YES | Current |
| `deployment.md` | Deployment shape (local + staging + production) | Phase 1+ | Aspirational | Future state not yet implemented |
| `deployment-architecture.md` | High-level hosting decisions | Phase 1+ | Aspirational | Current |
| `deployment-environments.md` | Per-environment constraints table | Phase 1+ | YES | Current |
| `development-workflow.md` | Branch naming, PR rules, local checks | Phase 1 | YES | Current |
| `error-catalog.md` | All error codes and HTTP mappings | Phase 1 | YES | Current |
| `logging-structure.md` | Log fields and redaction rules | Phase 1 | YES | Current |
| `secrets-and-environments.md` | Secret management rules and variable locations | Phase 1 | YES | Current |
| `model-infrastructure.md` | vLLM topology, client config, fallback, health | Phase 1 | YES | Current |
| `model-infrastructure-audit.md` | Change log for model infrastructure PR | Phase 1 retrospective | YES | Current |
| `model-runtime-environment.md` | Observed hardware environment on 2026-07-19 | Phase 1 | YES | Current; blocked |
| `model-runtime-startup.md` | vLLM startup commands; status: BLOCKED | Phase 1 | YES | Current; blocked |
| `model-runtime-finalization-audit.md` | What is complete vs. mocked for model runtime | Phase 1 | YES | Current; accurate |
| `model-server-security.md` | Network and secret security rules | Phase 1 | YES | Current |
| `model-benchmark-results.md` | Intended benchmark procedure; no results captured | Phase 1 | YES | Accurately states no results |
| `model-fallback.md` | Fallback strategy description | Phase 1 | YES | Current |
| `model-training.md` | QLoRA training process and stack | Phase 1–2 | YES (describes scaffold) | Current; training not implemented |
| `phase1-final-gap-audit.md` | Gap audit dated 2026-08-02; lists remaining Phase 1 work | Phase 1 gap analysis | YES | Current; highly accurate |
| `vllm-metrics-sample.txt` | vLLM metrics sample; content: "Not captured" | Phase 1 | YES (honestly absent) | Current |

**Assessment:** Documentation is thorough and honest about what is not complete. `docs/phase1-final-gap-audit.md` is the most accurate single-document summary of current state.

---

## 15. Completed Work

| # | Item | Evidence | Classification |
|---|---|---|---|
| 1 | Repository structure and monorepo skeleton | Directory tree | VERIFIED |
| 2 | FastAPI application with versioned `/api/v1` routing | `services/api/app/` source | VERIFIED |
| 3 | Supabase JWT authentication (JWKS and HS256) | `app/auth/jwt.py`, tests | VERIFIED |
| 4 | Internal user synchronization (`get_or_create`) | `app/repositories/user_repository.py` | VERIFIED |
| 5 | Classroom-scoped role/permission authorization | `app/auth/permissions.py`, `authorization.py`, `roles.py` | VERIFIED |
| 6 | Stable error envelope (`{ error: { code, message, request_id } }`) | `app/core/errors.py`, `schemas/errors.py`, tests | VERIFIED |
| 7 | X-Request-ID middleware | `app/core/middleware.py`, tests | VERIFIED |
| 8 | Structured redacted JSON logging | `app/core/logging.py`, tests | VERIFIED |
| 9 | Environment configuration with full validation | `app/core/config.py`, 80 variables, tests | VERIFIED |
| 10 | Production/staging safety guards in config | `app/core/config.py` model_validator | VERIFIED |
| 11 | Async httpx model client with timeouts | `app/services/model_client.py` | VERIFIED |
| 12 | Circuit breaker (3 failures → open, 30 s reset) | `app/services/model_circuit_breaker.py`, tests | VERIFIED |
| 13 | Model gateway (primary → stable adapter → fallback) | `app/services/model_gateway.py` | VERIFIED |
| 14 | Response policy (reject full-solution code blocks) | `app/services/model_response_policy.py`, tests | VERIFIED |
| 15 | Model telemetry repository (pending/succeeded/failed) | `app/repositories/model_request_repository.py` | VERIFIED |
| 16 | Health probes (`/health`, `/health/live`, `/health/ready`, `/health/dependencies`) | `app/api/health.py`, tests | VERIFIED |
| 17 | Internal smoke-test route (dev/test only, token-protected) | `app/main.py` | VERIFIED |
| 18 | All 4 database migrations (identity, classrooms, model_requests, Phase 1 domain schema) | `database/migrations/` | VERIFIED |
| 19 | RLS enabled on all product tables (no anonymous policies for product tables) | Migration SQL | VERIFIED |
| 20 | Docker Compose topology (private network, GPU overlay, local overlay) | `docker-compose*.yml` | VERIFIED |
| 21 | vLLM model server Dockerfile and startup scripts | `services/model-server/` | VERIFIED |
| 22 | Adapter validation script | `scripts/validate-adapters.py` | VERIFIED |
| 23 | QLoRA training config | `services/model-training/configs/qlora.yaml` | VERIFIED |
| 24 | Benchmark prompts | `benchmarks/prompts/socra-smoke.jsonl` | VERIFIED |
| 25 | Benchmark and endpoint scripts | `scripts/benchmark_model.py`, `run_benchmark_matrix.py`, etc. | VERIFIED |
| 26 | CI workflows (lint, typecheck, test, build, secret scan, Docker config dry-run) | `.github/workflows/` | VERIFIED |
| 27 | `.env.example` with all 80 variables | Root `.env.example` | VERIFIED |
| 28 | PR and issue templates | `.github/` | VERIFIED |
| 29 | 24 documentation files | `docs/` | VERIFIED |
| 30 | Unit test suite (8 test files, all passing in CI) | `services/api/tests/` | VERIFIED |
| 31 | Frontend Next.js scaffold and build | `apps/web/` | VERIFIED |
| 32 | Shared TypeScript contract types | `packages/shared-types/` | VERIFIED |
| 33 | Legacy static research site (retained) | Root HTML/JS/CSS | VERIFIED |

---

## 16. Partial Work

### 1. Model server startup

**What exists:** Dockerfile, entrypoints, GPU Compose overlay, adapter validator, documentation.

**What is missing:** A successfully started vLLM server with a downloaded Gemma checkpoint. `HF_TOKEN` is absent, vLLM image download did not complete, no checkpoint has been pulled.

**Files involved:** `services/model-server/`, `docker-compose.gpu.yml`, `docs/model-runtime-startup.md`

---

### 2. Next.js frontend UI

**What exists:** Next.js 16 scaffold, single placeholder home page, thin API client (health endpoint only), env config, 2 tests.

**What is missing:** Authentication UI (Supabase sign-in/sign-out), tutoring chat interface, session creation flow, message display, any connection to domain routes, all React components in `components/`, `features/`, `hooks/`.

**Files involved:** `apps/web/app/page.tsx`, `apps/web/lib/api.ts`, `apps/web/components/` (empty)

---

### 3. Domain route implementations

**What exists:** Route stubs for all classroom, materials, tutoring-session, message, feedback, and research routes — all returning `501 NOT_IMPLEMENTED` after authentication.

**What is missing:** The domain repositories, business logic, and service calls that would make these routes functional.

**Files involved:** `app/api/v1/contracts.py`

---

### 4. QLoRA fine-tuning

**What exists:** `qlora.yaml` config, `train_qlora.py` scaffold, `requirements.txt`.

**What is missing:** Actual training implementation (body is `TODO: implement on GPU`), training dataset, trained adapters, evaluation harness.

**Files involved:** `services/model-training/`

---

### 5. Live Supabase integration

**What exists:** Migration SQL, UserRepository, JWT verification, all configuration.

**What is missing:** Actual live Supabase credentials; migrations never applied to a real project; no live user row ever written.

**Files involved:** `database/migrations/`, `services/api/app/repositories/user_repository.py`, `test-results/model-request-persistence.md`

---

### 6. `shared-types` monorepo wiring

**What exists:** TypeScript types defined in `packages/shared-types/src/index.ts`.

**What is missing:** Workspace dependency wiring in `apps/web/package.json` so the frontend consumes these types. No `workspaces` config in root `package.json`.

**Files involved:** `packages/shared-types/`, `apps/web/types/index.ts` (duplicates some types locally)

---

### 7. Frontend Dockerfile (production-ready)

**What exists:** A development-mode Dockerfile (`npm run dev`).

**What is missing:** Multi-stage production build (explicitly noted in file comment).

**Files involved:** `apps/web/Dockerfile`

---

### 8. Benchmark results

**What exists:** Benchmark prompts, scripts with defined targets, empty result directory structure.

**What is missing:** Any actual benchmark run results; model server was never available.

**Files involved:** `benchmarks/`, `scripts/benchmark_model.py`, `docs/model-benchmark-results.md`

---

## 17. Missing Work

### Mandatory — blocks Phase 1 completion

| # | Item | Documented? |
|---|---|---|
| 1 | Live Supabase project credentials configured, migrations applied, RLS verified | YES — `docs/phase1-final-gap-audit.md` |
| 2 | Live Gemma primary model endpoint started and verified | YES |
| 3 | Live fallback model endpoint configured and verified (or explicitly deferred) | YES |
| 4 | Real sequential and concurrent model benchmark results recorded | YES |
| 5 | Frontend tutoring UI (auth, chat, session flow) | YES |
| 6 | Frontend E2E tutoring flow tested against live backend | YES |
| 7 | Domain repositories for classrooms, materials, sessions, messages, feedback | YES |
| 8 | Domain routes returning real data (not `NOT_IMPLEMENTED`) | YES |
| 9 | Integration tests against real Supabase (not just unit mocks) | YES (implied) |
| 10 | Supabase RLS policies for product domain tables | YES (comment in migration: "backend-only in Phase 1") |

### Optional improvements

| # | Item |
|---|---|
| A | `infra/` directory populated with environment-specific IaC |
| B | `shared-types` wired as proper workspace dependency |
| C | Production multi-stage Dockerfile for `apps/web` |
| D | Input/output checksums for benchmark prompts |
| E | CODEOWNERS file (noted as absent in gap audit) |
| F | Golden expected outputs for benchmark prompts |
| G | Model card for any trained adapter version |

---

## 18. Out-of-Scope / Later-Phase Work

| Item | Phase | Evidence |
|---|---|---|
| pgvector RAG pipeline (PDF ingestion, embedding, chunk retrieval) | Phase 2+ | `database/migrations/0001_init.sql` defines tables; no ingestion code exists |
| Model training on real data | Phase 2+ | `train_qlora.py` is a scaffold; data directory is empty |
| Streaming responses (TTFT measurement) | Phase 2+ | `docs/model-runtime-finalization-audit.md` notes "full-response mode; TTFT null" |
| Shared circuit breaker state across API processes | Phase 2 | `docs/model-fallback.md`: "Shared breaker state is Phase 2" |
| Production secret manager integration | Phase 2+ | `docs/deployment.md` checklist item |
| Staging and production Supabase projects | Phase 2+ | `docs/deployment-environments.md` |
| Supabase Storage for learning materials | Phase 2+ | Referenced in config but no upload code |
| Research participant consent flows (live) | Phase 3+ | Route stubs exist; tables defined |
| Pilot cohort deployment | Phase 4+ | Referenced in `docs/deployment.md` |
| mTLS between services | Phase 2+ | `docs/model-server-security.md` mentions it |

---

## 19. Duplicate / Obsolete Files

### Overlapping model server startup scripts

`services/model-server/scripts/serve.sh` and `services/model-server/start-primary.sh` both start a vLLM server. The Dockerfile uses `start-primary.sh` as the entrypoint. `serve.sh` uses slightly different flag names (`MODEL_NAME` vs. `BASE_MODEL_NAME`, different defaults). It is unclear which is authoritative for production.

**Recommendation:** Clarify whether `serve.sh` is a development convenience or a duplicate that should be removed.

---

### Two type definition files

`packages/shared-types/src/index.ts` defines `ChatRole`, `ChatMessage`, `TutorRequest`, `TutorResponse`, `HealthStatus`. `apps/web/types/index.ts` also defines `AppEnv` and `HealthStatus`. The frontend is not consuming the shared package. Two separate type definitions for the same concept exist.

---

### Legacy static site co-resident with product code

The root of the repository contains the legacy research-project site (`index.html`, `calendar.html`, `gantt.html`, `chat.html`, `login.html`, `supabase_schema.sql`, `css/`, `js/`) alongside the tutoring product scaffold. These serve entirely different purposes and different databases. This creates confusion about which "Supabase schema" applies to the product.

---

### `supabase_schema.sql` vs. `database/migrations/`

The root `supabase_schema.sql` creates tables for the legacy static site (`chat_messages`, `day_comments`, `phase_statuses`, `chat_perms`). The `database/migrations/` directory contains the product domain schema. These are unrelated schemas. The README still references `supabase_schema.sql` as the setup step for "the site," which is confusing alongside the FastAPI migration workflow.

---

### `test-results/model-runtime-verification.json` and `.md`

Both files record the same FAIL status from `verify_model_runtime.py`. The JSON is the raw output; the Markdown summarizes it. Not a problem, but the JSON is sparse (three keys) and could be inlined into the `.md`.

---

### `example.config.js` and `scripts/generate-config.js`

`example.config.js` is a static example of the generated `config.js` file used by the legacy static site. `generate-config.js` is the script that generates `config.js` at Vercel deploy time. These two files relate only to the legacy static site, not to the product.

---

## 20. End-to-End Repository Flow

The following describes what a developer would do from clone to a working local development environment.

### Legacy static site flow (currently functional)

1. Clone repository.
2. Copy `.env.example` → `.env` (or `example.config.js` → `config.js`) with a real Supabase project URL and anon key.
3. Run `supabase_schema.sql` in Supabase SQL editor.
4. Open `login.html` in a browser.
5. Collaborate using the chat, calendar, and Gantt pages.

### Backend API flow (partially functional)

1. Clone repository.
2. Copy `.env.example` → `.env` in root and `services/api/.env`; fill in Supabase credentials and `DATABASE_URL`.
3. Run database migrations in order: `0001_init.sql` → `202607190001_...` → `202607190002_...` → `202608020001_...`.
4. `cd services/api && pip install -r requirements-dev.txt`
5. `uvicorn app.main:app --app-dir services/api` (starts API on port 8000).
6. `GET /health` → `{ "status": "ok" }`.
7. `GET /api/v1/health/dependencies` → `{ "database": "healthy", "supabase_jwks": "healthy", "primary_model": "unavailable" }` (if credentials are correct).
8. Authenticate via a Supabase frontend → obtain JWT → `GET /api/v1/auth/me` → `{ auth_user_id, internal_user_id, email }`.
9. Domain routes return `501 NOT_IMPLEMENTED`.

### Model server flow (BLOCKED)

1. Accept Gemma model terms on Hugging Face.
2. Set `HF_TOKEN` in `.env`.
3. `docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build model-primary`
4. Wait for `vllm serve` to download weights and start (requires GPU, ~15 GB+ download).
5. `POST /api/v1/model/generate` with bearer token and messages body → returns Socratic question.
6. Model telemetry written to `public.model_requests`.

**Steps 1–4 have never succeeded in this repository.**

### Full developer flow (aspirational — not currently achievable)

```
Developer clones repository
     ↓
Sets up Supabase project (separate dev instance)
     ↓
Runs 4 migrations in order
     ↓
Installs Python deps, starts FastAPI (`uvicorn`)
     ↓
Installs Node deps, starts Next.js (`npm run dev`)
     ↓
Configures HF_TOKEN + Gemma access
     ↓
Pulls vLLM image, starts model server with NVIDIA GPU
     ↓
Opens Next.js frontend → signs in via Supabase Auth
     ↓
Asks tutoring question → frontend → FastAPI → vLLM → Socratic response
     ↓
Model telemetry persisted in Supabase
     ↓
Runs benchmark: python scripts/benchmark_model.py --base-url ... --model gemma-3-4b-base
     ↓
Records latency results in benchmark-results/
```

---

## 21. Repository Health

| Area | Rating | Reason |
|---|---|---|
| Repository organization | GOOD | Clear monorepo structure; `apps/`, `services/`, `packages/`, `database/`, `docs/`, `scripts/` are logically separated |
| Documentation | GOOD | 24 documents; accurate about gaps; audit trail in `*-audit.md` files; honest about blocked state |
| Reproducibility | NEEDS WORK | No live integration has been demonstrated; all "live" verification is blocked; no benchmark results exist |
| Docker organization | GOOD | Private network, GPU overlay, local overlay, non-root API image, healthcheck defined |
| Script organization | ACCEPTABLE | Scripts exist and are syntactically valid; `serve.sh` vs. `start-primary.sh` ambiguity needs resolution |
| Testing setup | ACCEPTABLE | Comprehensive unit tests; no integration or E2E tests against live services; conftest prevents accidental credential use |
| Benchmark organization | NEEDS WORK | Prompts and scripts exist but zero results have been captured; targets defined but unverifiable |
| Architecture portability | NEEDS WORK | Model server requires NVIDIA GPU (AMD64 only); no ARM64 path; Apple Silicon cannot run the model server |
| Git cleanliness | GOOD | Clean working tree; CI passes; secret scanning in workflow; no credentials in history per workflow check |
| Phase separation | ACCEPTABLE | Phase 1 is clearly in progress; later-phase features are documented as out-of-scope; some aspirational docs mix phases |

---

## 22. Current Phase Status

| Phase | Description | Evidence Found | Status |
|---|---|---|---|
| Phase 1a | Repository skeleton, CI, documentation | Directory tree, workflows, 24 docs | COMPLETE |
| Phase 1b | FastAPI backend scaffold (auth, middleware, config, errors) | `services/api/app/` full source | COMPLETE |
| Phase 1c | Database schema and migrations | 4 migration files | COMPLETE (files); NOT_APPLIED (live) |
| Phase 1d | Model infrastructure (client, gateway, circuit breaker, telemetry) | `services/api/app/services/` | COMPLETE (unit-tested); NOT_VERIFIED (live) |
| Phase 1e | Domain route contracts (`NOT_IMPLEMENTED` stubs) | `app/api/v1/contracts.py` | COMPLETE (stubs only) |
| Phase 1f | Live Supabase integration | No live credentials configured | NOT STARTED |
| Phase 1g | Live model server (vLLM + Gemma) | Image never built; `HF_TOKEN` missing | NOT STARTED |
| Phase 1h | Frontend tutoring UI | Placeholder page only; no components | NOT STARTED |
| Phase 1i | Domain repositories and route logic | Not implemented | NOT STARTED |
| Phase 1j | End-to-end integration tests | No live integration tests | NOT STARTED |
| Phase 1k | Benchmark results | Zero results captured | NOT STARTED |
| Phase 2 | RAG pipeline, model training, staging deployment | Scaffold only | NOT STARTED |

**Overall Phase 1 status: PARTIAL (~30% complete)**. Infrastructure and scaffold are solid; all live integration work remains.

---

## 23. Next Steps

### Immediate — required before Phase 1 can be declared complete

1. **Configure a live Supabase development project.** Set `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, `DATABASE_URL`, `SUPABASE_JWKS_URL` in `services/api/.env`. Apply all 4 migrations in order. Verify `GET /api/v1/health/dependencies` returns `database: healthy, supabase_jwks: healthy`.

2. **Obtain Gemma model access and start the primary model server.** Accept Gemma license on Hugging Face. Set `HF_TOKEN` and `MODEL_PRIMARY_API_KEY`. Run `docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build model-primary`. Confirm `GET /health` on port 8001 returns 200.

3. **Verify end-to-end model generate route.** Send `POST /api/v1/model/generate` with a valid JWT and a Socratic question. Confirm a response is returned and a row appears in `public.model_requests`.

4. **Run the benchmark.** Execute `python scripts/benchmark_model.py --base-url http://localhost:8001 --model gemma-3-4b-base --requests 20 --concurrency 1`. Record results against the defined targets (p50 < 8 s, p95 < 20 s, error rate < 1%).

5. **Implement domain repositories.** Create `ClassroomRepository`, `MaterialRepository`, `TutoringSessionRepository`, `MessageRepository` backed by the Phase 1 migration schema. Wire them into the contract routes to replace `NOT_IMPLEMENTED`.

6. **Build the frontend tutoring UI.** Add Supabase Auth sign-in, a chat interface, session creation, and message display to `apps/web`. Wire the API client to the domain routes.

7. **Add integration tests.** Create tests that run against a real (development) Supabase instance — covering user sync, classroom membership, and the generate→persist flow.

### Next Phase

8. **RAG pipeline.** Implement PDF ingestion, chunking, BGE/E5 embedding, and pgvector storage using the `0001_init.sql` schema. Wire retrieval into the Socratic prompt builder.

9. **Model fine-tuning.** Implement `train_qlora.py` body; collect or generate synthetic training data; run fine-tuning on Colab Pro+; register the adapter; set `MODEL_PRIMARY_ADAPTER_ENABLED=true`.

10. **Staging environment.** Create a separate Supabase project for staging, configure GitHub secrets, set up staging CI/CD deployment.

### Cleanup

11. Resolve `serve.sh` vs. `start-primary.sh` ambiguity — keep one, remove the other, or document the difference.
12. Wire `packages/shared-types` as a workspace dependency in `apps/web/package.json` and remove the duplicate `HealthStatus` type definition.
13. Add a `CODEOWNERS` file (noted absent in gap audit).
14. Upgrade `apps/web/Dockerfile` to a production multi-stage build.
15. Add checksums for `benchmarks/prompts/socra-smoke.jsonl`.
