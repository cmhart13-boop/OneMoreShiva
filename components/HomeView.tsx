'use client'

import { useEffect, useMemo, useState } from 'react'
import type { NewsArticle } from '../lib/types'

export default function HomeView() {
  const [news, setNews] = useState<NewsArticle[]>([])

  useEffect(() => {
    fetch('/api/news')
      .then((response) => response.json())
      .then((data) => setNews(data.articles || []))
      .catch(() => setNews([]))
  }, [])

  const latestArticles = useMemo(() => news.slice(0, 4), [news])

  return <>
    <div className="section-kicker">SHIVA EDGE</div>
    <h1>Shiva Edge</h1>
    <p className="lede">Historical evidence, not a mystery score.</p>

    <div className="edge-grid">
      <article className="panel edge-panel">
        <h2 className="edge-title">Raise the Floor</h2>
        <p className="edge-subtitle">Consistent 15+ scoring</p>
        <div className="metric-row">
          <div><strong>Drake Maye</strong><span>QB · 20.7 PPG</span></div>
          <b>94%</b>
        </div>
        <button type="button">Floor Rankings →</button>
      </article>

      <article className="panel edge-panel">
        <h2 className="edge-title">Keep the Ceiling</h2>
        <p className="edge-subtitle">Week-winning upside</p>
        <div className="metric-row">
          <div><strong>Christian McCaffrey</strong><span>RB · 24.5 PPG</span></div>
          <b>47%</b>
        </div>
        <button type="button">Ceiling Rankings →</button>
      </article>
    </div>

    <div className="section-heading shiva-blast-heading"><h2>Shiva Blast</h2></div>

    {latestArticles.length > 0 ? (
      <div className="blast-list">
        {latestArticles.map((article) => (
          <a
            className="blast-card"
            href={article.url || '#'}
            target={article.url ? '_blank' : undefined}
            rel="noreferrer"
            key={`${article.published || ''}-${article.headline}`}
          >
            {article.image
              ? <img src={article.image} alt="" />
              : <div className="blast-fallback" aria-hidden="true" />}
            <div className="blast-copy">
              <b>{article.headline}</b>
              <p>{article.description}</p>
              <span>{article.url ? 'Open story →' : 'ESPN story'}</span>
            </div>
          </a>
        ))}
      </div>
    ) : <div className="panel loading-panel">Loading ESPN articles…</div>}
  </>
}
