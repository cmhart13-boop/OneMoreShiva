'use client'

import { useEffect, useState } from 'react'
import type { Evidence, Player } from '../lib/types'

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
  useEffect(() => {
    let active = true
    fetch(`/api/evidence?player=${encodeURIComponent(player.name)}`)
      .then((response) => response.json())
      .then((data) => { if (active) setEvidence(data.evidence || null) })
      .catch(() => {})
    return () => { active = false }
  }, [player.name])

  const ppg = player.ppg ?? evidence?.ppg ?? null
  const seasonPoints = player.seasonPoints ?? (evidence?.ppg != null && evidence?.games ? evidence.ppg * evidence.games : null)
  const posRank = player.posRank ?? null
  const teamColor = TEAM_COLOR[player.team || ''] || '#12344a'

  return <div className="player-page-backdrop" role="presentation" onClick={onClose}>
    <section className="player-page" role="dialog" aria-modal="true" aria-label={`${player.name} player page`} onClick={(event) => event.stopPropagation()}>
      <button className="player-page-close" type="button" aria-label="Close player page" onClick={onClose}>×</button>
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
      <div className="player-page-tabs"><b>Overview</b><span>News</span><span>Stats</span><span>Game Log</span><span>Projections</span></div>
      <div className="player-page-section">
        <h3>PLAYER OVERVIEW</h3>
        <div className="player-overview-grid">
          <div><span>Shiva Rank</span><b>{player.rank ? `#${player.rank}` : '—'}</b></div>
          <div><span>ADP</span><b>{metric(player.adp)}</b></div>
          <div><span>Team</span><b>{player.team || '—'}</b></div>
          <div><span>Position</span><b>{player.pos || '—'}</b></div>
        </div>
      </div>
    </section>
  </div>
}
