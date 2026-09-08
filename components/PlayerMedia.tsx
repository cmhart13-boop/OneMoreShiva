'use client'

import { useEffect, useRef, useState } from 'react'
import type { Evidence, NewsArticle, Player } from '../lib/types'

const TEAM_COLOR: Record<string, string> = {
  ARI:'#97233f', ATL:'#a71930', BAL:'#241773', BUF:'#00338d', CAR:'#0085ca', CHI:'#0b162a', CIN:'#fb4f14', CLE:'#311d00', DAL:'#003594', DEN:'#fb4f14', DET:'#0076b6', GB:'#203731', HOU:'#03202f', IND:'#002c5f', JAX:'#006778', KC:'#e31837', LV:'#000000', LAC:'#0080c6', LAR:'#003594', MIA:'#008e97', MIN:'#4f2683', NE:'#002244', NO:'#d3bc8d', NYG:'#0b2265', NYJ:'#125740', PHI:'#004c54', PIT:'#101820', SEA:'#002244', SF:'#aa0000', TB:'#d50a0a', TEN:'#0c2340', WAS:'#5a1414'
}

export function playerHeadshotUrl(playerId: string, large = false) {
  if (!playerId) return ''
  const size = large ? '&w=320&h=230' : '&w=96&h=70'
  return `https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/${encodeURIComponent(playerId)}.png${size}`
}

export function PlayerAvatar({ playerId, name, large = false, className = '' }: { playerId?: string; name: string; large?: boolean; className?: string }) {
  const [failed, setFailed] = useState(!playerId)
  useEffect(() => setFailed(!playerId), [playerId])
  if (failed) return <span className={`player-silhouette ${large ? 'large' : ''} ${className}`} aria-label={`${name} photo unavailable`}><span aria-hidden="true">●</span></span>
  return <img className={`${large ? 'player-detail-photo' : 'player-avatar'} ${className}`} src={playerHeadshotUrl(playerId || '', large)} alt={name} loading="lazy" decoding="async" onError={() => setFailed(true)} />
}

export type PlayerDetailData = Partial<Player> & {
  id: string
  name: string
  team?: string
  pos?: string
  rank?: number | null
  ppg?: number | null
  seasonPoints?: number | null
  percentOwned?: number | null
  injuryStatus?: string
}

function metric(value: number | null | undefined, digits = 1, suffix = '') {
  return value === null || value === undefined || !Number.isFinite(value) ? '—' : `${value.toFixed(digits)}${suffix}`
}

