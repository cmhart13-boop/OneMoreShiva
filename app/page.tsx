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
import { activateLeague } from '../lib/league-client'
import type { NewsArticle, SavedLeague } from '../lib/types'

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

function HomeHero() {
  const [news, setNews] = useState<NewsArticle[]>([])
  const [leagueName, setLeagueName] = useState('Your fantasy command center')
  const [teamLine, setTeamLine] = useState('Add a league to make Shiva personal.')

  useEffect(() => {
    fetch('/api/news').then((r) => r.json()).then((d) => setNews(d.articles || [])).catch(() => setNews([]))
    const refresh = () => {
      try {
        const storedLeague = sessionStorage.getItem('shiva-league')
        const storedTeam = sessionStorage.getItem('shiva-team-id')
        if (!storedLeague) {
          setLeagueName('Your fantasy command center')
          setTeamLine('Add a league to make Shiva personal.')
          return
        }
        const league = JSON.parse(storedLeague)
        const team = league?.teams?.find((item: any) => String(item.id) === String(storedTeam))
        const record = Number.isFinite(team?.wins) && Number.isFinite(team?.losses) ? `${team.wins}-${team.losses}` : ''
        const week = league?.league?.scoringPeriod ?? league?.league?.matchupPeriod
        setLeagueName(league?.league?.name || 'Your league')
        setTeamLine([team?.name, record, week ? `Week ${week}` : ''].filter(Boolean).join(' · ') || 'League synced')
      } catch {}
    }
    refresh()
    window.addEventListener('shiva:league-changed', refresh)
    return () => window.removeEventListener('shiva:league-changed', refresh)
  }, [])

  const images = news.filter((article) => article.image).slice(0, 3)

  return <section className="rebuild-hero" aria-label="Current Shiva league context">
    <div className="rebuild-hero-images" aria-hidden="true">
      {images.map((article, index) => <img key={`${article.headline}-${index}`} src={article.image} alt="" />)}
      {!images.length && <div className="rebuild-hero-fallback" />}
    </div>
    <div className="rebuild-hero-shade" />
    <div className="rebuild-hero-content">
      <span className="rebuild-eyebrow">SHIVA FANTASY IQ</span>
      <h1>{leagueName}</h1>
      <p>{teamLine}</p>
    </div>
  </section>
}

function LeagueRail() {
  const [leagues, setLeagues] = useState<SavedLeague[]>([])
  const [openAdd, setOpenAdd] = useState(false)

  const load = () => fetch('/api/leagues', { cache:'no-store' })
    .then((r) => r.ok ? r.json() : null)
    .then((d) => setLeagues(d?.leagues || []))
    .catch(() => setLeagues([]))

  useEffect(() => {
    load()
    const changed = () => load()
    window.addEventListener('shiva:league-changed', changed)
    return () => window.removeEventListener('shiva:league-changed', changed)
  }, [])

  return <section className="league-rail-section" aria-label="My leagues">
    <div className="rebuild-section-head"><div><span>MY LEAGUES</span><h2>Swipe between teams</h2></div><button type="button" onClick={() => setOpenAdd((value) => !value)}>+ Add League</button></div>
    <div className="league-rail">
      {leagues.map((saved) => {
        const team = saved.league_data?.teams?.find((item: any) => String(item.id) === String(saved.team_id))
        const record = team && Number.isFinite(team.wins) && Number.isFinite(team.losses) ? `${team.wins}-${team.losses}` : 'Synced'
        return <button className="league-swipe-card" type="button" key={saved.id} onClick={() => saved.league_data && activateLeague(saved.league_data, saved.team_id)}>
          <span>{String(saved.provider || 'espn').toUpperCase()}</span>
          <strong>{team?.name || saved.team_name || saved.league_data?.league?.name || 'Fantasy League'}</strong>
          <small>{saved.league_data?.league?.name || 'League'} · {record}</small>
          <b>Open league →</b>
        </button>
      })}
      {!leagues.length && <button className="league-swipe-card empty" type="button" onClick={() => setOpenAdd(true)}><span>START HERE</span><strong>+ Add your first league</strong><small>ESPN or Sleeper</small><b>Connect →</b></button>}
    </div>
    {openAdd && <div className="league-add-drawer"><CoachView showTabs={false} activeTab="Overview" /></div>}
  </section>
}

