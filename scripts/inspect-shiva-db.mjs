import { writeFile } from 'node:fs/promises'
import { DatabaseSync } from 'node:sqlite'
const u='https://raw.githubusercontent.com/cmhart13-boop/Shiva-and-Shiva-2.0-Database/main/shiva_draft_roi.sqlite';
const r=await fetch(u);if(!r.ok)throw new Error(`db ${r.status}`);const p='/tmp/s.sqlite';await writeFile(p,new Uint8Array(await r.arrayBuffer()));
const db=new DatabaseSync(p,{readOnly:true});const q=(s,...a)=>db.prepare(s).all(...a);
const searches=[[2016,'Rudolph'],[2017,'Kamara'],[2017,'Engram'],[2018,'Kittle'],[2018,'Cook'],[2019,'Waller'],[2020,'Thomas'],[2020,'Tonyan'],[2021,'Schultz'],[2021,'Ertz'],[2022,'Engram'],[2023,'Nacua'],[2024,'Smith']];
for(const [season,name] of searches){const rows=q(`select season,player_id,player_name,league_name,round,overall_pick from draft_picks_full where season=? and player_name like ? order by league_id,overall_pick`,season,`%${name}%`);console.log('SEARCH',season,name,JSON.stringify(rows));}
db.close();