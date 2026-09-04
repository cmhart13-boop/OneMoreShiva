import type { LeagueState } from '../types'

const SLOT: Record<number, string> = { 0:'QB', 2:'RB', 4:'WR', 6:'TE', 16:'DST', 17:'K', 20:'BE', 21:'IR', 23:'FLEX' }

export function normalizeEspnLeague(raw: any, requestedId: string, requestedSeason: number, freeAgents: LeagueState['freeAgents'] = []): LeagueState {
  const members = new Map((raw.members || []).map((member: any) => [String(member.id), member]))
  const teams: LeagueState['teams'] = []
  const roster: LeagueState['roster'] = []
  for (const team of raw.teams || []) {
    const id = Number(team.id || 0)
    const owners = (team.owners || []).map((ownerId: unknown) => {
      const member: any = members.get(String(ownerId)) || {}
      return `${member.firstName || ''} ${member.lastName || ''}`.trim()
    }).filter(Boolean)
    const name = `${team.location || ''} ${team.nickname || ''}`.trim() || team.name || `Team ${id}`
    teams.push({ id, name, owners, wins:team.record?.overall?.wins ?? null, losses:team.record?.overall?.losses ?? null })
    for (const entry of team.roster?.entries || []) {
      const pool = entry.playerPoolEntry || {}
      const player = pool.player || {}
      const slotId = Number(entry.lineupSlotId ?? 20)
      const position = String(player.defaultPositionId ? SLOT[Number(player.defaultPositionId)] || '' : '')
      roster.push({
        teamId:id, team:name, playerId:String(player.id || ''), player:String(player.fullName || ''),
        slotId, slot:SLOT[slotId] || String(slotId), proTeamId:player.proTeamId ?? null, position,
        eligibleSlots:Array.from(new Set((player.eligibleSlots || []).map((value: unknown) => SLOT[Number(value)]).filter(Boolean))),
        injuryStatus:player.injuryStatus || '', percentOwned:pool.percentOwned ?? null, percentStarted:pool.percentStarted ?? null,
      })
    }
  }
  const lineupSlotCounts = raw.settings?.rosterSettings?.lineupSlotCounts || {}
  const rosterSlots = Object.entries(lineupSlotCounts).flatMap(([id, count]) => Array(Number(count) || 0).fill(SLOT[Number(id)] || id))
  return {
    league:{
      id:String(raw.id || requestedId), provider:'espn', season:Number(raw.seasonId || requestedSeason),
      name:String(raw.settings?.name || 'ESPN League'), scoringPeriod:raw.status?.currentScoringPeriod ?? null,
      matchupPeriod:raw.status?.currentMatchupPeriod ?? null, rosterSlots,
      scoringSettings:raw.settings?.scoringSettings?.scoringItems?.reduce((acc: Record<string, number>, item: any) => {
        if (item?.statId !== undefined && Number.isFinite(Number(item.points))) acc[String(item.statId)] = Number(item.points)
        return acc
      }, {}) || {},
    },
    teams, roster, freeAgents,
  }
}
