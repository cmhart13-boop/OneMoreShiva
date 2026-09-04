'use client'

import { useEffect, useMemo, useState } from 'react'
import { PlayerAvatar, PlayerDetailOverlay, type PlayerDetailData } from './PlayerMedia'
import type { Evidence, LeagueProvider, LeagueState, NewsArticle, Player, SavedLeague } from '../lib/types'
import { activateLeague, importSaveActivate, PENDING_LEAGUE_KEY, type LeagueImportRequest } from '../lib/league-client'
import { recommendStart, type Recommendation } from '../lib/recommendation'

export type CoachTab = 'Overview' | 'League' | 'Start / Sit' | 'Waivers' | 'Lineup' | 'Player Watch' | 'Ask Shiva' | 'Players'
type SelectedPlayer = PlayerDetailData & { slot?: string; percentStarted?: number | null }
type CoachViewProps = {
  showTabs?: boolean
  activeTab?: CoachTab
  onTabChange?: (tab: CoachTab) => void
}

const PRO_TEAM: Record<number, string> = {
  1:'ATL',2:'BUF',3:'CHI',4:'CIN',5:'CLE',6:'DAL',7:'DEN',8:'DET',9:'GB',10:'TEN',11:'IND',12:'KC',13:'LV',14:'LAR',15:'MIA',16:'MIN',17:'NE',18:'NO',19:'NYG',20:'NYJ',21:'PHI',22:'ARI',23:'PIT',24:'LAC',25:'SF',26:'SEA',27:'TB',28:'WAS',29:'CAR',30:'JAX',33:'BAL',34:'HOU'
}

function num(value: number | null | undefined, digits = 1, suffix = '') {
  return value === null || value === undefined || !Number.isFinite(value) ? '—' : `${value.toFixed(digits)}${suffix}`
}

function teamLogoUrl(team: string) {
  return team ? `https://a.espncdn.com/i/teamlogos/nfl/500/${team.toLowerCase()}.png` : ''
}

