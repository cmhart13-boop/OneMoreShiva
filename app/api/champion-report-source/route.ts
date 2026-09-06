import { NextResponse } from 'next/server'

const BASE = 'https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl'
const LEAGUES = [
  { label: 'Shiva', id: '1465338' },
  { label: 'Shiva 2.0', id: '1506903' },
]

async function fetchSeason(leagueId: string, season: number) {
  const url = `${BASE}/seasons/${season}/segments/0/leagues/${leagueId}?view=mSettings&view=mTeam&view=mDraftDetail&view=mStandings&view=mMatchup`
  const r = await fetch(url, {
    cache: 'no-store',
    headers: { Accept: 'application/json', 'User-Agent': 'Mozilla/5.0 Shiva historical report' },
  })
  if (!r.ok) throw new Error(`ESPN ${r.status}`)
  return r.json()
}

function compactTeam(t: any) {
  return {
    id: t?.id ?? null,
    name: [t?.location, t?.nickname].filter(Boolean).join(' ').trim() || t?.name || t?.abbrev || '',
    abbrev: t?.abbrev || '',
    owners: t?.owners || [],
    rankCalculatedFinal: t?.rankCalculatedFinal ?? null,
    playoffSeed: t?.playoffSeed ?? null,
    finalStandingsPosition: t?.finalStandingsPosition ?? null,
    points: t?.record?.overall?.pointsFor ?? null,
    wins: t?.record?.overall?.wins ?? null,
    losses: t?.record?.overall?.losses ?? null,
  }
}

export async function GET() {
  const out: any[] = []
  for (const league of LEAGUES) {
    for (let season = 2014; season <= 2025; season++) {
      try {
        const j = await fetchSeason(league.id, season)
        const teams = Array.isArray(j?.teams) ? j.teams.map(compactTeam) : []
        const picks = Array.isArray(j?.draftDetail?.picks) ? j.draftDetail.picks.map((p: any) => ({
          roundId: p?.roundId ?? null,
          roundPickNumber: p?.roundPickNumber ?? null,
          overallPickNumber: p?.overallPickNumber ?? null,
          teamId: p?.teamId ?? null,
          playerId: p?.playerId ?? null,
          keeper: p?.keeper ?? false,
          autoDraftTypeId: p?.autoDraftTypeId ?? null,
        })) : []
        const members = Array.isArray(j?.members) ? j.members.map((m: any) => ({
          id: m?.id ?? null,
          displayName: m?.displayName ?? '',
          firstName: m?.firstName ?? '',
          lastName: m?.lastName ?? '',
        })) : []
        out.push({
          league: league.label,
          leagueId: league.id,
          season,
          name: j?.settings?.name || '',
          teamCount: teams.length,
          teams,
          members,
          picks,
          draftComplete: j?.draftDetail?.drafted ?? null,
          status: 'ok',
        })
      } catch (e) {
        out.push({ league: league.label, leagueId: league.id, season, status: 'error', error: e instanceof Error ? e.message : String(e) })
      }
    }
  }
  return NextResponse.json({ generatedAt: new Date().toISOString(), seasons: out })
}
