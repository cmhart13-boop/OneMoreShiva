'use client'

import { useEffect, useMemo, useState } from 'react'
import { cpuChoice, draftRecommendations, pickOrder, type DraftPick } from '../lib/draft'
import { PlayerAvatar, PlayerDetailOverlay, type PlayerDetailData } from './PlayerMedia'
import type { Player } from '../lib/types'

const TOTAL_TEAMS = 12
const TOTAL_ROUNDS = 15

type PoolTab = 'Available' | 'My Roster' | 'Queue'

export default function DraftView() {
  const [players, setPlayers] = useState<Player[]>([])
  const [slot, setSlot] = useState(1)
  const [started, setStarted] = useState(false)
  const [picks, setPicks] = useState<DraftPick[]>([])
  const [currentOverall, setCurrentOverall] = useState(1)
  const [queue, setQueue] = useState<string[]>([])
  const [poolTab, setPoolTab] = useState<PoolTab>('Available')
  const [posFilter, setPosFilter] = useState('ALL')
  const [search, setSearch] = useState('')
  const [selectedPlayer, setSelectedPlayer] = useState<PlayerDetailData | null>(null)

  useEffect(() => {
    fetch('/api/rankings').then((response) => response.json()).then((data) => setPlayers(data.players || [])).catch(() => setPlayers([]))
  }, [])

  const draftedIds = useMemo(() => new Set(picks.map((pick) => pick.player.id)), [picks])
  const available = useMemo(() => players.filter((player) => !draftedIds.has(player.id)), [players, draftedIds])
  const myPicks = useMemo(() => picks.filter((pick) => pick.team === slot), [picks, slot])
  const order = pickOrder(currentOverall, TOTAL_TEAMS)
  const completed = currentOverall > TOTAL_TEAMS * TOTAL_ROUNDS
  const isUserPick = !completed && order.team === slot
  const recommendations = isUserPick ? draftRecommendations(available, myPicks.map((pick) => pick.player), currentOverall, order.round) : []

  const openPlayer = (player: Player) => setSelectedPlayer({ ...player, id: player.espnId || player.id })

  const fillCpuUntilUser = (base: DraftPick[], firstOverall: number) => {
    const next = [...base]
    let overall = firstOverall
    const max = TOTAL_TEAMS * TOTAL_ROUNDS
    while (overall <= max) {
      const context = pickOrder(overall, TOTAL_TEAMS)
      if (context.team === slot) break
      const taken = new Set(next.map((pick) => pick.player.id))
      const pool = players.filter((player) => !taken.has(player.id))
      const roster = next.filter((pick) => pick.team === context.team).map((pick) => pick.player)
      const choice = cpuChoice(pool, roster, overall, context.team)
      if (!choice) break
      next.push({ overall, round: context.round, slot: context.slot, team: context.team, player: choice, user: false })
      overall += 1
    }
    setPicks(next)
    setCurrentOverall(overall)
  }

  const startDraft = () => {
    if (!players.length) return
    setStarted(true); setPicks([]); setQueue([]); setPoolTab('Available'); fillCpuUntilUser([], 1)
  }

  const draftPlayer = (player: Player) => {
    if (!isUserPick || draftedIds.has(player.id)) return
    const context = pickOrder(currentOverall, TOTAL_TEAMS)
    const next: DraftPick[] = [...picks, { overall: currentOverall, round: context.round, slot: context.slot, team: context.team, player, user: true }]
    setQueue((items) => items.filter((id) => id !== player.id))
    fillCpuUntilUser(next, currentOverall + 1)
  }

  const restart = () => { setStarted(false); setPicks([]); setCurrentOverall(1); setQueue([]) }

  if (!started) return <>
    <div className="section-kicker">MOCK DRAFT</div><h1>2026 Shiva Draft</h1>
    <p className="lede">Choose your draft position first. Shiva uses the live available pool, ADP, current rankings and roster construction before every recommendation.</p>
    <div className="panel start-draft-card"><label htmlFor="draft-slot">Draft position</label><div className="slot-grid">{Array.from({ length: 12 }, (_, index) => index + 1).map((value) => <button key={value} className={slot === value ? 'active' : ''} onClick={() => setSlot(value)}>{value}</button>)}</div><button className="primary-button start-button" onClick={startDraft} disabled={!players.length}>{players.length ? 'Start Mock Draft' : 'Loading draft board…'}</button></div>
  </>

  return <>
    <div className="draft-topline"><div><div className="section-kicker">LIVE MOCK</div><h1>Round {completed ? TOTAL_ROUNDS : order.round} · Pick {completed ? 'Complete' : currentOverall}</h1></div><button className="ghost-button compact" onClick={restart}>Restart</button></div>
    <div className={`clock-card ${isUserPick ? 'on-clock' : ''}`}><span>{completed ? 'DRAFT COMPLETE' : isUserPick ? 'YOU ARE ON THE CLOCK' : `Team ${order.team} picking`}</span><b>{completed ? `${myPicks.length} players drafted` : `Pick ${currentOverall} · Slot ${order.slot}`}</b></div>

    {!completed && <section className="draft-iq"><div className="draft-iq-head"><div><span>SHIVA DRAFT IQ</span><h2>Best choices right now</h2></div><em>LIVE CONTEXT</em></div>{recommendations.length ? <div className="rec-list">{recommendations.map((rec) => <article key={rec.player.id} className="rec-card"><button type="button" className="rec-player clickable-name" onClick={() => openPlayer(rec.player)}><PlayerAvatar playerId={rec.player.espnId || rec.player.id} name={rec.player.name} /><div><span>{rec.label}</span><h3>{rec.player.name}</h3><p>{rec.player.pos} · {rec.player.team} · ADP {rec.player.adp?.toFixed(1) ?? '—'}</p><small>{rec.reason}</small></div></button><button onClick={() => draftPlayer(rec.player)}>DRAFT</button></article>)}</div> : <p className="muted-copy">Shiva IQ unlocks on your pick.</p>}</section>}

    <div className="draft-tabs">{(['Available','My Roster','Queue'] as PoolTab[]).map((tab) => <button key={tab} className={poolTab === tab ? 'active' : ''} onClick={() => setPoolTab(tab)}>{tab}{tab === 'Queue' && queue.length ? ` (${queue.length})` : ''}</button>)}</div>

    {poolTab === 'Available' && <>
      <div className="pool-controls"><input aria-label="Search players" placeholder="Search player" value={search} onChange={(event) => setSearch(event.target.value)} /><div className="filter-pills compact-pills">{['ALL','RB','WR','QB','TE','K','DST'].map((filter) => <button key={filter} className={posFilter === filter ? 'active' : ''} onClick={() => setPosFilter(filter)}>{filter}</button>)}</div></div>
      <div className="player-pool">{available.filter((player) => posFilter === 'ALL' || player.pos === posFilter).filter((player) => !search || player.name.toLowerCase().includes(search.toLowerCase())).slice(0, 100).map((player) => <div className="pool-row has-player-photo" key={player.id}><div className="pool-rank">{player.rank < 10000 ? `#${player.rank}` : '—'}</div><span className={`pos-chip pos-${player.pos}`}>{player.pos}</span><button type="button" className="player-inline clickable-name" onClick={() => openPlayer(player)}><PlayerAvatar playerId={player.espnId || player.id} name={player.name} /><div className="pool-name"><b>{player.name}</b><small>{player.team || '—'} · ADP {player.adp?.toFixed(1) ?? '—'}</small></div></button><div className="pool-actions"><button aria-label={`Queue ${player.name}`} className={queue.includes(player.id) ? 'queued' : ''} onClick={() => setQueue((items) => items.includes(player.id) ? items.filter((id) => id !== player.id) : [...items, player.id])}>☆</button><button disabled={!isUserPick} onClick={() => draftPlayer(player)}>Draft</button></div></div>)}</div>
    </>}

    {poolTab === 'My Roster' && <div className="roster-list">{myPicks.length ? myPicks.map((pick) => <div className="pool-row has-player-photo" key={pick.overall}><div className="pool-rank">R{pick.round}</div><span className={`pos-chip pos-${pick.player.pos}`}>{pick.player.pos}</span><button type="button" className="player-inline clickable-name" onClick={() => openPlayer(pick.player)}><PlayerAvatar playerId={pick.player.espnId || pick.player.id} name={pick.player.name} /><div className="pool-name"><b>{pick.player.name}</b><small>{pick.player.team} · Pick {pick.overall}</small></div></button></div>) : <div className="empty-state">No picks yet.</div>}</div>}

    {poolTab === 'Queue' && <div className="roster-list">{queue.length ? queue.map((id) => available.find((player) => player.id === id)).filter(Boolean).map((player) => <div className="pool-row has-player-photo" key={player!.id}><div className="pool-rank">{player!.rank < 10000 ? `#${player!.rank}` : '—'}</div><span className={`pos-chip pos-${player!.pos}`}>{player!.pos}</span><button type="button" className="player-inline clickable-name" onClick={() => openPlayer(player!)}><PlayerAvatar playerId={player!.espnId || player!.id} name={player!.name} /><div className="pool-name"><b>{player!.name}</b><small>{player!.team} · ADP {player!.adp?.toFixed(1) ?? '—'}</small></div></button><div className="pool-actions"><button onClick={() => setQueue((items) => items.filter((item) => item !== player!.id))}>×</button><button disabled={!isUserPick} onClick={() => draftPlayer(player!)}>Draft</button></div></div>) : <div className="empty-state">Your queue is empty.</div>}</div>}

    {selectedPlayer && <PlayerDetailOverlay player={selectedPlayer} onClose={() => setSelectedPlayer(null)} />}
  </>
}
