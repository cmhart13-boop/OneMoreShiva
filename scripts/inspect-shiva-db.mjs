import { writeFile } from 'node:fs/promises'
import { DatabaseSync } from 'node:sqlite'
const u='https://raw.githubusercontent.com/cmhart13-boop/Shiva-and-Shiva-2.0-Database/main/shiva_draft_roi.sqlite';
const r=await fetch(u);if(!r.ok)throw new Error(`db ${r.status}`);const p='/tmp/s.sqlite';await writeFile(p,new Uint8Array(await r.arrayBuffer()));
const db=new DatabaseSync(p,{readOnly:true});const q=(s,...a)=>db.prepare(s).all(...a);
for(let season=2016;season<=2025;season++){
 const rows=q(`WITH top5 AS (SELECT season,player_id,player_name,position,MIN(position_finish_total) finish FROM draft_roi_scores WHERE season=? AND position IN ('RB','WR','TE') AND position_finish_total BETWEEN 1 AND 5 GROUP BY season,player_id,player_name,position), d AS (SELECT season,player_id,MAX(CASE WHEN league_id=1465338 THEN round END) shiva_round,MAX(CASE WHEN league_id=1506903 THEN round END) shiva2_round,MAX(CASE WHEN league_id=1465338 THEN overall_pick END) shiva_pick,MAX(CASE WHEN league_id=1506903 THEN overall_pick END) shiva2_pick FROM draft_picks_full WHERE season=? GROUP BY season,player_id) SELECT t.season,t.position,t.finish,t.player_name,d.shiva_round,d.shiva_pick,d.shiva2_round,d.shiva2_pick FROM top5 t LEFT JOIN d ON d.season=t.season AND d.player_id=t.player_id ORDER BY t.position,t.finish`,season,season);
 console.log('TOP5_YEAR',season,JSON.stringify(rows));
}
db.close();