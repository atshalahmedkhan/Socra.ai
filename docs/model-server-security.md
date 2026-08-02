# Model server security

- Model services are on an internal network and publish no host ports.
- Bearer keys are runtime secrets and never `NEXT_PUBLIC_`.
- Adapters are read-only; weights, caches, secrets, and benchmark output are Git-ignored.
- Prompts, transcripts, authorization headers, and secret settings are not logged.
- `model_requests` has metadata only and no anonymous RLS policy.
- Keep `/metrics` private.
- On disclosure: revoke and rotate the key, restart services, and audit sanitized request IDs.
- Use a secret manager and TLS/mTLS between production hosts.
