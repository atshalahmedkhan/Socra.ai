-- Forward-only Phase 1 domain schema. Earlier migrations may already be applied.

create table if not exists public.learning_materials (
  id uuid primary key default gen_random_uuid(),
  classroom_id uuid not null references public.classrooms(id) on delete cascade,
  uploaded_by uuid not null references public.users(id),
  title text not null,
  storage_path text not null,
  media_type text not null,
  byte_size bigint not null check (byte_size >= 0),
  status text not null default 'pending'
    check (status in ('pending', 'processing', 'ready', 'failed', 'deleted')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  deleted_at timestamptz
);

create table if not exists public.tutoring_sessions (
  id uuid primary key default gen_random_uuid(),
  classroom_id uuid not null references public.classrooms(id) on delete cascade,
  student_id uuid not null references public.users(id),
  learning_objective text,
  status text not null default 'active'
    check (status in ('active', 'completed', 'abandoned', 'error')),
  hints_used integer not null default 0 check (hints_used >= 0),
  attempts integer not null default 0 check (attempts >= 0),
  started_at timestamptz not null default now(),
  ended_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (ended_at is null or ended_at >= started_at)
);

create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.tutoring_sessions(id) on delete cascade,
  author_user_id uuid references public.users(id),
  role text not null check (role in ('student', 'assistant', 'system')),
  content text not null check (length(btrim(content)) > 0),
  sequence_number integer not null check (sequence_number >= 0),
  hint_level integer check (hint_level between 0 and 5),
  created_at timestamptz not null default now(),
  unique (session_id, sequence_number),
  check ((role = 'student' and author_user_id is not null) or role <> 'student')
);

create table if not exists public.feedback (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.tutoring_sessions(id) on delete cascade,
  message_id uuid references public.messages(id) on delete cascade,
  submitted_by uuid not null references public.users(id),
  rating smallint check (rating between 1 and 5),
  category text,
  comment text,
  created_at timestamptz not null default now(),
  check (rating is not null or category is not null or comment is not null)
);

create table if not exists public.research_participants (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references public.users(id) on delete restrict,
  participant_code text not null unique,
  consent_status text not null default 'not_recorded'
    check (consent_status in ('not_recorded', 'consented', 'declined', 'withdrawn')),
  consent_version text,
  consented_at timestamptz,
  withdrawn_at timestamptz,
  study_condition text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (consent_status <> 'consented' or consented_at is not null),
  check (consent_status <> 'withdrawn' or withdrawn_at is not null)
);

create table if not exists public.anonymized_event_logs (
  id uuid primary key default gen_random_uuid(),
  participant_id uuid not null references public.research_participants(id) on delete restrict,
  session_id uuid references public.tutoring_sessions(id) on delete set null,
  event_type text not null,
  event_data jsonb not null default '{}'::jsonb,
  occurred_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  check (jsonb_typeof(event_data) = 'object')
);

create index if not exists learning_materials_classroom_idx
  on public.learning_materials(classroom_id, created_at desc);
create index if not exists tutoring_sessions_student_idx
  on public.tutoring_sessions(student_id, started_at desc);
create index if not exists tutoring_sessions_classroom_idx
  on public.tutoring_sessions(classroom_id, started_at desc);
create index if not exists messages_session_idx
  on public.messages(session_id, sequence_number);
create index if not exists feedback_session_idx on public.feedback(session_id);
create index if not exists feedback_message_idx on public.feedback(message_id);
create index if not exists research_participants_code_idx
  on public.research_participants(participant_code);
create index if not exists anonymized_event_logs_participant_idx
  on public.anonymized_event_logs(participant_id, occurred_at desc);
create index if not exists anonymized_event_logs_session_idx
  on public.anonymized_event_logs(session_id, occurred_at desc);

alter table public.learning_materials enable row level security;
alter table public.tutoring_sessions enable row level security;
alter table public.messages enable row level security;
alter table public.feedback enable row level security;
alter table public.research_participants enable row level security;
alter table public.anonymized_event_logs enable row level security;

-- Product-domain access is backend-only in Phase 1. No anon/authenticated
-- policies are created; the backend service role performs authorization.

do $$
begin
  if not exists (
    select 1 from pg_constraint where conname = 'model_requests_session_id_fkey'
      and conrelid = 'public.model_requests'::regclass
  ) then
    alter table public.model_requests
      add constraint model_requests_session_id_fkey
      foreign key (session_id) references public.tutoring_sessions(id) on delete set null;
  end if;
  if not exists (
    select 1 from pg_constraint where conname = 'model_requests_student_message_id_fkey'
      and conrelid = 'public.model_requests'::regclass
  ) then
    alter table public.model_requests
      add constraint model_requests_student_message_id_fkey
      foreign key (student_message_id) references public.messages(id) on delete set null;
  end if;
  if not exists (
    select 1 from pg_constraint where conname = 'model_requests_assistant_message_id_fkey'
      and conrelid = 'public.model_requests'::regclass
  ) then
    alter table public.model_requests
      add constraint model_requests_assistant_message_id_fkey
      foreign key (assistant_message_id) references public.messages(id) on delete set null;
  end if;
  if not exists (
    select 1 from pg_constraint where conname = 'model_requests_classroom_id_fkey'
      and conrelid = 'public.model_requests'::regclass
  ) then
    alter table public.model_requests
      add constraint model_requests_classroom_id_fkey
      foreign key (classroom_id) references public.classrooms(id) on delete set null;
  end if;
end $$;
