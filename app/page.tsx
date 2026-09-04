'use client'

import { useEffect, useMemo, useState } from 'react'
import AuthButton from '../components/AuthButton'
import CoachHub from '../components/CoachHub'
import CoachView from '../components/CoachView'
import EdgeRankingsView from '../components/EdgeRankingsView'
import GuideView from '../components/GuideView'
import { PlayerAvatar } from '../components/PlayerMedia'
import RosterUpdates from '../components/RosterUpdates'
import ScoresView from '../components/ScoresView'
import type { NewsArticle } from '../lib/types'

type Tab = 'Home' | 'Coach' | 'Guide' | 'Scores'
type EdgeView = 'floor' | 'ceiling' | null
type HomeEdgePlayer = {
  id: string
  espnId?: string
  name: string
  team: string
  pos: string
  rank: number
  ppg: number
  floor: number
  ceiling: number
  rate15: number
  boom25: number
}

function readRosterNames() {
  try {
    const storedLeague = window.sessionStorage.getItem('shiva-league')
    const storedTeam = window.sessionStorage.getItem('shiva-team-id')
    if (!storedLeague || !storedTeam) return [] as string[]
    const league = JSON.parse(storedLeague)
    const teamId = Number(storedTeam)
    return (league?.roster || [])
      .filter((row: any) => Number(row.teamId) === teamId && typeof row.player === 'string')
      .map((row: any) => row.player as string)
  } catch {
    return [] as string[]
  }
}

