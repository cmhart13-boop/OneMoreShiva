'use client'

import { useEffect, useMemo, useState } from 'react'
import { PlayerAvatar, PlayerDetailOverlay, type PlayerDetailData } from './PlayerMedia'
import type { Evidence, LeagueState, NewsArticle, Player } from '../lib/types'

type CoachTab = 'Overview' | 'League' | 'Start / Sit' | 'Waivers' | 'Lineup' | 'Player Watch' | 'Ask Shiva' | 'Players'
type SelectedPlayer = PlayerDetailData & { slot?: string; percentStarted?: number | null }

const PRO_TEAM: Record<number, string> = {
  1:'ATL',2:'BUF',3:'CHI',4:'CIN',5:'CLE',6:'DAL',7:'DEN',8:'DET',9:'GB',10:'TEN',11:'IND',12:'KC',13:'LV',14:'LAR',15:'MIA',16:'MIN',17:'NE',18:'NO',19:'NYG',20:'NYJ',21:'PHI',22:'ARI',23:'PIT',24:'LAC',25:'SF',26:'SEA',27:'TB',28:'WAS',29:'CAR',30:'JAX',33:'BAL',34:'HOU'
}

function num(value: number | null | undefined, digits = 1, suffix = '') {
  return value === null || value === undefined || !Number.isFinite(value) ? '—' : `${value.toFixed(digits)}${suffix}`
}

function score(evidence: Evidence | null, rank?: number | null) {
  if (!evidence) return -999
  const rankComponent = rank ? Math.max(0, 220 - rank) / 22 : 0
  return (evidence.floor ?? 0) * 1.35 + (evidence.ppg ?? 0) + (evidence.ceiling ?? 0) * .35 + ((evidence.rate15 ?? 0) / 10) * .9 - ((evidence.bust10 ?? 0) / 12) + rankComponent * .8
}

function teamLogoUrl(team: string) {
  return team ? `https://a.espncdn.com/i/teamlogos/nfl/500/${team.toLowerCase()}.png` : ''
}

