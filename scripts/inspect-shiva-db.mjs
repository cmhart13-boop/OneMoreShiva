import { writeFile } from 'node:fs/promises'
import { DatabaseSync } from 'node:sqlite'
const u='https://raw.githubusercontent.com/cmhart13-boop/Shiva-and-Shiva-2.0-Database/main/shiva_draft_roi.sqlite';
const r=await fetch(u);if(!r.ok)throw new Error(`db ${r.status}`);const p='/tmp/s.sqlite';await writeFile(p,new Uint8Array(await r.arrayBuffer()));
const db=new DatabaseSync(p,{readOnly:true});const q=(s,...a)=>db.prepare(s).all(...a);
const rows=q(`SELECT season,player_name,league_name,round,overall_pick FROM draft_picks_full WHERE
(season=2016 AND player_name IN ('David Johnson','Kyle Rudolph')) OR
(season=2017 AND player_name IN ('Alvin Kamara','Evan Engram')) OR
(season=2018 AND player_name IN ('George Kittle','Jared Cook')) OR
(season=2019 AND player_name IN ('Darren Waller')) OR
(season=2020 AND player_name IN ('Logan Thomas','Robert Tonyan')) OR
(season=2021 AND player_name IN ('Dalton Schultz','Zach Ertz')) OR
(season=2022 AND player_name IN ('Evan Engram')) OR
(season=2023 AND player_name IN ('Puka Nacua')) OR
(season=2024 AND player_name IN ('Jonnu Smith'))
ORDER BY season,player_name,league_id`);
console.log('MISSING_ROUNDS',JSON.stringify(rows));
db.close();