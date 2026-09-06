import { NextResponse } from 'next/server'
import { parseCsv } from '../../../lib/csv'

export const dynamic = 'force-dynamic'

const SOURCE = 'https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_week_2025.csv'
const POSITIONS = ['QB','RB','WR','TE'] as const
const TEAM_ALIAS:Record<string,string> = { LA:'LAR', OAK:'LV', SD:'LAC', STL:'LAR' }

type Position = typeof POSITIONS[number]
type Matchup = { rank:number; pointsAllowed:number; leagueAverage:number; factor:number }
type DefenseMap = Record<string, Partial<Record<Position, Matchup>>>

let memoryCache:{ at:number; payload:any }|null = null

function normalizeTeam(team:string){ return TEAM_ALIAS[team] || team }
function clamp(value:number,min:number,max:number){ return Math.max(min,Math.min(max,value)) }

export async function GET(){
  if(memoryCache && Date.now()-memoryCache.at < 24*60*60*1000) return NextResponse.json(memoryCache.payload)
  try{
    const response = await fetch(SOURCE,{ next:{ revalidate:86400 }, headers:{ 'User-Agent':'One More Shiva defensive matchup model' } })
    if(!response.ok) throw new Error(`nflverse returned ${response.status}`)
    const csv = await response.text()
    const rows = parseCsv(csv)

    const weekly = new Map<string,number>()
    for(const row of rows){
      if(String(row.season_type || 'REG').toUpperCase() !== 'REG') continue
      const pos = String(row.position || '').toUpperCase() as Position
      if(!POSITIONS.includes(pos)) continue
      const defense = normalizeTeam(String(row.opponent_team || '').toUpperCase())
      const week = Number(row.week)
      const points = Number(row.fantasy_points_ppr ?? row.fantasy_points ?? 0)
      if(!defense || !Number.isFinite(week) || week < 1 || week > 18 || !Number.isFinite(points)) continue
      const key = `${defense}|${pos}|${week}`
      weekly.set(key,(weekly.get(key)||0)+points)
    }

    const totals = new Map<string,{ total:number; games:number }>()
    for(const [key,points] of weekly){
      const [defense,pos] = key.split('|')
      const group = `${defense}|${pos}`
      const current = totals.get(group) || { total:0,games:0 }
      current.total += points
      current.games += 1
      totals.set(group,current)
    }

    const defenses:DefenseMap = {}
    for(const pos of POSITIONS){
      const values = [...totals.entries()].filter(([key])=>key.endsWith(`|${pos}`)).map(([key,value])=>({ defense:key.split('|')[0], average:value.games?value.total/value.games:0 }))
      const leagueAverage = values.length ? values.reduce((sum,item)=>sum+item.average,0)/values.length : 0
      values.sort((a,b)=>a.average-b.average)
      values.forEach((item,index)=>{
        const rawRatio = leagueAverage > 0 ? item.average/leagueAverage : 1
        const factor = clamp(1+(rawRatio-1)*0.65,0.88,1.12)
        defenses[item.defense] ||= {}
        defenses[item.defense][pos] = {
          rank:index+1,
          pointsAllowed:Number(item.average.toFixed(2)),
          leagueAverage:Number(leagueAverage.toFixed(2)),
          factor:Number(factor.toFixed(3)),
        }
      })
    }

    const payload = {
      baselineSeason:2025,
      methodology:'2025 regular-season PPR fantasy points allowed per game by opponent and position; matchup impact is regressed 65% toward neutral and capped at ±12%.',
      source:'nflverse weekly player stats',
      sourceUrl:SOURCE,
      defenses,
    }
    memoryCache = { at:Date.now(), payload }
    return NextResponse.json(payload)
  }catch(error){
    return NextResponse.json({ baselineSeason:2025,methodology:'unavailable',source:'nflverse weekly player stats',defenses:{},error:error instanceof Error?error.message:'Defense matchup model unavailable.' },{ status:502 })
  }
}
