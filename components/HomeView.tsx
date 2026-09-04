'use client'

import { useEffect, useMemo, useState } from 'react'
import type { NewsArticle } from '../lib/types'

function Countdown() {
  const [now, setNow] = useState<number | null>(null)
  useEffect(() => {
    const tick = () => setNow(Date.now())
    tick()
    const timer = window.setInterval(tick, 1000)
    return () => window.clearInterval(timer)
  }, [])
  const target = new Date('2026-09-09T20:00:00-04:00').getTime()
  if (now === null) {
    return <div className="countdown"><span>WEEK 1 COUNTDOWN</span><b>--d --h --m --s</b></div>
  }
  const distance = Math.max(0, target - now)
  const days = Math.floor(distance / 86400000)
  const hours = Math.floor((distance % 86400000) / 3600000)
  const minutes = Math.floor((distance % 3600000) / 60000)
  const seconds = Math.floor((distance % 60000) / 1000)
  if (!distance) return null
  return <div className="countdown"><span>WEEK 1 COUNTDOWN</span><b>{days}d {hours}h {minutes}m {seconds}s</b></div>
}

export default function HomeView() {
  const [news, setNews] = useState<NewsArticle[]>([])
  useEffect(() => {
    fetch('/api/news').then((response) => response.json()).then((data) => setNews(data.articles || [])).catch(() => setNews([]))
  }, [])
  const feature = useMemo(() => news.find((article) => article.image) || news[0], [news])

  return <>
    <Countdown />
    <div className="section-kicker">THE SHIVA EDGE</div>
    <h1>The Shiva Edge</h1>
    <p className="lede">Historical evidence, not a mystery score.</p>
    <div className="edge-grid">
      <article className="panel edge-panel">
        <div className="eyebrow">RAISE THE FLOOR</div>
        <h2>Consistent 15+ scoring</h2>
        <div className="metric-row"><div><strong>Drake Maye</strong><span>QB · 20.7 PPG</span></div><b>94%</b></div>
        <button type="button">Floor Rankings →</button>
      </article>
      <article className="panel edge-panel">
        <div className="eyebrow">KEEP THE CEILING</div>
        <h2>Week-winning upside</h2>
        <div className="metric-row"><div><strong>Christian McCaffrey</strong><span>RB · 24.5 PPG</span></div><b>47%</b></div>
        <button type="button">Ceiling Rankings →</button>
      </article>
    </div>

    <div className="section-heading"><div><div className="section-kicker">CURRENT CONTEXT</div><h2>Shiva Blast</h2></div><span className="live-dot">LIVE ESPN</span></div>
    {feature ? <a className="blast-card" href={feature.url || '#'} target={feature.url ? '_blank' : undefined} rel="noreferrer">
      {feature.image ? <img src={feature.image} alt="" /> : <div className="blast-fallback" />}
      <div className="blast-copy"><b>{feature.headline}</b><p>{feature.description}</p><span>{feature.url ? 'Open story →' : 'Current ESPN context'}</span></div>
    </a> : <div className="panel loading-panel">Loading current ESPN context…</div>}

    {news.length > 1 && <div className="news-strip">{news.slice(1, 4).map((article) => <a href={article.url || '#'} target="_blank" rel="noreferrer" key={article.headline}><span>ESPN</span><b>{article.headline}</b></a>)}</div>}
  </>
}
