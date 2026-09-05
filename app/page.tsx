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

const NAV_ITEMS: Array<[Tab, string]> = [['Home','⌂'],['Team','♟'],['Leagues','♜'],['News','▤'],['More','•••']]
const TOOL_ITEMS = [
  ['↕','Start / Sit','Get lineup advice','Start / Sit'],
  ['♟','Waivers','Find top adds','Waivers'],
  ['⇄','Trade Analyzer','Win more trades','Players'],
  ['▤','Draft Guide','Prep for your draft','Guide'],
  ['▥','Power Rankings','See the big picture','League'],
  ['▣','Schedule','Matchups & strength','Scores'],
] as const

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

function BellIcon() {
  return <span className="spec-bell" aria-label="Notifications"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/></svg><i /></span>
}

function Hero() {
  const [news,setNews] = useState<NewsArticle[]>([])
  const [week,setWeek] = useState(1)
  useEffect(() => {
    fetch('/api/news').then(r => r.json()).then(d => setNews(d.articles || [])).catch(() => setNews([]))
    const refresh = () => {
      const ctx = activeLeagueContext()
      setWeek(Number(ctx?.league?.league?.scoringPeriod ?? ctx?.league?.league?.matchupPeriod ?? 1) || 1)
    }
    refresh(); window.addEventListener('shiva:league-changed',refresh)
    return () => window.removeEventListener('shiva:league-changed',refresh)
  },[])
  const images = news.filter(item => item.image).slice(0,5)
  return <section className="spec-hero" aria-label="NFL fantasy football hero">
    <div className="spec-hero-media" aria-hidden="true">
      {images.map((item,index) => <img key={`${item.headline}-${index}`} src={item.image} alt="" />)}
      {!images.length && <div className="spec-hero-fallback" />}
    </div>
    <div className="spec-hero-shade" />
    <div className="spec-week"><b>WEEK {week}</b><span>NFL SEASON</span></div>
  </section>
}

function LeagueSwitcher() {
  const [leagues,setLeagues] = useState<SavedLeague[]>([])
  const [selected,setSelected] = useState('')
  const [adding,setAdding] = useState(false)
  const load = () => fetch('/api/leagues',{ cache:'no-store' }).then(r => r.ok ? r.json() : null).then(d => setLeagues(d?.leagues || [])).catch(() => setLeagues([]))
  useEffect(() => { load(); const refresh=()=>load(); window.addEventListener('shiva:league-changed',refresh); return()=>window.removeEventListener('shiva:league-changed',refresh) },[])
  useEffect(() => { if (!selected && leagues[0]?.id) setSelected(leagues[0].id) },[leagues,selected])
  const iconFor = (index:number) => ['🏆','♛','♟','◉'][index % 4]
  return <section className="spec-leagues" aria-label="League switcher">
    <div className="spec-league-row">
      {leagues.map((saved,index) => {
        const team = saved.league_data?.teams?.find((item:any) => String(item.id) === String(saved.team_id))
        const leagueName = saved.nickname || saved.league_name || saved.league_data?.league?.name || 'Fantasy League'
        const teamCount = saved.league_data?.teams?.length || ''
        const format = String(saved.provider || 'espn').toUpperCase()
        return <button key={saved.id} type="button" className={`spec-league-card${selected === saved.id ? ' selected' : ''}`} onClick={() => { setSelected(saved.id); if (saved.league_data) activateLeague(saved.league_data,saved.team_id) }}>
          <span className="spec-league-icon">{iconFor(index)}</span><span><b>{team?.name || leagueName}</b><small>{teamCount ? `${teamCount} Teams · ` : ''}{format}</small></span>
        </button>
      })}
      <button type="button" className="spec-league-card spec-add-league" onClick={() => setAdding(value => !value)}><span className="spec-league-icon">＋</span><span><b>Add League</b><small>ESPN or Sleeper</small></span></button>
    </div>
    <div className="spec-dots" aria-hidden="true">{(leagues.length ? leagues : [{id:'add'}]).map((item:any,index:number) => <i key={item.id || index} className={(selected ? item.id === selected : index===0) ? 'active' : ''} />)}</div>
    {adding && <div className="spec-add-drawer"><CoachView showTabs={false} activeTab="Overview" /></div>}
  </section>
}

