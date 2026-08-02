# Logging structure

Every request receives a constrained or generated `X-Request-ID`. Completion logs include request ID, method, route, status, and latency. JSON logs include timestamp, level, service, and structured fields.

Recursive redaction covers authorization, cookies, passwords, tokens, API keys, service-role keys, database URLs, and secrets. Callers must never attach student messages, complete transcripts, prompts, or model responses to log metadata. Operational audit events such as role changes, classroom deletion, research exports, and admin actions should use a future dedicated audit repository/table, separate from research analytics.
