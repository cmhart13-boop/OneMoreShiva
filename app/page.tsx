'use client'

import { useEffect, useState } from 'react'
import AuthButton from '../components/AuthButton'
import CoachView from '../components/CoachView'
import GuideView from '../components/GuideView'
import ScoresView from '../components/ScoresView'
import { activateLeague } from '../lib/league-client'
import type { NewsArticle, SavedLeague } from '../lib/types'

type Tab = 'Home' | 'Leagues' | 'Ask Shiva' | 'Players' | 'Tools' | 'More'
type AskScope = 'league' | 'all'
type Detail = 'Guide' | 'Scores' | 'Waivers' | 'Start / Sit' | 'Lineup' | null
type IconName = 'home' | 'trophy' | 'chat' | 'bars' | 'swap' | 'news' | 'users' | 'more' | 'plus' | 'document' | 'waivers'

const NAV_ITEMS: Array<{ tab:Tab; label:string; icon:IconName }> = [
  { tab:'Home', label:'Home', icon:'home' },
  { tab:'Leagues', label:'Leagues', icon:'trophy' },
  { tab:'Ask Shiva', label:'Ask Shiva', icon:'chat' },
  { tab:'Players', label:'Players', icon:'users' },
  { tab:'Tools', label:'Tools', icon:'bars' },
  { tab:'More', label:'More', icon:'more' },
]

const HOME_SHORTCUTS: Array<{ label:string; icon:IconName; target:string }> = [
  { label:'My Leagues', icon:'trophy', target:'League' },
  { label:'Ask Shiva', icon:'chat', target:'Ask Shiva' },
  { label:'Projections', icon:'bars', target:'Players' },
  { label:'Start/Sit', icon:'swap', target:'Start / Sit' },
  { label:'Player News', icon:'news', target:'Scores' },
]

const QUICK_ACTIONS: Array<{ label:string; icon:IconName; target:string; primary?:boolean }> = [
  { label:'Set Lineup', icon:'plus', target:'Lineup', primary:true },
  { label:'View Matchups', icon:'users', target:'Lineup' },
  { label:'Trade Analyzer', icon:'swap', target:'Players' },
  { label:'Waiver Wire', icon:'document', target:'Waivers' },
  { label:'Check Projections', icon:'bars', target:'Players' },
]

