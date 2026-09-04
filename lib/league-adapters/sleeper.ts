import type { LeagueState } from '../types'

type SleeperBundle = { league:any; users:any[]; rosters:any[]; players:Record<string, any> }

const FLEX_ELIGIBILITY: Record<string, string[]> = {
  FLEX:['RB','WR','TE'], SUPER_FLEX:['QB','RB','WR','TE'], REC_FLEX:['RB','WR','TE'], WRRB_FLEX:['RB','WR'],
}

export function normalizeSleeperLeague({ league, users, rosters, players }: SleeperBundle): LeagueState {
  const userMap = new Map(users.map((user) => [String(user.user_id), user]))
  const teams: LeagueState['teams'] = []
  const rosterRows: LeagueState['roster'] = []
  const rosterSlots = Array.isArray(league.roster_positions) ? league.roster_positions.map(String) : []
  for (const roster of rosters) {
    const teamId = String(roster.roster_id)
    const owner = userMap.get(String(roster.owner_id))
    const name = String(owner?.metadata?.team_name || owner?.display_name || `Team ${teamId}`)
    teams.push({ id:teamId, name, owners:owner?.display_name ? [String(owner.display_name)] : [], wins:roster.settings?.wins ?? null, losses:roster.settings?.losses ?? null })
    const starters: string[] = Array.isArray(roster.starters) ? roster.starters.map(String) : []
    const allPlayers: string[] = Array.isArray(roster.players) ? roster.players.map(String) : []
    for (const playerId of allPlayers) {
      if (!playerId || playerId === '0') continue
      const player = players[playerId] || {}
      const starterIndex = starters.indexOf(playerId)
      const slot = starterIndex >= 0 ? String(rosterSlots[starterIndex] || player.position || 'START') : 'BE'
      const positions = (player.fantasy_positions || [player.position]).filter(Boolean).map(String)
      const eligibleSlots = Array.from(new Set([...positions, ...Object.entries(FLEX_ELIGIBILITY).filter(([, allowed]) => positions.some((pos) => allowed.includes(pos))).map(([flex]) => flex)]))
      rosterRows.push({
        teamId, team:name, playerId, player:String(player.full_name || `${player.first_name || ''} ${player.last_name || ''}`.trim() || `Player ${playerId}`),
        slotId:slot, slot, proTeamId:null, proTeam:String(player.team || ''), position:String(player.position || positions[0] || ''), eligibleSlots,
        injuryStatus:String(player.injury_status || ''), percentOwned:null, percentStarted:null,
      })
    }
  }
  return {
    league:{
      id:String(league.league_id || ''), provider:'sleeper', season:Number(league.season || new Date().getFullYear()),
      name:String(league.name || 'Sleeper League'), scoringPeriod:Number(league.settings?.leg || 0) || null,
      matchupPeriod:Number(league.settings?.leg || 0) || null, rosterSlots,
      scoringSettings:Object.fromEntries(Object.entries(league.scoring_settings || {}).map(([key, value]) => [key, Number(value) || 0])),
    },
    teams, roster:rosterRows, freeAgents:[],
  }
}

export async function importSleeperLeague(leagueId: string): Promise<LeagueState> {
  const base = 'https://api.sleeper.app/v1'
  const get = async (path: string) => {
    const response = await fetch(`${base}${path}`, { next:{ revalidate:3600 } })
    if (!response.ok) throw new Error(`Sleeper returned ${response.status}. Check the league ID.`)
    return response.json()
  }
  const [league, users, rosters] = await Promise.all([get(`/league/${encodeURIComponent(leagueId)}`), get(`/league/${encodeURIComponent(leagueId)}/users`), get(`/league/${encodeURIComponent(leagueId)}/rosters`)])
  if (!league?.league_id) throw new Error('Sleeper league not found. Check the league ID.')
  const allPlayers = await get('/players/nfl')
  const needed = new Set<string>(rosters.flatMap((roster:any) => Array.isArray(roster.players) ? roster.players.map(String) : []))
  const players = Object.fromEntries([...needed].map((id) => [id, allPlayers[id] || {}]))
  return normalizeSleeperLeague({ league, users:users || [], rosters:rosters || [], players })
}
