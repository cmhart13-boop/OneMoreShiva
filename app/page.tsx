'use client'

import { useEffect, useMemo, useState } from 'react'
import AuthButton from '../components/AuthButton'
import CoachView from '../components/CoachView'
import GuideView from '../components/GuideView'
import { PlayerAvatar } from '../components/PlayerMedia'
import ScoresView from '../components/ScoresView'
import { activateLeague } from '../lib/league-client'
import type { NewsArticle, SavedLeague } from '../lib/types'

type Tab = 'Home' | 'Team' | 'Leagues' | 'News' | 'More'
type AskScope = 'league' | 'all'
type EdgePlayer = { id:string; espnId?:string; name:string; team:string; pos:string; rank:number; ppg:number; floor:number; ceiling:number; rate15:number; boom25:number }

function activeLeagueContext() {
  try {
    const raw = sessionStorage.getItem('shiva-league')
    const teamId = sessionStorage.getItem('shiva-team-id')
    if (!raw) return null
    const league = JSON.parse(raw)
    const team = league?.teams?.find((item:any) => String(item.id) === String(teamId))
    const roster = (league?.roster || []).filter((row:any) => String(row.teamId) === String(teamId))
    return { league, team, roster }
  } catch { return null }
}

function HomeHero() {
  const [news, setNews] = useState<NewsArticle[]>([])
  const [week, setWeek] = useState<number | null>(1)
  useEffect(() => {
    fetch('/api/news').then(r => r.json()).then(d => setNews(d.articles || [])).catch(() => setNews([]))
    const refresh = () => {
      const ctx = activeLeagueContext()
      setWeek(ctx?.league?.league?.scoringPeriod ?? ctx?.league?.league?.matchupPeriod ?? 1)
    }
    refresh(); window.addEventListener('shiva:league-changed', refresh)
    return () => window.removeEventListener('shiva:league-changed', refresh)
  }, [])
  const images = news.filter(a => a.image).slice(0,5)
  return <section className="approved-hero" aria-label="NFL fantasy football hero">
    <div className="approved-hero-images" aria-hidden="true">
      {images.map((a,i) => <img key={`${a.headline}-${i}`} src={a.image} alt="" />)}
      {!images.length && <div className="approved-hero-fallback" />}
    </div>
    <div className="approved-hero-vignette" />
    <div className="approved-week"><b>WEEK {week || 1}</b><span>NFL SEASON</span></div>
  </section>
}

function LeagueStrip() {
  const [leagues, setLeagues] = useState<SavedLeague[]>([])
  const [adding, setAdding] = useState(false)
  const load = () => fetch('/api/leagues', { cache:'no-store' }).then(r => r.ok ? r.json() : null).then(d => setLeagues(d?.leagues || [])).catch(() => setLeagues([]))
  useEffect(() => { load(); const fn = () => load(); window.addEventListener('shiva:league-changed', fn); return () => window.removeEventListener('shiva:league-changed', fn) }, [])
  return <section className="approved-league-wrap" aria-label="My leagues">
    <div className="approved-league-strip">
      {leagues.map((saved, index) => {
        const team = saved.league_data?.teams?.find((item:any) => String(item.id) === String(saved.team_id))
        return <button type="button" className={`approved-league-pill${index === 0 ? ' selected' : ''}`} key={saved.id} onClick={() => saved.league_data && activateLeague(saved.league_data, saved.team_id)}>
          <span className="league-icon">{index === 0 ? '🏆' : '♛'}</span><span><b>{team?.name || saved.team_name || saved.league_data?.league?.name || 'My League'}</b><small>{saved.league_data?.league?.settings?.size || saved.league_data?.teams?.length || ''} Teams · {String(saved.provider || 'ESPN').toUpperCase()}</small></span>
        </button>
      })}
      <button type="button" className="approved-league-pill add" onClick={() => setAdding(v => !v)}><span className="league-plus">＋</span><span><b>Add League</b><small>ESPN or Sleeper</small></span></button>
    </div>
    <div className="league-dots" aria-hidden="true"><i className="active"/><i/><i/><i/></div>
    {adding && <div className="approved-add-drawer"><CoachView showTabs={false} activeTab="Overview" /></div>}
  </section>
}

