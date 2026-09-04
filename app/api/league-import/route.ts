import { NextRequest, NextResponse } from 'next/server'
import { importSleeperLeague } from '../../../lib/league-adapters/sleeper'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}))
    const provider = String(body.provider || 'espn').toLowerCase()
    const leagueId = String(body.leagueId || '').trim()
    if (!leagueId) return NextResponse.json({ error:'League ID is required.' }, { status:400 })
    if (provider === 'espn') {
      const url = new URL('/api/espn', request.url)
      const response = await fetch(url, { method:'POST', headers:{ 'Content-Type':'application/json', cookie:request.headers.get('cookie') || '' }, body:JSON.stringify(body) })
      return NextResponse.json(await response.json(), { status:response.status })
    }
    if (provider === 'sleeper') return NextResponse.json(await importSleeperLeague(leagueId))
    return NextResponse.json({ error:'Choose ESPN or Sleeper.' }, { status:400 })
  } catch (error) {
    return NextResponse.json({ error:error instanceof Error ? error.message : 'League import failed.' }, { status:502 })
  }
}
