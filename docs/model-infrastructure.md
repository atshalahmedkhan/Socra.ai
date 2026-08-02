# Socra model infrastructure

The browser calls FastAPI only. FastAPI calls vLLM on an internal Docker network. Order: primary current model, stable LoRA in the same process (behavior fallback), optional separate fallback process (infrastructure fallback), then a controlled failure.

Copy `.env.example` to `.env`, generate strong model API keys, accept Gemma terms using an authorized Hugging Face account, and run `python scripts/verify_gemma_access.py`. A full weight download requires the explicit `--download-model` flag.

Start with `docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build`. Test a reachable server with `python scripts/test_model_endpoint.py --base-url URL --model gemma-3-4b-base`. Model ports use `expose`, not host publishing.

The API shares one async client and semaphore. Connect/read/write/pool timeouts are 5/30/5/5 seconds and the total deadline is 35 seconds. Temporary transport and 502/503/504 failures retry once. The per-process breaker opens after three infrastructure failures for 30 seconds. Full-response mode is used; TTFT remains null.

Health routes are `/health/live`, `/health/ready`, and the default-disabled `/health/model`. Benchmarks use `benchmark_model.py` and `run_benchmark_matrix.py`.

The current site has no tutoring-message domain. Before UI integration, add authenticated session/message tables, transactionally store a unique client message and student text, call the gateway, and store the assistant only on success.
