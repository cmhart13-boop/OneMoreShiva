import { writeFile } from 'node:fs/promises'
import { DatabaseSync } from 'node:sqlite'

const url = 'https://raw.githubusercontent.com/cmhart13-boop/Shiva-and-Shiva-2.0-Database/main/shiva_draft_roi.sqlite'
const r = await fetch(url)
if (!r.ok) throw new Error(`db download ${r.status}`)
const path = '/tmp/shiva-report.sqlite'
await writeFile(path, new Uint8Array(await r.arrayBuffer()))
const db = new DatabaseSync(path, { readOnly: true })

const q = (sql) => db.prepare(sql).all()
const one = (sql) => db.prepare(sql).get()

console.log('CHAMPION_VALUES_MANAGER', JSON.stringify(q(`select champion, count(*) n from manager_seasons group by champion order by champion`)))
console.log('CHAMPION_VALUES_STANDINGS', JSON.stringify(q(`select champion, count(*) n from teams_standings group by champion order by champion`)))
console.log('CHAMPION_ROWS_MANAGER', JSON.stringify(q(`select * from manager_seasons where lower(coalesce(champion,'')) in ('1','true','yes','y') or champion='1' order by cast(season as integer), manager_name`)))
console.log('CHAMPION_ROWS_STANDINGS', JSON.stringify(q(`select * from teams_standings where lower(coalesce(champion,'')) in ('1','true','yes','y') or champion='1' order by cast(season as integer), manager_names`)))

console.log('DRAFT_LEAGUE_SEASONS', JSON.stringify(q(`select league_name, season, count(distinct team_id) teams, count(*) picks from draft_picks_full group by league_name,season order by league_name,season`)))

console.log('CHAMPION_CANDIDATE_MAP', JSON.stringify(q(`
with champs as (
  select cast(season as integer) season, cast(team_id as integer) team_id, owner_id, manager_name, team_name
  from manager_seasons
  where lower(coalesce(champion,'')) in ('1','true','yes','y') or champion='1'
)
select c.season,c.team_id,c.owner_id,c.manager_name,c.team_name,
       d.league_name, d.league_id, count(*) draft_picks,
       min(d.overall_pick) first_pick, max(d.round) max_round,
       min(d.team_name) draft_team_name, min(d.manager_names) draft_manager_names, min(d.owner_ids) draft_owner_ids
from champs c
join draft_picks_full d on d.season=c.season and d.team_id=c.team_id
where (c.owner_id is null or c.owner_id='' or d.owner_ids like '%'||c.owner_id||'%')
group by c.season,c.team_id,c.owner_id,c.manager_name,c.team_name,d.league_name,d.league_id
order by c.season,d.league_name
`)))

console.log('CHAMPION_CANDIDATE_MAP_STANDINGS', JSON.stringify(q(`
with champs as (
  select cast(season as integer) season, cast(team_id as integer) team_id, owner_ids, manager_names, team_name
  from teams_standings
  where lower(coalesce(champion,'')) in ('1','true','yes','y') or champion='1'
)
select c.season,c.team_id,c.owner_ids,c.manager_names,c.team_name,
       d.league_name,d.league_id,count(*) draft_picks,
       min(d.team_name) draft_team_name,min(d.manager_names) draft_manager_names,min(d.owner_ids) draft_owner_ids
from champs c join draft_picks_full d on d.season=c.season and d.team_id=c.team_id
where (c.owner_ids is null or c.owner_ids='' or d.owner_ids=c.owner_ids or d.owner_ids like '%'||replace(replace(c.owner_ids,'[',''),']','')||'%')
group by c.season,c.team_id,c.owner_ids,c.manager_names,c.team_name,d.league_name,d.league_id
order by c.season,d.league_name
`)))

db.close()
