export type Player = {
  id: string
  espnId?: string
  name: string
  team: string
  bye: number | null
  pos: string
  posRank: number | null
  adp: number | null
  consensusAdp: number | null
  rank: number
  espnRank?: number | null
  projectedPoints?: number | null
  percentOwned?: number | null
  percentStarted?: number | null
  injuryStatus?: string
}

export type Evidence = {
  name: string
  pos: string
  team: string
  games: number
  season: number | null
  ppg: number | null
  floor: number | null
  ceiling: number | null
  rate15: number | null
  boom25: number | null
  bust10: number | null
  recent: number | null
}

export type LeagueProvider = 'espn' | 'sleeper'
export type LeagueTeam = { id: string | number; name: string; owners: string[]; wins: number | null; losses: number | null }
export type LeagueMatchup = {
  period: number
  homeTeamId: string | number
  awayTeamId: string | number
  homeScore: number | null
  awayScore: number | null
  homeProjected: number | null
  awayProjected: number | null
}
export type LeagueRosterRow = {
  teamId: string | number
  team: string
  playerId: string
  player: string
  slotId: string | number
  slot: string
  proTeamId: number | null
  proTeam?: string
  position?: string
  eligibleSlots?: string[]
  injuryStatus: string
  percentOwned: number | null
  percentStarted: number | null
  projectedPoints?: number | null
}
export type FreeAgent = {
  playerId: string
  player: string
  status: string
  proTeamId: number | null
  injuryStatus: string
  percentOwned: number | null
  percentStarted: number | null
}
export type LeagueState = {
  league: {
    id: string
    provider: LeagueProvider
    season: number
    name: string
    scoringPeriod: number | null
    matchupPeriod: number | null
    rosterSlots: string[]
    scoringSettings: Record<string, number>
  }
  teams: LeagueTeam[]
  roster: LeagueRosterRow[]
  freeAgents: FreeAgent[]
  matchups?: LeagueMatchup[]
}

export type SavedLeague = {
  id: string
  provider: LeagueProvider
  league_id: string
  season: number
  nickname?: string | null
  team_id?: string | number | null
  league_name?: string | null
  team_name?: string | null
  league_data?: LeagueState | null
}

export type NewsArticle = { headline: string; description: string; published: string; url: string; image: string }
