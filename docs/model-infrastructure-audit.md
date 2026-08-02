# Model infrastructure audit

Date: 2026-07-19.

The repository was a static HTML/JavaScript research-project site using a browser Supabase client. It had no FastAPI entry point, Python settings, server database client, migration framework, health routes, model integration, Docker, tutoring message/session tables, or Python tests. Existing pages, JavaScript, CSS, Vercel build, and Supabase SQL are retained.

Environment: Windows, Python 3.12.10, pytest 9.0.3, NVIDIA RTX 4060 Laptop GPU (8,188 MiB), driver 592.82 and reported CUDA 13.1. vLLM is not installed. Hugging Face authentication/Gemma-term acceptance is not established, and no Socra adapters exist. The 8 GB GPU may require quantization and reduced context/concurrency.

Implementation adds an isolated API, private vLLM topology, shared async client, deadlines, retry, circuit breaker, fallback, policy checks, telemetry migration, health routes, tools, tests, CI, and documentation. Production tutoring integration remains blocked until its domain schema and authenticated endpoint exist; inventing one would conflict with the existing app.