function HomeAsk() {
  const [scope, setScope] = useState<AskScope>('league')
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [status, setStatus] = useState('')
  const [leagues, setLeagues] = useState<SavedLeague[]>([])
  const [edges, setEdges] = useState<EdgePlayer[]>([])
  const [rosterNames, setRosterNames] = useState<string[]>([])

  useEffect(() => {
    fetch('/api/leagues', { cache:'no-store' }).then(r => r.ok ? r.json() : null).then(d => setLeagues(d?.leagues || [])).catch(() => {})
    fetch('/api/edges').then(r => r.json()).then(d => setEdges(d.players || [])).catch(() => setEdges([]))
    const refresh = () => {
      const ctx = activeLeagueContext()
      setRosterNames((ctx?.roster || []).map((r:any) => r.player).filter(Boolean))
    }
    refresh(); window.addEventListener('shiva:league-changed', refresh)
    return () => window.removeEventListener('shiva:league-changed', refresh)
  }, [])

  const defaultInsight = useMemo(() => {
    const rosterSet = new Set(rosterNames.map(n => n.toLowerCase()))
    const scoped = rosterNames.length ? edges.filter(p => rosterSet.has(p.name.toLowerCase())) : edges
    const pick = [...scoped].sort((a,b) => b.rate15 - a.rate15 || b.floor - a.floor)[0]
    if (pick) return `${pick.name} is your strongest floor play right now — ${Math.round(pick.rate15)}% chance of 15+ PPG based on Shiva's current data.`
    return 'Add a league and Shiva will automatically analyze your roster, scoring settings, waivers and weekly decisions.'
  }, [edges, rosterNames])

  const ask = async () => {
    if (!question.trim()) return
    setStatus('Thinking…'); setAnswer('')
    const active = activeLeagueContext()
    const contextParts:string[] = []
    if (scope === 'league' && active) {
      contextParts.push(`League: ${active.league?.league?.name || ''}`)
      if (active.team?.name) contextParts.push(`Team: ${active.team.name}`)
      if (active.roster?.length) contextParts.push(`Roster: ${active.roster.map((r:any) => `${r.slot} ${r.player}`).join(', ')}`)
    }
    if (scope === 'all') {
      for (const saved of leagues) {
        const team = saved.league_data?.teams?.find((item:any) => String(item.id) === String(saved.team_id))
        const roster = (saved.league_data?.roster || []).filter((row:any) => String(row.teamId) === String(saved.team_id))
        contextParts.push(`League: ${saved.league_data?.league?.name || saved.league_name || saved.league_id}; Team: ${team?.name || saved.team_name || ''}; Roster: ${roster.map((r:any) => `${r.slot} ${r.player}`).join(', ')}`)
      }
    }
    try {
      const res = await fetch('/api/ask', { method:'POST', headers:{ 'Content-Type':'application/json' }, body:JSON.stringify({ question:question.trim(), context:contextParts.join('\n') }) })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Shiva Intelligence unavailable.')
      setAnswer(data.answer || ''); setStatus('')
    } catch (e) { setStatus(e instanceof Error ? e.message : 'Shiva Intelligence unavailable.') }
  }

  return <section className="approved-ask-card" aria-label="Ask Shiva">
    <div className="approved-ask-top">
      <div className="approved-ask-brand"><div className="trident">♆</div><h2>Ask Shiva</h2></div>
      <div className="scope-toggle"><button className={scope === 'league' ? 'active' : ''} onClick={() => setScope('league')}>This League</button><button className={scope === 'all' ? 'active' : ''} onClick={() => setScope('all')}>All My Leagues</button></div>
    </div>
    <div className="ask-inline"><input aria-label="Ask Shiva question" value={question} onChange={e => setQuestion(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') ask() }} placeholder="Should I start Jeanty or Skattebo in Week 1?"/><button type="button" aria-label="Send to Shiva" onClick={ask}>➤</button></div>
    <div className="approved-shiva-says">
      <div className="says-head"><span>♆</span><b>SHIVA SAYS</b><em>{status === 'Thinking…' ? 'ANALYZING' : 'HIGH CONFIDENCE'}</em></div>
      <p>{status && status !== 'Thinking…' ? status : (answer || defaultInsight)}</p>
      <div className="says-actions"><button type="button" onClick={() => setQuestion('Why?')}>◉ Ask Why</button><button type="button" onClick={() => window.dispatchEvent(new CustomEvent('shiva:open-coach', { detail:'Start / Sit' }))}>⇄ Compare</button><button type="button" onClick={() => window.dispatchEvent(new CustomEvent('shiva:open-coach', { detail:'Lineup' }))}>☷ Fix Lineup</button></div>
    </div>
  </section>
}

const TOOL_ITEMS = [
  ['↕','Start / Sit','Get lineup advice','Start / Sit'],['♟','Waivers','Find top adds','Waivers'],['⇄','Trade Analyzer','Win more trades','Players'],
  ['▤','Draft Guide','Prep for your draft','Guide'],['▥','Power Rankings','See the big picture','League'],['▣','Schedule','Matchups & strength','Scores'],
] as const

function QuickTools({ open }: { open:(target:string)=>void }) {
  return <section className="approved-tools">{TOOL_ITEMS.map(([icon,title,sub,target]) => <button key={title} type="button" onClick={() => open(target)}><span>{icon}</span><b>{title}</b><small>{sub}</small></button>)}</section>
}

function BottomSnapshot() {
  const [edges,setEdges] = useState<EdgePlayer[]>([])
  const [ctx,setCtx] = useState<any>(null)
  useEffect(() => {
    fetch('/api/edges').then(r => r.json()).then(d => setEdges(d.players || [])).catch(() => setEdges([]))
    const refresh = () => setCtx(activeLeagueContext())
    refresh(); window.addEventListener('shiva:league-changed', refresh)
    return () => window.removeEventListener('shiva:league-changed', refresh)
  }, [])
  const rosterSet = new Set((ctx?.roster || []).map((r:any) => String(r.player).toLowerCase()))
  const keyPlayers = (rosterSet.size ? edges.filter(p => rosterSet.has(p.name.toLowerCase())) : edges).slice(0,4)
  const teams = [...(ctx?.league?.teams || [])].sort((a:any,b:any) => (b.wins ?? 0) - (a.wins ?? 0)).slice(0,5)
  return <section className="approved-snapshot">
    <article><header><b>My League</b><span>View All ›</span></header><strong>{ctx?.league?.league?.name || 'Add a league'}</strong><div className="mini-standings">{teams.map((t:any,i:number) => <div key={t.id}><span>{i+1}</span><b>{t.name}</b><em>{t.wins ?? 0}-{t.losses ?? 0}</em></div>)}</div></article>
    <article><header><b>My Matchup</b><span>Week {ctx?.league?.league?.scoringPeriod || 1}</span></header><div className="matchup-center"><div className="helmet">◖</div><b>VS</b><div className="helmet">◗</div></div><strong>{ctx?.team?.name || 'Your Team'}</strong><button type="button" onClick={() => window.dispatchEvent(new CustomEvent('shiva:open-coach', { detail:'Lineup' }))}>View Matchup</button></article>
    <article><header><b>Key Players This Week</b><span>See All ›</span></header>{keyPlayers.map(p => <div className="key-player" key={p.id}><PlayerAvatar playerId={p.espnId || p.id} name={p.name}/><span><b>{p.name}</b><small>{p.pos} · {p.ppg.toFixed(1)} PPG</small></span><em>{p.rate15 >= 60 ? 'START' : 'CONSIDER'}</em></div>)}</article>
  </section>
}

function MoreHub({ open }: { open:(target:string)=>void }) {
  return <div className="approved-more"><h1>More Shiva</h1><button onClick={() => open('Guide')}>Draft Guide</button><button onClick={() => open('Scores')}>Scores & NFL News</button><button onClick={() => open('Players')}>Players</button><button onClick={() => open('Waivers')}>Waivers</button></div>
}

export default function ShivaApp() {
  const [tab,setTab] = useState<Tab>('Home')
  const [detail,setDetail] = useState<'Guide'|'Scores'|'Players'|'Waivers'|'Start / Sit'|'League'|'Lineup'|null>(null)
  const [launching,setLaunching] = useState(true)
  useEffect(() => { const t = window.setTimeout(() => setLaunching(false), 2500); return () => window.clearTimeout(t) }, [])
  useEffect(() => {
    const openCoach = (event:Event) => {
      const target = (event as CustomEvent<string>).detail
      if (target === 'League') { setTab('Leagues'); setDetail(null) }
      else if (target === 'Lineup') { setTab('Team'); setDetail(null) }
      else { setTab('More'); setDetail((target as any) || null) }
      requestAnimationFrame(() => window.scrollTo({ top:0, behavior:'instant' as ScrollBehavior }))
    }
    window.addEventListener('shiva:open-coach', openCoach)
    return () => window.removeEventListener('shiva:open-coach', openCoach)
  }, [])
  const open = (target:string) => {
    if (target === 'Guide') { setTab('More'); setDetail('Guide') }
    else if (target === 'Scores') { setTab('News'); setDetail(null) }
    else if (target === 'League') { setTab('Leagues'); setDetail(null) }
    else if (target === 'Lineup') { setTab('Team'); setDetail(null) }
    else { setTab('More'); setDetail(target as any) }
    window.scrollTo({ top:0, behavior:'instant' as ScrollBehavior })
  }
  return <>
    {launching && <div className="launch-screen" aria-label="Shiva loading"><img src="/shiva-trophy.png" alt="The Shiva trophy" /></div>}
    <main className="app-shell approved-shell">
      <header className="approved-header"><div className="approved-wordmark"><span>♛</span>SHIVA</div><div className="approved-header-actions"><AuthButton /></div></header>
      <section className="content approved-content">
        {tab === 'Home' && <div className="approved-home"><HomeHero/><LeagueStrip/><HomeAsk/><QuickTools open={open}/><BottomSnapshot/></div>}
        {tab === 'Team' && <CoachView showTabs={false} activeTab="Lineup" />}
        {tab === 'Leagues' && <CoachView showTabs={false} activeTab="League" />}
        {tab === 'News' && <ScoresView />}
        {tab === 'More' && (detail === 'Guide' ? <GuideView/> : detail === 'Scores' ? <ScoresView/> : detail === 'Start / Sit' ? <CoachView showTabs={false} activeTab="Start / Sit"/> : detail === 'Waivers' ? <CoachView showTabs={false} activeTab="Waivers"/> : detail === 'Players' ? <CoachView showTabs={false} activeTab="Players"/> : <MoreHub open={open}/>)}
      </section>
      <nav className="bottom-nav approved-bottom" aria-label="Primary navigation">
        {[['Home','⌂'],['Team','♟'],['Leagues','🏆'],['News','▤'],['More','•••']] as const satisfies readonly (readonly [Tab,string])[]}.map(([item,icon]) => <button type="button" key={item} aria-label={item === 'Team' ? 'My Team' : item} className={tab === item ? 'active' : ''} onClick={() => { setTab(item); setDetail(null); window.scrollTo({ top:0, behavior:'instant' as ScrollBehavior }) }}><span className="approved-nav-icon">{icon}</span><span>{item === 'Team' ? 'My Team' : item}</span></button>)}
      </nav>
    </main>
  </>
}