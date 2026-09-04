import { createReadStream } from 'node:fs'
import path from 'node:path'
import { createGunzip } from 'node:zlib'
import { createInterface } from 'node:readline'
import { readFile } from 'node:fs/promises'
import { NextResponse } from 'next/server'
import { normalizeName, numberOrNull, parseCsv } from '../../../lib/csv'

type Row = Record<string, string>
type Weekly = { name: string; pos: string; team: string; season: number; week: number; pts: number }

type EdgeRow = {
  id: string
  name: string
  team: string
  pos: string
  rank: number
  adp: number | null
  season: number
  ppg: number
  floor: number
  ceiling: number
  rate15: number
  boom25: number
}

let cached: EdgeRow[] | null = null

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

function rowFrom(headers: string[], values: string[]) {
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
  const index = (sorted.length - 1) * q
  const lo = Math.floor(index), hi = Math.ceil(index)
  return lo === hi ? sorted[lo] : sorted[lo] + (sorted[hi] - sorted[lo]) * (index - lo)
}

async function buildRows() {
  const rankingsCsv = await readFile(path.join(process.cwd(), 'current_rankings.csv'), 'utf8')
  const rankings = parseCsv(rankingsCsv).map((row, index) => ({
    name: row.player_name,
    key: normalizeName(row.player_name || ''),
    team: row.team || '',
    pos: (row.position || '').toUpperCase(),
    rank: numberOrNull(row.overall_rank) ?? index + 1,
    adp: numberOrNull(row.adp),
  })).filter((row) => row.name && ['QB','RB','WR','TE'].includes(row.pos))

  const source = createReadStream(path.join(process.cwd(), 'player_weekly_master_2014_2025.csv.gz'))
  const lines = createInterface({ input: source.pipe(createGunzip()), crlfDelay: Infinity })
  let headers: string[] | null = null
  const byPlayer = new Map<string, Weekly[]>()

  for await (const line of lines) {
    if (!headers) { headers = parseLine(line).map((value) => value.trim()); continue }
    if (!line) continue
    const row = rowFrom(headers, parseLine(line))
    const name = str(row, 'player_display_name', 'player_name', 'player', 'name')
    const key = normalizeName(name)
    if (!key) continue
    const season = Number(str(row, 'season', 'year'))
    const week = Number(str(row, 'week'))
    const pts = ppr(row)
    if (!Number.isFinite(season) || !Number.isFinite(week) || week < 1 || week > 18 || pts === null || !Number.isFinite(pts)) continue
    const list = byPlayer.get(key) || []
    list.push({ name, pos: str(row,'position','pos'), team: str(row,'recent_team','team','posteam'), season, week, pts })
    byPlayer.set(key, list)
  }

  return rankings.flatMap((ranked) => {
    const games = byPlayer.get(ranked.key) || []
    if (!games.length) return []
    const latestSeason = Math.max(...games.map((game) => game.season))
    const latest = games.filter((game) => game.season === latestSeason)
    if (latest.length < 4) return []
    const values = latest.map((game) => game.pts).sort((a,b) => a - b)
    const ppg = values.reduce((sum, value) => sum + value, 0) / values.length
    return [{
      id: `${ranked.pos}-${ranked.rank}-${ranked.name}`.replace(/[^a-zA-Z0-9-]/g, '-'),
      name: ranked.name,
      team: ranked.team || latest.at(-1)?.team || '',
      pos: ranked.pos,
      rank: ranked.rank,
      adp: ranked.adp,
      season: latestSeason,
      ppg,
      floor: quantile(values, .25),
      ceiling: quantile(values, .90),
      rate15: values.filter((value) => value >= 15).length / values.length * 100,
      boom25: values.filter((value) => value >= 25).length / values.length * 100,
    }]
  })
}

export async function GET() {
  try {
    if (!cached) cached = await buildRows()
    return NextResponse.json({ players: cached })
  } catch (error) {
    return NextResponse.json({ players: [], error: error instanceof Error ? error.message : 'Edge rankings unavailable.' }, { status: 500 })
  }
}
