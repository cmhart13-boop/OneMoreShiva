import { writeFile, mkdir } from 'node:fs/promises'
import { DatabaseSync } from 'node:sqlite'
const u='https://raw.githubusercontent.com/cmhart13-boop/Shiva-and-Shiva-2.0-Database/main/shiva_draft_roi.sqlite'
const r=await fetch(u); if(!r.ok) throw new Error(`db download ${r.status}`)
const p='/tmp/shiva.sqlite'; await writeFile(p,new Uint8Array(await r.arrayBuffer()))
const db=new DatabaseSync(p,{readOnly:true}); const q=(s,...a)=>db.prepare(s).all(...a)
const champs=[
[1465338,'Shiva',2014,3,'luke ahlenius','.. Stay Yucky'],[1465338,'Shiva',2015,1,'Chris H','Password Is Taco'],[1465338,'Shiva',2016,1,'Chris H','Password Is Taco'],[1465338,'Shiva',2017,2,'Jason Hewitt','Team Hewitt'],[1465338,'Shiva',2018,1,'Chris H','Password Is Taco'],[1465338,'Shiva',2019,5,'Dustin Hodges','Team Hodges'],[1465338,'Shiva',2020,5,'Dustin Hodges','everybody was kungflu fightin'],[1465338,'Shiva',2021,9,'Stewart Helton','Scary Larry'],[1465338,'Shiva',2022,4,'Jacob Barton','Show me  the TDs'],[1465338,'Shiva',2023,2,'Rob Derrig','Olave Asians'],[1465338,'Shiva',2024,1,'Chris H','Password Is Taco'],[1465338,'Shiva',2025,1,'Chris H','Password Is Taco'],
[1506903,'Shiva 2.0',2016,1,'Chris H','Rafi Bombs'],[1506903,'Shiva 2.0',2017,10,'Rob Derrig','Kennan and Mel '],[1506903,'Shiva 2.0',2018,10,'Rob Derrig','Rock, Flag  and Eagle...'],[1506903,'Shiva 2.0',2019,9,'Bruce Self','Cum So Hard I  Philip Rivers'],[1506903,'Shiva 2.0',2020,3,'Dustin Hodges','stranger danger'],[1506903,'Shiva 2.0',2021,8,'Mike Hart','No sacko no sacko '],[1506903,'Shiva 2.0',2022,2,'Pascual Rodarte','Team Rodarte'],[1506903,'Shiva 2.0',2023,6,'Zack Brower','Herdsman '],[1506903,'Shiva 2.0',2024,1,'Chris H','Rafi Bombs'],[1506903,'Shiva 2.0',2025,6,'Zack Brower','N1pple Burners']]
const esc=v=>{const s=String(v??'');return /[",\n]/.test(s)?`"${s.replaceAll('"','""')}"`:s}
const rows=[['league_id','league','season','champion','team','team_id','round','round_pick','overall','player','position','keeper','player_id']]
const audits=[['league','season','team_id','expected_champion','expected_team','db_champion','db_team','pick_count','rounds']]
for(const [league_id,league,season,team_id,manager,team] of champs){
 const picks=q(`select overall_pick,round,round_pick,team_id,team_name,manager_names,player_id,player_name,position,keeper from draft_picks_full where league_id=? and season=? and team_id=? order by overall_pick`,league_id,season,team_id)
 const dbTeam=picks[0]?.team_name??''; const dbMgr=picks[0]?.manager_names??''; const rounds=[...new Set(picks.map(x=>Number(x.round)))].sort((a,b)=>a-b).join('|')
 audits.push([league,season,team_id,manager,team,dbMgr,dbTeam,picks.length,rounds])
 for(const x of picks) rows.push([league_id,league,season,manager,dbTeam||team,team_id,Number(x.round),Number(x.round_pick),Number(x.overall_pick),x.player_name,x.position,x.keeper,x.player_id])
}
await mkdir('public',{recursive:true})
await writeFile('public/champion_drafts.csv',rows.map(r=>r.map(esc).join(',')).join('\n'))
await writeFile('public/champion_audit.csv',audits.map(r=>r.map(esc).join(',')).join('\n'))
console.log('FINAL_AUDIT',JSON.stringify({champions:champs.length,total_picks:rows.length-1,audits:audits.length-1}))
db.close()