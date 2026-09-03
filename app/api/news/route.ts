import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { NextRequest, NextResponse } from 'next/server'

export const revalidate = 300

type Article = { headline: string; description: string; published: string; url: string; image: string }

function filterArticles(articles: Article[], player: string) {
  const terms = player ? [player, player.split(/\s+/).at(-1) || ''].filter(Boolean) : []
  return articles.filter((article) => {
    if (!terms.length) return true
    const text = `${article.headline || ''} ${article.description || ''}`.toLowerCase()
    return terms.some((term) => text.includes(term))
  }).slice(0, player ? 10 : 24)
}

async function localArticles(): Promise<Article[]> {
  const raw = await readFile(path.join(process.cwd(), 'data', 'live_news.json'), 'utf8')
  const data = JSON.parse(raw)
  return (data.articles || []).map((article: any) => ({
    headline: String(article.headline || ''),
    description: String(article.description || ''),
    published: String(article.published || ''),
    url: String(article.url || ''),
    image: String(article.image || ''),
  }))
}

export async function GET(request: NextRequest) {
  const player = request.nextUrl.searchParams.get('player')?.trim().toLowerCase() || ''
  try {
    const response = await fetch('https://site.web.api.espn.com/apis/site/v2/sports/football/nfl/news?region=us&lang=en&contentorigin=espn&limit=100', {
      next: { revalidate: 300 },
      headers: {
        Accept: 'application/json, text/plain, */*',
        Referer: 'https://www.espn.com/',
        Origin: 'https://www.espn.com',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1',
      },
    })
    if (!response.ok) throw new Error(`ESPN returned ${response.status}`)
    const data = await response.json()
    const articles: Article[] = (data.articles || []).map((article: any) => ({
      headline: String(article.headline || ''),
      description: String(article.description || ''),
      published: String(article.published || article.lastModified || ''),
      url: article.links?.web?.href || article.links?.mobile?.href || article.url || '',
      image: article.images?.[0]?.url || article.image || '',
    }))
    return NextResponse.json({ articles: filterArticles(articles, player), source: 'espn-live' })
  } catch {
    try {
      const articles = await localArticles()
      return NextResponse.json({ articles: filterArticles(articles, player), source: 'last-verified-espn' })
    } catch (error) {
      return NextResponse.json({ articles: [], error: error instanceof Error ? error.message : 'News unavailable.' }, { status: 502 })
    }
  }
}
