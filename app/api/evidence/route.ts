import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { gunzipSync } from 'node:zlib'
import { NextRequest, NextResponse } from 'next/server'
import { normalizeName, parseCsv } from '../../../../lib/csv'

type Row = Record<string, string>
type Evidence = {
  name: string
  pos: string
  team: string
  games: number
  season: number | null
  ppg: number | null
  floor: number | null
  ceiling: number | null
  rate15: number | null
  boom25: number | null
  bust10: number | null
  recent: number | null
}

let evidencePromise: Promise<Map<string, Evidence>> | null = null

function n(row: Row, ...keys: string[]) {
  for (const key of keys) {
    const value = Number(row[key])
    if (Number.isFinite(value)) return value
  }
  return 0
}

function str(row: Row, ...keys: string[]) {
  for (const key of keys) {
    const value = row[key]
    if (value) return String(value)
  }
  return ''
}

function ppr(row: Row): number | null {
  const direct = Number(row.fantasy_points_ppr || row.fantasy_points_ppr_total || '')
  if (Number.isFinite(direct)) return direct
  const recognizable = ['passing_yards','passing_tds','rushing_yards','rushing_tds','receptions','receiving_yards','receiving_tds'].some((key) => row[key] !== undefined)
  if (!recognizable) return null
  const twoPoint = n(row, 'passing_2pt_conversions') + n(row, 'rushing_2pt_conversions') + n(row, 'receiving_2pt_conversions') + n(row, 'two_point_conversions')
  return (
    n(row, 'passing_yards') * 0.04 +
    n(row, 'passing_tds') * 4 -
    n(row, 'interceptions') * 2 +
    n(row, 'rushing_yards') * 0.1 +
    n(row, 'rushing_tds') * 6 +
    n(row, 'receptions') +
    n(row, 'receiving_yards') * 0.1 +
    n(row, 'receiving_tds') * 6 +
    n(row, 'return_tds') * 6 +
    twoPoint * 2 -
    n(row, 'fumbles_lost') * 2
  )
}

function quantile(sorted: number[], q: number) {
  if (!sorted.length) return null
  const index = (sorted.length - 1) * q
  const lo = Math.floor(index)
  const hi = Math.ceil(index)
  if (lo === hi) return sorted[lo]
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (index - lo)
}

async function buildEvidence() {
  const compressed = await readFile(path.join(process.cwd(), 'player_weekly_master_2014_2025.csv.gz'))
  const text = gunzipSync(compressed).toString('utf8')
  const rows = parseCsv(text)
  const grouped = new Map<string, { name: string; pos: string; team: string; season: number; week: number; pts: number }[]>()

  for (const row of rows) {
    const name = str(row, 'player_display_name', 'player_name', 'player', 'name')
    if (!name) continue
    const season = Number(str(row, 'season', 'year'))
    const week = Number(str(row, 'week'))
    const pts = ppr(row)
    if (!Number.isFinite(season) || !Number.isFinite(week) || week < 1 || week > 18 || pts === null || !Number.isFinite(pts)) continue
    const key = normalizeName(name)
    const list = grouped.get(key) || []
    list.push({
      name,
      pos: str(row, 'position', 'pos'),
      team: str(row, 'recent_team', 'team', 'posteam'),
      season,
      week,
      pts,
    })
    grouped.set(key, list)
  }

  const output = new Map<string, Evidence>()
  for (const [key, games] of grouped) {
    const latestSeason = Math.max(...games.map((game) => game.season))
    const latest = games.filter((game) => game.season === latestSeason).sort((a, b) => a.week - b.week)
    const values = latest.map((game) => game.pts).sort((a, b) => a - b)
    const chronological = latest.map((game) => game.pts)
    const mean = values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null
    const recent = chronological.length ? chronological.slice(-4).reduce((sum, value) => sum + value, 0) / Math.min(4, chronological.length) : null
    output.set(key, {
      name: games[0].name,
      pos: latest.at(-1)?.pos || games[0].pos || '',
      team: latest.at(-1)?.team || games[0].team || '',
      games: games.length,
      season: latestSeason,
      ppg: mean,
      floor: quantile(values, 0.25),
      ceiling: quantile(values, 0.90),
      rate15: values.length ? values.filter((value) => value >= 15).length / values.length * 100 : null,
      boom25: values.length ? values.filter((value) => value >= 25).length / values.length * 100 : null,
      bust10: values.length ? values.filter((value) => value < 10).length / values.length * 100 : null,
      recent,
    })
  }
  return output
}

export async function GET(request: NextRequest) {
  const name = request.nextUrl.searchParams.get('player')?.trim() || ''
  if (!name) return NextResponse.json({ error: 'Player is required.' }, { status: 400 })
  try {
    evidencePromise ||= buildEvidence()
    const evidence = (await evidencePromise).get(normalizeName(name)) || null
    return NextResponse.json({ evidence })
  } catch (error) {
    evidencePromise = null
    return NextResponse.json({ evidence: null, error: error instanceof Error ? error.message : 'Historical evidence unavailable.' }, { status: 500 })
  }
}