export function PlayerDetailOverlay({ player, onClose }: { player: PlayerDetailData; onClose: () => void }) {
  const [evidence, setEvidence] = useState<Evidence | null>(null)
  const [news, setNews] = useState<NewsArticle[]>([])
  const [newsStatus, setNewsStatus] = useState('')
  const [tab, setTab] = useState<'Overview'|'News'|'Stats'|'Game Log'|'Projections'>('Overview')
  const closeButton = useRef<HTMLButtonElement>(null)
  const newsLoaded = useRef(false)
  useEffect(() => {
    let active = true
    fetch(`/api/evidence?player=${encodeURIComponent(player.name)}`)
      .then((response) => response.json())
      .then((data) => { if (active) setEvidence(data.evidence || null) })
      .catch(() => {})
    return () => { active = false }
  }, [player.name])

  useEffect(() => {
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    closeButton.current?.focus()
    const keydown = (event:KeyboardEvent) => { if (event.key === 'Escape') onClose() }
    window.addEventListener('keydown', keydown)
    return () => { document.body.style.overflow = previousOverflow; window.removeEventListener('keydown', keydown) }
  }, [onClose])

  useEffect(() => {
    if (tab !== 'News' || newsLoaded.current) return
    newsLoaded.current = true
    setNewsStatus('Loading current player news…')
    fetch(`/api/news?player=${encodeURIComponent(player.name)}`)
      .then(async response => response.ok ? response.json() : Promise.reject(new Error('Player news is unavailable.')))
      .then(data => { setNews(data.articles || []); setNewsStatus('') })
      .catch(error => setNewsStatus(error instanceof Error ? error.message : 'Player news is unavailable.'))
  }, [tab, player.name])

  const ppg = player.ppg ?? evidence?.ppg ?? null
  const seasonPoints = player.seasonPoints ?? (evidence?.ppg != null && evidence?.games ? evidence.ppg * evidence.games : null)
  const posRank = player.posRank ?? null
  const teamColor = TEAM_COLOR[player.team || ''] || '#12344a'

  const tabs = ['Overview','News','Stats','Game Log','Projections'] as const
  const log = [...(evidence?.gameLog || [])].sort((a,b) => b.week-a.week)

  return <div className="player-page-backdrop" role="presentation" onPointerDown={(event) => { if (event.target === event.currentTarget) onClose() }}>
    <section className="player-page" role="dialog" aria-modal="true" aria-label={`${player.name} player page`} onClick={(event) => event.stopPropagation()}>
      <button ref={closeButton} className="player-page-close" type="button" aria-label="Close player page" onClick={onClose}><span aria-hidden="true">×</span><span>Back</span></button>
      <div className="player-page-hero" style={{ '--team-color': teamColor } as React.CSSProperties}>
        <div className="player-page-copy">
          <h2>{player.name}</h2>
          <div className="player-page-meta">{[player.team, player.pos, player.injuryStatus].filter(Boolean).join(' · ')}</div>
        </div>
        <PlayerAvatar playerId={player.espnId || player.id} name={player.name} large />
      </div>
      <div className="player-stat-strip">
        <div><b>{posRank ? `#${posRank}` : player.rank ? `#${player.rank}` : '—'}</b><span>POS RANK</span></div>
        <div><b>{metric(ppg)}</b><span>AVG FPTS</span></div>
        <div><b>{metric(seasonPoints)}</b><span>SEASON PTS</span></div>
        <div><b>{metric(player.percentOwned, 0, '%')}</b><span>%ROST</span></div>
      </div>
      <div className="player-page-tabs" role="tablist" aria-label="Player information">{tabs.map(item => <button type="button" role="tab" aria-selected={tab === item} className={tab === item ? 'active' : ''} key={item} onClick={() => setTab(item)}>{item}</button>)}</div>
      {tab === 'Overview' && <div className="player-page-section" role="tabpanel">
        <h3>PLAYER OVERVIEW</h3>
        <div className="player-overview-grid">
          <div><span>Shiva Rank</span><b>{player.rank ? `#${player.rank}` : '—'}</b></div>
          <div><span>ADP</span><b>{metric(player.adp)}</b></div>
          <div><span>Team</span><b>{player.team || '—'}</b></div>
          <div><span>Position</span><b>{player.pos || '—'}</b></div>
        </div>
      </div>}
      {tab === 'Stats' && <div className="player-page-section" role="tabpanel"><h3>{evidence?.season || 'LATEST'} STATS</h3><div className="player-overview-grid"><div><span>Games</span><b>{evidence?.gameLog?.length ?? '—'}</b></div><div><span>PPR / Game</span><b>{metric(evidence?.ppg)}</b></div><div><span>Recent Role</span><b>{metric(evidence?.recent)}</b></div><div><span>15+ Rate</span><b>{metric(evidence?.rate15,0,'%')}</b></div><div><span>Floor</span><b>{metric(evidence?.floor)}</b></div><div><span>Ceiling</span><b>{metric(evidence?.ceiling)}</b></div><div><span>Boom 25+</span><b>{metric(evidence?.boom25,0,'%')}</b></div><div><span>Bust &lt;10</span><b>{metric(evidence?.bust10,0,'%')}</b></div></div></div>}
      {tab === 'Game Log' && <div className="player-page-section" role="tabpanel"><h3>{evidence?.season || 'LATEST'} GAME LOG</h3>{log.length ? <div className="player-game-log"><div className="player-game-row head"><span>WK</span><span>OPP</span><span>STAT LINE</span><span>PPR</span></div>{log.map(game => <div className="player-game-row" key={`${game.season}-${game.week}`}><span>{game.week}</span><span>{game.opponent || '—'}</span><span>{game.statLine}</span><b>{metric(game.points)}</b></div>)}</div> : <p className="player-page-empty">Historical weekly data is unavailable for this player.</p>}</div>}
      {tab === 'Projections' && <div className="player-page-section" role="tabpanel"><h3>SHIVA PROJECTIONS</h3><div className="player-projection-card"><b>{metric(player.projectedPoints)}</b><span>Current weekly projection</span><p>{player.projectedPoints == null ? 'A verified live projection is not available for this player.' : `The current projection is ${metric(player.projectedPoints)} PPR points. Historical range: ${metric(evidence?.floor)} floor to ${metric(evidence?.ceiling)} ceiling.`}</p></div></div>}
      {tab === 'News' && <div className="player-page-section" role="tabpanel"><h3>CURRENT NEWS</h3>{newsStatus && <p className="player-page-empty">{newsStatus}</p>}{!newsStatus && !news.length && <p className="player-page-empty">No current ESPN headlines found for this player.</p>}{news.map(article => <a className="player-news-row" href={article.url} target="_blank" rel="noreferrer" key={`${article.headline}-${article.published}`}><b>{article.headline}</b><span>{article.description}</span><em>Open story →</em></a>)}</div>}
    </section>
  </div>
}
