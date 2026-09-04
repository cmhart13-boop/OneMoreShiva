'use client'

import { useEffect, useMemo, useState } from 'react'
import type { NewsArticle } from '../lib/types'

type ScoreTeam = {
  abbreviation: string
  displayName: string
  homeAway: string
  score: string
}

type ScoreGame = {
  id: string
  name: string
  date: string
  status: string
  detail: string
  completed: boolean
  teams: ScoreTeam[]
}

export default function ScoresView() {
  const [news, setNews] = useState<NewsArticle[]>([])
  const [games, setGames] = useState<ScoreGame[]>([])

  useEffect(() => {
    fetch('/api/news')
      .then((response) => response.json())
      .then((data) => setNews(data.articles || []))
      .catch(() => setNews([]))

    fetch('/api/scoreboard')
      .then((response) => response.json())
      .then((data) => setGames(data.games || []))
      .catch(() => setGames([]))
  }, [])

  const latestArticles = useMemo(() => news.slice(0, 4), [news])

  return <>
    <h1>Scores</h1>
    <p className="lede">NFL scores and the latest ESPN football news.</p>

    <div className="section-heading scores-heading"><h2>NFL Scores</h2></div>
    {games.length > 0 ? (
      <div className="score-list">
        {games.map((game) => {
          const away = game.teams.find((team) => team.homeAway === 'away') || game.teams[0]
          const home = game.teams.find((team) => team.homeAway === 'home') || game.teams[1]
          return <article className="panel score-card" key={game.id}>
            <div className="score-status"><span>{game.status || 'NFL'}</span><b>{game.detail}</b></div>
            <div className="score-team"><strong>{away?.displayName || game.name}</strong><b>{away?.score || '—'}</b></div>
            <div className="score-team"><strong>{home?.displayName || ''}</strong><b>{home?.score || '—'}</b></div>
          </article>
        })}
      </div>
    ) : <div className="panel loading-panel">Loading NFL scores…</div>}

    <div className="section-heading shiva-blast-heading"><h2>Latest ESPN</h2></div>
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