function AskShiva() {
  const [scope,setScope] = useState<AskScope>('league')
  const [question,setQuestion] = useState('')
  const [answer,setAnswer] = useState('')
  const [status,setStatus] = useState('')
  const [leagues,setLeagues] = useState<SavedLeague[]>([])
  useEffect(() => { fetch('/api/leagues',{ cache:'no-store' }).then(r=>r.ok?r.json():null).then(d=>setLeagues(d?.leagues || [])).catch(()=>{}) },[])
  const ask = async () => {
    if (!question.trim()) return
    setStatus('Thinking…'); setAnswer('')
    const active = activeLeagueContext()
    const context:string[] = []
    if (scope === 'league' && active) {
      context.push(`League: ${active.league?.league?.name || ''}`)
      if (active.team?.name) context.push(`Team: ${active.team.name}`)
      if (active.roster?.length) context.push(`Roster: ${active.roster.map((row:any) => `${row.slot} ${row.player}`).join(', ')}`)
    }
    if (scope === 'all') {
      for (const saved of leagues) {
        const team = saved.league_data?.teams?.find((item:any) => String(item.id) === String(saved.team_id))
        const roster = (saved.league_data?.roster || []).filter((row:any) => String(row.teamId) === String(saved.team_id))
        context.push(`League: ${saved.league_data?.league?.name || saved.league_name || saved.league_id}; Team: ${team?.name || saved.team_name || ''}; Roster: ${roster.map((row:any) => `${row.slot} ${row.player}`).join(', ')}`)
      }
    }
    try {
      const response = await fetch('/api/ask',{ method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ question:question.trim(),context:context.join('\n') }) })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || 'Shiva Intelligence unavailable.')
      setAnswer(data.answer || ''); setStatus('')
    } catch (error) { setStatus(error instanceof Error ? error.message : 'Shiva Intelligence unavailable.') }
  }
  const hasResult = Boolean(answer || status)
  return <section className="spec-ask" aria-label="Ask Shiva">
    <div className="spec-ask-head"><div className="spec-ask-brand"><span className="spec-trident">♆</span><h2>Ask Shiva</h2></div><div className="spec-scope"><button className={scope==='league'?'active':''} onClick={()=>setScope('league')}>This League</button><button className={scope==='all'?'active':''} onClick={()=>setScope('all')}>All My Leagues</button></div></div>
    <div className="spec-input-row"><div className="spec-input-wrap"><input aria-label="Ask Shiva question" value={question} onChange={e=>setQuestion(e.target.value)} onKeyDown={e=>{if(e.key==='Enter') ask()}} placeholder="Should I start Jeanty or Skattebo in Week 1?" />{question && <button type="button" className="spec-clear" aria-label="Clear question" onClick={()=>{setQuestion('');setAnswer('');setStatus('')}}>×</button>}</div><button type="button" className="spec-send" aria-label="Send to Shiva" onClick={ask}>➤</button></div>
    {hasResult && <div className="spec-answer"><div className="spec-answer-head"><span>♆</span><b>SHIVA SAYS</b><em>{status==='Thinking…'?'ANALYZING':'▥ HIGH CONFIDENCE'}</em></div><p>{status || answer}</p>{answer && <div className="spec-answer-actions"><button type="button" onClick={()=>window.dispatchEvent(new CustomEvent('shiva:open-coach',{detail:'Lineup'}))}>▤ Fix Lineup</button><button type="button" onClick={()=>setQuestion(`Why? ${answer}`)}>◉ Ask Why</button><button type="button" onClick={()=>window.dispatchEvent(new CustomEvent('shiva:open-coach',{detail:'Start / Sit'}))}>☷ See Options</button></div>}</div>}
  </section>
}

function QuickActions({ open }:{ open:(target:string)=>void }) {
  return <section className="spec-tools">{TOOL_ITEMS.map(([icon,title,sub,target]) => <button key={title} type="button" onClick={()=>open(target)}><span>{icon}</span><b>{title}</b><small>{sub}</small></button>)}</section>
}

function Snapshot() {
  const [ctx,setCtx] = useState<any>(null)
  const [edges,setEdges] = useState<EdgePlayer[]>([])
  useEffect(() => {
    fetch('/api/edges').then(r=>r.json()).then(d=>setEdges(d.players || [])).catch(()=>setEdges([]))
    const refresh=()=>setCtx(activeLeagueContext())
    refresh(); window.addEventListener('shiva:league-changed',refresh)
    return()=>window.removeEventListener('shiva:league-changed',refresh)
  },[])
  const teams = useMemo(()=>[...(ctx?.league?.teams || [])].sort((a:any,b:any)=>(b.wins ?? 0)-(a.wins ?? 0)||(a.losses ?? 0)-(b.losses ?? 0)).slice(0,5),[ctx])
  const rosterNames = new Set((ctx?.roster || []).map((row:any)=>String(row.player).toLowerCase()))
  const players = (rosterNames.size ? edges.filter(player=>rosterNames.has(player.name.toLowerCase())) : []).slice(0,5)
  const opponent = (ctx?.league?.teams || []).find((team:any)=>String(team.id)!==String(ctx?.team?.id))
  return <section className="spec-snapshot">
    <article><header><b>My League</b><button type="button" onClick={()=>window.dispatchEvent(new CustomEvent('shiva:open-coach',{detail:'League'}))}>View All ›</button></header><div className="spec-league-summary"><span>🏆</span><div><b>{ctx?.league?.league?.name || 'No league connected'}</b><small>{ctx?.league?.teams?.length ? `${ctx.league.teams.length} Teams` : 'Add a league to populate standings'}</small></div><em>⚙</em></div><div className="spec-standings">{teams.map((team:any,index:number)=><div key={team.id}><span>{index+1}</span><i>♟</i><b>{team.name}</b><em>{team.wins ?? 0}-{team.losses ?? 0}</em></div>)}</div></article>
    <article><header><b>My Matchup</b><button type="button" onClick={()=>window.dispatchEvent(new CustomEvent('shiva:open-coach',{detail:'Lineup'}))}>Week {ctx?.league?.league?.scoringPeriod || 1} ›</button></header><div className="spec-matchup"><div><span>◖</span><strong>0.0</strong><b>My Team</b><small>{ctx?.team?.name || 'Connect league'}</small></div><i>VS</i><div><span>◗</span><strong>0.0</strong><b>{opponent?.name || 'Opponent'}</b><small>Projected matchup</small></div></div><button className="spec-matchup-button" type="button" onClick={()=>window.dispatchEvent(new CustomEvent('shiva:open-coach',{detail:'Lineup'}))}>View Matchup</button></article>
    <article><header><b>Key Players This Week</b><button type="button" onClick={()=>window.dispatchEvent(new CustomEvent('shiva:open-coach',{detail:'Players'}))}>See All ›</button></header><div className="spec-key-players">{players.length ? players.map(player=><div key={player.id}><PlayerAvatar playerId={player.espnId || player.id} name={player.name}/><span><b>{player.name}</b><small>{player.pos} · {player.team || 'NFL'}</small></span><em className={player.rate15 >= 60 ? 'start' : 'consider'}>{player.rate15 >= 60 ? 'START' : 'CONSIDER'}</em></div>) : <p>Connect a league to populate your flagged players.</p>}</div></article>
  </section>
}

