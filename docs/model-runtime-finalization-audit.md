# Model runtime finalization audit

Date: 2026-07-19

## Complete

- Shared asynchronous model client, bounded concurrency, layered timeouts, one retry, circuit breaker, policy validation, and ordered fallback orchestration.
- Private primary/fallback Compose network, GPU reservation, read-only adapter mount, generated local model API key, and base served name `gemma-3-4b-base`.
- Conservative laptop settings: 4096 context, one sequence, 128 backend output tokens, and 0.80 GPU memory utilization.
- Real optional PostgreSQL telemetry repository. With `DATABASE_URL`, it creates a pending `model_requests` row before generation and updates it on success/failure.
- Development/test-only internal smoke route protected by `INTERNAL_SMOKE_TOKEN`.
- Endpoint, metrics, runtime-verification, single-user benchmark, and progressive concurrency-matrix tools.
- Mocked tests; no GPU is required in CI.

## Mocked or disconnected

- HTTP behavior is unit-tested with mocked transports, not a live Gemma server.
- Database SQL calls are unit-tested with a fake pool. No `DATABASE_URL` or Supabase service-role credential is configured, so the migration and a live row are unverified.
- Fallback orchestration is implemented but no real adapter or second model host exists.

## Runtime configuration

- Checkpoint: `google/gemma-3-4b-it`
- Served model: `gemma-3-4b-base`
- Primary: `http://model-primary:8001`
- Fallback: `http://model-fallback:8002` (disabled)
- Image: `vllm/vllm-openai:v0.9.2`
- Command: `vllm serve google/gemma-3-4b-it --host 0.0.0.0 --port 8001 --api-key … --max-model-len 4096 --gpu-memory-utilization 0.80 --max-num-seqs 1 --served-model-name gemma-3-4b-base`

Required credentials are `HF_TOKEN`, `MODEL_PRIMARY_API_KEY`, and, for persistence, `DATABASE_URL`. The model and database credentials are absent except for the generated ignored model key. Secret values are never recorded here.

## Constraints

Windows uses Docker Desktop’s WSL2/Linux engine. GPU passthrough was verified, but Docker Desktop later stopped. The RTX 4060 Laptop GPU has 8,188 MiB VRAM, which may not fit an unquantized 4B model plus vLLM/KV-cache overhead.
