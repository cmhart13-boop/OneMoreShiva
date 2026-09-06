import { writeFile } from 'node:fs/promises'
import { DatabaseSync } from 'node:sqlite'
const u='https://raw.githubusercontent.com/cmhart13-boop/Shiva-and-Shiva-2.0-Database/main/shiva_draft_roi.sqlite';
const r=await fetch(u);const p='/tmp/s.sqlite';await writeFile(p,new Uint8Array(await r.arrayBuffer()));
const db=new DatabaseSync(p,{readOnly:true});const q=(s,...a)=>db.prepare(s).all(...a);
const rows=q(`select season, team_id, min(team_name) team_name, min(manager_names) manager_names, min(owner_ids) owner_ids from draft_picks_full where league_id=1506903 group by season,team_id order by season,team_id`);
for(const season of [...new Set(rows.map(x=>x.season))]) console.log('S2_TEAMS',season,JSON.stringify(rows.filter(x=>x.season===season)));
db.close();