function MoreHub({ open }:{ open:(target:string)=>void }) {
  return <div className="approved-more"><h1>More Shiva</h1><button onClick={()=>open('Guide')}>Draft Guide</button><button onClick={()=>open('Scores')}>Scores & NFL News</button><button onClick={()=>open('Players')}>Players</button><button onClick={()=>open('Waivers')}>Waivers</button></div>
}

export default function ShivaApp() {
  const [tab,setTab] = useState<Tab>('Home')
  const [detail,setDetail] = useState<'Guide'|'Scores'|'Players'|'Waivers'|'Start / Sit'|'League'|'Lineup'|null>(null)
  const [launching,setLaunching] = useState(true)
  useEffect(()=>{const timer=window.setTimeout(()=>setLaunching(false),2500);return()=>window.clearTimeout(timer)},[])
  useEffect(()=>{
    const handler=(event:Event)=>{const target=(event as CustomEvent<string>).detail;openTarget(target)}
    window.addEventListener('shiva:open-coach',handler)
    return()=>window.removeEventListener('shiva:open-coach',handler)
  })
  const openTarget=(target:string)=>{
    if(target==='Guide'){setTab('More');setDetail('Guide')}
    else if(target==='Scores'){setTab('News');setDetail(null)}
    else if(target==='League'){setTab('Leagues');setDetail(null)}
    else if(target==='Lineup'){setTab('Team');setDetail(null)}
    else{setTab('More');setDetail(target as any)}
    requestAnimationFrame(()=>window.scrollTo({top:0,behavior:'instant' as ScrollBehavior}))
  }
  return <>
    {launching && <div className="launch-screen" aria-label="Shiva loading"><img src="/shiva-trophy.png" alt="The Shiva trophy" /></div>}
    <main className="app-shell spec-shell">
      <header className="spec-header"><div className="spec-header-spacer"/><div className="spec-wordmark"><span>♛</span>SHIVA</div><div className="spec-header-actions"><BellIcon/><AuthButton/></div></header>
      <section className="content spec-content">
        {tab==='Home' && <div className="spec-home"><Hero/><LeagueSwitcher/><AskShiva/><QuickActions open={openTarget}/><Snapshot/></div>}
        {tab==='Team' && <CoachView showTabs={false} activeTab="Lineup"/>}
        {tab==='Leagues' && <CoachView showTabs={false} activeTab="League"/>}
        {tab==='News' && <ScoresView/>}
        {tab==='More' && (detail==='Guide'?<GuideView/>:detail==='Scores'?<ScoresView/>:detail==='Start / Sit'?<CoachView showTabs={false} activeTab="Start / Sit"/>:detail==='Waivers'?<CoachView showTabs={false} activeTab="Waivers"/>:detail==='Players'?<CoachView showTabs={false} activeTab="Players"/>:<MoreHub open={openTarget}/>)}
      </section>
      <nav className="bottom-nav spec-bottom" aria-label="Primary navigation">{NAV_ITEMS.map(([item,icon])=><button type="button" key={item} aria-label={item==='Team'?'My Team':item} className={tab===item?'active':''} onClick={()=>{setTab(item);setDetail(null);window.scrollTo({top:0,behavior:'instant' as ScrollBehavior})}}><span className="spec-nav-icon">{icon}</span><span>{item==='Team'?'My Team':item}</span></button>)}</nav>
    </main>
  </>
}
