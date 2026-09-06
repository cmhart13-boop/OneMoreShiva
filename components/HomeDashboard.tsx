'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import Image from 'next/image'
import { PlayerAvatar } from './PlayerMedia'
import type { LeagueRosterRow, LeagueState, Player, SavedLeague } from '../lib/types'

type IconName = 'users'
type AppIconProps = { name: IconName }

type ActiveSelection = { league: LeagueState; teamId: string | number | null } | null

type Game = {
  id: string
  name: string
  date: string
  status: string
  teams: Array<{ abbreviation:string; homeAway:string }>
}

type KeyPlayer = {
  row: LeagueRosterRow
  ranked?: Player
  projection: number
  expected: number
  state: 'start' | 'sit'
  opponent: string
  opponentPrefix: string
  importance: number
}

const key = (name:string) => name.toLowerCase().replace(/[^a-z0-9]/g, '')
const score = (value:number|null|undefined) => value == null || !Number.isFinite(value) ? '0.0' : value.toFixed(1)
const BENCH = new Set(['BE','BN','IR'])

function AppIcon({ name }: AppIconProps) {
  if (name !== 'users') return null
  return <svg className="og-icon" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><circle cx="9" cy="8" r="3"/><path d="M3.5 19c.4-3.5 2.3-5 5.5-5s5.1 1.5 5.5 5M15 5.5a3 3 0 0 1 0 5.8M16.5 14c2.5.3 3.8 1.8 4 4.5"/></svg>
}

function Helmet({ side }:{ side:'left'|'right' }) {
  return <span className={`live-helmet ${side}`} aria-hidden="true"><Image src={side === 'left' ? '/helmet-gold-3d.webp' : '/helmet-red-3d.webp'} alt="" fill sizes="(max-width: 430px) 38vw, 150px" priority/></span>
}

function readActiveSelection(): ActiveSelection {
  try {
    const raw = sessionStorage.getItem('shiva-league')
    const teamId = sessionStorage.getItem('shiva-team-id')
    if (!raw) return null
    return { league:JSON.parse(raw), teamId }
  } catch {
    return null
  }
}

function injuryFactor(status:string) {
  if (/out|ir|suspend/i.test(status)) return 0
  if (/doubtful/i.test(status)) return .45
  if (/questionable/i.test(status)) return .88
  return 1
}

function eligibleForSlot(row: LeagueRosterRow, slot:string) {
  const pos = (row.position || row.slot || '').toUpperCase()
  const eligible = (row.eligibleSlots || []).map((value) => value.toUpperCase())
  if (eligible.includes(slot)) return true
  if (slot === 'FLEX') return ['RB','WR','TE'].includes(pos)
  if (slot === 'SUPERFLEX' || slot === 'OP') return ['QB','RB','WR','TE'].includes(pos)
  return pos === slot || row.slot.toUpperCase() === slot
}

function projectionFor(row:LeagueRosterRow, ranked:Player|undefined) {
  if (row.projectedPoints != null) {
    const direct = Number(row.projectedPoints)
    if (Number.isFinite(direct) && direct >= 0) return direct
  }
  if (ranked?.projectedPoints != null) {
    const live = Number(ranked.projectedPoints)
    if (Number.isFinite(live) && live >= 0) return live
  }
  return 0
}

function matchupFor(team:string, games:Game[]) {
  if (!team) return { opponent:'', opponentPrefix:'' }
  const game = games.find((item) => item.teams?.some((side) => side.abbreviation === team))
  if (!game) return { opponent:'', opponentPrefix:'' }
  const mine = game.teams.find((side) => side.abbreviation === team)
  const opponent = game.teams.find((side) => side.abbreviation !== team)?.abbreviation || ''
  return { opponent, opponentPrefix:mine?.homeAway === 'away' ? '@' : 'vs' }
}

