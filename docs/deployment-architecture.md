# Deployment architecture

Use a Next.js-compatible frontend host, a Python/Docker backend host, Supabase for Auth/PostgreSQL/Storage, and a private GPU host for vLLM. Hostinger may provide DNS or frontend hosting, but a normal shared plan cannot run NVIDIA vLLM.

Apply migrations before API traffic. Inject backend secrets at runtime, use HTTPS, private model networking, backups, restricted CORS, JSON logs, and health probes. Never place `.env` in an image. The current local Compose validates, but live Supabase and Gemma startup remain credential-blocked.