function ShivaSays() {
  const [players, setPlayers] = useState<HomeEdgePlayer[]>([])
  const [rosterNames, setRosterNames] = useState<string[]>([])

  useEffect(() => {
    fetch('/api/edges').then((r) => r.json()).then((d) => setPlayers(d.players || [])).catch(() => setPlayers([]))
    const refresh = () => setRosterNames(readRosterNames())
    refresh()
    window.addEventListener('shiva:league-changed', refresh)
    return () => window.removeEventListener('shiva:league-changed', refresh)
  }, [])

  const scoped = useMemo(() => {
    if (!rosterNames.length) return players
    const set = new Set(rosterNames.map((name) => name.toLowerCase()))
    return players.filter((player) => set.has(player.name.toLowerCase()))
  }, [players, rosterNames])

  const floor = [...scoped].sort((a,b) => b.rate15 - a.rate15)[0]
  const ceiling = [...scoped].sort((a,b) => b.boom25 - a.boom25)[0]

  return <section className="shiva-says-card">
    <div className="shiva-says-title"><img src="/shiva-trophy.png" alt="" /><div><span>SHIVA SAYS</span><h2>Your edge right now</h2></div></div>
    <div className="shiva-says-grid">
      <div><small>SAFEST FLOOR</small><strong>{floor?.name || 'Connect a league'}</strong><span>{floor ? `${Math.round(floor.rate15)}% chance of 15+ PPG` : 'Shiva will analyze your roster automatically.'}</span></div>
      <div><small>BEST CEILING</small><strong>{ceiling?.name || 'Then ask anything'}</strong><span>{ceiling ? `${Math.round(ceiling.boom25)}% chance of 25+ PPG` : 'Lineups, trades, waivers, draft and more.'}</span></div>
    </div>
  </section>
}

function HomeEdgeCards() {
  const [open, setOpen] = useState<EdgeView>(null)
  const [players, setPlayers] = useState<HomeEdgePlayer[]>([])
  const [rosterNames, setRosterNames] = useState<string[]>([])

  useEffect(() => {
    fetch('/api/edges').then((response) => response.json()).then((data) => setPlayers(data.players || [])).catch(() => setPlayers([]))
  }, [])
  useEffect(() => {
    const refresh = () => setRosterNames(readRosterNames())
    refresh()
    window.addEventListener('shiva:league-changed', refresh)
    return () => window.removeEventListener('shiva:league-changed', refresh)
  }, [])

  const scopedPlayers = useMemo(() => {
    if (!rosterNames.length) return players
    const rosterSet = new Set(rosterNames.map((name) => name.toLowerCase()))
    return players.filter((player) => rosterSet.has(player.name.toLowerCase()))
  }, [players, rosterNames])
  const floorPlayers = useMemo(() => [...scopedPlayers].sort((a, b) => b.floor - a.floor || b.rate15 - a.rate15 || a.rank - b.rank).slice(0, 3), [scopedPlayers])
  const ceilingPlayers = useMemo(() => [...scopedPlayers].sort((a, b) => b.ceiling - a.ceiling || b.boom25 - a.boom25 || a.rank - b.rank).slice(0, 3), [scopedPlayers])
  const preview = (rows: HomeEdgePlayer[], mode: Exclude<EdgeView, null>) => <div className="edge-preview-list">{rows.map((player) => <div className="edge-preview-row" key={`${mode}-${player.id}`}><PlayerAvatar playerId={player.espnId || player.id} name={player.name} /><strong>{player.name}</strong><span>{player.pos} · {player.ppg.toFixed(1)} PPG</span><b>{Math.round(mode === 'floor' ? player.rate15 : player.boom25)}%</b></div>)}</div>

  return <div className="home-edge-cards rebuild-edge-grid">
    <article className={`panel edge-panel${open === 'floor' ? ' expanded' : ''}`}><div className="edge-panel-head"><div><h2 className="edge-title">Raise the Floor</h2><p className="edge-subtitle">Consistency Shiva trusts</p></div></div>{preview(floorPlayers, 'floor')}<div className="edge-card-action-row"><button type="button" className="edge-action edge-pill" onClick={() => setOpen(open === 'floor' ? null : 'floor')}>Shiva Floor Rankings →</button></div>{open === 'floor' && <EdgeRankingsView mode="floor" inline playerNames={rosterNames} limit={10} />}</article>
    <article className={`panel edge-panel${open === 'ceiling' ? ' expanded' : ''}`}><div className="edge-panel-head"><div><h2 className="edge-title">Keep the Ceiling</h2><p className="edge-subtitle">Week-winning upside</p></div></div>{preview(ceilingPlayers, 'ceiling')}<div className="edge-card-action-row"><button type="button" className="edge-action edge-pill" onClick={() => setOpen(open === 'ceiling' ? null : 'ceiling')}>Shiva Ceiling Rankings →</button></div>{open === 'ceiling' && <EdgeRankingsView mode="ceiling" inline playerNames={rosterNames} limit={10} />}</article>
  </div>
}

