'use client'

import { useEffect, useRef, useState } from 'react'
import Image from 'next/image'
import AuthButton from '../components/AuthButton'
import CoachView from '../components/CoachView'
import GuideView from '../components/GuideView'
import { PlayerAvatar } from '../components/PlayerMedia'
import ScoresView from '../components/ScoresView'
import type { Player, SavedLeague } from '../lib/types'

type Tab = 'Home' | 'Leagues' | 'Ask Shiva' | 'Players' | 'Tools' | 'More'
type AskScope = 'league' | 'all'
type Detail = 'Guide' | 'Scores' | 'Waivers' | 'Start / Sit' | 'Lineup' | null
type IconName = 'home' | 'trophy' | 'chat' | 'bars' | 'swap' | 'news' | 'users' | 'more' | 'plus' | 'document' | 'player-add' | 'calendar'

const NAV_ITEMS:Array<{tab:Tab;label:string;icon:IconName;detail?:Detail}> = [
  {tab:'Home',label:'Home',icon:'home'},
  {tab:'Tools',label:'My Team',icon:'users',detail:'Lineup'},
  {tab:'Leagues',label:'Leagues',icon:'trophy'},
  {tab:'More',label:'News',icon:'news',detail:'Scores'},
  {tab:'More',label:'More',icon:'more'},
]

const SHORTCUTS:Array<{label:string;description:string;icon:IconName;target:string}> = [
  {label:'Start / Sit',description:'Get lineup advice',icon:'swap',target:'Start / Sit'},
  {label:'Waivers',description:'Find top adds',icon:'player-add',target:'Waivers'},
  {label:'Trade Analyzer',description:'Win more trades',icon:'swap',target:'Players'},
  {label:'Draft Guide',description:'Prep for your draft',icon:'document',target:'Guide'},
  {label:'Power Rankings',description:'See the big picture',icon:'bars',target:'Players'},
  {label:'Schedule',description:'Matchups & strength',icon:'calendar',target:'Scores'},
]

