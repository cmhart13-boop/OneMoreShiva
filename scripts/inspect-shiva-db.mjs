import { writeFile } from 'node:fs/promises'
import { DatabaseSync } from 'node:sqlite'
const u='https://raw.githubusercontent.com/cmhart13-boop/Shiva-and-Shiva-2.0-Database/main/shiva_draft_roi.sqlite';
const r=await fetch(u);if(!r.ok)throw new Error(`db ${r.status}`);const p='/tmp/s.sqlite';await writeFile(p,new Uint8Array(await r.arrayBuffer()));
const db=new DatabaseSync(p,{readOnly:true});const q=(s,...a)=>db.prepare(s).all(...a);
const rows=q(`
WITH top5 AS (
  SELECT season, player_id, player_name, position, MIN(position_finish_total) finish
  FROM draft_roi_scores
  WHERE season BETWEEN 2016 AND 2025 AND position IN ('RB','WR','TE') AND position_finish_total BETWEEN 1 AND 5
  GROUP BY season, player_id, player_name, position
), d AS (
  SELECT season, player_id,
    MAX(CASE WHEN league_id=1465338 THEN round END) shiva_round,
    MAX(CASE WHEN league_id=1506903 THEN round END) shiva2_round,
    MAX(CASE WHEN league_id=1465338 THEN overall_pick END) shiva_pick,
    MAX(CASE WHEN league_id=1506903 THEN overall_pick END) shiva2_pick
  FROM draft_picks_full
  WHERE season BETWEEN 2016 AND 2025
  GROUP BY season, player_id
)
SELECT t.season,t.position,t.finish,t.player_id,t.player_name,
       d.shiva_round,d.shiva_pick,d.shiva2_round,d.shiva2_pick
FROM top5 t LEFT JOIN d ON d.season=t.season AND d.player_id=t.player_id
ORDER BY t.season,t.position,t.finish,t.player_name;
`);
console.log('TOP5_ACTUAL_ROUNDS',JSON.stringify(rows));
const counts=q(`
WITH top5 AS (
  SELECT season, player_id, position, MIN(position_finish_total) finish
  FROM draft_roi_scores
  WHERE season BETWEEN 2016 AND 2025 AND position IN ('RB','WR','TE') AND position_finish_total BETWEEN 1 AND 5
  GROUP BY season, player_id, position
), instances AS (
  SELECT t.season,t.position,t.player_id,d.league_name,d.round
  FROM top5 t JOIN draft_picks_full d ON d.season=t.season AND d.player_id=t.player_id
  WHERE d.league_id IN (1465338,1506903)
)
SELECT season,position,league_name,round,COUNT(*) n FROM instances
GROUP BY season,position,league_name,round ORDER BY season,position,league_name,round;
`);
console.log('TOP5_COUNTS',JSON.stringify(counts));
console.log('ROWCOUNT',rows.length);
db.close();