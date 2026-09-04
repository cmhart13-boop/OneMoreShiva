import { NextResponse } from 'next/server'

export const revalidate = 180

export async function GET() {
  try {
    const response = await fetch('https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard', {
      next: { revalidate: 180 },
      headers: { 'User-Agent': 'Mozilla/5.0 (One More Shiva)' },
    })
    if (!response.ok) throw new Error(`ESPN returned ${response.status}`)
    const data = await response.json()
    const games = (data.events || []).map((event: any) => {
      const competition = event.competitions?.[0] || {}
      const competitors = competition.competitors || []
      const statusType = event.status?.type || competition.status?.type || {}
      return {
        id: String(event.id || ''),
        name: String(event.name || event.shortName || ''),
        date: String(event.date || ''),
        status: String(statusType.shortDetail || statusType.description || statusType.name || ''),
        detail: String(statusType.detail || ''),
        completed: Boolean(statusType.completed),
        teams: competitors.map((item: any) => ({
          abbreviation: String(item.team?.abbreviation || ''),
          displayName: String(item.team?.displayName || item.team?.shortDisplayName || ''),
          homeAway: String(item.homeAway || ''),
          score: String(item.score ?? ''),
        })),
      }
    })
    return NextResponse.json({ games })
  } catch (error) {
    return NextResponse.json({ games: [], error: error instanceof Error ? error.message : 'Scoreboard unavailable.' }, { status: 502 })
  }
}