function AppIcon({name}:{name:IconName}) {
  const common={fill:'none',stroke:'currentColor',strokeWidth:1.8,strokeLinecap:'round' as const,strokeLinejoin:'round' as const}
  return <svg className="og-icon" viewBox="0 0 24 24" aria-hidden="true" {...common}>
    {name==='home'&&<><path d="m3 11 9-8 9 8"/><path d="M5.5 9.5V21h13V9.5"/></>}
    {name==='trophy'&&<><path d="M8 4h8v4c0 4-1.8 6-4 6s-4-2-4-6V4Z"/><path d="M8 6H4v2c0 2.2 1.5 3.7 4.2 4M16 6h4v2c0 2.2-1.5 3.7-4.2 4M12 14v4M8 21h8M9 18h6"/></>}
    {name==='chat'&&<><path d="M4 5.5h16v11H9l-5 3v-14Z"/><path d="M8 11h.01M12 11h.01M16 11h.01"/></>}
    {name==='bars'&&<><path d="M5 20v-6h3v6M10.5 20V9h3v11M16 20V4h3v16"/></>}
    {name==='swap'&&<><path d="M7 3 3 7l4 4M3 7h14a4 4 0 0 1 4 4M17 21l4-4-4-4M21 17H7a4 4 0 0 1-4-4"/></>}
    {name==='news'&&<><path d="M6 3h12v18H6zM9 7h6M9 11h6M9 15h4"/><path d="M3 7h3v12a2 2 0 0 1-2 2"/></>}
    {name==='users'&&<><circle cx="9" cy="8" r="3"/><path d="M3.5 19c.4-3.5 2.3-5 5.5-5s5.1 1.5 5.5 5M15 5.5a3 3 0 0 1 0 5.8M16.5 14c2.5.3 3.8 1.8 4 4.5"/></>}
    {name==='more'&&<><circle cx="5" cy="12" r="1" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1" fill="currentColor" stroke="none"/><circle cx="19" cy="12" r="1" fill="currentColor" stroke="none"/></>}
    {name==='plus'&&<><circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/></>}
    {name==='document'&&<><path d="M6 3h8l4 4v14H6zM14 3v5h4M9 12h6M9 16h6"/></>}
    {name==='player-add'&&<><circle cx="9" cy="7" r="3.5"/><path d="M2.8 20c.4-4.3 2.5-6.4 6.2-6.4s5.8 2.1 6.2 6.4M18.5 7v7M15 10.5h7"/></>}
    {name==='calendar'&&<><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01M16 18h.01"/></>}
  </svg>
}

function activeLeagueContext(){
  try{const raw=sessionStorage.getItem('shiva-league');const teamId=sessionStorage.getItem('shiva-team-id');if(!raw)return null;const league=JSON.parse(raw);const team=league?.teams?.find((item:any)=>String(item.id)===String(teamId));const roster=(league?.roster||[]).filter((row:any)=>String(row.teamId)===String(teamId));return{league,team,roster}}catch{return null}
}
const key=(name:string)=>name.toLowerCase().replace(/[^a-z0-9]/g,'')
const score=(value:number|null|undefined)=>value==null||!Number.isFinite(value)?'0.0':value.toFixed(1)

function Hero(){
  return <section className="live-hero" aria-label="Shiva fantasy football home">
    <div className="live-hero-stadium"/>
    <div className="live-hero-shade"/>
    <div className="live-hero-wordmark" aria-label="Shiva Fantasy IQ"><span className="live-hero-logo-mark" aria-hidden="true"><Image src="/shiva-logo-trophy.webp" alt="" fill sizes="31px" priority/></span><span className="live-hero-logo-copy"><b>Shiva</b><small>FANTASY IQ</small></span></div>
    <div className="live-hero-actions">
      <div className="live-profile"><AuthButton respondToAuthRequests={false}/></div>
    </div>
  </section>
}

function Helmet({side}:{side:'left'|'right'}){
  return <span className={`live-helmet ${side}`} aria-hidden="true"><Image src={side==='left'?'/helmet-gold-3d.webp':'/helmet-red-3d.webp'} alt="" fill sizes="(max-width: 430px) 38vw, 150px" priority/></span>
}

function AskHome({open,leagues}:{open:(target:string)=>void;leagues:SavedLeague[]}){
  const [scope,setScope]=useState<AskScope>('league');const [question,setQuestion]=useState('');const [answer,setAnswer]=useState('');const [status,setStatus]=useState('');const input=useRef<HTMLInputElement>(null)
  const ask=async()=>{if(!question.trim())return input.current?.focus();setStatus('Thinking…');setAnswer('');const active=activeLeagueContext();const context:string[]=[];if(scope==='league'){const fallback=leagues[0];const league=active?.league||fallback?.league_data;const team=active?.team||league?.teams?.find((item:any)=>String(item.id)===String(fallback?.team_id));const roster=active?.roster||(league?.roster||[]).filter((row:any)=>String(row.teamId)===String(fallback?.team_id));if(league?.league?.name)context.push(`League: ${league.league.name}`);if(team?.name)context.push(`Team: ${team.name}`);if(roster?.length)context.push(`Roster: ${roster.map((row:any)=>`${row.slot} ${row.player}`).join(', ')}`)}else{for(const saved of leagues){const team=saved.league_data?.teams?.find((item:any)=>String(item.id)===String(saved.team_id));const roster=(saved.league_data?.roster||[]).filter((row:any)=>String(row.teamId)===String(saved.team_id));context.push(`League: ${saved.league_data?.league?.name||saved.league_name||saved.league_id}; Team: ${team?.name||saved.team_name||''}; Roster: ${roster.map((row:any)=>`${row.slot} ${row.player}`).join(', ')}`)}}try{const response=await fetch('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:question.trim(),context:context.join('\n')})});const data=await response.json();if(!response.ok)throw new Error(data.error||'Shiva Intelligence unavailable.');setAnswer(data.answer||'');setStatus('')}catch(error){setStatus(error instanceof Error?error.message:'Shiva Intelligence unavailable.')}}
  return <section className="og-home-ask" aria-label="Ask Shiva"><header><div className="og-home-ask-title"><span><Image src="/shiva-logo-trophy.webp" alt="" width={32} height={32}/></span><h2>Ask Shiva</h2></div><div className="og-home-scope"><button type="button" className={scope==='league'?'active':''} onClick={()=>setScope('league')}>This League</button><button type="button" className={scope==='all'?'active':''} onClick={()=>setScope('all')}>All My Leagues</button></div></header><div className="og-home-composer"><input ref={input} aria-label="Ask Shiva home question" value={question} onChange={e=>{setQuestion(e.target.value);setAnswer('');setStatus('')}} onKeyDown={e=>{if(e.key==='Enter')ask()}} placeholder="Ask Shiva a question…"/>{question&&<button type="button" className="og-home-clear" aria-label="Clear home question" onClick={()=>{setQuestion('');setAnswer('');setStatus('')}}>×</button>}<button type="button" className="og-home-send" aria-label="Send home question to Shiva" onClick={ask}>➤</button></div>{(answer||status)&&<div className="og-home-answer"><div className="og-home-answer-head"><b>SHIVA SAYS</b><span><i/><i/><i/> {answer?'HIGH CONFIDENCE':'WORKING'}</span></div><p>{status||answer}</p><div className="og-home-answer-actions"><button onClick={()=>open('Lineup')}><AppIcon name="document"/>Fix Lineup</button><button onClick={()=>{setQuestion(current=>current?`Why? ${current}`:'Why is this the best move?');setAnswer('');requestAnimationFrame(()=>input.current?.focus())}}><span>?</span>Ask Why</button><button onClick={()=>open('Players')}><AppIcon name="bars"/>See Options</button></div></div>}</section>
}

function Shortcuts({open}:{open:(target:string)=>void}){return <nav className="og-shortcuts" aria-label="Shiva features">{SHORTCUTS.map(item=><button key={item.label} type="button" onClick={()=>open(item.target)}><AppIcon name={item.icon}/><span className="og-shortcut-copy"><b>{item.label}</b><small>{item.description}</small></span></button>)}</nav>}

function Dashboard({open,leagues}:{open:(target:string)=>void;leagues:SavedLeague[]}){
  const [players,setPlayers]=useState<Player[]>([]);const [page,setPage]=useState(0);const track=useRef<HTMLDivElement>(null)
  useEffect(()=>{fetch('/api/rankings').then(r=>r.ok?r.json():null).then(d=>setPlayers(d?.players||[])).catch(()=>setPlayers([]))},[])
  const playerMap=new Map(players.map(player=>[key(player.name),player]));const pages:Array<SavedLeague|null>=leagues.length?leagues:[null]
  return <section className="og-snapshots" aria-label="League dashboard"><div className="og-snapshot-track" ref={track} onScroll={e=>{const w=e.currentTarget.clientWidth;if(w)setPage(Math.round(e.currentTarget.scrollLeft/w))}}>{pages.map((saved,index)=>{const league=saved?.league_data||null;const week=league?.league.scoringPeriod||league?.league.matchupPeriod||1;const teamId=saved?.team_id??league?.teams[0]?.id??null;const team=league?.teams.find(t=>String(t.id)===String(teamId))||league?.teams[0]||null;const standings=[...(league?.teams||[])].sort((a,b)=>(b.wins??-1)-(a.wins??-1)||(a.losses??999)-(b.losses??999)||a.name.localeCompare(b.name));const matchup=league?.matchups?.find(m=>m.period===week&&(String(m.homeTeamId)===String(teamId)||String(m.awayTeamId)===String(teamId)))||league?.matchups?.find(m=>String(m.homeTeamId)===String(teamId)||String(m.awayTeamId)===String(teamId));const isHome=matchup?String(matchup.homeTeamId)===String(teamId):true;const opponentId=matchup?(isHome?matchup.awayTeamId:matchup.homeTeamId):standings.find(t=>String(t.id)!==String(teamId))?.id;const opponent=league?.teams.find(t=>String(t.id)===String(opponentId))||null;const mine=(league?.roster||[]).filter(r=>String(r.teamId)===String(teamId));const theirs=(league?.roster||[]).filter(r=>String(r.teamId)===String(opponentId));const projected=(rows:typeof mine)=>rows.filter(r=>!['BE','BN','IR'].includes(r.slot)).reduce((sum,r)=>sum+(playerMap.get(key(r.player))?.projectedPoints||0),0);const myProj=(isHome?matchup?.homeProjected:matchup?.awayProjected)??projected(mine);const oppProj=(isHome?matchup?.awayProjected:matchup?.homeProjected)??projected(theirs);const myScore=isHome?matchup?.homeScore:matchup?.awayScore;const oppScore=isHome?matchup?.awayScore:matchup?.homeScore;const rosterPlayers=mine.map(row=>({name:row.player,id:row.playerId,pos:row.position||row.slot,team:row.proTeam||'',pct:playerMap.get(key(row.player))?.percentStarted??row.percentStarted??0,injury:row.injuryStatus,ranked:playerMap.get(key(row.player))}));const fallbackPlayers=players.slice(0,5).map(player=>({name:player.name,id:player.espnId||player.id,pos:player.pos,team:player.team,pct:player.percentStarted??Math.max(20,100-player.rank*4),injury:player.injuryStatus||'',ranked:player}));const keyPlayers=(rosterPlayers.length?rosterPlayers:fallbackPlayers).sort((a,b)=>(b.ranked?.projectedPoints||b.pct)-(a.ranked?.projectedPoints||a.pct)).slice(0,5);return <div className="og-snapshot-page" key={saved?.id||index}><article className="og-snapshot-card og-my-matchup"><header><b>My Matchup</b><button onClick={()=>open('Lineup')}>{league?`Week ${week} ›`:'Open ›'}</button></header><div className="og-helmet-clash"><Helmet side="left"/><i>VS</i><Helmet side="right"/></div><div className="og-matchup-score"><div><strong>{score(myScore)}</strong><b>{team?.name||'My Team'}</b><small>Proj {score(myProj)}</small></div><div><strong>{score(oppScore)}</strong><b>{opponent?.name||'Opponent'}</b><small>Proj {score(oppProj)}</small></div></div><button className="og-view-matchup" onClick={()=>open(league?'Lineup':'League')}>{league?'View Matchup':'Connect League'}</button></article><article className="og-snapshot-card og-key-players"><header><b>Key Players</b><button onClick={()=>open('Players')}>See All ›</button></header>{keyPlayers.length?<div className="og-key-list">{keyPlayers.map(player=>{const injured=Boolean(player.injury&&!['ACTIVE','NORMAL'].includes(player.injury.toUpperCase()));const state=injured||player.pct<25?'sit':player.pct<65?'consider':'start';return <div key={`${player.id}-${player.name}`}><PlayerAvatar playerId={player.ranked?.espnId||player.ranked?.id||player.id} name={player.name}/><span><b>{player.name}</b><small>{player.pos} · {player.team||'NFL'}</small></span><em className={state}>{state==='start'?'START':state==='consider'?'CONSIDER':'SIT'}</em></div>})}</div>:<div className="og-key-empty"><AppIcon name="users"/><p>Player recommendations are loading.</p></div>}</article></div>})}</div>{pages.length>1&&<div className="og-snapshot-dots">{pages.map((saved,index)=><button key={saved?.id||index} className={index===page?'active':''} aria-label={`View league ${index+1}`} onClick={()=>{track.current?.scrollTo({left:track.current.clientWidth*index,behavior:'smooth'});setPage(index)}}/>)}</div>}</section>
}

function Home({open}:{open:(target:string)=>void}){
  const [leagues,setLeagues]=useState<SavedLeague[]>([])
  useEffect(()=>{const load=()=>fetch('/api/leagues',{cache:'no-store'}).then(r=>r.ok?r.json():null).then(d=>setLeagues(d?.leagues||[])).catch(()=>setLeagues([]));load();window.addEventListener('shiva:league-changed',load);return()=>window.removeEventListener('shiva:league-changed',load)},[])
  return <div className="og-home"><Hero/><AskHome open={open} leagues={leagues}/><Shortcuts open={open}/><Dashboard open={open} leagues={leagues}/></div>
}

function AskShiva(){const [scope,setScope]=useState<AskScope>('league');const [question,setQuestion]=useState('');const [answer,setAnswer]=useState('');const [status,setStatus]=useState('');const ask=async()=>{if(!question.trim())return;setStatus('Thinking…');setAnswer('');const active=activeLeagueContext();const context=scope==='league'&&active?`League: ${active.league?.league?.name||''}\nTeam: ${active.team?.name||''}\nRoster: ${active.roster?.map((r:any)=>`${r.slot} ${r.player}`).join(', ')||''}`:'';try{const response=await fetch('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:question.trim(),context})});const data=await response.json();if(!response.ok)throw new Error(data.error||'Shiva Intelligence unavailable.');setAnswer(data.answer||'');setStatus('')}catch(error){setStatus(error instanceof Error?error.message:'Shiva Intelligence unavailable.')}};return <div className="og-inner-page og-ask-page"><div className="og-ask-title"><span><AppIcon name="trophy"/></span><div><small>FANTASY INTELLIGENCE</small><h1>Ask Shiva</h1></div></div><section className="og-ask-card"><div className="og-scope"><button className={scope==='league'?'active':''} onClick={()=>setScope('league')}>This League</button><button className={scope==='all'?'active':''} onClick={()=>setScope('all')}>All My Leagues</button></div><label htmlFor="ask-shiva">What do you need to win?</label><div className="og-composer"><input id="ask-shiva" aria-label="Ask Shiva question" value={question} onChange={e=>setQuestion(e.target.value)} onKeyDown={e=>{if(e.key==='Enter')ask()}} placeholder="Should I start Jeanty or Skattebo?"/><button className="og-send" aria-label="Send to Shiva" onClick={ask}>➤</button></div>{(answer||status)&&<div className="og-answer"><small>SHIVA SAYS</small><p>{status||answer}</p></div>}</section></div>}
function ToolsHub({open}:{open:(target:string)=>void}){return <div className="og-inner-page approved-more"><h1>Shiva Tools</h1><button onClick={()=>open('Start / Sit')}>Start / Sit</button><button onClick={()=>open('Waivers')}>Waiver Wire</button><button onClick={()=>open('Players')}>Trade Analyzer & Projections</button><button onClick={()=>open('Lineup')}>Lineup & Matchups</button></div>}
function MoreHub({open}:{open:(target:string)=>void}){return <div className="og-inner-page approved-more"><h1>More Shiva</h1><button onClick={()=>open('Guide')}>Draft Guide</button><button onClick={()=>open('Scores')}>Scores & NFL News</button><button onClick={()=>open('League')}>Manage Leagues</button><button onClick={()=>open('Players')}>Player Rankings</button></div>}

export default function ShivaApp(){
  const [tab,setTab]=useState<Tab>('Home');const [detail,setDetail]=useState<Detail>(null);const [launching,setLaunching]=useState(true)
  useEffect(()=>{const timer=window.setTimeout(()=>setLaunching(false),2500);return()=>window.clearTimeout(timer)},[])
  const goTop=()=>requestAnimationFrame(()=>window.scrollTo({top:0,behavior:'instant' as ScrollBehavior}))
  const open=(target:string)=>{if(target==='League'){setTab('Leagues');setDetail(null)}else if(target==='Ask Shiva'){setTab('Ask Shiva');setDetail(null)}else if(target==='Players'){setTab('Players');setDetail(null)}else if(target==='Guide'){setTab('More');setDetail('Guide')}else if(target==='Scores'){setTab('More');setDetail('Scores')}else if(target==='Start / Sit'||target==='Waivers'||target==='Lineup'){setTab('Tools');setDetail(target as Detail)}goTop()}
  return <>{launching&&<div className="launch-screen" aria-label="Shiva loading"><img src="/shiva-trophy.png" alt="The Shiva trophy"/></div>}<main className="app-shell spec-shell og-shell"><section className="content spec-content og-content">{tab==='Home'&&<Home open={open}/>} {tab==='Leagues'&&<div className="og-inner-page"><CoachView showTabs={false} activeTab="Overview"/></div>} {tab==='Ask Shiva'&&<AskShiva/>} {tab==='Players'&&<div className="og-inner-page"><CoachView showTabs={false} activeTab="Players"/></div>} {tab==='Tools'&&(detail==='Start / Sit'?<div className="og-inner-page"><CoachView showTabs={false} activeTab="Start / Sit"/></div>:detail==='Waivers'?<div className="og-inner-page"><CoachView showTabs={false} activeTab="Waivers"/></div>:detail==='Lineup'?<div className="og-inner-page"><CoachView showTabs={false} activeTab="Lineup"/></div>:<ToolsHub open={open}/>)} {tab==='More'&&(detail==='Guide'?<div className="og-inner-page"><GuideView/></div>:detail==='Scores'?<div className="og-inner-page"><ScoresView/></div>:<MoreHub open={open}/>)}</section><nav className="bottom-nav spec-bottom og-bottom" aria-label="Primary navigation">{NAV_ITEMS.map(item=>{const active=tab===item.tab&&(item.detail?detail===item.detail:item.tab==='More'?detail===null:true);return <button type="button" key={item.label} aria-label={item.label} className={active?'active':''} onClick={()=>{setTab(item.tab);setDetail(item.detail||null);goTop()}}><AppIcon name={item.icon}/><span>{item.label}</span></button>})}</nav></main></>
}
