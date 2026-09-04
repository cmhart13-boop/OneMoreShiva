import { NextRequest, NextResponse } from 'next/server'

const BASE = 'https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl'
const SLOT: Record<number, string> = { 0: 'QB', 2: 'RB', 4: 'WR', 6: 'TE', 16: 'DST', 17: 'K', 20: 'BE', 21: 'IR', 23: 'FLEX' }

function cookieHeader(swid?: string, espnS2?: string) {
  return [swid?.trim() ? `SWID=${swid.trim()}` : '', espnS2?.trim() ? `espn_s2=${espnS2.trim()}` : ''].filter(Boolean).join('; ')
}

async function espnJson(url: string, cookie = '', extraHeaders: Record<string, string> = {}) {
  const response = await fetch(url, {
    cache: 'no-store',
    headers: {
      Accept: 'application/json',
      'User-Agent': 'Mozilla/5.0 (One More Shiva; native fantasy client)',
      ...(cookie ? { Cookie: cookie } : {}),
      ...extraHeaders,
    },
  })
  if (!response.ok) throw new Error(`ESPN returned ${response.status}`)
  return response.json()
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const leagueId = String(body.leagueId || '').trim()
    const season = Number(body.season || 2026)
    const swid = String(body.swid || '')
    const espnS2 = String(body.espnS2 || '')
    if (!leagueId || !Number.isFinite(season)) return NextResponse.json({ error: 'League ID and season are required.' }, { status: 400 })

    const cookie = cookieHeader(swid, espnS2)
    const leagueUrl = `${BASE}/seasons/${season}/segments/0/leagues/${encodeURIComponent(leagueId)}`
    const views = ['mSettings', 'mTeam', 'mRoster', 'mStatus'].map((view) => `view=${view}`).join('&')
    const league = await espnJson(`${leagueUrl}?${views}`, cookie)
    if (!Array.isArray(league?.teams) || !league.teams.length) throw new Error('No teams were returned. Check the league ID, season, and private-league credentials.')

    const members = new Map((league.members || []).map((member: any) => [String(member.id), member]))
    const teams: any[] = []
    const roster: any[] = []
    for (const team of league.teams || []) {
      const id = Number(team.id || 0)
      const owners = (team.owners || []).map((ownerId: unknown) => {
        const member: any = members.get(String(ownerId)) || {}
        return `${member.firstName || ''} ${member.lastName || ''}`.trim()
      }).filter(Boolean)
      const name = `${team.location || ''} ${team.nickname || ''}`.trim() || team.name || `Team ${id}`
      teams.push({
        id,
        name,
        owners,
        wins: team.record?.overall?.wins ?? null,
        losses: team.record?.overall?.losses ?? null,
      })
      for (const entry of team.roster?.entries || []) {
        const pool = entry.playerPoolEntry || {}
        const player = pool.player || {}
        const slotId = Number(entry.lineupSlotId ?? 20)
        roster.push({
          teamId: id,
          team: name,
          playerId: String(player.id || ''),
          player: String(player.fullName || ''),
          slotId,
          slot: SLOT[slotId] || String(slotId),
          proTeamId: player.proTeamId ?? null,
          injuryStatus: player.injuryStatus || '',
          percentOwned: pool.percentOwned ?? null,
          percentStarted: pool.percentStarted ?? null,
        })
      }
    }

    let freeAgents: any[] = []
    try {
      const filter = {
        players: {
          filterStatus: { value: ['FREEAGENT', 'WAIVERS'] },
          limit: 300,
          sortPercOwned: { sortPriority: 1, sortAsc: false },
        },
      }
      const pool = await espnJson(`${leagueUrl}?view=kona_player_info`, cookie, { 'x-fantasy-filter': JSON.stringify(filter) })
      freeAgents = (pool?.players || []).map((outer: any) => {
        const ppe = outer?.playerPoolEntry || outer || {}
        const player = ppe.player || {}
        return {
          playerId: String(player.id || ''),
          player: String(player.fullName || ''),
          status: String(ppe.status || outer?.status || ''),
          proTeamId: player.proTeamId ?? null,
          injuryStatus: player.injuryStatus || '',
          percentOwned: ppe.percentOwned ?? null,
          percentStarted: ppe.percentStarted ?? null,
        }
      }).filter((row: any) => row.player)
    } catch {
      freeAgents = []
    }

    return NextResponse.json({
      league: {
        id: String(league.id || leagueId),
        season: Number(league.seasonId || season),
        name: String(league.settings?.name || 'ESPN League'),
        scoringPeriod: league.status?.currentScoringPeriod ?? null,
        matchupPeriod: league.status?.currentMatchupPeriod ?? null,
      },
      teams,
      roster,
      freeAgents,
    })
  } catch (error) {
    const message = error instanceof Error ? error.message : 'ESPN connection failed.'
    return NextResponse.json({ error: message }, { status: 502 })
  }
}
