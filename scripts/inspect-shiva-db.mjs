import { writeFile } from 'node:fs/promises'
import { DatabaseSync } from 'node:sqlite'
const u='https://raw.githubusercontent.com/cmhart13-boop/Shiva-and-Shiva-2.0-Database/main/shiva_draft_roi.sqlite';
const r=await fetch(u);if(!r.ok)throw new Error(`db ${r.status}`);const p='/tmp/s.sqlite';await writeFile(p,new Uint8Array(await r.arrayBuffer()));
const db=new DatabaseSync(p,{readOnly:true});const q=(s,...a)=>db.prepare(s).all(...a);
const targets=[[2016,14054,'Kyle Rudolph'],[2017,3054850,'Alvin Kamara'],[2017,3051876,'Evan Engram'],[2018,3040151,'George Kittle'],[2018,12537,'Jared Cook'],[2019,2576925,'Darren Waller'],[2020,16813,'Logan Thomas'],[2020,2975674,'Robert Tonyan'],[2021,3117256,'Dalton Schultz'],[2021,15835,'Zach Ertz'],[2022,3051876,'Evan Engram'],[2023,4426515,'Puka Nacua']];
for(const [season,pid,name] of targets){const rows=q(`select season,player_id,player_name,league_name,round,overall_pick from draft_picks_full where season=? and player_id=? order by league_id`,season,pid);console.log('PID',season,name,pid,JSON.stringify(rows));}
db.close();