function buildKeyPlayers(roster:LeagueRosterRow[], playerMap:Map<string,Player>, games:Game[]):KeyPlayer[] {
  if (!roster.length) return []
  const candidates = roster.filter((row) => row.slot !== 'IR').map((row) => {
    const ranked = playerMap.get(key(row.player))
    const projection = projectionFor(row, ranked)
    const startPct = ranked?.percentStarted ?? row.percentStarted ?? 50
    const roleFactor = 0.97 + Math.max(0, Math.min(100, startPct)) / 1666
    const expected = projection * injuryFactor(row.injuryStatus || '') * roleFactor
    const team = row.proTeam || ranked?.team || ''
    return { row, ranked, projection, expected, ...matchupFor(team, games) }
  })

  const starters = candidates.filter((item) => !BENCH.has(item.row.slot))
  const bench = candidates.filter((item) => BENCH.has(item.row.slot))

  const evaluated = candidates.map((item) => {
    const currentSlot = item.row.slot.toUpperCase()
    const unavailable = injuryFactor(item.row.injuryStatus || '') === 0 || item.projection <= 0
    let state:'start'|'sit' = unavailable ? 'sit' : BENCH.has(currentSlot) ? 'sit' : 'start'

    if (!unavailable && !BENCH.has(currentSlot)) {
      const replacement = bench
        .filter((other) => other.row.playerId !== item.row.playerId && eligibleForSlot(other.row, currentSlot))
        .sort((a,b) => b.expected - a.expected)[0]
      if (replacement && replacement.expected > item.expected + Math.max(1.5, item.projection * .08)) state = 'sit'
      else if (item.expected < item.projection * .9) state = 'sit'
    }

    if (!unavailable && BENCH.has(currentSlot)) {
      const replaceable = starters
        .filter((other) => eligibleForSlot(item.row, other.row.slot.toUpperCase()))
        .sort((a,b) => a.expected - b.expected)[0]
      if (replaceable && item.expected > replaceable.expected + Math.max(1.5, replaceable.projection * .08)) state = 'start'
    }

    const starterWeight = BENCH.has(currentSlot) ? 0 : 3
    const swingWeight = state === 'sit' && !BENCH.has(currentSlot) ? 4 : state === 'start' && BENCH.has(currentSlot) ? 4 : 0
    return { ...item, state, importance:Math.max(item.expected, item.projection) + starterWeight + swingWeight }
  })

  return evaluated.sort((a,b) => b.importance - a.importance || b.projection - a.projection).slice(0,5)
}

