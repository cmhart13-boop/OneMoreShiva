import { createReadStream } from 'node:fs'
import path from 'node:path'
import { createGunzip } from 'node:zlib'
import { createInterface } from 'node:readline'
import { NextRequest, NextResponse } from 'next/server'
import { normalizeName } from '../../../lib/csv'

type Row = Record<string, string>
type Game = { name: string; pos: string; team: string; season: number; week: number; pts: number }
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

const cache = new Map<string, Evidence | null>()

function parseLine(line: string) {
  const fields: string[] = []
  let field = ''
  let quoted = false
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i]
    if (quoted) {
      if (ch === '"') {
        if (line[i + 1] === '"') { field += '"'; i += 1 } else quoted = false
      } else field += ch
    } else if (ch === '"') quoted = true
    else if (ch === ',') { fields.push(field); field = '' }
    else field += ch
  }
  fields.push(field)
  return fields
}

function rowFrom(headers: string[], values: string[]): Row {
  const row: Row = {}
  for (let i = 0; i < headers.length; i += 1) row[headers[i]] = values[i] ?? ''
  return row
}

function n(row: Row, ...keys: string[]) {
  for (const key of keys) {
    const raw = row[key]
    if (raw === undefined || raw === '') continue
    const value = Number(raw)
    if (Number.isFinite(value)) return value
  }
  return 0
}

function str(row: Row, ...keys: string[]) {
  for (const key of keys) if (row[key]) return String(row[key])
  return ''
}

function ppr(row: Row): number | null {
  const directRaw = row.fantasy_points_ppr || row.fantasy_points_ppr_total
  const direct = directRaw === undefined || directRaw === '' ? Number.NaN : Number(directRaw)
  if (Number.isFinite(direct)) return direct
  const recognizable = ['passing_yards','passing_tds','rushing_yards','rushing_tds','receptions','receiving_yards','receiving_tds'].some((key) => row[key] !== undefined)
  if (!recognizable) return null
  const twoPoint = n(row, 'passing_2pt_conversions') + n(row, 'rushing_2pt_conversions') + n(row, 'receiving_2pt_conversions') + n(row, 'two_point_conversions')
  return n(row,'passing_yards')*.04 + n(row,'passing_tds')*4 - n(row,'interceptions')*2 + n(row,'rushing_yards')*.1 + n(row,'rushing_tds')*6 + n(row,'receptions') + n(row,'receiving_yards')*.1 + n(row,'receiving_tds')*6 + n(row,'return_tds')*6 + twoPoint*2 - n(row,'fumbles_lost')*2
}

function quantile(sorted: number[], q: number) {
  if (!sorted.length) return null
  const index = (sorted.length - 1) * q
  const lo = Math.floor(index), hi = Math.ceil(index)
  return lo === hi ? sorted[lo] : sorted[lo] + (sorted[hi] - sorted[lo]) * (index - lo)
}

async function evidenceFor(targetName: string): Promise<Evidence | null> {
  const key = normalizeName(targetName)
  if (cache.has(key)) return cache.get(key) ?? null

  const source = createReadStream(path.join(process.cwd(), 'player_weekly_master_2014_2025.csv.gz'))
  const gunzip = createGunzip()
  const lines = createInterface({ input: source.pipe(gunzip), crlfDelay: Infinity })
  let headers: string[] | null = null
  const games: Game[] = []

  for await (const line of lines) {
    if (!headers) { headers = parseLine(line).map((value) => value.trim()); continue }
    if (!line) continue
    const row = rowFrom(headers, parseLine(line))
    const name = str(row, 'player_display_name', 'player_name', 'player', 'name')
    if (!name || normalizeName(name) !== key) continue
    const season = Number(str(row, 'season', 'year'))
    const week = Number(str(row, 'week'))
    const pts = ppr(row)
    if (!Number.isFinite(season) || !Number.isFinite(week) || week < 1 || week > 18 || pts === null || !Number.isFinite(pts)) continue
    games.push({ name, pos: str(row,'position','pos'), team: str(row,'recent_team','team','posteam'), season, week, pts })
  }

  if (!games.length) { cache.set(key, null); return null }
  const latestSeason = Math.max(...games.map((game) => game.season))
  const latest = games.filter((game) => game.season === latestSeason).sort((a,b) => a.week - b.week)
  const values = latest.map((game) => game.pts).sort((a,b) => a - b)
  const chronological = latest.map((game) => game.pts)
  const evidence: Evidence = {
    name: games[0].name,
    pos: latest.at(-1)?.pos || games[0].pos || '',
    team: latest.at(-1)?.team || games[0].team || '',
    games: games.length,
    season: latestSeason,
    ppg: values.reduce((sum,value) => sum + value, 0) / values.length,
    floor: quantile(values,.25),
    ceiling: quantile(values,.90),
    rate15: values.filter((value) => value >= 15).length / values.length * 100,
    boom25: values.filter((value) => value >= 25).length / values.length * 100,
    bust10: values.filter((value) => value < 10).length / values.length * 100,
    recent: chronological.slice(-4).reduce((sum,value) => sum + value, 0) / Math.min(4, chronological.length),
  }
  cache.set(key, evidence)
  return evidence
}

export async function GET(request: NextRequest) {
  const name = request.nextUrl.searchParams.get('player')?.trim() || ''
  if (!name) return NextResponse.json({ error: 'Player is required.' }, { status: 400 })
  try {
    return NextResponse.json({ evidence: await evidenceFor(name) })
  } catch (error) {
    return NextResponse.json({ evidence: null, error: error instanceof Error ? error.message : 'Historical evidence unavailable.' }, { status: 500 })
  }
}
