import { writeFile } from 'node:fs/promises'
import { DatabaseSync } from 'node:sqlite'

const u='https://raw.githubusercontent.com/cmhart13-boop/Shiva-and-Shiva-2.0-Database/main/shiva_draft_roi.sqlite'
const r=await fetch(u)
if(!r.ok) throw new Error(`db download ${r.status}`)
const p='/tmp/shiva.sqlite'
await writeFile(p,new Uint8Array(await r.arrayBuffer()))
const db=new DatabaseSync(p,{readOnly:true})
const q=(s,...a)=>db.prepare(s).all(...a)

const champs=[
{league_id:1465338,league:'Shiva',season:2014,team_id:3,manager:'luke ahlenius',team:'.. Stay Yucky'},
{league_id:1465338,league:'Shiva',season:2015,team_id:1,manager:'Chris H',team:'Password Is Taco'},
{league_id:1465338,league:'Shiva',season:2016,team_id:1,manager:'Chris H',team:'Password Is Taco'},
{league_id:1465338,league:'Shiva',season:2017,team_id:2,manager:'Jason Hewitt',team:'Team Hewitt'},
{league_id:1465338,league:'Shiva',season:2018,team_id:1,manager:'Chris H',team:'Password Is Taco'},
{league_id:1465338,league:'Shiva',season:2019,team_id:5,manager:'Dustin Hodges',team:'Team Hodges'},
{league_id:1465338,league:'Shiva',season:2020,team_id:5,manager:'Dustin Hodges',team:'everybody was kungflu fightin'},
{league_id:1465338,league:'Shiva',season:2021,team_id:9,manager:'Stewart Helton',team:'Scary Larry'},
{league_id:1465338,league:'Shiva',season:2022,team_id:4,manager:'Jacob Barton',team:'Show me  the TDs'},
{league_id:1465338,league:'Shiva',season:2023,team_id:2,manager:'Rob Derrig',team:'Olave Asians'},
{league_id:1465338,league:'Shiva',season:2024,team_id:1,manager:'Chris H',team:'Password Is Taco'},
{league_id:1465338,league:'Shiva',season:2025,team_id:1,manager:'Chris H',team:'Password Is Taco'},
{league_id:1506903,league:'Shiva 2.0',season:2016,team_id:1,manager:'Chris H',team:'Rafi Bombs'},
{league_id:1506903,league:'Shiva 2.0',season:2017,team_id:10,manager:'Rob Derrig',team:'Kennan and Mel '},
{league_id:1506903,league:'Shiva 2.0',season:2018,team_id:10,manager:'Rob Derrig',team:'Rock, Flag  and Eagle...'},
{league_id:1506903,league:'Shiva 2.0',season:2019,team_id:9,manager:'Bruce Self',team:'Cum So Hard I  Philip Rivers'},
{league_id:1506903,league:'Shiva 2.0',season:2020,team_id:3,manager:'Dustin Hodges',team:'stranger danger'},
{league_id:1506903,league:'Shiva 2.0',season:2021,team_id:8,manager:'Mike Hart',team:'No sacko no sacko '},
{league_id:1506903,league:'Shiva 2.0',season:2022,team_id:2,manager:'Pascual Rodarte',team:'Team Rodarte'},
{league_id:1506903,league:'Shiva 2.0',season:2023,team_id:6,manager:'Zack Brower',team:'Herdsman '},
{league_id:1506903,league:'Shiva 2.0',season:2024,team_id:1,manager:'Chris H',team:'Rafi Bombs'},
{league_id:1506903,league:'Shiva 2.0',season:2025,team_id:6,manager:'Zack Brower',team:'N1pple Burners'}
]

let total=0
for(const c of champs){
 const picks=q(`select league_id,league_name,season,overall_pick,round,round_pick,team_id,team_name,owner_ids,manager_names,player_id,player_name,position,keeper from draft_picks_full where league_id=? and season=? and team_id=? order by overall_pick`,c.league_id,c.season,c.team_id)
 const rounds=[...new Set(picks.map(x=>Number(x.round)))].sort((a,b)=>a-b)
 const dbTeam=picks[0]?.team_name??''; const dbManager=picks[0]?.manager_names??''
 console.log('AUDIT',JSON.stringify({league:c.league,season:c.season,team_id:c.team_id,expected_manager:c.manager,expected_team:c.team,db_manager:dbManager,db_team:dbTeam,pick_count:picks.length,rounds}))
 for(const x of picks){console.log('PICK',JSON.stringify({league:c.league,league_id:c.league_id,season:c.season,champion:c.manager,team:dbTeam||c.team,team_id:c.team_id,round:Number(x.round),round_pick:Number(x.round_pick),overall:Number(x.overall_pick),player:x.player_name,position:x.position,keeper:x.keeper,player_id:x.player_id}))}
 total+=picks.length
}
console.log('FINAL_AUDIT',JSON.stringify({champions:champs.length,total_picks:total}))
db.close()