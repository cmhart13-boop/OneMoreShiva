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
    return <svg className="nav-icon nav-icon-coach" viewBox="0 0 48 48" aria-hidden="true">
      <path d="M11 17.5c2.5-7 8.2-10.8 15.5-10.8 5.1 0 9.3 1.8 12.6 5.3-3.2.2-6.9.8-10.4 2.2-5.4 2.1-9 5.4-10.8 10" />
      <path d="M18 14.8c4.8-1.4 10.3-1.8 16.5-1.1" />
      <path d="M17.9 22.8c0 7 4.1 12.1 10.1 12.1 5.4 0 9.1-4.1 9.1-9.8 0-2.8-.8-5.2-2.3-7" />
      <path d="M8.5 41.2c2.7-5.3 7.6-8 14.5-8h7.2c5.8 0 9.9 2.3 12.2 6.8" />
      <circle cx="36.8" cy="33.5" r="2.2" />
      <path d="M35.7 35.4l-3.2 5.1 3.4 1.8 3-5.2" />
    </svg>
  }

  if (item === 'Guide') {
    return <svg className="nav-icon nav-icon-guide" viewBox="0 0 48 48" aria-hidden="true">
      <path d="M14 6.5h15l8 8V41H14z" />
      <path d="M29 6.5v8h8" />
      <path d="M19 21h13M19 27h13M19 33h9" />
    </svg>
  }

  return <svg className="nav-icon nav-icon-scores" viewBox="0 0 48 48" aria-hidden="true">
    <rect x="6.5" y="9" width="35" height="25" rx="3" />
    <path d="M13 15.5h8v12h-8zM27 15.5h8v12h-8z" />
    <path d="M24 14.5v13M12 39h24M15 34v5M33 34v5" />
    <circle cx="17" cy="19.5" r="1" /><circle cx="31" cy="19.5" r="1" />
    <circle cx="17" cy="24" r="1" /><circle cx="31" cy="24" r="1" />
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
