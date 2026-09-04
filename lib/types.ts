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

export type LeagueTeam = { id: number; name: string; owners: string[]; wins: number | null; losses: number | null }
export type LeagueRosterRow = {
  teamId: number
  team: string
  playerId: string
  player: string
  slotId: number
  slot: string
  proTeamId: number | null
  injuryStatus: string
  percentOwned: number | null
  percentStarted: number | null
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
  league: { id: string; season: number; name: string; scoringPeriod: number | null; matchupPeriod: number | null }
  teams: LeagueTeam[]
  roster: LeagueRosterRow[]
  freeAgents: FreeAgent[]
}

export type NewsArticle = { headline: string; description: string; published: string; url: string; image: string }
