import type { LeagueRosterRow, LeagueState, Player } from './types'

export type TeamDraftGrade = {
  teamId: string | number
  teamName: string
  grade: string
  score: number
  projected: number
  starterRank: number
  benchRank: number
  overallRank: number
  positionGrades: Array<{ position:string; grade:string; score:number }>
  notes: string[]
}

export type DraftAnalysis = {
  teams: TeamDraftGrade[]
  leagueAverage: number
  selected: TeamDraftGrade | null
}

const normalize = (value:string) => value.toLowerCase().replace(/[^a-z0-9]/g, '')
const benchSlot = (slot:string) => ['BE','BN','IR'].includes(slot.toUpperCase())

function grade(score:number) {
  if (score >= 91) return 'A+'
  if (score >= 86) return 'A'
  if (score >= 81) return 'A-'
  if (score >= 76) return 'B+'
  if (score >= 71) return 'B'
  if (score >= 66) return 'B-'
  if (score >= 61) return 'C+'
  if (score >= 56) return 'C'
  if (score >= 51) return 'C-'
  if (score >= 46) return 'D+'
  if (score >= 41) return 'D'
  return 'F'
}

function playerValue(row:LeagueRosterRow, ranked:Player | undefined) {
  const projection = row.projectedPoints ?? ranked?.projectedPoints ?? 0
  const rank = ranked?.rank && ranked.rank < 10000 ? ranked.rank : 220
  const started = row.percentStarted ?? ranked?.percentStarted ?? 0
  return projection * 3.1 + Math.max(0, 52 - rank * .22) + started * .16
}

function positionOf(row:LeagueRosterRow, ranked:Player | undefined) {
  return (row.position || ranked?.pos || row.slot || 'FLEX').toUpperCase()
}

function rankValues(values:Array<{id:string | number; value:number}>) {
  const sorted = [...values].sort((a,b) => b.value - a.value)
  let rank = 1
  return new Map(sorted.map((item,index) => {
    if (index > 0 && item.value < sorted[index-1].value) rank = index + 1
    return [String(item.id), rank]
  }))
}

export function analyzeDraft(league:LeagueState, players:Player[], selectedTeamId:string | number | null):DraftAnalysis {
  const playerMap = new Map(players.map(player => [normalize(player.name), player]))
  const raw = league.teams.map(team => {
    const roster = league.roster.filter(row => String(row.teamId) === String(team.id))
    const starters = roster.filter(row => !benchSlot(row.slot))
    const bench = roster.filter(row => benchSlot(row.slot) && row.slot.toUpperCase() !== 'IR')
    const scoreRows = (rows:LeagueRosterRow[]) => rows.map(row => ({ row, ranked:playerMap.get(normalize(row.player)) }))
    const starterValue = scoreRows(starters).reduce((sum,item) => sum + playerValue(item.row,item.ranked),0)
    const benchValue = scoreRows(bench).sort((a,b) => playerValue(b.row,b.ranked)-playerValue(a.row,a.ranked)).slice(0,6).reduce((sum,item) => sum + playerValue(item.row,item.ranked),0)
    const projected = scoreRows(starters).reduce((sum,item) => sum + (item.row.projectedPoints ?? item.ranked?.projectedPoints ?? 0),0)
    const positionScores = ['QB','RB','WR','TE'].map(position => {
      const rows = scoreRows(roster).filter(item => positionOf(item.row,item.ranked) === position)
      const value = rows.sort((a,b) => playerValue(b.row,b.ranked)-playerValue(a.row,a.ranked)).slice(0,position === 'RB' || position === 'WR' ? 3 : 2).reduce((sum,item) => sum + playerValue(item.row,item.ranked),0)
      return { position, value }
    })
    return { team, roster, starters, bench, starterValue, benchValue, projected, positionScores }
  })

  const starterRanks = rankValues(raw.map(item => ({id:item.team.id,value:item.starterValue})))
  const benchRanks = rankValues(raw.map(item => ({id:item.team.id,value:item.benchValue})))
  const positionRanges = new Map(['QB','RB','WR','TE'].map(position => {
    const values = raw.map(item => item.positionScores.find(row => row.position === position)?.value ?? 0)
    return [position,{min:Math.min(...values),max:Math.max(...values)}]
  }))
  const composites = raw.map(item => {
    const starterRank = starterRanks.get(String(item.team.id)) || raw.length
    const benchRank = benchRanks.get(String(item.team.id)) || raw.length
    const percentile = (rank:number) => raw.length <= 1 ? 1 : (raw.length-rank)/(raw.length-1)
    const completeness = Math.min(1,item.starters.length / Math.max(1,league.league.rosterSlots.filter(slot => !benchSlot(slot)).length || 8))
    const score = Math.round(42 + percentile(starterRank)*34 + percentile(benchRank)*16 + completeness*8)
    return {item,starterRank,benchRank,score}
  }).sort((a,b) => b.score-a.score || b.item.projected-a.item.projected)

  const teams = composites.map((entry,index) => {
    const positionGrades = entry.item.positionScores.map(row => {
      const range = positionRanges.get(row.position)!
      const pct = range.max === range.min ? .65 : (row.value-range.min)/(range.max-range.min)
      const score = row.value === 0 ? 35 : Math.round(45+pct*47)
      return {position:row.position,score,grade:grade(score)}
    })
    const weak = [...positionGrades].sort((a,b) => a.score-b.score).slice(0,2)
    const notes = [
      entry.starterRank <= Math.ceil(raw.length/3) ? `Starter strength ranks ${entry.starterRank} of ${raw.length}.` : `Starters rank ${entry.starterRank} of ${raw.length}; prioritize weekly ceiling.`,
      entry.benchRank <= Math.ceil(raw.length/3) ? `Bench depth is a strength at ${entry.benchRank} of ${raw.length}.` : `Bench depth ranks ${entry.benchRank} of ${raw.length}; add upside before low-ceiling depth.`,
      `The clearest upgrade path is ${weak.map(item => item.position).join(' and ')}.`,
    ]
    return {teamId:entry.item.team.id,teamName:entry.item.team.name,grade:grade(entry.score),score:entry.score,projected:entry.item.projected,starterRank:entry.starterRank,benchRank:entry.benchRank,overallRank:index+1,positionGrades,notes}
  })
  const leagueAverage = teams.length ? teams.reduce((sum,team) => sum+team.projected,0)/teams.length : 0
  return {teams,leagueAverage,selected:teams.find(team => String(team.teamId) === String(selectedTeamId)) || teams[0] || null}
}
