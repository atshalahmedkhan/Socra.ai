# Fallback

The stable adapter protects against current-adapter regression, malformed/empty output, and policy rejection. It is not an infrastructure fallback because it shares the same vLLM process. The optional fallback Compose profile is a separate process; deploy it on independent hardware to protect against host failure. Complete failure returns a stable 503/504 and never routes to paid or unapproved APIs. The breaker is per API process; shared breaker state is Phase 2.
