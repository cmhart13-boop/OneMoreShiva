import { writeFile } from 'node:fs/promises'
import { DatabaseSync } from 'node:sqlite'

const dbUrl = 'https://raw.githubusercontent.com/cmhart13-boop/Shiva-and-Shiva-2.0-Database/main/shiva_draft_roi.sqlite'
const r = await fetch(dbUrl)
if (!r.ok) throw new Error(`db download ${r.status}`)
const path = '/tmp/shiva-report.sqlite'
await writeFile(path, new Uint8Array(await r.arrayBuffer()))
const db = new DatabaseSync(path, { readOnly: true })
const q = (sql, ...args) => db.prepare(sql).all(...args)

const champs = q(`select cast(season as integer) season, 1465338 league_id, 'Shiva' league_name, cast(team_id as integer) team_id, manager_name, team_name
from manager_seasons where champion='1' order by cast(season as integer)`)

for (let season=2016; season<=2025; season++) {
  const url = `https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/leagueHistory/1506903?seasonId=${season}&view=mSettings&view=mTeam&view=mRoster&view=mMatchup&view=mMatchupScore&view=mDraftDetail&view=mStatus`
  const resp = await fetch(url, { headers: { Accept:'application/json', 'User-Agent':'Mozilla/5.0' } })
  if (!resp.ok) { console.log('S2_ERROR', season, resp.status); continue }
  const j = await resp.json(); const obj = Array.isArray(j) ? j[0] : j; const teams=obj?.teams||[]
  let win=teams.find(t=>Number(t?.rankCalculatedFinal)===1)
  if (!win) { const sched=(obj?.schedule||[]).filter(m=>m?.playoffTierType==='WINNERS_BRACKET').sort((a,b)=>(b.matchupPeriodId||0)-(a.matchupPeriodId||0)); const latest=sched[0]; if(latest){const tid=latest.winner==='HOME'?latest.home?.teamId:latest.away?.teamId;win=teams.find(t=>Number(t.id)===Number(tid))} }
  console.log('S2_CHAMP',JSON.stringify({season,id:win?.id,name:win?.name,owners:win?.owners,rank:win?.rankCalculatedFinal,seed:win?.playoffSeed}))
  if(win) champs.push({season,league_id:1506903,league_name:'Shiva 2.0',team_id:Number(win.id),manager_name:null,team_name:win.name||''})
}
champs.sort((a,b)=>a.league_id-b.league_id||a.season-b.season)
console.log('ALL_CHAMPS',JSON.stringify(champs))
const all=[]
for(const c of champs){
 const picks=q(`select league_id,league_name,season,overall_pick,round,round_pick,team_id,team_name,manager_names,player_id,player_name,position from draft_picks_full where league_id=? and season=? and team_id=? order by overall_pick`,c.league_id,c.season,c.team_id)
 console.log('CHAMP_DRAFT',JSON.stringify({league:c.league_name,season:c.season,team_id:c.team_id,team:picks[0]?.team_name||c.team_name,manager:picks[0]?.manager_names||c.manager_name,picks:picks.map(x=>({r:x.round,rp:x.round_pick,o:x.overall_pick,p:x.player_name,pos:x.position,pid:x.player_id}))}))
 all.push(...picks)
}
const rc={};for(let r=1;r<=16;r++)rc[r]={QB:0,RB:0,WR:0,TE:0,DST:0,K:0,Other:0,total:0}
for(const x of all){let p=['QB','RB','WR','TE'].includes(x.position)?x.position:(['D/ST','DST'].includes(x.position)?'DST':x.position==='K'?'K':'Other');if(rc[x.round]){rc[x.round][p]++;rc[x.round].total++}}
console.log('ROUND_COUNTS',JSON.stringify(rc))
const bp={};
for(const c of champs){const ps=all.filter(x=>x.league_id===c.league_id&&x.season===c.season&&x.team_id===c.team_id);const cnt=(m,p)=>ps.filter(x=>x.round<=m&&x.position===p).length;const first=p=>ps.find(x=>x.position===p)?.round??null;bp[`${c.league_name}|${c.season}`]={early8:ps.filter(x=>x.round<=8).map(x=>x.position),rb2:cnt(2,'RB'),rb3:cnt(3,'RB'),wr3:cnt(3,'WR'),rb5:cnt(5,'RB'),wr5:cnt(5,'WR'),firstQB:first('QB'),firstTE:first('TE')}}
console.log('BLUEPRINTS',JSON.stringify(bp))
for(const c of champs){const rows=q(`select league_name,season,round,overall_pick,team_id,team_name,manager_name,player_name,position,position_finish_total,position_finish_ppg,fantasy_points_ppr,ppg,games_played,classification,final_draft_roi from draft_roi_scores where league_id=? and season=? and team_id=? order by overall_pick`,c.league_id,c.season,c.team_id);console.log('CHAMP_PERF',JSON.stringify({league:c.league_name,season:c.season,rows:rows.map(x=>({r:x.round,p:x.player_name,pos:x.position,fp:x.fantasy_points_ppr,ppg:x.ppg,fr:x.position_finish_ppg,cls:x.classification}))}))}
db.close()
