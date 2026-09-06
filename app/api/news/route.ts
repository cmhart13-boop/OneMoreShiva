import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { NextRequest, NextResponse } from 'next/server'

export const revalidate = 300

type Article = { headline: string; description: string; published: string; url: string; image: string }

const FANTASY_TERMS = [
  'fantasy','start','sit','waiver','injury','inactive','questionable','doubtful','out','depth chart','starter','starting','touches','targets','snaps','running back','wide receiver','quarterback','tight end','rookie','trade','breakout','sleeper','projection'
]

function normalizeText(value: string) {
  return value.toLowerCase().replace(/[’']/g, "'").replace(/[^a-z0-9' -]+/g, ' ').replace(/\s+/g, ' ').trim()
}

function articleScore(article:Article){
  const text=normalizeText(`${article.headline || ''} ${article.description || ''}`)
  let score=0
  for(const term of FANTASY_TERMS)if(text.includes(term))score+=term==='fantasy'?8:2
  const published=new Date(article.published).getTime()
  if(Number.isFinite(published)){
    const ageHours=Math.max(0,(Date.now()-published)/3600000)
    score+=Math.max(0,8-ageHours/12)
  }
  if(article.image)score+=1
  return score
}

function filterArticles(articles: Article[], player: string, fantasy:boolean, limit:number) {
  const fullName = normalizeText(player)
  let rows=articles.filter((article) => {
    if (!fullName) return true
    const text = normalizeText(`${article.headline || ''} ${article.description || ''}`)
    return text.includes(fullName)
  })
  if(fantasy)rows=[...rows].sort((a,b)=>articleScore(b)-articleScore(a))
  return rows.slice(0,limit)
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
  const fantasy = request.nextUrl.searchParams.get('fantasy') === '1'
  const requestedLimit=Number(request.nextUrl.searchParams.get('limit')||'')
  const limit=Number.isFinite(requestedLimit)&&requestedLimit>0?Math.min(24,Math.floor(requestedLimit)):(player?10:24)
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
    })).filter((article:Article)=>article.headline&&article.url)
    return NextResponse.json({ articles: filterArticles(articles, player, fantasy, limit), source: 'espn-live' })
  } catch {
    try {
      const articles = await localArticles()
      return NextResponse.json({ articles: filterArticles(articles, player, fantasy, limit), source: 'last-verified-espn' })
    } catch (error) {
      return NextResponse.json({ articles: [], error: error instanceof Error ? error.message : 'News unavailable.' }, { status: 502 })
    }
  }
}
