create table if not exists public.user_leagues (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  league_id text not null,
  season integer not null default 2026,
  nickname text,
  team_id integer,
  league_name text,
  team_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (user_id, league_id, season)
);

alter table public.user_leagues enable row level security;

create policy "Users can read their own leagues"
on public.user_leagues for select
using (auth.uid() = user_id);

create policy "Users can add their own leagues"
on public.user_leagues for insert
with check (auth.uid() = user_id);

create policy "Users can update their own leagues"
on public.user_leagues for update
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

create policy "Users can delete their own leagues"
on public.user_leagues for delete
using (auth.uid() = user_id);

create index if not exists user_leagues_user_id_idx on public.user_leagues(user_id);
