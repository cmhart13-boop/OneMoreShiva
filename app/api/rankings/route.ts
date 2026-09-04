import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { NextResponse } from 'next/server'
import { normalizeName, numberOrNull, parseCsv } from '../../../lib/csv'
import { getEspnFantasyPlayers } from '../../../lib/espnPlayers'

export const revalidate = 3600

export async function GET() {
  const csv = await readFile(path.join(process.cwd(), 'current_rankings.csv'), 'utf8')
  const rankedRows = parseCsv(csv)
    .map((row, index) => ({
      name: row.player_name,
      key: normalizeName(row.player_name || ''),
      team: row.team || '',
      bye: numberOrNull(row.bye),
      pos: (row.position || '').toUpperCase(),
      posRank: numberOrNull(row.position_rank),
      adp: numberOrNull(row.adp),
      consensusAdp: numberOrNull(row.consensus_adp),
      rank: numberOrNull(row.overall_rank) ?? index + 1,
    }))
    .filter((row) => row.name)

  const rankedByName = new Map(rankedRows.map((row) => [row.key, row]))
  const espnPlayers = await getEspnFantasyPlayers(2026)
  const seen = new Set<string>()

  const players = espnPlayers.map((espn, index) => {
    const ranked = rankedByName.get(normalizeName(espn.name))
    seen.add(normalizeName(espn.name))
    return {
      id: espn.id,
      espnId: espn.id,
      name: espn.name,
      team: ranked?.team || espn.team,
      bye: ranked?.bye ?? null,
      pos: ranked?.pos || espn.pos,
      posRank: ranked?.posRank ?? null,
      adp: ranked?.adp ?? null,
      consensusAdp: ranked?.consensusAdp ?? null,
      rank: ranked?.rank ?? 10000 + index,
      percentOwned: espn.percentOwned,
      percentStarted: espn.percentStarted,
      injuryStatus: espn.injuryStatus,
    }
  })

  for (const ranked of rankedRows) {
    if (seen.has(ranked.key)) continue
    players.push({
      id: `${ranked.pos}-${ranked.rank}-${ranked.name}`.replace(/[^a-zA-Z0-9-]/g, '-'),
      espnId: '',
      name: ranked.name,
      team: ranked.team,
      bye: ranked.bye,
      pos: ranked.pos,
      posRank: ranked.posRank,
      adp: ranked.adp,
      consensusAdp: ranked.consensusAdp,
      rank: ranked.rank,
      percentOwned: null,
      percentStarted: null,
      injuryStatus: '',
    })
  }

  players.sort((a, b) => a.rank - b.rank || (b.percentOwned ?? 0) - (a.percentOwned ?? 0) || a.name.localeCompare(b.name))
  return NextResponse.json({ players })
}
