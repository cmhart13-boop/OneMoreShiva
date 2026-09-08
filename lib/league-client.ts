'use client'

import type { LeagueProvider, LeagueState, SavedLeague } from './types'

export const PENDING_LEAGUE_KEY = 'shiva-pending-league-import'
export const ACTIVE_LEAGUE_KEY = 'shiva-active-league'
export const ACTIVE_TEAM_KEY = 'shiva-active-team-id'
export const ACTIVE_SAVED_LEAGUE_KEY = 'shiva-active-saved-league-id'

export type LeagueImportRequest = { provider:LeagueProvider; leagueId:string; season:number; nickname?:string; swid?:string; espnS2?:string }

export async function importLeague(input: LeagueImportRequest): Promise<LeagueState> {
  const response = await fetch('/api/league-import', { method:'POST', headers:{ 'Content-Type':'application/json' }, body:JSON.stringify(input) })
  const data = await response.json()
  if (!response.ok) throw new Error(data.error || 'League import failed.')
  return data
}

export async function saveLeague(input: LeagueImportRequest, leagueData: LeagueState, teamId?: string | number | null): Promise<SavedLeague> {
  const team = leagueData.teams.find((item) => String(item.id) === String(teamId)) || leagueData.teams[0] || null
  const response = await fetch('/api/leagues', { method:'POST', headers:{ 'Content-Type':'application/json' }, body:JSON.stringify({
    provider:input.provider, leagueId:input.leagueId, season:leagueData.league.season || input.season, nickname:input.nickname,
    teamId:team?.id ?? null, leagueName:leagueData.league.name, teamName:team?.name || null, leagueData,
  }) })
  const data = await response.json()
  if (!response.ok) throw new Error(data.error || 'Unable to save league.')
  return data.league
}

export function activateLeague(leagueData: LeagueState, teamId?: string | number | null, savedId?: string | null) {
  const selected = leagueData.teams.find(team => String(team.id) === String(teamId))?.id ?? leagueData.teams[0]?.id ?? null
  const serialized = JSON.stringify(leagueData)
  sessionStorage.setItem('shiva-league', serialized)
  localStorage.setItem(ACTIVE_LEAGUE_KEY, serialized)
  if (selected !== null) {
    sessionStorage.setItem('shiva-team-id', String(selected))
    localStorage.setItem(ACTIVE_TEAM_KEY, String(selected))
  }
  if (savedId) localStorage.setItem(ACTIVE_SAVED_LEAGUE_KEY, savedId)
  window.dispatchEvent(new CustomEvent('shiva:league-changed', { detail:{ league:leagueData, teamId:selected, savedId:savedId || '' } }))
}

export async function importSaveActivate(input: LeagueImportRequest) {
  const leagueData = await importLeague(input)
  const teamId = leagueData.teams[0]?.id ?? null
  const saved = await saveLeague(input, leagueData, teamId)
  activateLeague(leagueData, saved?.team_id ?? teamId, saved?.id)
  localStorage.removeItem(PENDING_LEAGUE_KEY)
  return { leagueData, saved }
}
