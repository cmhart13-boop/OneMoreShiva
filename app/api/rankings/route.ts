import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { NextResponse } from 'next/server'
import { numberOrNull, parseCsv } from '../../../../lib/csv'

export const revalidate = 3600

export async function GET() {
  const csv = await readFile(path.join(process.cwd(), 'current_rankings.csv'), 'utf8')
  const rows = parseCsv(csv)
    .map((row, index) => ({
      id: `${row.position || 'NA'}-${index + 1}-${row.player_name}`.replace(/[^a-zA-Z0-9-]/g, '-'),
      name: row.player_name,
      team: row.team || '',
      bye: numberOrNull(row.bye),
      pos: (row.position || '').toUpperCase(),
      posRank: numberOrNull(row.position_rank),
      adp: numberOrNull(row.adp),
      consensusAdp: numberOrNull(row.consensus_adp),
      rank: numberOrNull(row.overall_rank) ?? index + 1,
    }))
    .filter((row) => row.name)
    .sort((a, b) => a.rank - b.rank)

  return NextResponse.json({ players: rows })
}
