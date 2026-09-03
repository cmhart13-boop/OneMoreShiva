import { NextRequest, NextResponse } from 'next/server'

export const revalidate = 300

export async function GET(request: NextRequest) {
  try {
    const player = request.nextUrl.searchParams.get('player')?.trim().toLowerCase() || ''
    const response = await fetch('https://site.api.espn.com/apis/site/v2/sports/football/nfl/news?limit=100', {
      next: { revalidate: 300 },
      headers: { 'User-Agent': 'Mozilla/5.0 (One More Shiva)' },
    })
    if (!response.ok) throw new Error(`ESPN returned ${response.status}`)
    const data = await response.json()
    const terms = player ? [player, player.split(/\s+/).at(-1) || ''].filter(Boolean) : []
    const articles = (data.articles || []).filter((article: any) => {
      if (!terms.length) return true
      const text = `${article.headline || ''} ${article.description || ''}`.toLowerCase()
      return terms.some((term) => text.includes(term))
    }).slice(0, player ? 10 : 24).map((article: any) => ({
      headline: String(article.headline || ''),
      description: String(article.description || ''),
      published: String(article.published || article.lastModified || ''),
      url: article.links?.web?.href || article.links?.mobile?.href || '',
      image: article.images?.[0]?.url || '',
    }))
    return NextResponse.json({ articles })
  } catch (error) {
    return NextResponse.json({ articles: [], error: error instanceof Error ? error.message : 'News unavailable.' }, { status: 502 })
  }
}
