import { NextRequest, NextResponse } from 'next/server'

const accessCookie = 'shiva-access-token'

function config() {
  const url = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL
  const key = process.env.SUPABASE_ANON_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
  if (!url || !key) throw new Error('Shiva accounts are not configured yet.')
  return { url: url.replace(/\/$/, ''), key }
}

async function sessionUser(request: NextRequest) {
  const access = request.cookies.get(accessCookie)?.value
  if (!access) return null
  const { url, key } = config()
  const response = await fetch(`${url}/auth/v1/user`, {
    headers: { apikey: key, Authorization: `Bearer ${access}` },
    cache: 'no-store',
  })
  if (!response.ok) return null
  const user = await response.json()
  return user?.id ? { id: String(user.id), access } : null
}

async function db(path: string, access: string, init: RequestInit = {}) {
  const { url, key } = config()
  return fetch(`${url}/rest/v1/${path}`, {
    ...init,
    headers: {
      apikey: key,
      Authorization: `Bearer ${access}`,
      'Content-Type': 'application/json',
      ...(init.headers || {}),
    },
    cache: 'no-store',
  })
}

async function apiError(response: Response) {
  const data = await response.json().catch(() => ({}))
  return NextResponse.json({ error: data?.message || data?.hint || 'League account request failed.' }, { status: response.status || 400 })
}

export async function GET(request: NextRequest) {
  try {
    const user = await sessionUser(request)
    if (!user) return NextResponse.json({ error: 'Sign in required.' }, { status: 401 })
    const response = await db('user_leagues?select=id,league_id,season,nickname,team_id,league_name,team_name,created_at&order=created_at.asc', user.access)
    if (!response.ok) return apiError(response)
    return NextResponse.json({ leagues: await response.json() })
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : 'League account service unavailable.' }, { status: 503 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const user = await sessionUser(request)
    if (!user) return NextResponse.json({ error: 'Sign in required.' }, { status: 401 })
    const body = await request.json().catch(() => ({}))
    const leagueId = String(body?.leagueId || '').trim()
    const season = Number(body?.season || 2026)
    const nickname = String(body?.nickname || '').trim() || null
    const teamId = Number.isFinite(Number(body?.teamId)) ? Number(body.teamId) : null
    const leagueName = String(body?.leagueName || '').trim() || null
    const teamName = String(body?.teamName || '').trim() || null
    if (!leagueId || !Number.isInteger(season)) return NextResponse.json({ error: 'League ID and season are required.' }, { status: 400 })

    const response = await db('user_leagues?on_conflict=user_id,league_id,season', user.access, {
      method: 'POST',
      headers: { Prefer: 'resolution=merge-duplicates,return=representation' },
      body: JSON.stringify({ user_id: user.id, league_id: leagueId, season, nickname, team_id: teamId, league_name: leagueName, team_name: teamName, updated_at: new Date().toISOString() }),
    })
    if (!response.ok) return apiError(response)
    const rows = await response.json()
    return NextResponse.json({ league: rows?.[0] ?? null })
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : 'League account service unavailable.' }, { status: 503 })
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const user = await sessionUser(request)
    if (!user) return NextResponse.json({ error: 'Sign in required.' }, { status: 401 })
    const id = new URL(request.url).searchParams.get('id')
    if (!id) return NextResponse.json({ error: 'League record ID is required.' }, { status: 400 })
    const response = await db(`user_leagues?id=eq.${encodeURIComponent(id)}`, user.access, { method: 'DELETE' })
    if (!response.ok) return apiError(response)
    return NextResponse.json({ ok: true })
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : 'League account service unavailable.' }, { status: 503 })
  }
}
