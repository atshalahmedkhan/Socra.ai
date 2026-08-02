# Error catalog

Every handled error is `{ "error": { "code", "message", "request_id", "details" } }`. Validation errors use the same envelope. Stack traces, SQL, tokens, provider payloads, and internal URLs are excluded.

Authentication: `AUTH_REQUIRED`, `INVALID_TOKEN`, `TOKEN_EXPIRED`, `FORBIDDEN`, `MEMBERSHIP_REQUIRED`, `ROLE_REQUIRED`. Validation: `VALIDATION_ERROR`, `INVALID_REQUEST`. Resources use `<RESOURCE>_NOT_FOUND`. Conflicts use `ALREADY_EXISTS`, `MEMBERSHIP_ALREADY_EXISTS`, `IDEMPOTENCY_CONFLICT`. Model codes retain `MODEL_TIMEOUT`, `MODEL_UNAVAILABLE`, `MODEL_INVALID_RESPONSE`, `MODEL_POLICY_REJECTED`, and `MODEL_CIRCUIT_OPEN`. Infrastructure uses `DATABASE_UNAVAILABLE`, `STORAGE_UNAVAILABLE`, `INTERNAL_ERROR`, and `NOT_IMPLEMENTED`.

HTTP mapping follows 400 invalid, 401 authentication, 403 authorization, 404 missing, 409 conflict, 422 validation, 429 rate, 500 unexpected, 501 contract unavailable, 503 dependency unavailable, and 504 model deadline.
