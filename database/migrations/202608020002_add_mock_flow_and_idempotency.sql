alter table public.messages add column if not exists status text not null default 'completed';
alter table public.messages add column if not exists client_request_id text;
alter table public.messages add column if not exists reply_to_message_id uuid references public.messages(id) on delete set null;
alter table public.messages drop constraint if exists messages_status_check;
alter table public.messages add constraint messages_status_check check (status in ('pending', 'completed', 'failed'));
create unique index if not exists messages_session_client_request_uidx
  on public.messages(session_id, client_request_id) where client_request_id is not null;
create unique index if not exists messages_reply_to_uidx
  on public.messages(reply_to_message_id) where reply_to_message_id is not null;

alter table public.model_requests add column if not exists provider_route text;
alter table public.model_requests add column if not exists latency_ms integer;
alter table public.model_requests add column if not exists input_tokens integer not null default 0;
alter table public.model_requests add column if not exists output_tokens integer not null default 0;
alter table public.model_requests drop constraint if exists model_requests_status_check;
update public.model_requests set status = 'completed' where status = 'succeeded';
update public.model_requests set latency_ms = total_latency_ms where latency_ms is null;
update public.model_requests set input_tokens = prompt_tokens, output_tokens = completion_tokens;
alter table public.model_requests add constraint model_requests_status_check
  check (status in ('pending', 'completed', 'failed'));
