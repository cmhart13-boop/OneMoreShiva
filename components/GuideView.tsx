'use client'

import { useEffect, useMemo, useState } from 'react'
import { featuredPlayers, guideSections, researchArticles, strategyRounds } from '../lib/guide'
import type { Player } from '../lib/types'

type View = 'home' | 'rankings' | 'strategy' | 'research' | 'luck' | 'players'

export default function GuideView() {
  const [view, setView] = useState<View>('home')
  const [rankFilter, setRankFilter] = useState('ALL')
  const [players, setPlayers] = useState<Player[]>([])
  const [articleId, setArticleId] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/rankings').then((response) => response.json()).then((data) => setPlayers(data.players || [])).catch(() => setPlayers([]))
  }, [])

  const filtered = useMemo(() => players.filter((player) => rankFilter === 'ALL' || player.pos === rankFilter).slice(0, rankFilter === 'ALL' ? 75 : 40), [players, rankFilter])
  const article = researchArticles.find((item) => item.id === articleId)

  if (view === 'home') return <>
    <div className="section-kicker">2026 DRAFT GUIDE</div>
    <h1>2026 Shiva Draft Guide</h1>
    <p className="lede">Full-PPR intelligence built for draft-day decisions.</p>
    <div className="guide-grid">{guideSections.map((section) => <button className="guide-card" key={section.id} onClick={() => setView(section.id as View)}><h2>{section.title}</h2><p>{section.desc}</p><span>Open section →</span></button>)}</div>
  </>

  return <>
    <button className="back-link" onClick={() => { setView('home'); setArticleId(null) }}>← Guide contents</button>
    {view === 'rankings' && <>
      <div className="section-kicker">SHIVA BOARD</div><h1>2026 Rankings</h1>
      <div className="filter-pills">{['ALL','QB','RB','WR','TE'].map((filter) => <button key={filter} className={rankFilter === filter ? 'active' : ''} onClick={() => setRankFilter(filter)}>{filter === 'ALL' ? 'PPR' : filter}</button>)}</div>
      <div className="rank-list">{filtered.map((player, index) => <div className="rank-row" key={player.id}><span className="rank-number">{index + 1}</span><span className={`pos-chip pos-${player.pos}`}>{player.pos}</span><div><b>{player.name}</b><small>{player.team || '—'} · ADP {player.adp?.toFixed(1) ?? '—'}</small></div><strong>#{player.rank}</strong></div>)}</div>
    </>}

    {view === 'strategy' && <>
      <div className="section-kicker">ROSTER CONSTRUCTION</div><h1>Draft Strategy</h1>
      <p className="lede">Build for weekly ceiling without giving away value to the room.</p>
      <div className="strategy-grid"><article className="panel"><span className="eyebrow">EARLY ROUNDS</span><h2>RB/WR foundation</h2><p>Attack elite workload and target volume first. Use positional scarcity only when the value actually supports it.</p></article><article className="panel"><span className="eyebrow">VALUE RULE</span><h2>Rank ≠ draft slot</h2><p>Use Shiva ranking against ADP. Capture the discount instead of paying your ranking when the room will let a player fall.</p></article></div>
      <div className="round-plan">{strategyRounds.map(([rounds, text]) => <div key={rounds}><b>{rounds}</b><p>{text}</p></div>)}</div>
    </>}

    {view === 'research' && <>
      <div className="section-kicker">RESEARCH LIBRARY</div><h1>Research</h1>
      {article ? <article className="article-detail"><button className="back-link" onClick={() => setArticleId(null)}>← Research notes</button><h2>{article.title}</h2><p>{article.body}</p>{article.players.length > 0 && <div className="tag-row">{article.players.map((name) => <span key={name}>{name}</span>)}</div>}</article> : <div className="article-grid">{researchArticles.map((item) => <button key={item.id} className="article-card" onClick={() => setArticleId(item.id)}><h2>{item.title}</h2><p>{item.body}</p><span>Open research →</span></button>)}</div>}
    </>}

    {view === 'luck' && <>
      <div className="section-kicker">REGRESSION SIGNAL</div><h1>Luck Metric</h1>
      <article className="panel hero-panel"><span className="eyebrow">2025 LUCK MODEL</span><h2>Separate repeatable skill from noisy outcomes.</h2><p>The guide uses a multi-factor framework to flag players whose fantasy output was materially pushed up or down by events unlikely to repeat at the same rate.</p></article>
      <div className="strategy-grid"><article className="panel"><h2>CeeDee Lamb</h2><p>Rated among the strongest upward-regression profiles after an estimated ~2.7 PPG of negative-luck drag in 2025.</p></article><article className="panel"><h2>How to use it</h2><p>Luck never replaces talent, role or price. It is a tie-breaker when market cost and underlying opportunity already make sense.</p></article></div>
    </>}

    {view === 'players' && <>
      <div className="section-kicker">PLAYER SHORTCUTS</div><h1>Player Cards</h1>
      <p className="lede">Quick access to the players most often referenced by the guide.</p>
      <div className="player-card-grid">{featuredPlayers.map((name) => { const player = players.find((item) => item.name === name); return <article className="player-card" key={name}><span className={`pos-chip pos-${player?.pos || 'NA'}`}>{player?.pos || '—'}</span><h2>{name}</h2><p>{player ? `${player.team} · Overall #${player.rank} · ADP ${player.adp?.toFixed(1) ?? '—'}` : 'Guide research target'}</p></article> })}</div>
    </>}
  </>
}
