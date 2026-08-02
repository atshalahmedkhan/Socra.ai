create table if not exists public.users (
  id uuid primary key default gen_random_uuid(),
  auth_user_id uuid not null unique,
  email text,
  display_name text,
  is_admin boolean not null default false,
  is_researcher boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table if not exists public.classrooms (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  course_code text,
  term text,
  status text not null default 'active' check(status in ('active','archived')),
  created_by uuid not null references public.users(id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table if not exists public.classroom_members (
  id uuid primary key default gen_random_uuid(),
  classroom_id uuid not null references public.classrooms(id) on delete cascade,
  user_id uuid not null references public.users(id) on delete cascade,
  role text not null check(role in ('student','ta','instructor')),
  status text not null default 'active' check(status in ('active','invited','removed')),
  joined_at timestamptz not null default now(),
  unique(classroom_id,user_id)
);
create index if not exists users_auth_user_id_idx on public.users(auth_user_id);
create index if not exists classrooms_created_by_idx on public.classrooms(created_by);
create index if not exists classroom_members_classroom_idx on public.classroom_members(classroom_id);
create index if not exists classroom_members_user_idx on public.classroom_members(user_id);
alter table public.users enable row level security;
alter table public.classrooms enable row level security;
alter table public.classroom_members enable row level security;
-- Backend service role bypasses RLS. No anonymous policies are granted.
