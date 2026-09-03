import type { Player } from './types'

export type DraftPick = { overall: number; round: number; slot: number; team: number; player: Player; user: boolean }
export type DraftRec = { label: string; player: Player; reason: string; score: number }

function need(pos: string, roster: Player[], round: number) {
  const count = (p: string) => roster.filter((player) => player.pos === p).length
  const rb = count('RB'), wr = count('WR'), qb = count('QB'), te = count('TE')
  if (pos === 'RB') {
    let value = rb < 2 ? 20 : rb === 2 ? 8 : -2
    if (round <= 3 && rb < 2) value += 8
    if (wr === 0 && rb >= 2) value -= 8
    return value
  }
  if (pos === 'WR') {
    let value = wr < 2 ? 22 : wr === 2 ? 7 : -2
    if (wr === 0 && rb >= 2) value += 18
    if (round <= 4 && wr < 2) value += 6
    return value
  }
  if (pos === 'TE') return te ? -8 : round <= 2 ? 5 : round <= 6 ? 13 : 8
  if (pos === 'QB') {
    if (qb) return -12
    if (round <= 2) return -22
    if (round === 3) return -5
    return round <= 7 ? 9 : 13
  }
  if (pos === 'DST' || pos === 'K') return round < 10 ? -65 : 3
  return 0
}

function market(player: Player) {
  return player.adp ?? player.consensusAdp ?? player.rank ?? 999
}

export function draftRecommendations(available: Player[], roster: Player[], currentPick: number, round: number, limit = 3): DraftRec[] {
  let pool = available.slice(0, 80)
  const maxReach = round <= 2 ? 8 : round <= 4 ? 14 : round <= 7 ? 22 : 34
  const realistic = pool.filter((player) => market(player) - currentPick <= maxReach || market(player) <= currentPick)
  if (realistic.length >= 6) pool = realistic

  const scored = pool.map((player) => {
    const m = market(player)
    const delta = currentPick - m
    const value = delta >= 0 ? Math.min(28, delta * 1.25) : Math.max(-48, delta * 2.2)
    const fit = need(player.pos, roster, round)
    const rankScore = Math.max(-12, 16 - Math.max(0, m - currentPick) * 0.45)
    const score = 60 + value + fit + rankScore
    return { player, score, value, fit, delta, m }
  })

  const buckets: [string, typeof scored][] = [
    ['BEST PICK', [...scored].sort((a, b) => b.score - a.score || a.m - b.m)],
    ['BEST ROSTER FIT', [...scored].sort((a, b) => b.fit - a.fit || b.score - a.score || a.m - b.m)],
    ['BEST VALUE', [...scored].sort((a, b) => b.value - a.value || b.score - a.score || a.m - b.m)],
  ]
  const used = new Set<string>()
  const out: DraftRec[] = []
  for (const [label, bucket] of buckets) {
    const item = bucket.find((candidate) => !used.has(candidate.player.id))
    if (!item) continue
    used.add(item.player.id)
    let reason = `Fits this pick range and keeps the roster build balanced at ${item.player.pos}.`
    if (item.fit >= 25) reason = `Fills the biggest roster need without abandoning the Round ${round} value tier.`
    else if (item.delta >= 8) reason = `Strong value: ADP ${item.m.toFixed(1)}, still available at pick ${currentPick}.`
    else if (item.delta >= 0) reason = `Positive ADP value at ${item.player.pos} without reaching.`
    out.push({ label, player: item.player, reason, score: item.score })
    if (out.length >= limit) break
  }
  return out
}

export function pickOrder(overall: number, teams = 12) {
  const round = Math.floor((overall - 1) / teams) + 1
  const index = (overall - 1) % teams
  const slot = round % 2 === 1 ? index + 1 : teams - index
  return { round, slot, team: slot }
}

function seededNoise(seed: number) {
  const x = Math.sin(seed * 12.9898 + 78.233) * 43758.5453
  return (x - Math.floor(x)) * 2 - 1
}

export function cpuChoice(available: Player[], roster: Player[], overall: number, team: number) {
  const { round } = pickOrder(overall)
  const slice = available.slice(0, Math.min(60, available.length))
  return [...slice].sort((a, b) => {
    const score = (player: Player) => {
      const m = market(player)
      const reachPenalty = Math.max(0, m - overall) * 1.6
      const valueBonus = Math.max(0, overall - m) * 0.7
      return 100 - reachPenalty + valueBonus + need(player.pos, roster, round) + seededNoise(overall * 31 + team * 7 + player.rank) * 6
    }
    return score(b) - score(a)
  })[0]
}
