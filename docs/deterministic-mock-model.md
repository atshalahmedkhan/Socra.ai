# Deterministic mock model adapter

The deterministic mock adapter exercises backend control flow without a model server. It is not Gemma and must never be presented as model-runtime verification.

Set `MODEL_PROVIDER=mock` only in test or development. `MODEL_MOCK_SCENARIO` accepts `success`, `timeout`, `retryable_failure`, `non_retryable_failure`, `primary_failure_fallback_success`, or `primary_and_fallback_failure`. Production configuration rejects the mock provider.

The tutoring-message service atomically creates a completed student message and pending assistant message. It then creates pending model telemetry, invokes the configured gateway, and marks both assistant/telemetry records completed or failed. `client_request_id` is unique per session, and duplicate frontend requests read back the existing message pair without another adapter call.

Mock telemetry uses `provider_route=mock`, a safe model identity (`deterministic-mock`), deterministic latency/token counts when successful, retry/fallback metadata, and stable error codes. It never claims to be a live inference result.

Apply `database/migrations/202608020002_add_mock_flow_and_idempotency.sql` after earlier Phase 1 migrations. The automated full-flow test uses a deterministic database repository double; live PostgreSQL application/read-back still requires an explicitly configured test database.
