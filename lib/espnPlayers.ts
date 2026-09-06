import { normalizeName } from './csv'

const ESPN_PLAYERS = 'https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons'
const POSITION: Record<number, string> = { 1:'QB', 2:'RB', 3:'WR', 4:'TE', 5:'K', 16:'DST' }
const PRO_TEAM: Record<number, string> = {1:'ATL',2:'BUF',3:'CHI',4:'CIN',5:'CLE',6:'DAL',7:'DEN',8:'DET',9:'GB',10:'TEN',11:'IND',12:'KC',13:'LV',14:'LAR',15:'MIA',16:'MIN',17:'NE',18:'NO',19:'NYG',20:'NYJ',21:'PHI',22:'ARI',23:'PIT',24:'LAC',25:'SF',26:'SEA',27:'TB',28:'WAS',29:'CAR',30:'JAX',33:'BAL',34:'HOU'}
export type EspnFantasyPlayer={id:string;name:string;team:string;proTeamId:number|null;pos:string;percentOwned:number|null;percentStarted:number|null;injuryStatus:string;espnRank:number|null;projectedPoints:number|null}
let memoryCache:{season:number;week:number;players:EspnFantasyPlayer[];at:number}|null=null
function finite(value:unknown){const n=Number(value);return Number.isFinite(n)?n:null}

function espnDraftRank(player:any){
 const ranks=player?.draftRanksByRankType||{}
 const candidates=[ranks?.PPR?.rank,ranks?.STANDARD?.rank,ranks?.ROOKIE?.rank,player?.rank]
 for(const candidate of candidates){const value=finite(candidate);if(value&&value>0)return value}
 return null
}

function espnProjection(player:any,week:number){
 const stats=Array.isArray(player?.stats)?player.stats:[]
 const projected=stats.filter((row:any)=>Number(row?.statSourceId)===1)
 const exact=week>0?projected.find((row:any)=>Number(row?.scoringPeriodId)===week):null
 const weekly=projected.filter((row:any)=>Number(row?.scoringPeriodId)>0).sort((a:any,b:any)=>Number(a?.scoringPeriodId)-Number(b?.scoringPeriodId))
 const active=exact||weekly.find((row:any)=>finite(row?.appliedTotal)!=null)||weekly[0]
 const season=projected.find((row:any)=>Number(row?.scoringPeriodId)===0)
 return finite(active?.appliedTotal??season?.appliedTotal)
}

export async function getEspnFantasyPlayers(season=2026,week=0):Promise<EspnFantasyPlayer[]>{
 if(memoryCache&&memoryCache.season===season&&memoryCache.week===week&&Date.now()-memoryCache.at<3600000)return memoryCache.players
 const response=await fetch(`${ESPN_PLAYERS}/${season}/players?scoringPeriodId=${week>0?week:0}&view=players_wl`,{headers:{Accept:'application/json','User-Agent':'Mozilla/5.0 (One More Shiva; ESPN fantasy player catalog)','x-fantasy-filter':JSON.stringify({filterActive:{value:true}})},cache:'no-store'})
 if(!response.ok)throw new Error(`ESPN player universe returned ${response.status}`)
 const text=await response.text(); let data:any
 try{data=JSON.parse(text)}catch{throw new Error('ESPN player universe returned a non-JSON response')}
 const rows=Array.isArray(data)?data:Array.isArray(data?.players)?data.players:[]
 const players=rows.map((raw:any)=>{const pool=raw?.playerPoolEntry||raw;const player=pool?.player||raw?.player||raw;const positionId=Number(player?.defaultPositionId??raw?.defaultPositionId??0);const proTeamId=finite(player?.proTeamId??raw?.proTeamId);return{id:String(player?.id??raw?.id??''),name:String(player?.fullName??raw?.fullName??'').trim(),team:proTeamId?PRO_TEAM[proTeamId]||'':'',proTeamId,pos:POSITION[positionId]||'',percentOwned:finite(pool?.percentOwned??raw?.ownership?.percentOwned??player?.ownership?.percentOwned),percentStarted:finite(pool?.percentStarted??raw?.ownership?.percentStarted??player?.ownership?.percentStarted),injuryStatus:String(player?.injuryStatus??raw?.injuryStatus??''),espnRank:espnDraftRank(player),projectedPoints:espnProjection(player,week)}}).filter((p:EspnFantasyPlayer)=>p.id&&p.name&&p.pos)
 memoryCache={season,week,players,at:Date.now()};return players
}
export function espnPlayerMap(players:EspnFantasyPlayer[]){const map=new Map<string,EspnFantasyPlayer>();for(const player of players){map.set(normalizeName(player.name),player);if(player.team)map.set(`${normalizeName(player.name)}|${player.team}`,player)}return map}