function AppIcon({ name }:{ name:IconName }) {
  const common = { fill:'none', stroke:'currentColor', strokeWidth:1.8, strokeLinecap:'round' as const, strokeLinejoin:'round' as const }
  return <svg className="og-icon" viewBox="0 0 24 24" aria-hidden="true" {...common}>
    {name === 'home' && <><path d="m3 11 9-8 9 8"/><path d="M5.5 9.5V21h13V9.5"/></>}
    {name === 'trophy' && <><path d="M8 4h8v4c0 4-1.8 6-4 6s-4-2-4-6V4Z"/><path d="M8 6H4v2c0 2.2 1.5 3.7 4.2 4M16 6h4v2c0 2.2-1.5 3.7-4.2 4M12 14v4M8 21h8M9 18h6"/></>}
    {name === 'chat' && <><path d="M4 5.5h16v11H9l-5 3v-14Z"/><path d="M8 11h.01M12 11h.01M16 11h.01"/></>}
    {name === 'bars' && <><path d="M5 20v-6h3v6M10.5 20V9h3v11M16 20V4h3v16"/></>}
    {name === 'swap' && <><path d="M7 3 3 7l4 4M3 7h14a4 4 0 0 1 4 4M17 21l4-4-4-4M21 17H7a4 4 0 0 1-4-4"/></>}
    {name === 'news' && <><path d="M6 3h12v18H6zM9 7h6M9 11h6M9 15h4"/><path d="M3 7h3v12a2 2 0 0 1-2 2"/></>}
    {name === 'users' && <><circle cx="9" cy="8" r="3"/><path d="M3.5 19c.4-3.5 2.3-5 5.5-5s5.1 1.5 5.5 5M15 5.5a3 3 0 0 1 0 5.8M16.5 14c2.5.3 3.8 1.8 4 4.5"/></>}
    {name === 'more' && <><circle cx="5" cy="12" r="1" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1" fill="currentColor" stroke="none"/><circle cx="19" cy="12" r="1" fill="currentColor" stroke="none"/></>}
    {name === 'plus' && <><circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/></>}
    {name === 'document' && <><path d="M6 3h8l4 4v14H6zM14 3v5h4M9 12h6M9 16h6"/></>}
    {name === 'waivers' && <><path d="M8 20h8M9 17h6M10 4h4v8a2 2 0 0 1-4 0V4Z"/><path d="M8.5 8h7M8 21h8"/></>}
  </svg>
}

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

function Hero() {
  return <section className="og-hero" aria-label="Shiva Fantasy Football — smarter players, better decisions, more wins" />
}

function HomeShortcuts({ open }:{ open:(target:string)=>void }) {
  return <nav className="og-shortcuts" aria-label="Shiva features">
    {HOME_SHORTCUTS.map(item => <button key={item.label} type="button" onClick={()=>open(item.target)}><AppIcon name={item.icon}/><span>{item.label}</span></button>)}
  </nav>
}

function LeagueOverview({ open }:{ open:(target:string)=>void }) {
  const [leagues,setLeagues] = useState<SavedLeague[]>([])
  useEffect(() => {
    const load = () => fetch('/api/leagues',{ cache:'no-store' }).then(r=>r.ok?r.json():null).then(d=>setLeagues(d?.leagues || [])).catch(()=>setLeagues([]))
    load(); window.addEventListener('shiva:league-changed',load)
    return()=>window.removeEventListener('shiva:league-changed',load)
  },[])

  return <article className="og-panel og-leagues-panel">
    <header><h2>MY LEAGUES</h2><button type="button" onClick={()=>open('League')}>View All <span>›</span></button></header>
    <div className="og-league-list">
      {leagues.slice(0,3).map((saved,index) => {
        const leagueData:any = saved.league_data
        const team = leagueData?.teams?.find((row:any)=>String(row.id)===String(saved.team_id))
        const sorted = [...(leagueData?.teams || [])].sort((a:any,b:any)=>(b.wins || 0)-(a.wins || 0)||(a.losses || 0)-(b.losses || 0))
        const rank = Math.max(1,sorted.findIndex((row:any)=>String(row.id)===String(saved.team_id))+1)
        const count = leagueData?.teams?.length || 0
        return <button className="og-league-row" type="button" key={saved.id} onClick={()=>{ if(leagueData) activateLeague(leagueData,saved.team_id); open('League') }}>
          <span className={`og-team-mark mark-${index+1}`}><AppIcon name="trophy"/></span>
          <span className="og-league-copy"><b>{team?.name || saved.nickname || saved.league_name || 'Fantasy League'}</b><small>{count ? `${count}-Team ` : ''}{String(saved.provider || 'ESPN').toUpperCase()}</small></span>
          <span className="og-record"><strong>{rank}<sup>{rank===1?'st':rank===2?'nd':rank===3?'rd':'th'}</sup></strong><small>({team?.wins || 0}-{team?.losses || 0})</small></span>
        </button>
      })}
      {!leagues.length && <button className="og-league-row og-empty-league" type="button" onClick={()=>open('League')}>
        <span className="og-team-mark mark-1"><AppIcon name="plus"/></span>
        <span className="og-league-copy"><b>Connect your league</b><small>ESPN OR SLEEPER</small></span>
        <span className="og-connect-arrow">›</span>
      </button>}
    </div>
  </article>
}

function QuickActions({ open }:{ open:(target:string)=>void }) {
  return <article className="og-panel og-actions-panel">
    <header><h2>QUICK ACTIONS</h2></header>
    <div className="og-action-list">{QUICK_ACTIONS.map(item=><button type="button" key={item.label} className={item.primary?'primary':''} onClick={()=>open(item.target)}><AppIcon name={item.icon}/><span>{item.label}</span></button>)}</div>
  </article>
}

function HomeNews({ open }:{ open:(target:string)=>void }) {
  const [news,setNews] = useState<NewsArticle[]>([])
  useEffect(()=>{fetch('/api/news').then(r=>r.json()).then(d=>setNews((d.articles || []).filter((item:NewsArticle)=>item.image).slice(0,3))).catch(()=>setNews([]))},[])
  return <section className="og-panel og-news">
    <header><h2>TOP NEWS</h2><button type="button" onClick={()=>open('Scores')}>See All <span>›</span></button></header>
    <div className="og-news-grid">
      {(news.length ? news : [null,null,null]).map((article,index)=><a key={article?.headline || index} className="og-news-card" href={article?.url || undefined} target={article?.url?'_blank':undefined} rel="noreferrer">
        <div className="og-news-image">{article?.image ? <img src={article.image} alt="" loading="lazy"/> : <span />}</div>
        <div className="og-news-copy"><em className={`tag-${index+1}`}>{index===0?'INJURY UPDATE':index===1?'ANALYSIS':'WAIVER WIRE'}</em><b>{article?.headline || 'Latest fantasy football intelligence'}</b><small>{article?.published || 'Live updates'}</small></div>
      </a>)}
    </div>
  </section>
}

function Home({ open }:{ open:(target:string)=>void }) {
  return <div className="og-home"><Hero/><HomeShortcuts open={open}/><section className="og-dashboard"><LeagueOverview open={open}/><QuickActions open={open}/></section><HomeNews open={open}/></div>
}

function AskShiva() {
  const [scope,setScope] = useState<AskScope>('league')
  const [question,setQuestion] = useState('')
  const [answer,setAnswer] = useState('')
  const [status,setStatus] = useState('')
  const [leagues,setLeagues] = useState<SavedLeague[]>([])
  useEffect(()=>{fetch('/api/leagues',{cache:'no-store'}).then(r=>r.ok?r.json():null).then(d=>setLeagues(d?.leagues || [])).catch(()=>{})},[])
  const ask = async () => {
    if(!question.trim()) return
    setStatus('Thinking…'); setAnswer('')
    const active = activeLeagueContext(); const context:string[] = []
    if(scope==='league' && active){context.push(`League: ${active.league?.league?.name || ''}`);if(active.team?.name)context.push(`Team: ${active.team.name}`);if(active.roster?.length)context.push(`Roster: ${active.roster.map((row:any)=>`${row.slot} ${row.player}`).join(', ')}`)}
    if(scope==='all'){for(const saved of leagues){const team=saved.league_data?.teams?.find((item:any)=>String(item.id)===String(saved.team_id));const roster=(saved.league_data?.roster || []).filter((row:any)=>String(row.teamId)===String(saved.team_id));context.push(`League: ${saved.league_data?.league?.name || saved.league_name || saved.league_id}; Team: ${team?.name || saved.team_name || ''}; Roster: ${roster.map((row:any)=>`${row.slot} ${row.player}`).join(', ')}`)}}
    try{const response=await fetch('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:question.trim(),context:context.join('\n')})});const data=await response.json();if(!response.ok)throw new Error(data.error || 'Shiva Intelligence unavailable.');setAnswer(data.answer || '');setStatus('')}catch(error){setStatus(error instanceof Error?error.message:'Shiva Intelligence unavailable.')}
  }
  return <div className="og-inner-page og-ask-page"><div className="og-ask-title"><span><img src="/shiva-trophy-clean.svg" alt=""/></span><div><small>FANTASY INTELLIGENCE</small><h1>Ask Shiva</h1></div></div><section className="og-ask-card"><div className="og-scope"><button className={scope==='league'?'active':''} onClick={()=>setScope('league')}>This League</button><button className={scope==='all'?'active':''} onClick={()=>setScope('all')}>All My Leagues</button></div><label htmlFor="ask-shiva">What do you need to win?</label><div className="og-composer"><input id="ask-shiva" aria-label="Ask Shiva question" value={question} onChange={e=>setQuestion(e.target.value)} onKeyDown={e=>{if(e.key==='Enter')ask()}} placeholder="Should I start Jeanty or Skattebo?"/>{question&&<button className="og-clear" aria-label="Clear question" onClick={()=>{setQuestion('');setAnswer('');setStatus('')}}>×</button>}<button className="og-send" aria-label="Send to Shiva" onClick={ask}>➤</button></div>{(answer||status)&&<div className="og-answer"><small>SHIVA SAYS</small><p>{status || answer}</p></div>}</section></div>
}

function ToolsHub({ open }:{ open:(target:string)=>void }) {
  return <div className="og-inner-page approved-more"><h1>Shiva Tools</h1><button onClick={()=>open('Start / Sit')}>Start / Sit</button><button onClick={()=>open('Waivers')}>Waiver Wire</button><button onClick={()=>open('Players')}>Trade Analyzer & Projections</button><button onClick={()=>open('Lineup')}>Lineup & Matchups</button></div>
}

function MoreHub({ open }:{ open:(target:string)=>void }) {
  return <div className="og-inner-page approved-more"><h1>More Shiva</h1><button onClick={()=>open('Guide')}>Draft Guide</button><button onClick={()=>open('Scores')}>Scores & NFL News</button><button onClick={()=>open('League')}>Manage Leagues</button><button onClick={()=>open('Players')}>Player Rankings</button></div>
}

export default function ShivaApp() {
  const [tab,setTab] = useState<Tab>('Home')
  const [detail,setDetail] = useState<Detail>(null)
  const [launching,setLaunching] = useState(true)
  useEffect(()=>{const timer=window.setTimeout(()=>setLaunching(false),2500);return()=>window.clearTimeout(timer)},[])
  const goTop=()=>requestAnimationFrame(()=>window.scrollTo({top:0,behavior:'instant' as ScrollBehavior}))
  const openTarget=(target:string)=>{
    if(target==='League'){setTab('Leagues');setDetail(null)}
    else if(target==='Ask Shiva'){setTab('Ask Shiva');setDetail(null)}
    else if(target==='Players'){setTab('Players');setDetail(null)}
    else if(target==='Guide'){setTab('More');setDetail('Guide')}
    else if(target==='Scores'){setTab('More');setDetail('Scores')}
    else if(target==='Start / Sit'||target==='Waivers'||target==='Lineup'){setTab('Tools');setDetail(target as Detail)}
    goTop()
  }

  return <>
    {launching&&<div className="launch-screen" aria-label="Shiva loading"><img src="/shiva-trophy.png" alt="The Shiva trophy"/></div>}
    <main className="app-shell spec-shell og-shell">
      <div className="og-auth"><AuthButton/></div>
      <section className="content spec-content og-content">
        {tab==='Home'&&<Home open={openTarget}/>}
        {tab==='Leagues'&&<div className="og-inner-page"><CoachView showTabs={false} activeTab="Overview"/></div>}
        {tab==='Ask Shiva'&&<AskShiva/>}
        {tab==='Players'&&<div className="og-inner-page"><CoachView showTabs={false} activeTab="Players"/></div>}
        {tab==='Tools'&&(detail==='Start / Sit'?<div className="og-inner-page"><CoachView showTabs={false} activeTab="Start / Sit"/></div>:detail==='Waivers'?<div className="og-inner-page"><CoachView showTabs={false} activeTab="Waivers"/></div>:detail==='Lineup'?<div className="og-inner-page"><CoachView showTabs={false} activeTab="Lineup"/></div>:<ToolsHub open={openTarget}/>)}
        {tab==='More'&&(detail==='Guide'?<div className="og-inner-page"><GuideView/></div>:detail==='Scores'?<div className="og-inner-page"><ScoresView/></div>:<MoreHub open={openTarget}/>)}
      </section>
      <nav className="bottom-nav spec-bottom og-bottom" aria-label="Primary navigation">{NAV_ITEMS.map(item=><button type="button" key={item.tab} aria-label={item.label} className={tab===item.tab?'active':''} onClick={()=>{setTab(item.tab);setDetail(null);goTop()}}><AppIcon name={item.icon}/><span>{item.label}</span></button>)}</nav>
    </main>
  </>
}