function HomeEdgeCards() {
  const [open, setOpen] = useState<EdgeView>(null)
  const [players, setPlayers] = useState<HomeEdgePlayer[]>([])
  const [rosterNames, setRosterNames] = useState<string[]>([])

  useEffect(() => {
    fetch('/api/edges')
      .then((response) => response.json())
      .then((data) => setPlayers(data.players || []))
      .catch(() => setPlayers([]))
  }, [])

  useEffect(() => {
    const refreshRoster = () => {
      const next = readRosterNames()
      setRosterNames((current) => current.join('|') === next.join('|') ? current : next)
    }
    refreshRoster()
    const timer = window.setInterval(refreshRoster, 900)
    return () => window.clearInterval(timer)
  }, [])

  const scopedPlayers = useMemo(() => {
    if (!rosterNames.length) return players
    const rosterSet = new Set(rosterNames.map((name) => name.toLowerCase()))
    return players.filter((player) => rosterSet.has(player.name.toLowerCase()))
  }, [players, rosterNames])

  const floorPlayers = useMemo(() => [...scopedPlayers]
    .sort((a, b) => b.floor - a.floor || b.rate15 - a.rate15 || a.rank - b.rank)
    .slice(0, 3), [scopedPlayers])
  const ceilingPlayers = useMemo(() => [...scopedPlayers]
    .sort((a, b) => b.ceiling - a.ceiling || b.boom25 - a.boom25 || a.rank - b.rank)
    .slice(0, 3), [scopedPlayers])

  const toggle = (view: Exclude<EdgeView, null>) => setOpen((current) => current === view ? null : view)
  const preview = (rows: HomeEdgePlayer[], mode: Exclude<EdgeView, null>) => rows.length
    ? <div className="edge-preview-list">{rows.map((player) => <div className="edge-preview-row" key={`${mode}-${player.id}`}>
        <PlayerAvatar playerId={player.espnId || player.id} name={player.name} />
        <strong>{player.name}</strong>
        <span>{player.pos} · {player.ppg.toFixed(1)} PPG</span>
        <b>{Math.round(mode === 'floor' ? player.rate15 : player.boom25)}%</b>
      </div>)}</div>
    : <div className="edge-preview-loading">Loading rankings…</div>

  return <div className="home-edge-cards">
    <article className={`panel edge-panel${open === 'floor' ? ' expanded' : ''}`}>
      <div className="edge-panel-head">
        <div><h2 className="edge-title">Raise the Floor</h2><p className="edge-subtitle">Consistent 15+ PPG scoring</p></div>
      </div>
      {preview(floorPlayers, 'floor')}
      <div className="edge-card-action-row"><button type="button" className="edge-action edge-pill" aria-expanded={open === 'floor'} onClick={() => toggle('floor')}>See Floor Rankings →</button></div>
      {open === 'floor' && <EdgeRankingsView mode="floor" inline playerNames={rosterNames} limit={10} />}
    </article>
    <article className={`panel edge-panel${open === 'ceiling' ? ' expanded' : ''}`}>
      <div className="edge-panel-head">
        <div><h2 className="edge-title">Keep the Ceiling</h2><p className="edge-subtitle">Week-winning upside</p></div>
      </div>
      {preview(ceilingPlayers, 'ceiling')}
      <div className="edge-card-action-row"><button type="button" className="edge-action edge-pill" aria-expanded={open === 'ceiling'} onClick={() => toggle('ceiling')}>See Ceiling Rankings →</button></div>
      {open === 'ceiling' && <EdgeRankingsView mode="ceiling" inline playerNames={rosterNames} limit={10} />}
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

function NavIcon({ item }: { item: Exclude<Tab, 'Home'> }) {
  if (item === 'Coach') {
    return <svg className="nav-icon nav-icon-coach" viewBox="0 0 64 64" aria-hidden="true">
      <path className="coach-fill" d="M21.3 14.2c2.7-5.5 7.2-8.5 13.4-8.5 6.4 0 11.5 2.4 15.4 7.1-5.6-.2-10.9.6-15.8 2.4-4.3 1.6-7.9 3.8-10.8 6.7-1.8-1.9-2.6-4.5-2.2-7.7Z" />
      <path className="coach-fill" d="M33.8 16.1c4.8-1.8 10-2.4 15.5-1.9-1.8 2.8-4.3 4.5-7.5 5.1-2 .4-4 .5-6 .4-1.4 0-2.8.3-4 .9l-6 3c1.7-3.2 4.3-5.7 8-7.5Z" />
      <path className="coach-stroke" d="M24.8 22.7v6.6c0 6.4 4.1 11.6 10.1 11.6 6.1 0 10.3-5.1 10.3-11.4v-7.1" />
      <path className="coach-stroke" d="M21.4 58c1.6-8.8 6.6-13.3 14.8-13.3h4.1c8 0 13 4.4 14.6 13.3" />
      <path className="coach-fill" d="M11.2 58c1.2-6.7 4.5-11.2 9.8-13.6l7.2-3.2 6.5 8.1 6.6-8.1 7.1 3.2c5.4 2.4 8.7 6.9 9.9 13.6H11.2Z" />
      <circle className="coach-hole" cx="34.8" cy="48.6" r="3.1" />
      <path className="coach-stroke" d="M34.8 51.7v5.1" />
    </svg>
  }

  if (item === 'Guide') {
    return <svg className="nav-icon nav-icon-guide" viewBox="0 0 64 64" aria-hidden="true">
      <path d="M18 8h22l8 8v40H18z" />
      <path d="M40 8v10h8" />
      <path d="M25 27h16M25 34h16M25 41h13" />
    </svg>
  }

  return <svg className="nav-icon nav-icon-scores" viewBox="0 0 72 64" aria-hidden="true">
    <rect x="8" y="10" width="56" height="32" rx="4" />
    <path d="M36 14v24" />
    <text x="21.5" y="33" textAnchor="middle" className="score-digits">24</text>
    <text x="50.5" y="33" textAnchor="middle" className="score-digits">17</text>
    <path d="M20 42v10M52 42v10M14 52h44" />
  </svg>
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
        <div className="brand-copy"><div className="brand-name">Shiva</div><div className="brand-subtitle">FANTASY IQ</div></div>
        <AuthButton />
      </header>

      <section className="content" key={tab}>
        {tab === 'Home' && <div className="home-coach"><CoachView /><HomeEdgeCards /><RosterUpdates /><HomeNews /></div>}
        {tab === 'Coach' && <CoachHub />}
        {tab === 'Guide' && <GuideView />}
        {tab === 'Scores' && <ScoresView />}
      </section>

      <nav className="bottom-nav" aria-label="Primary navigation">
        {(['Home','Coach','Guide','Scores'] as Tab[]).map((item) => {
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
              : <NavIcon item={item as Exclude<Tab, 'Home'>} />}
            <span>{label}</span>
          </button>
        })}
      </nav>
    </main>
  </>
}
