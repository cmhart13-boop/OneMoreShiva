'use client'

import { useEffect, useMemo, useState } from 'react'
import { PlayerAvatar, PlayerDetailOverlay, type PlayerDetailData } from './PlayerMedia'

type Mode = 'floor' | 'ceiling'
type EdgePlayer = {
  id: string
  espnId?: string
  name: string
  team: string
  pos: string
  rank: number
  posRank?: number | null
  adp: number | null
  percentOwned?: number | null
  season: number
  ppg: number
  floor: number
  ceiling: number
  rate15: number
  boom25: number
}

const FILTERS = ['ALL','QB','RB','WR','TE'] as const

export default function EdgeRankingsView({ mode, onBack }: { mode: Mode; onBack: () => void }) {
  const [players, setPlayers] = useState<EdgePlayer[]>([])
  const [filter, setFilter] = useState<(typeof FILTERS)[number]>('ALL')
  const [loading, setLoading] = useState(true)
  const [selectedPlayer, setSelectedPlayer] = useState<PlayerDetailData | null>(null)

  useEffect(() => {
    fetch('/api/edges').then((response) => response.json()).then((data) => setPlayers(data.players || [])).catch(() => setPlayers([])).finally(() => setLoading(false))
  }, [])

  const rows = useMemo(() => {
    const filtered = players.filter((player) => filter === 'ALL' || player.pos === filter)
    return [...filtered].sort((a, b) => mode === 'floor'
      ? b.floor - a.floor || b.rate15 - a.rate15 || a.rank - b.rank
      : b.ceiling - a.ceiling || b.boom25 - a.boom25 || a.rank - b.rank
    ).slice(0, filter === 'ALL' ? 75 : 40)
  }, [players, filter, mode])

  const title = mode === 'floor' ? 'Raise the Floor' : 'Keep the Ceiling'
  const subtitle = mode === 'floor' ? 'Weekly floor + 15-point consistency' : '90th-percentile ceiling + 25-point boom rate'

  return <div className="edge-rankings-view">
    <button className="back-link" onClick={onBack}>← Shiva Coach</button>
    <div className="section-kicker">SHIVA EDGE</div><h1>{title}</h1><p className="lede">{subtitle}</p>

    <div className="filter-pills edge-filter-pills">{FILTERS.map((item) => <button key={item} className={`${filter === item ? 'active ' : ''}edge-filter-${item}`} onClick={() => setFilter(item)}>{item}</button>)}</div>

    {loading ? <div className="panel loading-panel">Loading historical edge rankings…</div> : rows.length ? <div className="rank-list edge-rank-list">
      {rows.map((player, index) => <button type="button" className="rank-row edge-rank-row has-player-photo clickable-player" key={player.id} onClick={() => setSelectedPlayer({ ...player, id: player.espnId || player.id, ppg: player.ppg })}>
        <span className="rank-number">{index + 1}</span>
        <span className={`pos-chip pos-${player.pos}`}>{player.pos}</span>
        <PlayerAvatar playerId={player.espnId || player.id} name={player.name} />
        <div><b>{player.name}</b><small>{player.team || '—'} · {player.season} · {player.ppg.toFixed(1)} PPG</small></div>
        <div className="edge-rank-metric"><strong>{mode === 'floor' ? player.floor.toFixed(1) : player.ceiling.toFixed(1)}</strong><span>{mode === 'floor' ? `${Math.round(player.rate15)}% 15+` : `${Math.round(player.boom25)}% 25+`}</span></div>
      </button>)}
    </div> : <div className="empty-state">No historical edge data is available for this position.</div>}

    {selectedPlayer && <PlayerDetailOverlay player={selectedPlayer} onClose={() => setSelectedPlayer(null)} />}
  </div>
}
