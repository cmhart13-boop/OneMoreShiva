alter table public.user_leagues add column if not exists provider text not null default 'espn';
alter table public.user_leagues add column if not exists league_data jsonb;
alter table public.user_leagues alter column team_id type text using team_id::text;
alter table public.user_leagues drop constraint if exists user_leagues_user_id_league_id_season_key;
alter table public.user_leagues add constraint user_leagues_provider_check check (provider in ('espn', 'sleeper'));
alter table public.user_leagues add constraint user_leagues_user_provider_league_season_key unique (user_id, provider, league_id, season);

grant select, insert, update, delete on table public.user_leagues to authenticated;

drop policy if exists "Users can read their own leagues" on public.user_leagues;
drop policy if exists "Users can add their own leagues" on public.user_leagues;
drop policy if exists "Users can update their own leagues" on public.user_leagues;
drop policy if exists "Users can delete their own leagues" on public.user_leagues;

create policy "Users can read their own leagues" on public.user_leagues for select to authenticated using ((select auth.uid()) = user_id);
create policy "Users can add their own leagues" on public.user_leagues for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "Users can update their own leagues" on public.user_leagues for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "Users can delete their own leagues" on public.user_leagues for delete to authenticated using ((select auth.uid()) = user_id);
