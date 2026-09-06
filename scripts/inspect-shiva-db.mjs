import { writeFile } from 'node:fs/promises'
import { DatabaseSync } from 'node:sqlite'
const u='https://raw.githubusercontent.com/cmhart13-boop/Shiva-and-Shiva-2.0-Database/main/shiva_draft_roi.sqlite';const r=await fetch(u);const p='/tmp/s.sqlite';await writeFile(p,new Uint8Array(await r.arrayBuffer()));const db=new DatabaseSync(p,{readOnly:true});const q=(s,...a)=>db.prepare(s).all(...a);
for(const t of ['end_rosters','league_settings','seasons','teams_standings','manager_summary','manager_draft_roi_summary']){console.log('SCHEMA',t,JSON.stringify(q(`pragma table_info(${t})`)));console.log('SAMPLE',t,JSON.stringify(q(`select * from ${t} limit 5`)))}
try{console.log('END_GROUP',JSON.stringify(q(`select * from end_rosters where league_name='Shiva 2.0' limit 20`)))}catch(e){console.log('END_ERR',String(e))}
db.close();