function HomeNews() {
  const [news, setNews] = useState<NewsArticle[]>([])
  useEffect(() => { fetch('/api/news').then((r) => r.json()).then((d) => setNews(d.articles || [])).catch(() => setNews([])) }, [])
  return <section className="home-news"><div className="rebuild-section-head"><div><span>NFL FEED</span><h2>Latest football news</h2></div></div><div className="rebuild-news-list">{news.slice(0,4).map((article) => <a href={article.url || '#'} target={article.url ? '_blank' : undefined} rel="noreferrer" key={`${article.published || ''}-${article.headline}`}><div>{article.image ? <img src={article.image} alt="" /> : <div className="news-image-fallback" />}</div><p><strong>{article.headline}</strong><span>{article.description}</span></p></a>)}</div></section>
}

function NavIcon({ item }: { item: Exclude<Tab, 'Home'> }) {
  if (item === 'Coach') return <svg className="nav-icon nav-icon-coach" viewBox="0 0 64 64" aria-hidden="true"><path className="coach-fill" d="M21.3 14.2c2.7-5.5 7.2-8.5 13.4-8.5 6.4 0 11.5 2.4 15.4 7.1-5.6-.2-10.9.6-15.8 2.4-4.3 1.6-7.9 3.8-10.8 6.7-1.8-1.9-2.6-4.5-2.2-7.7Z"/><path className="coach-fill" d="M11.2 58c1.2-6.7 4.5-11.2 9.8-13.6l7.2-3.2 6.5 8.1 6.6-8.1 7.1 3.2c5.4 2.4 8.7 6.9 9.9 13.6H11.2Z"/></svg>
  if (item === 'Guide') return <svg className="nav-icon nav-icon-guide" viewBox="0 0 64 64" aria-hidden="true"><path d="M18 8h22l8 8v40H18z"/><path d="M40 8v10h8"/><path d="M25 27h16M25 34h16M25 41h13"/></svg>
  return <svg className="nav-icon nav-icon-scores" viewBox="0 0 72 64" aria-hidden="true"><rect x="8" y="10" width="56" height="32" rx="4"/><path d="M36 14v24"/><text x="21.5" y="33" textAnchor="middle" className="score-digits">24</text><text x="50.5" y="33" textAnchor="middle" className="score-digits">17</text><path d="M20 42v10M52 42v10M14 52h44"/></svg>
}

export default function ShivaApp() {
  const [tab, setTab] = useState<Tab>('Home')
  const [launching, setLaunching] = useState(true)
  useEffect(() => { const timer = window.setTimeout(() => setLaunching(false), 2500); return () => window.clearTimeout(timer) }, [])

  return <>
    {launching && <div className="launch-screen" aria-label="Shiva loading"><img src="/shiva-trophy.png" alt="The Shiva trophy" /></div>}
    <main className="app-shell rebuild-shell">
      <header className="brand-header rebuild-header"><div className="rebuild-brand"><img src="/shiva-trophy.png" alt="" className="brand-trophy"/><div className="brand-copy"><div className="brand-name">SHIVA</div><div className="brand-subtitle">FANTASY FOOTBALL INTELLIGENCE</div></div></div><AuthButton /></header>

      <section className="content" key={tab}>
        {tab === 'Home' && <div className="rebuild-home">
          <HomeHero />
          <LeagueRail />
          <section className="rebuild-ask"><div className="rebuild-ask-heading"><div><span>ASK SHIVA</span><h2>Your league. Your roster. Your answer.</h2></div><small>League context included automatically</small></div><CoachView showTabs={false} activeTab="Ask Shiva" /></section>
          <ShivaSays />
          <HomeEdgeCards />
          <RosterUpdates />
          <HomeNews />
        </div>}
        {tab === 'Coach' && <CoachHub />}
        {tab === 'Guide' && <GuideView />}
        {tab === 'Scores' && <ScoresView />}
      </section>

      <nav className="bottom-nav" aria-label="Primary navigation">{(['Home','Coach','Guide','Scores'] as Tab[]).map((item) => { const isShiva = item === 'Home'; const label = isShiva ? 'Shiva' : item; return <button type="button" key={item} aria-label={label} className={`${tab === item ? 'active' : ''}${isShiva ? ' shiva-nav' : ''}`.trim()} onClick={() => { setTab(item); window.scrollTo({ top:0, behavior:'instant' as ScrollBehavior }) }}>{isShiva ? <img src="/shiva-trophy.png" alt="" className="nav-trophy"/> : <NavIcon item={item as Exclude<Tab,'Home'>}/>}<span>{label}</span></button> })}</nav>
    </main>
  </>
}
