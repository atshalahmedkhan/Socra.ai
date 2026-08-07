create table if not exists public.model_requests (
 id uuid primary key default gen_random_uuid(), request_id text not null unique,
 session_id uuid, student_message_id uuid, assistant_message_id uuid, classroom_id uuid,
 provider_endpoint text not null, model_name text not null, model_version text not null, prompt_version text not null,
 prompt_tokens integer not null default 0, completion_tokens integer not null default 0, total_tokens integer not null default 0,
 queue_latency_ms integer, total_latency_ms integer, time_to_first_token_ms integer, generation_latency_ms integer,
 status text not null check(status in ('pending','succeeded','failed')), error_code text,
 fallback_used boolean not null default false, fallback_reason text, retry_count integer not null default 0,
 created_at timestamptz not null default now()
);
create index model_requests_session_idx on public.model_requests(session_id);
create index model_requests_classroom_idx on public.model_requests(classroom_id);
create index model_requests_created_idx on public.model_requests(created_at);
create index model_requests_model_idx on public.model_requests(model_name,model_version);
create index model_requests_status_idx on public.model_requests(status);
create index model_requests_fallback_idx on public.model_requests(fallback_used);
alter table public.model_requests enable row level security;
