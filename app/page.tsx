'use client'

import { useEffect, useMemo, useState } from 'react'
import AuthButton from '../components/AuthButton'
import CoachView from '../components/CoachView'
import DraftView from '../components/DraftView'
import EdgeRankingsView from '../components/EdgeRankingsView'
import GuideView from '../components/GuideView'
import ScoresView from '../components/ScoresView'
import type { NewsArticle } from '../lib/types'

type Tab = 'Home' | 'Draft' | 'Guide' | 'Scores'
type EdgeView = 'floor' | 'ceiling' | null

function HomeEdgeCards() {
  const [open, setOpen] = useState<EdgeView>(null)

  const toggle = (view: Exclude<EdgeView, null>) => setOpen((current) => current === view ? null : view)

  return <div className="home-edge-cards">
    <article className={`panel edge-panel${open === 'floor' ? ' expanded' : ''}`}>
      <div className="edge-panel-head">
        <div><h2 className="edge-title">Raise the Floor</h2><p className="edge-subtitle">Consistent 15+ scoring</p></div>
        <button type="button" className="edge-action edge-pill" aria-expanded={open === 'floor'} onClick={() => toggle('floor')}>See Floor Rankings →</button>
      </div>
      <div className="metric-row">
        <div><strong>Drake Maye</strong><span>QB · 20.7 PPG</span></div>
        <b>94%</b>
      </div>
      {open === 'floor' && <EdgeRankingsView mode="floor" inline />}
    </article>
    <article className={`panel edge-panel${open === 'ceiling' ? ' expanded' : ''}`}>
      <div className="edge-panel-head">
        <div><h2 className="edge-title">Keep the Ceiling</h2><p className="edge-subtitle">Week-winning upside</p></div>
        <button type="button" className="edge-action edge-pill" aria-expanded={open === 'ceiling'} onClick={() => toggle('ceiling')}>See Ceiling Rankings →</button>
      </div>
      <div className="metric-row">
        <div><strong>Christian McCaffrey</strong><span>RB · 24.5 PPG</span></div>
        <b>47%</b>
      </div>
      {open === 'ceiling' && <EdgeRankingsView mode="ceiling" inline />}
    </article>
  </div>
}

function HomeNews() {
  const [news, setNews] = useState<NewsArticle[]>([])

  useEffect(() => {
    fetch('/api/news')
      .then((response) => response.json())
      .then((data) => setNews(data.articles || []))
      .catch(() => setNews([]))
  }, [])

  const latestArticles = useMemo(() => news.slice(0, 6), [news])

  return <section className="home-news" aria-label="Latest ESPN football news">
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
              ? <img src={article.image} alt="" loading="lazy" decoding="async" />
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
  </section>
}

export default function ShivaApp() {
  const [tab, setTab] = useState<Tab>('Home')
  const [launching, setLaunching] = useState(true)
  const [testTheme, setTestTheme] = useState(false)

  useEffect(() => {
    const timer = window.setTimeout(() => setLaunching(false), 2500)
    setTestTheme(window.location.hostname.startsWith('shiva-vercel-native'))
    return () => window.clearTimeout(timer)
  }, [])

  return <>
    {launching && <div className="launch-screen" aria-label="Shiva loading"><img src="/shiva-trophy.png" alt="The Shiva trophy" /></div>}
    <main className={`app-shell${testTheme ? ' test-theme' : ''}`}>
      <header className="brand-header">
        <img src="/shiva-trophy.png" alt="The Shiva trophy" className="brand-trophy" />
        <div className="brand-copy"><div className="brand-name">Shiva</div><div className="brand-subtitle">FANTASY FOOTBALL INTELLIGENCE</div></div>
        <AuthButton />
      </header>

      <section className="content" key={tab}>
        {tab === 'Home' && <div className="home-coach"><CoachView /><HomeEdgeCards /><HomeNews /></div>}
        {tab === 'Draft' && <DraftView />}
        {tab === 'Guide' && <GuideView />}
        {tab === 'Scores' && <ScoresView />}
      </section>

      <nav className="bottom-nav" aria-label="Primary navigation">
        {(['Home','Draft','Guide','Scores'] as Tab[]).map((item) => {
          const isShiva = item === 'Home'
          const label = isShiva ? 'Shiva' : item
          return <button
            type="button"
            key={item}
            aria-label={label}
            className={`${tab === item ? 'active' : ''}${isShiva ? ' shiva-nav' : ''}`.trim()}
            onClick={() => { setTab(item); window.scrollTo({ top: 0, behavior:'instant' as ScrollBehavior }) }}
          >
            {isShiva
              ? <img src="/shiva-trophy.png" alt="" className="nav-trophy" />
              : <span className="nav-mark" aria-hidden="true">{item === 'Draft' ? 'D' : item === 'Guide' ? 'G' : 'S'}</span>}
            <span>{label}</span>
          </button>
        })}
      </nav>
    </main>
  </>
}