export default function CoachView() {
  const [tab, setTab] = useState<CoachTab>('Overview')
  const [players, setPlayers] = useState<Player[]>([])
  const [playerFilter, setPlayerFilter] = useState('ALL')
  const [league, setLeague] = useState<LeagueState | null>(null)
  const [teamId, setTeamId] = useState<number | null>(null)
  const [leagueId, setLeagueId] = useState('')
  const [season] = useState(2026)
  const [connectStatus, setConnectStatus] = useState('')
  const [playerA, setPlayerA] = useState('')
  const [playerB, setPlayerB] = useState('')
  const [evidenceA, setEvidenceA] = useState<Evidence | null>(null)
  const [evidenceB, setEvidenceB] = useState<Evidence | null>(null)
  const [compareLoading, setCompareLoading] = useState(false)
  const [watchPlayer, setWatchPlayer] = useState('')
  const [watchNews, setWatchNews] = useState<NewsArticle[]>([])
  const [games, setGames] = useState<any[]>([])
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [askStatus, setAskStatus] = useState('')
  const [selectedPlayer, setSelectedPlayer] = useState<SelectedPlayer | null>(null)

  useEffect(() => {
    fetch('/api/rankings').then((response) => response.json()).then((data) => {
      const loaded = data.players || []
      setPlayers(loaded)
      if (loaded.length) {
        setPlayerA((value) => value || loaded[0].name)
        setPlayerB((value) => value || loaded[1]?.name || loaded[0].name)
        setWatchPlayer((value) => value || loaded[0].name)
      }
    }).catch(() => setPlayers([]))
    fetch('/api/scoreboard').then((response) => response.json()).then((data) => setGames(data.games || [])).catch(() => setGames([]))
    try {
      const stored = window.sessionStorage.getItem('shiva-league')
      const storedTeam = window.sessionStorage.getItem('shiva-team-id')
      if (stored) setLeague(JSON.parse(stored))
      if (storedTeam) setTeamId(Number(storedTeam))
    } catch {}
  }, [])

  const roster = useMemo(() => league && teamId !== null ? league.roster.filter((row) => row.teamId === teamId) : [], [league, teamId])
  const starters = useMemo(() => roster.filter((row) => row.slot !== 'BE' && row.slot !== 'IR'), [roster])
  const bench = useMemo(() => roster.filter((row) => row.slot === 'BE' || row.slot === 'IR'), [roster])
  const standings = useMemo(() => league ? [...league.teams].sort((a, b) => (b.wins ?? -1) - (a.wins ?? -1) || (a.losses ?? 999) - (b.losses ?? 999) || a.name.localeCompare(b.name)) : [], [league])
  const comparisonNames = useMemo(() => {
    const rosterNames = roster.map((row) => row.player).filter(Boolean)
    return rosterNames.length >= 2 ? rosterNames : players.slice(0, 180).map((player) => player.name)
  }, [roster, players])
  const playerRows = useMemo(() => players.filter((player) => playerFilter === 'ALL' || (playerFilter === 'FLEX' ? ['RB','WR','TE'].includes(player.pos) : player.pos === playerFilter)).slice(0, playerFilter === 'ALL' ? 150 : 75), [players, playerFilter])

  useEffect(() => {
    if (comparisonNames.length && !comparisonNames.includes(playerA)) setPlayerA(comparisonNames[0])
    if (comparisonNames.length > 1 && !comparisonNames.includes(playerB)) setPlayerB(comparisonNames[1])
  }, [comparisonNames, playerA, playerB])

  const rankedByName = (name: string) => players.find((player) => player.name.toLowerCase() === name.toLowerCase())
  const openRanked = (name: string, extra: Partial<SelectedPlayer> = {}) => {
    const ranked = rankedByName(name)
    const id = extra.espnId || ranked?.espnId || ranked?.id || extra.id || ''
    setSelectedPlayer({ ...ranked, ...extra, id, espnId: id, name, team: extra.team || ranked?.team || '', pos: extra.pos || ranked?.pos || '' })
  }

  const openRosterPlayer = (row: LeagueState['roster'][number]) => {
    const ranked = rankedByName(row.player)
    setSelectedPlayer({
      ...ranked,
      id: row.playerId,
      espnId: row.playerId,
      name: row.player,
      team: PRO_TEAM[row.proTeamId || 0] || ranked?.team || '',
      slot: row.slot,
      injuryStatus: row.injuryStatus,
      percentOwned: row.percentOwned,
      percentStarted: row.percentStarted,
      rank: ranked?.rank,
      posRank: ranked?.posRank,
      pos: ranked?.pos,
    })
  }

  const connect = async () => {
    setConnectStatus('Connecting…')
    try {
      const response = await fetch('/api/espn', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ leagueId, season }) })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || 'ESPN connection failed.')
      setLeague(data)
      const firstTeam = data.teams?.[0]?.id ?? null
      setTeamId(firstTeam)
      window.sessionStorage.setItem('shiva-league', JSON.stringify(data))
      if (firstTeam !== null) window.sessionStorage.setItem('shiva-team-id', String(firstTeam))
      setConnectStatus('Connected')
    } catch (error) {
      setConnectStatus(error instanceof Error ? error.message : 'ESPN connection failed.')
    }
  }

  const disconnect = () => {
    setLeague(null); setTeamId(null); setConnectStatus('')
    try { window.sessionStorage.removeItem('shiva-league'); window.sessionStorage.removeItem('shiva-team-id') } catch {}
  }

  const compare = async () => {
    if (!playerA || !playerB || playerA === playerB) return
    setCompareLoading(true)
    try {
      const [a, b] = await Promise.all([
        fetch(`/api/evidence?player=${encodeURIComponent(playerA)}`).then((response) => response.json()),
        fetch(`/api/evidence?player=${encodeURIComponent(playerB)}`).then((response) => response.json()),
      ])
      setEvidenceA(a.evidence || null); setEvidenceB(b.evidence || null)
    } finally { setCompareLoading(false) }
  }

  const winner = useMemo(() => {
    if (!evidenceA || !evidenceB) return null
    const rankA = players.find((player) => player.name === playerA)?.rank
    const rankB = players.find((player) => player.name === playerB)?.rank
    return score(evidenceA, rankA) >= score(evidenceB, rankB) ? playerA : playerB
  }, [evidenceA, evidenceB, playerA, playerB, players])

  const waiverRows = useMemo(() => {
    if (!league) return []
    const byName = new Map(players.map((player) => [player.name.toLowerCase(), player]))
    return league.freeAgents.map((agent) => ({ agent, player: byName.get(agent.player.toLowerCase()) })).sort((a, b) => (a.player?.rank ?? 9999) - (b.player?.rank ?? 9999) || (b.agent.percentOwned ?? 0) - (a.agent.percentOwned ?? 0)).slice(0, 40)
  }, [league, players])

  const lineupWarnings = useMemo(() => {
    if (!roster.length) return []
    return roster.filter((row) => row.slot === 'FLEX').map((row) => {
      const abbr = row.proTeamId ? PRO_TEAM[row.proTeamId] : ''
      const game = games.find((item) => item.teams?.some((team: any) => team.abbreviation === abbr))
      if (!game?.date) return null
      const day = new Date(game.date).toLocaleDateString('en-US', { weekday:'long' })
      return { row, day, danger: day === 'Thursday' }
    }).filter(Boolean) as { row: any; day: string; danger: boolean }[]
  }, [roster, games])

  const loadWatch = async () => {
    if (!watchPlayer) return
    const data = await fetch(`/api/news?player=${encodeURIComponent(watchPlayer)}`).then((response) => response.json()).catch(() => ({ articles:[] }))
    setWatchNews(data.articles || [])
  }

  const askShiva = async () => {
    if (!question.trim()) return
    setAskStatus('Thinking…'); setAnswer('')
    const context = [league ? `League: ${league.league.name}` : '', roster.length ? `My roster: ${roster.map((row) => `${row.slot} ${row.player}`).join(', ')}` : ''].filter(Boolean).join('\n')
    try {
      const response = await fetch('/api/ask', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ question, context }) })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || 'Shiva Intelligence unavailable.')
      setAnswer(data.answer || ''); setAskStatus('')
    } catch (error) { setAskStatus(error instanceof Error ? error.message : 'Shiva Intelligence unavailable.') }
  }

  const rosterRows = (rows: LeagueState['roster']) => <div className="espn-roster">{rows.map((row) => <button type="button" className="espn-roster-row clickable-player" key={`${row.playerId}-${row.slot}`} onClick={() => openRosterPlayer(row)}><span className="espn-slot">{row.slot}</span><PlayerAvatar playerId={row.playerId} name={row.player} /><div className="espn-player-copy"><b>{row.player}</b><small>{PRO_TEAM[row.proTeamId || 0] || ''}{row.injuryStatus ? ` · ${row.injuryStatus}` : ''}</small></div><span className="espn-row-rank">{rankedByName(row.player)?.rank && rankedByName(row.player)!.rank < 10000 ? `#${rankedByName(row.player)!.rank}` : ''}</span></button>)}</div>

  const watchCurrent = rankedByName(watchPlayer)

  return <>
    <div className="coach-tabs">{(['Overview','League','Start / Sit','Waivers','Lineup','Player Watch','Ask Shiva','Players'] as CoachTab[]).map((item) => <button key={item} className={tab === item ? 'active' : ''} onClick={() => setTab(item)}>{item}</button>)}</div>

    {tab === 'Overview' && <><div className="coach-hero overview-connect-card"><h2>{league ? `${league.league.name} is connected.` : 'Sync your fantasy football league below and let Shiva help you whoop some ass this year.'}</h2>{league ? <><p>{roster.length} players loaded for your selected team. Start/Sit, waivers and lineup checks can use that roster now.</p><button className="ghost-button compact" onClick={() => setTab('League')}>View League →</button></> : <><div className="overview-connect-row"><label>ESPN League ID<input value={leagueId} onChange={(event) => setLeagueId(event.target.value)} inputMode="numeric" placeholder="League ID" /></label><button className="primary-button compact-connect-button" onClick={connect}>Connect Your League</button></div>{connectStatus && <p className="status-copy">{connectStatus}</p>}</>}</div><div className="strategy-grid"><article className="panel"><span className="eyebrow">LINEUP EDGE</span><h2>{lineupWarnings.some((item) => item.danger) ? 'Thursday FLEX issue found' : 'No Thursday FLEX trap found'}</h2><p>{roster.length ? 'Lineup checks use the connected roster and current ESPN schedule.' : 'Connect a league to run the lineup rule engine.'}</p></article><article className="panel"><span className="eyebrow">DRAFT EDGE</span><h2>Rank + ADP, not rank alone</h2><p>Shiva Draft IQ protects against reaching while still filling roster needs.</p></article></div></>}

    {tab === 'League' && <>{league ? <div className="league-stack"><div className="panel league-panel"><div className="status-pill good">● ESPN LEAGUE CONNECTED</div><h2>{league.league.name}</h2><p>{league.league.season} · Week {league.league.scoringPeriod ?? '—'} · Matchup period {league.league.matchupPeriod ?? '—'}</p><button className="ghost-button compact" onClick={disconnect}>Disconnect league</button></div><div className="panel standings-panel"><div className="section-heading compact-heading"><div><div className="section-kicker">CURRENT TABLE</div><h2>League Standings</h2></div></div><div className="standings-list">{standings.map((team, index) => <div className={`standing-row ${team.id === teamId ? 'mine' : ''}`} key={team.id}><span>{index + 1}</span><div><b>{team.name}</b><small>{team.owners.join(', ') || 'ESPN team'}</small></div><strong>{team.wins ?? '—'}-{team.losses ?? '—'}</strong></div>)}</div></div><div className="panel league-panel"><label>Your team</label><select value={teamId ?? ''} onChange={(event) => { const id = Number(event.target.value); setTeamId(id); window.sessionStorage.setItem('shiva-team-id', String(id)) }}>{league.teams.map((team) => <option value={team.id} key={team.id}>{team.name}</option>)}</select><div className="section-kicker" style={{marginTop:14}}>STARTERS</div>{rosterRows(starters)}{bench.length > 0 && <><div className="section-kicker" style={{marginTop:14}}>BENCH / IR</div>{rosterRows(bench)}</>}</div></div> : <div className="empty-state">Connect your ESPN league from Overview. Once connected, current week context, standings, records and your roster will appear here.</div>}</>}

    {tab === 'Start / Sit' && <><div className="coach-hero"><span>SHIVA SAYS</span><h2>Start / Sit</h2><p>Compare the strongest verified combination of weekly floor, ceiling, consistency and current ranking context.</p></div><div className="compare-selects"><label>Player A<select value={playerA} onChange={(event) => { setPlayerA(event.target.value); setEvidenceA(null); setEvidenceB(null) }}>{comparisonNames.map((name) => <option key={name}>{name}</option>)}</select></label><label>Player B<select value={playerB} onChange={(event) => { setPlayerB(event.target.value); setEvidenceA(null); setEvidenceB(null) }}>{comparisonNames.map((name) => <option key={name}>{name}</option>)}</select></label></div><button className="primary-button" onClick={compare} disabled={playerA === playerB || compareLoading}>{compareLoading ? 'Reading historical database…' : 'Compare Players'}</button>{winner && evidenceA && evidenceB && <><div className="shiva-call"><span>SHIVA SAYS</span><h2>Start {winner}</h2><p>The call is based on the historical weekly database plus current ranking context. No fake weekly projection or confidence percentage is being invented.</p></div><div className="compare-grid">{[[playerA,evidenceA],[playerB,evidenceB]].map(([name, evidence]) => { const e = evidence as Evidence; const ranked = rankedByName(String(name)); return <button type="button" className={`compare-card clickable-player ${winner === name ? 'winner' : ''}`} key={String(name)} onClick={() => openRanked(String(name), { ppg:e.ppg })}><div className="compare-head"><div className="player-inline"><PlayerAvatar playerId={ranked?.espnId || ranked?.id} name={String(name)} /><div><b>{String(name)}</b><span>{e.pos} · {e.team}</span></div></div><strong>{ranked?.rank && ranked.rank < 10000 ? `#${ranked.rank}` : '—'}</strong></div><div className="evidence-grid"><div><b>{num(e.floor)}</b><span>Floor</span></div><div><b>{num(e.ppg)}</b><span>PPG</span></div><div><b>{num(e.ceiling)}</b><span>Ceiling</span></div><div><b>{num(e.rate15,0,'%')}</b><span>15+ Weeks</span></div></div></button> })}</div></>}</>}

    {tab === 'Waivers' && <><div className="section-heading"><div><div className="section-kicker">AVAILABLE TALENT</div><h2>Waiver Wire</h2></div>{league && <span className="live-dot">LEAGUE LIVE</span>}</div>{!league ? <div className="empty-state">Connect ESPN to rank your league’s actual free-agent pool.</div> : <div className="player-pool">{waiverRows.map(({ agent, player }, index) => <button type="button" className="pool-row waiver-photo-row clickable-player" key={agent.playerId || agent.player} onClick={() => openRanked(agent.player, { id:agent.playerId, espnId:agent.playerId, team:PRO_TEAM[agent.proTeamId || 0] || player?.team || '', injuryStatus:agent.injuryStatus, percentOwned:agent.percentOwned, percentStarted:agent.percentStarted, rank:player?.rank, posRank:player?.posRank, pos:player?.pos })}><div className="pool-rank">{index + 1}</div><PlayerAvatar playerId={agent.playerId} name={agent.player} /><span className={`pos-chip pos-${player?.pos || 'NA'}`}>{player?.pos || '—'}</span><div className="pool-name"><b>{agent.player}</b><small>{player ? `${player.team} · Shiva ${player.rank < 10000 ? `#${player.rank}` : '—'}` : 'ESPN free agent'}{agent.injuryStatus ? ` · ${agent.injuryStatus}` : ''}</small></div><div className="owned"><b>{num(agent.percentOwned,0,'%')}</b><span>Owned</span></div></button>)}</div>}</>}

    {tab === 'Lineup' && <><div className="section-kicker">LINEUP CHECK</div><h2 className="screen-subtitle">Protect your FLEX.</h2>{!league ? <div className="empty-state">Connect ESPN to run lineup checks against your actual roster.</div> : <>{lineupWarnings.length ? lineupWarnings.map(({ row, day, danger }) => <button type="button" className={`lineup-alert clickable-player ${danger ? 'danger' : 'good'}`} key={row.player} onClick={() => openRosterPlayer(row)}><div className="player-inline"><PlayerAvatar playerId={row.playerId} name={row.player} /><div><span>{danger ? 'SHIVA MOMENT' : 'LINEUP CHECK'}</span><b>{danger ? `Move ${row.player} out of FLEX.` : `${row.player}: no Thursday FLEX trap.`}</b></div></div><p>{danger ? `${PRO_TEAM[row.proTeamId || 0] || row.team} plays Thursday. Put him in his natural position slot and preserve FLEX for later injury/availability changes.` : `Current ESPN schedule has this player on ${day}.`}</p></button>) : <div className="lineup-alert good"><span>LINEUP CHECK</span><b>No FLEX alert is firing.</b><p>Shiva did not find a connected FLEX player with a Thursday game in the current ESPN scoreboard.</p></div>}<div className="lineup-roster">{rosterRows(starters)}</div></>}</>}

    {tab === 'Player Watch' && <><div className="section-kicker">CURRENT ESPN CONTEXT</div><h2 className="screen-subtitle">Player Watch</h2><p className="lede">Live article mentions for injury, role and team context. This is current news, not a fabricated injury database.</p><div className="watch-controls"><button type="button" className="player-inline clickable-name" onClick={() => watchCurrent && openRanked(watchCurrent.name)}><PlayerAvatar playerId={watchCurrent?.espnId || watchCurrent?.id} name={watchPlayer || 'Player'} /></button><select value={watchPlayer} onChange={(event) => { setWatchPlayer(event.target.value); setWatchNews([]) }}>{players.slice(0, 400).map((player) => <option key={player.id}>{player.name}</option>)}</select><button className="primary-button" onClick={loadWatch}>Check ESPN</button></div>{watchNews.length ? <div className="watch-list">{watchNews.map((article) => <a className="watch-card" href={article.url || '#'} target="_blank" rel="noreferrer" key={article.headline}><span>ESPN</span><b>{article.headline}</b><p>{article.description}</p><em>Open story →</em></a>)}</div> : <div className="empty-state">Choose a player and check the current ESPN feed.</div>}</>}

    {tab === 'Ask Shiva' && <><div className="coach-hero"><span>SHIVA INTELLIGENCE</span><h2>Ask Shiva</h2><p>Ask a roster, draft, lineup, waiver or player-comparison question. Connected league context is included automatically.</p></div><textarea className="ask-box" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Example: Should I start Zay Flowers or DeVonta Smith this week?" rows={5} /><button className="primary-button" onClick={askShiva}>Ask Shiva</button>{askStatus && <p className="status-copy">{askStatus}</p>}{answer && <div className="answer-card">{answer}</div>}</>}

    {tab === 'Players' && <><div className="section-heading players-heading"><div><div className="section-kicker">ESPN PLAYER RANKINGS</div><h2>Players</h2></div><span className="live-dot">ESPN LIVE</span></div><div className="filter-pills players-filter-pills">{['ALL','QB','RB','WR','TE','FLEX'].map((filter) => <button key={filter} className={playerFilter === filter ? 'active' : ''} onClick={() => setPlayerFilter(filter)}>{filter}</button>)}</div><div className="players-live-list">{playerRows.map((player, index) => <button type="button" className="players-live-row clickable-player" key={player.id} onClick={() => openRanked(player.name)}><span className="players-live-rank">{player.espnRank ? `#${player.espnRank}` : `#${index + 1}`}</span><PlayerAvatar playerId={player.espnId || player.id} name={player.name} /><div className="players-live-copy"><b>{player.name}</b><small>{player.pos} · {player.team || '—'}{player.injuryStatus ? ` · ${player.injuryStatus}` : ''}</small></div>{player.team && <img className="team-logo" src={teamLogoUrl(player.team)} alt={`${player.team} logo`} loading="lazy" />}<div className="players-live-proj"><b>{num(player.projectedPoints)}</b><span>PROJ</span></div></button>)}</div></>}

    {selectedPlayer && <PlayerDetailOverlay player={selectedPlayer} onClose={() => setSelectedPlayer(null)} />}
  </>
}
