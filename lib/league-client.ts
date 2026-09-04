'use client'

import type { LeagueProvider, LeagueState, SavedLeague } from './types'

export const PENDING_LEAGUE_KEY = 'shiva-pending-league-import'

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

export function activateLeague(leagueData: LeagueState, teamId?: string | number | null) {
  const selected = teamId ?? leagueData.teams[0]?.id ?? null
  sessionStorage.setItem('shiva-league', JSON.stringify(leagueData))
  if (selected !== null) sessionStorage.setItem('shiva-team-id', String(selected))
  window.dispatchEvent(new CustomEvent('shiva:league-changed', { detail:{ league:leagueData, teamId:selected } }))
}

export async function importSaveActivate(input: LeagueImportRequest) {
  const leagueData = await importLeague(input)
  const teamId = leagueData.teams[0]?.id ?? null
  const saved = await saveLeague(input, leagueData, teamId)
  activateLeague(leagueData, saved?.team_id ?? teamId)
  localStorage.removeItem(PENDING_LEAGUE_KEY)
  return { leagueData, saved }
}
