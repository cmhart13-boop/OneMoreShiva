import { writeFile } from 'node:fs/promises'
import { DatabaseSync } from 'node:sqlite'
const u='https://raw.githubusercontent.com/cmhart13-boop/Shiva-and-Shiva-2.0-Database/main/shiva_draft_roi.sqlite';
const r=await fetch(u);if(!r.ok)throw new Error(`db ${r.status}`);const p='/tmp/s.sqlite';await writeFile(p,new Uint8Array(await r.arrayBuffer()));
const db=new DatabaseSync(p,{readOnly:true});const q=(s,...a)=>db.prepare(s).all(...a);
const tables=q("select name from sqlite_master where type='table' order by name");
for(const {name} of tables){const cols=q(`pragma table_info(${name})`).map(x=>x.name); console.log('TABLE',name,'COLS',JSON.stringify(cols),'COUNT',q(`select count(*) n from ${name}`)[0].n);}
for(const t of ['manager_seasons','teams_standings','draft_picks_full','draft_roi_scores']){try{console.log('DISTINCT_LEAGUE',t,JSON.stringify(q(`select league_id,league_name,count(*) n from ${t} group by league_id,league_name order by league_id`)))}catch(e){console.log('NO_LEAGUE_COLS',t,String(e))}}
try{console.log('MANAGER_CHAMPS',JSON.stringify(q(`select * from manager_seasons where champion='1' order by cast(season as integer),manager_name`)))}catch(e){console.log('ERR',String(e))}
try{console.log('STANDINGS_CHAMPS',JSON.stringify(q(`select * from teams_standings where champion='1' order by cast(season as integer),manager_names`)))}catch(e){console.log('ERR2',String(e))}
db.close();