export default function CoachView({ showTabs = true, activeTab, onTabChange }: CoachViewProps) {
  const [internalTab, setInternalTab] = useState<CoachTab>(activeTab || 'Overview')
  const tab = activeTab ?? internalTab
  const setTab = (next: CoachTab) => {
    setInternalTab(next)
    onTabChange?.(next)
  }
  const [players, setPlayers] = useState<Player[]>([])
  const [playerFilter, setPlayerFilter] = useState('ALL')
  const [league, setLeague] = useState<LeagueState | null>(null)
  const [teamId, setTeamId] = useState<string | number | null>(null)
  const [savedLeagues, setSavedLeagues] = useState<SavedLeague[]>([])
  const [activeSavedId, setActiveSavedId] = useState('')
  const [provider, setProvider] = useState<LeagueProvider>('espn')
  const [leagueId, setLeagueId] = useState('')
  const [season] = useState(2026)
  const [connectStatus, setConnectStatus] = useState('')
  const [playerA, setPlayerA] = useState('')
  const [playerB, setPlayerB] = useState('')
  const [evidenceA, setEvidenceA] = useState<Evidence | null>(null)
  const [evidenceB, setEvidenceB] = useState<Evidence | null>(null)
  const [compareLoading, setCompareLoading] = useState(false)
  const [compareSlot, setCompareSlot] = useState('FLEX')
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null)
  const [watchPlayer, setWatchPlayer] = useState('')
  const [watchedPlayers, setWatchedPlayers] = useState<string[]>([])
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
        setWatchPlayer((value) => value || loaded[0].name)
      }
    }).catch(() => setPlayers([]))
    fetch('/api/scoreboard').then((response) => response.json()).then((data) => setGames(data.games || [])).catch(() => setGames([]))
    try {
      const stored = window.sessionStorage.getItem('shiva-league')
      const storedTeam = window.sessionStorage.getItem('shiva-team-id')
      const storedWatch = window.localStorage.getItem('shiva-player-watch')
      if (stored) setLeague(JSON.parse(stored))
      if (storedTeam) setTeamId(storedTeam)
      if (storedWatch) {
        const parsed = JSON.parse(storedWatch)
        if (Array.isArray(parsed)) setWatchedPlayers(parsed.filter((name): name is string => typeof name === 'string'))
      }
    } catch {}
    fetch('/api/leagues', { cache:'no-store' }).then(async (response) => response.ok ? response.json() : null).then((data) => setSavedLeagues(data?.leagues || [])).catch(() => {})
  }, [])

  useEffect(() => {
    const changed = (event: Event) => {
      const detail = (event as CustomEvent<{ league:LeagueState; teamId:string | number | null }>).detail
      if (detail?.league) { setLeague(detail.league); setTeamId(detail.teamId); setConnectStatus('League connected and saved.'); fetch('/api/leagues', { cache:'no-store' }).then((r) => r.ok ? r.json() : null).then((d) => setSavedLeagues(d?.leagues || [])).catch(() => {}) }
    }
    window.addEventListener('shiva:league-changed', changed)
    return () => window.removeEventListener('shiva:league-changed', changed)
  }, [])

  const roster = useMemo(() => league && teamId !== null ? league.roster.filter((row) => String(row.teamId) === String(teamId)) : [], [league, teamId])
  const starters = useMemo(() => roster.filter((row) => row.slot !== 'BE' && row.slot !== 'IR'), [roster])
  const bench = useMemo(() => roster.filter((row) => row.slot === 'BE' || row.slot === 'IR'), [roster])
  const lineupGroups = useMemo(() => {
    const order = Array.from(new Set([...(league?.league.rosterSlots || []), ...roster.map((row) => row.slot)]))
    return order.map((slot) => ({ slot, rows:roster.filter((row) => row.slot === slot) })).filter((group) => group.rows.length)
  }, [league, roster])
  const standings = useMemo(() => league ? [...league.teams].sort((a, b) => (b.wins ?? -1) - (a.wins ?? -1) || (a.losses ?? 999) - (b.losses ?? 999) || a.name.localeCompare(b.name)) : [], [league])
  const eligibleSlots = useMemo(() => Array.from(new Set((league?.league.rosterSlots || starters.map((row) => row.slot)).filter((slot) => !['BE','BN','IR'].includes(slot)))), [league, starters])
  const comparisonRows = useMemo(() => roster.filter((row) => row.slot !== 'IR' && (row.eligibleSlots?.includes(compareSlot) || row.position === compareSlot || row.slot === compareSlot || (compareSlot === 'FLEX' && ['RB','WR','TE'].includes(row.position || '')))), [roster, compareSlot])
  const comparisonNames = useMemo(() => comparisonRows.map((row) => row.player).filter(Boolean), [comparisonRows])
  const playerRows = useMemo(() => players.filter((player) => playerFilter === 'ALL' || (playerFilter === 'FLEX' ? ['RB','WR','TE'].includes(player.pos) : player.pos === playerFilter)).slice(0, playerFilter === 'ALL' ? 150 : 75), [players, playerFilter])

  useEffect(() => {
    setPlayerA((value) => comparisonNames.includes(value) ? value : comparisonNames[0] || '')
    setPlayerB((value) => comparisonNames.includes(value) && value !== comparisonNames[0] ? value : comparisonNames[1] || '')
    setRecommendation(null)
    setEvidenceA(null); setEvidenceB(null)
  }, [comparisonNames, playerA, playerB])

  useEffect(() => {
    if (watchedPlayers.length && !watchedPlayers.includes(watchPlayer)) {
      setWatchPlayer(watchedPlayers[0])
      setWatchNews([])
    }
  }, [watchedPlayers, watchPlayer])

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
      team: row.proTeam || PRO_TEAM[row.proTeamId || 0] || ranked?.team || '',
      slot: row.slot,
      injuryStatus: row.injuryStatus,
      percentOwned: row.percentOwned,
      percentStarted: row.percentStarted,
      rank: ranked?.rank,
      posRank: ranked?.posRank,
      pos: ranked?.pos,
    })
  }

  const toggleWatchedPlayer = (name: string) => {
    setWatchedPlayers((current) => {
      const adding = !current.includes(name)
      const next = adding ? [...current, name] : current.filter((item) => item !== name)
      try { window.localStorage.setItem('shiva-player-watch', JSON.stringify(next)) } catch {}
      if (adding) {
        setWatchPlayer(name)
        setWatchNews([])
      }
      return next
    })
  }

  const connect = async () => {
    if (!leagueId.trim()) { setConnectStatus('Enter a league ID.'); return }
    const input: LeagueImportRequest = { provider, leagueId:leagueId.trim(), season }
    setConnectStatus('Checking your account…')
    try {
      const session = await fetch('/api/auth/session', { cache:'no-store' })
      if (!session.ok) {
        localStorage.setItem(PENDING_LEAGUE_KEY, JSON.stringify(input))
        window.dispatchEvent(new CustomEvent('shiva:require-auth', { detail:input }))
        setConnectStatus('Sign in to save this league. Your selection is ready to continue.')
        return
      }
      setConnectStatus(`Importing from ${provider === 'espn' ? 'ESPN' : 'Sleeper'}…`)
      await importSaveActivate(input)
      setConnectStatus('League connected and saved.')
    } catch (error) {
      setConnectStatus(error instanceof Error ? error.message : 'League import failed.')
    }
  }

  const disconnect = () => {
    setLeague(null)
    setTeamId(null)
    setConnectStatus('')
    try {
      window.sessionStorage.removeItem('shiva-league')
      window.sessionStorage.removeItem('shiva-team-id')
    } catch {}
    setTab('Overview')
  }

  const compare = async () => {
    if (!playerA || !playerB || playerA === playerB) return
    setCompareLoading(true)
    try {
      const [a, b] = await Promise.all([
        fetch(`/api/evidence?player=${encodeURIComponent(playerA)}`).then((response) => response.json()),
        fetch(`/api/evidence?player=${encodeURIComponent(playerB)}`).then((response) => response.json()),
      ])
      const nextA = a.evidence || null
      const nextB = b.evidence || null
      setEvidenceA(nextA); setEvidenceB(nextB)
      const rowA = comparisonRows.find((row) => row.player === playerA)
      const rowB = comparisonRows.find((row) => row.player === playerB)
      if (rowA && rowB) setRecommendation(recommendStart(rowA, rowB, players, nextA, nextB, league?.league.scoringSettings || {}))
    } finally { setCompareLoading(false) }
  }

  const winner = recommendation?.winner || null

  const switchLeague = (id: string) => {
    const saved = savedLeagues.find((item) => item.id === id)
    if (!saved?.league_data) return
    setActiveSavedId(id)
    activateLeague(saved.league_data, saved.team_id)
  }

  const switchTeam = async (nextId: string) => {
    setTeamId(nextId)
    sessionStorage.setItem('shiva-team-id', nextId)
    const saved = savedLeagues.find((item) => item.id === activeSavedId) || savedLeagues.find((item) => item.league_data?.league.id === league?.league.id)
    const team = league?.teams.find((item) => String(item.id) === nextId)
    if (saved) await fetch('/api/leagues', { method:'PATCH', headers:{ 'Content-Type':'application/json' }, body:JSON.stringify({ id:saved.id, teamId:nextId, teamName:team?.name || '' }) }).catch(() => {})
  }

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

  const rosterRows = (rows: LeagueState['roster']) => <div className="espn-roster">{rows.map((row) => <button type="button" className="espn-roster-row clickable-player" key={`${row.teamId}-${row.playerId}-${row.slot}`} onClick={() => openRosterPlayer(row)}><span className="espn-slot">{row.slot}</span><PlayerAvatar playerId={row.playerId} name={row.player} /><div className="espn-player-copy"><b>{row.player}</b><small>{row.proTeam || PRO_TEAM[row.proTeamId || 0] || row.position || ''}{row.injuryStatus ? ` · ${row.injuryStatus}` : ''}</small></div><span className="espn-row-rank">{rankedByName(row.player)?.rank && rankedByName(row.player)!.rank < 10000 ? `#${rankedByName(row.player)!.rank}` : ''}</span></button>)}</div>

  const watchCurrent = rankedByName(watchPlayer)

  return <>
    {showTabs && <div className="coach-tabs">{(['Overview','League','Start / Sit','Waivers','Lineup','Player Watch','Ask Shiva','Players'] as CoachTab[]).map((item) => <button key={item} className={tab === item ? 'active' : ''} onClick={() => setTab(item)}>{item}</button>)}</div>}

    {league && <div className="panel league-context" aria-label="Active league and team"><label>League<select aria-label="Active league" value={activeSavedId || savedLeagues.find((item) => item.league_data?.league.id === league.league.id)?.id || ''} onChange={(event) => switchLeague(event.target.value)}><option value="">{league.league.name}</option>{savedLeagues.map((item) => <option key={item.id} value={item.id}>{item.nickname || item.league_name || `League ${item.league_id}`}</option>)}</select></label><label>Team<select aria-label="Active team" value={teamId ?? ''} onChange={(event) => switchTeam(event.target.value)}>{league.teams.map((team) => <option value={String(team.id)} key={team.id}>{team.name}</option>)}</select></label></div>}

    {tab === 'Overview' && <><div className="coach-hero overview-connect-card"><h2>{league ? `${league.league.name} is connected.` : 'Add Your League'}</h2>{league ? <><p>{roster.length} players loaded for your selected team. Start/Sit, waivers and lineup checks can use that roster now.</p><button className="ghost-button compact" onClick={() => setTab('League')}>View League →</button></> : <><div className="overview-connect-row provider-connect-row"><label>Provider<select aria-label="League provider" value={provider} onChange={(event) => setProvider(event.target.value as LeagueProvider)}><option value="espn">ESPN</option><option value="sleeper">Sleeper</option></select></label><label>League ID<input value={leagueId} onChange={(event) => setLeagueId(event.target.value)} inputMode="numeric" placeholder={provider === 'sleeper' ? 'Sleeper league ID' : 'ESPN league ID'} /></label><button className="primary-button compact-connect-button" onClick={connect} disabled={!leagueId.trim() || connectStatus.startsWith('Importing')}>Go</button></div>{connectStatus && <p className="status-copy" role="status">{connectStatus}</p>}</>}</div><div className="strategy-grid"><article className="panel"><span className="eyebrow">LINEUP EDGE</span><h2>{lineupWarnings.some((item) => item.danger) ? 'Thursday FLEX issue found' : 'No Thursday FLEX trap found'}</h2><p>{roster.length ? `Lineup checks use the connected ${league?.league.provider === 'sleeper' ? 'Sleeper' : 'ESPN'} roster.` : 'Connect a league to run the lineup rule engine.'}</p></article><article className="panel"><span className="eyebrow">DRAFT EDGE</span><h2>Rank + ADP, not rank alone</h2><p>Shiva Draft IQ protects against reaching while still filling roster needs.</p></article></div></>}

    {tab === 'League' && <>{league ? <div className="league-stack"><div className="panel league-panel"><div className="status-pill good">● {league.league.provider.toUpperCase()} LEAGUE CONNECTED</div><h2>{league.league.name}</h2><p>{league.league.season} · Week {league.league.scoringPeriod ?? '—'} · Matchup period {league.league.matchupPeriod ?? '—'}</p><button className="ghost-button compact" onClick={disconnect}>Disconnect league</button></div><div className="panel standings-panel"><div className="section-heading compact-heading"><div><div className="section-kicker">CURRENT TABLE</div><h2>League Standings</h2></div></div><div className="standings-list">{standings.map((team, index) => <div className={`standing-row ${String(team.id) === String(teamId) ? 'mine' : ''}`} key={team.id}><span>{index + 1}</span><div><b>{team.name}</b><small>{team.owners.join(', ') || `${league.league.provider.toUpperCase()} team`}</small></div><strong>{team.wins ?? '—'}-{team.losses ?? '—'}</strong></div>)}</div></div><div className="panel league-panel"><label>Your team</label><select value={teamId ?? ''} onChange={(event) => switchTeam(event.target.value)}>{league.teams.map((team) => <option value={String(team.id)} key={team.id}>{team.name}</option>)}</select><div className="section-kicker" style={{marginTop:14}}>STARTERS</div>{rosterRows(starters)}{bench.length > 0 && <><div className="section-kicker" style={{marginTop:14}}>BENCH / IR</div>{rosterRows(bench)}</>}</div></div> : <div className="empty-state">Add a league from Overview. Once connected, current context, standings, records and your roster will appear here.</div>}</>}

    {tab === 'Start / Sit' && <><div className="coach-hero"><span>SHIVA SAYS</span><h2>Start / Sit</h2><p>Compare eligible players from your selected team using this league’s roster rules and scoring.</p></div>{!league ? <div className="empty-state">Add a league first to compare players from your real roster.</div> : <><label className="compare-slot-label">Lineup slot<select aria-label="Lineup slot" value={compareSlot} onChange={(event) => setCompareSlot(event.target.value)}>{eligibleSlots.map((slot) => <option key={slot}>{slot}</option>)}</select></label>{comparisonNames.length < 2 ? <div className="empty-state">This team does not have two eligible players for {compareSlot}.</div> : <><div className="compare-selects"><label>Player A<select value={playerA} onChange={(event) => { setPlayerA(event.target.value); setRecommendation(null) }}>{comparisonNames.map((name) => <option key={name}>{name}</option>)}</select></label><label>Player B<select value={playerB} onChange={(event) => { setPlayerB(event.target.value); setRecommendation(null) }}>{comparisonNames.map((name) => <option key={name}>{name}</option>)}</select></label></div><button className="primary-button" onClick={compare} disabled={!playerA || !playerB || playerA === playerB || compareLoading}>{compareLoading ? 'Comparing…' : 'Compare Players'}</button>{winner && evidenceA && evidenceB && recommendation && <><div className="shiva-call recommendation-call"><span>{recommendation.confidence}</span><h2>Start {winner}</h2><p>{recommendation.explanation}</p></div><div className="compare-grid">{[[playerA,evidenceA],[playerB,evidenceB]].map(([name, evidence]) => { const e = evidence as Evidence; const ranked = rankedByName(String(name)); return <button type="button" className={`compare-card clickable-player ${winner === name ? 'winner recommended' : ''}`} key={String(name)} onClick={() => openRanked(String(name), { ppg:e.ppg })}><div className="compare-head"><div className="player-inline"><PlayerAvatar playerId={ranked?.espnId || ranked?.id} name={String(name)} /><div><b>{String(name)}</b><span>{e.pos} · {e.team}</span></div></div><strong>{winner === name ? 'START' : 'OPTION'}</strong></div><div className="evidence-grid"><div><b>{num(e.floor)}</b><span>Floor</span></div><div><b>{num(e.ppg)}</b><span>PPG</span></div><div><b>{num(e.ceiling)}</b><span>Ceiling</span></div><div><b>{num(e.recent)}</b><span>Recent role</span></div></div></button> })}</div></>}</>}</>}</>}

    {tab === 'Waivers' && <><div className="section-heading"><div><div className="section-kicker">AVAILABLE TALENT</div><h2>Waiver Wire</h2></div>{league && <span className="live-dot">LEAGUE LIVE</span>}</div>{!league ? <div className="empty-state">Connect ESPN to rank your league’s actual free-agent pool.</div> : <div className="player-pool">{waiverRows.map(({ agent, player }, index) => <button type="button" className="pool-row waiver-photo-row clickable-player" key={agent.playerId || agent.player} onClick={() => openRanked(agent.player, { id:agent.playerId, espnId:agent.playerId, team:PRO_TEAM[agent.proTeamId || 0] || player?.team || '', injuryStatus:agent.injuryStatus, percentOwned:agent.percentOwned, percentStarted:agent.percentStarted, rank:player?.rank, posRank:player?.posRank, pos:player?.pos })}><div className="pool-rank">{index + 1}</div><PlayerAvatar playerId={agent.playerId} name={agent.player} /><span className={`pos-chip pos-${player?.pos || 'NA'}`}>{player?.pos || '—'}</span><div className="pool-name"><b>{agent.player}</b><small>{player ? `${player.team} · Shiva ${player.rank < 10000 ? `#${player.rank}` : '—'}` : 'ESPN free agent'}{agent.injuryStatus ? ` · ${agent.injuryStatus}` : ''}</small></div><div className="owned"><b>{num(agent.percentOwned,0,'%')}</b><span>Owned</span></div></button>)}</div>}</>}

    {tab === 'Lineup' && <><div className="section-kicker">LINEUP</div><h2 className="screen-subtitle">Your actual roster.</h2>{!league ? <div className="empty-state">Add a league to load its real lineup slots and roster.</div> : <div className="lineup-slot-groups">{lineupGroups.map((group) => <section className="lineup-slot-group" key={group.slot}><div className="section-kicker">{['BE','BN'].includes(group.slot) ? 'BENCH' : group.slot}</div>{rosterRows(group.rows)}</section>)}</div>}</>}

    {tab === 'Player Watch' && <><div className="section-kicker">CURRENT ESPN CONTEXT</div><h2 className="screen-subtitle">Player Watch</h2><p className="lede">Live article mentions for injury, role and team context. This is current news, not a fabricated injury database.</p>{watchedPlayers.length ? <div className="watched-player-pills">{watchedPlayers.map((name) => <button type="button" key={name} className={watchPlayer === name ? 'active' : ''} onClick={() => { setWatchPlayer(name); setWatchNews([]) }}>{name}</button>)}</div> : <div className="empty-state watch-empty">Flag a player from Players to add him to Player Watch.</div>}<div className="watch-controls"><button type="button" className="player-inline clickable-name" onClick={() => watchCurrent && openRanked(watchCurrent.name)}><PlayerAvatar playerId={watchCurrent?.espnId || watchCurrent?.id} name={watchPlayer || 'Player'} /></button><select value={watchPlayer} onChange={(event) => { setWatchPlayer(event.target.value); setWatchNews([]) }}>{players.slice(0, 400).map((player) => <option key={player.id}>{player.name}</option>)}</select><button className="primary-button" onClick={loadWatch}>Check ESPN</button></div>{watchNews.length ? <div className="watch-list">{watchNews.map((article) => <a className="watch-card" href={article.url || '#'} target="_blank" rel="noreferrer" key={article.headline}><span>ESPN</span><b>{article.headline}</b><p>{article.description}</p><em>Open story →</em></a>)}</div> : <div className="empty-state">Choose a player and check the current ESPN feed.</div>}</>}

    {tab === 'Ask Shiva' && <><div className="coach-hero"><span>SHIVA INTELLIGENCE</span><h2>Ask Shiva</h2><p>Ask a roster, draft, lineup, waiver or player-comparison question. Connected league context is included automatically.</p></div><textarea className="ask-box" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Example: Should I start Zay Flowers or DeVonta Smith this week?" rows={5} /><button className="primary-button" onClick={askShiva}>Ask Shiva</button>{askStatus && <p className="status-copy">{askStatus}</p>}{answer && <div className="answer-card">{answer}</div>}</>}

    {tab === 'Players' && <><div className="section-heading players-heading"><div><div className="section-kicker">ESPN PLAYER RANKINGS</div><h2>Players</h2></div><button type="button" className="live-dot player-watch-link" onClick={() => setTab('Player Watch')}>Player Watch{watchedPlayers.length ? ` (${watchedPlayers.length})` : ''}</button></div><div className="filter-pills players-filter-pills">{['ALL','QB','RB','WR','TE','FLEX'].map((filter) => <button key={filter} className={playerFilter === filter ? 'active' : ''} onClick={() => setPlayerFilter(filter)}>{filter}</button>)}</div><div className="players-live-list">{playerRows.map((player, index) => <div role="button" tabIndex={0} className="players-live-row clickable-player" key={player.id} onClick={() => openRanked(player.name)} onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') openRanked(player.name) }}><span className="players-live-rank">{player.espnRank ? `#${player.espnRank}` : `#${index + 1}`}</span><PlayerAvatar playerId={player.espnId || player.id} name={player.name} /><div className="players-live-copy"><b>{player.name}</b><small>{player.pos} · {player.team || '—'}{player.injuryStatus ? ` · ${player.injuryStatus}` : ''}</small></div>{player.team && <img className="team-logo" src={teamLogoUrl(player.team)} alt={`${player.team} logo`} loading="lazy" />}<div className="players-live-proj"><b>{num(player.projectedPoints)}</b><span>PROJ</span></div><button type="button" className={`player-watch-flag${watchedPlayers.includes(player.name) ? ' active' : ''}`} aria-label={`${watchedPlayers.includes(player.name) ? 'Remove' : 'Add'} ${player.name} ${watchedPlayers.includes(player.name) ? 'from' : 'to'} Player Watch`} aria-pressed={watchedPlayers.includes(player.name)} onClick={(event) => { event.stopPropagation(); toggleWatchedPlayer(player.name) }}><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 17V3.25m0 .75h7.2l-1.35 2.35L12.2 8.7H5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg></button></div>)}</div></>}

    {selectedPlayer && <PlayerDetailOverlay player={selectedPlayer} onClose={() => setSelectedPlayer(null)} />}
  </>
}