export default function HomeDashboard({ open, leagues }:{ open:(target:string)=>void; leagues:SavedLeague[] }) {
  const [players,setPlayers] = useState<Player[]>([])
  const [games,setGames] = useState<Game[]>([])
  const [active,setActive] = useState<ActiveSelection>(null)
  const [page,setPage] = useState(0)
  const track = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const sync = (event?:Event) => {
      const detail = (event as CustomEvent<{ league:LeagueState; teamId:string|number|null }> | undefined)?.detail
      setActive(detail?.league ? { league:detail.league, teamId:detail.teamId } : readActiveSelection())
      setPage(0)
      track.current?.scrollTo({ left:0, behavior:'smooth' })
    }
    sync()
    window.addEventListener('shiva:league-changed', sync)
    return () => window.removeEventListener('shiva:league-changed', sync)
  }, [])

  const activeWeek = active?.league?.league.scoringPeriod || active?.league?.league.matchupPeriod || leagues.find((item) => item.league_data)?.league_data?.league.scoringPeriod || 1
  const activeSeason = active?.league?.league.season || leagues.find((item) => item.league_data)?.league_data?.league.season || 2026

  useEffect(() => {
    fetch(`/api/rankings?season=${encodeURIComponent(String(activeSeason))}&week=${encodeURIComponent(String(activeWeek))}`, { cache:'no-store' })
      .then((response) => response.ok ? response.json() : null)
      .then((data) => setPlayers(data?.players || []))
      .catch(() => setPlayers([]))
    fetch(`/api/scoreboard?week=${encodeURIComponent(String(activeWeek))}`, { cache:'no-store' })
      .then((response) => response.ok ? response.json() : null)
      .then((data) => setGames(data?.games || []))
      .catch(() => setGames([]))
  }, [activeSeason, activeWeek])

  const playerMap = useMemo(() => new Map(players.map((player) => [key(player.name),player])), [players])
  const pages:Array<SavedLeague|null> = useMemo(() => {
    if (!leagues.length) return [null]
    const activeId = active?.league?.league.id
    if (!activeId) return leagues
    const match = leagues.find((saved) => String(saved.league_data?.league.id || saved.league_id) === String(activeId))
    if (!match) return leagues
    return [match, ...leagues.filter((saved) => saved.id !== match.id)]
  }, [leagues, active?.league?.league.id])

  return <section className="og-snapshots" aria-label="League dashboard"><div className="og-snapshot-track" ref={track} onScroll={(event) => { const width=event.currentTarget.clientWidth; if (width) setPage(Math.round(event.currentTarget.scrollLeft/width)) }}>{pages.map((saved,index) => {
    const isActive = Boolean(saved && active?.league && String(saved.league_data?.league.id || saved.league_id) === String(active.league.league.id))
    const league = isActive ? active?.league || null : saved?.league_data || null
    const week = league?.league.scoringPeriod || league?.league.matchupPeriod || 1
    const teamId = isActive ? active?.teamId ?? saved?.team_id ?? league?.teams[0]?.id ?? null : saved?.team_id ?? league?.teams[0]?.id ?? null
    const team = league?.teams.find((item) => String(item.id) === String(teamId)) || league?.teams[0] || null
    const standings = [...(league?.teams || [])].sort((a,b) => (b.wins ?? -1) - (a.wins ?? -1) || (a.losses ?? 999) - (b.losses ?? 999) || a.name.localeCompare(b.name))
    const matchup = league?.matchups?.find((item) => item.period === week && (String(item.homeTeamId) === String(teamId) || String(item.awayTeamId) === String(teamId))) || league?.matchups?.find((item) => String(item.homeTeamId) === String(teamId) || String(item.awayTeamId) === String(teamId))
    const isHome = matchup ? String(matchup.homeTeamId) === String(teamId) : true
    const opponentId = matchup ? (isHome ? matchup.awayTeamId : matchup.homeTeamId) : standings.find((item) => String(item.id) !== String(teamId))?.id
    const opponent = league?.teams.find((item) => String(item.id) === String(opponentId)) || null
    const mine = (league?.roster || []).filter((row) => String(row.teamId) === String(teamId))
    const theirs = (league?.roster || []).filter((row) => String(row.teamId) === String(opponentId))
    const projected = (rows:LeagueRosterRow[]) => rows.filter((row) => !BENCH.has(row.slot)).reduce((sum,row) => sum + projectionFor(row, playerMap.get(key(row.player))), 0)
    const myProj = (isHome ? matchup?.homeProjected : matchup?.awayProjected) ?? projected(mine)
    const oppProj = (isHome ? matchup?.awayProjected : matchup?.homeProjected) ?? projected(theirs)
    const myScore = isHome ? matchup?.homeScore : matchup?.awayScore
    const oppScore = isHome ? matchup?.awayScore : matchup?.homeScore
    const personalized = buildKeyPlayers(mine, playerMap, games)
    const fallback = players.slice(0,5).map((ranked,index) => ({ row:{ teamId:'',team:'',playerId:ranked.espnId || ranked.id,player:ranked.name,slotId:'',slot:index < 5 ? 'FLEX':'BE',proTeamId:null,proTeam:ranked.team,position:ranked.pos,eligibleSlots:[ranked.pos],injuryStatus:ranked.injuryStatus || '',percentOwned:ranked.percentOwned ?? null,percentStarted:ranked.percentStarted ?? null,projectedPoints:ranked.projectedPoints ?? null }, ranked, projection:ranked.projectedPoints || 0, expected:ranked.projectedPoints || 0, state:'start' as const, opponent:'', opponentPrefix:'', importance:ranked.projectedPoints || 0 }))
    const keyPlayers = personalized.length ? personalized : fallback

    return <div className="og-snapshot-page" key={saved?.id || index}><article className="og-snapshot-card og-my-matchup"><header><b>My Matchup</b><button onClick={() => open('Lineup')}>{league ? `Week ${week} ›` : 'Open ›'}</button></header><div className="og-helmet-clash"><Helmet side="left"/><i>VS</i><Helmet side="right"/></div><div className="og-matchup-score"><div><strong>{score(myScore)}</strong><b>{team?.name || 'My Team'}</b><small>Proj {score(myProj)}</small></div><div><strong>{score(oppScore)}</strong><b>{opponent?.name || 'Opponent'}</b><small>Proj {score(oppProj)}</small></div></div><button className="og-view-matchup" onClick={() => open(league ? 'Lineup' : 'League')}>{league ? 'View Matchup' : 'Connect League'}</button></article><article className="og-snapshot-card og-key-players"><header><b>Key Players</b><button onClick={() => open('Players')}>See All ›</button></header>{keyPlayers.length ? <div className="og-key-list">{keyPlayers.map((player) => { const teamAbbr=player.row.proTeam || player.ranked?.team || ''; const projectionText=player.projection > 0 ? `${player.projection.toFixed(1)} proj` : ''; const scheduleText=player.opponent ? `${player.opponentPrefix} ${player.opponent}` : ''; return <div className={player.state} data-recommendation={player.state} key={`${player.row.playerId}-${player.row.player}`}><PlayerAvatar playerId={player.ranked?.espnId || player.ranked?.id || player.row.playerId} name={player.row.player}/><span><b>{player.row.player}</b><small>{[player.row.position || player.ranked?.pos || player.row.slot,teamAbbr,scheduleText,projectionText].filter(Boolean).join(' · ')}</small></span><em className={player.state}>{player.state === 'start' ? 'START' : 'SIT'}</em></div> })}</div> : <div className="og-key-empty"><AppIcon name="users"/><p>{league ? 'Loading recommendations for your selected team.' : 'Connect your league to personalize Key Players.'}</p></div>}</article></div>
  })}</div>{pages.length > 1 && <div className="og-snapshot-dots">{pages.map((saved,index) => <button key={saved?.id || index} className={index === page ? 'active' : ''} aria-label={`View league ${index+1}`} onClick={() => { track.current?.scrollTo({ left:(track.current?.clientWidth || 0) * index, behavior:'smooth' }); setPage(index) }}/>)}</div>}</section>
}
