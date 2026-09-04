import type { Evidence, LeagueRosterRow, Player } from './types'

export type Recommendation = { winner:string; alternative:string; confidence:'Strong Start'|'Lean'|'Close Call'; explanation:string; scores:Record<string, number> }

function pprValue(settings: Record<string, number>) {
  return settings.rec ?? settings['53'] ?? 0
}

function playerScore(row: LeagueRosterRow, current: Player | undefined, evidence: Evidence | null, scoring: Record<string, number>) {
  const injury = /out|ir|suspend/i.test(row.injuryStatus) ? -30 : /questionable|doubtful/i.test(row.injuryStatus) ? -8 : 0
  const projection = current?.projectedPoints ?? evidence?.recent ?? evidence?.ppg ?? 0
  const consensus = current?.rank && current.rank < 10000 ? Math.max(0, 220 - current.rank) / 22 : 0
  const workload = (row.percentStarted ?? current?.percentStarted ?? 0) / 10
  const role = (evidence?.recent ?? evidence?.ppg ?? 0) * .35 + (evidence?.floor ?? 0) * .25
  const upside = (evidence?.ceiling ?? projection) * .12
  const receptionFit = pprValue(scoring) * (row.position === 'WR' || row.position === 'TE' ? 1.2 : row.position === 'RB' ? .8 : 0)
  return projection * 1.5 + consensus + workload + role + upside + receptionFit + injury
}

export function recommendStart(a: LeagueRosterRow, b: LeagueRosterRow, players: Player[], evidenceA: Evidence | null, evidenceB: Evidence | null, scoring: Record<string, number>): Recommendation {
  const currentA = players.find((player) => player.name.toLowerCase() === a.player.toLowerCase())
  const currentB = players.find((player) => player.name.toLowerCase() === b.player.toLowerCase())
  const scoreA = playerScore(a, currentA, evidenceA, scoring)
  const scoreB = playerScore(b, currentB, evidenceB, scoring)
  const winner = scoreA >= scoreB ? a : b
  const alternative = winner === a ? b : a
  const delta = Math.abs(scoreA - scoreB)
  const confidence = delta >= 12 ? 'Strong Start' : delta >= 5 ? 'Lean' : 'Close Call'
  const factors = [winner.injuryStatus ? `${alternative.player} carries the greater availability risk` : '', pprValue(scoring) > 0 ? 'the league reception scoring' : '', 'current projection, workload, recent role and historical range'].filter(Boolean)
  return { winner:winner.player, alternative:alternative.player, confidence, explanation:`${winner.player} has the better combined profile from ${factors.join(', ')}.`, scores:{ [a.player]:scoreA, [b.player]:scoreB } }
}
