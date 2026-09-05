import { expect, test } from '@playwright/test'
import { normalizeSleeperLeague } from '../../lib/league-adapters/sleeper'
import { normalizeEspnLeague } from '../../lib/league-adapters/espn'
import { recommendStart } from '../../lib/recommendation'

const sleeper = normalizeSleeperLeague({
  league:{ league_id:'sl-1', name:'Sleeper Test', season:'2026', roster_positions:['QB','RB','FLEX','BN'], scoring_settings:{ rec:1 }, settings:{ leg:3 } },
  users:[{ user_id:'u1', display_name:'Chris', metadata:{ team_name:'Shiva Dogs' } }],
  rosters:[{ roster_id:1, owner_id:'u1', players:['p1','p2','p3'], starters:['p1','p2','0','0'], settings:{ wins:2, losses:1 } }],
  players:{ p1:{ full_name:'Test Quarterback', position:'QB', fantasy_positions:['QB'], team:'BUF' }, p2:{ full_name:'Test Runner', position:'RB', fantasy_positions:['RB'], team:'DET' }, p3:{ full_name:'Test Receiver', position:'WR', fantasy_positions:['WR'], team:'MIN', injury_status:'Questionable' } },
})
const sleeperTwo = { ...sleeper, league:{ ...sleeper.league, id:'sl-2', name:'Second League' }, teams:[{ ...sleeper.teams[0], id:'2', name:'Second Team' }], roster:sleeper.roster.map((row) => ({ ...row, teamId:'2', team:'Second Team' })) }

async function openHomeAddLeague(page: any) {
  const toggle = page.getByRole('button', { name:/Add League/i }).first()
  await expect(toggle).toBeVisible()
  await toggle.click()
  await expect(page.getByLabel('League provider')).toBeVisible()
}

async function openTeam(page: any) {
  await page.locator('.approved-bottom').getByRole('button', { name:'My Team', exact:true }).click()
  await expect(page.getByText(/My Team|Lineup/i).first()).toBeVisible()
}

test('provider adapters normalize ESPN and Sleeper into the same league model', () => {
  expect(sleeper.league.provider).toBe('sleeper')
  expect(sleeper.league.scoringSettings.rec).toBe(1)
  expect(sleeper.teams[0].name).toBe('Shiva Dogs')
  expect(sleeper.roster.find((row) => row.player === 'Test Runner')?.eligibleSlots).toContain('FLEX')
  const espn = normalizeEspnLeague({ id:'e1', seasonId:2026, settings:{ name:'ESPN Test', rosterSettings:{ lineupSlotCounts:{ 0:1, 2:2, 20:5 } } }, status:{ currentScoringPeriod:1 }, teams:[{ id:1, location:'Shiva', nickname:'Team', roster:{ entries:[] } }] }, 'e1', 2026)
  expect(espn.league.provider).toBe('espn')
  expect(espn.league.rosterSlots).toEqual(['QB','RB','RB','BE','BE','BE','BE','BE'])
})

test('signed-out Go preserves provider and league id while opening account gate', async ({ page }) => {
  await page.route('**/api/auth/session', (route) => route.fulfill({ status:401, contentType:'application/json', body:JSON.stringify({ error:'Sign in required.' }) }))
  await page.goto('/')
  await openHomeAddLeague(page)
  await page.getByLabel('League provider').selectOption('sleeper')
  await page.getByLabel('League ID', { exact:true }).fill('123456789')
  await page.getByRole('button', { name:'Go', exact:true }).click()
  await expect(page.getByRole('dialog', { name:'Shiva account' })).toBeVisible()
  await expect(page.getByText('It will continue automatically.')).toBeVisible()
  await expect(page.getByLabel('League provider')).toHaveValue('sleeper')
  await expect(page.getByLabel('League ID', { exact:true })).toHaveValue('123456789')
})

test('authentication resumes the pending import and persists it', async ({ page }) => {
  await page.route('**/api/auth/session', (route) => route.fulfill({ status:401, contentType:'application/json', body:'{}' }))
  await page.route('**/api/auth/signin', (route) => route.fulfill({ status:200, contentType:'application/json', body:JSON.stringify({ user:{ id:'u', email:'u@test.dev' } }) }))
  await page.route('**/api/league-import', (route) => route.fulfill({ status:200, contentType:'application/json', body:JSON.stringify(sleeper) }))
  let saved = false
  await page.route('**/api/leagues', async (route) => {
    if (route.request().method() === 'POST') { saved = true; return route.fulfill({ status:200, contentType:'application/json', body:JSON.stringify({ league:{ id:'saved', team_id:'1' } }) }) }
    return route.fulfill({ status:200, contentType:'application/json', body:JSON.stringify({ leagues:[] }) })
  })
  await page.goto('/')
  await openHomeAddLeague(page)
  await page.getByLabel('League provider').selectOption('sleeper')
  await page.getByLabel('League ID', { exact:true }).fill('sl-1')
  await page.getByRole('button', { name:'Go', exact:true }).click()
  await page.getByRole('button', { name:'Sign In', exact:true }).click()
  await page.getByLabel('Email').fill('u@test.dev')
  await page.getByLabel('Password').fill('password123')
  await page.getByRole('button', { name:'Sign In', exact:true }).last().click()
  await expect.poll(() => saved).toBeTruthy()
})

test('signed-in import saves, activates real roster and switches to team view', async ({ page }, testInfo) => {
  await page.route('**/api/auth/session', (route) => route.fulfill({ status:200, contentType:'application/json', body:JSON.stringify({ user:{ id:'u', email:'u@test.dev' } }) }))
  await page.route('**/api/leagues', async (route) => {
    if (route.request().method() === 'GET') return route.fulfill({ status:200, contentType:'application/json', body:JSON.stringify({ leagues:[
      { id:'saved', provider:'sleeper', league_id:'sl-1', season:2026, team_id:'1', league_name:'Sleeper Test', league_data:sleeper },
      { id:'saved-2', provider:'sleeper', league_id:'sl-2', season:2026, team_id:'2', league_name:'Second League', league_data:sleeperTwo },
    ] }) })
    if (route.request().method() === 'PATCH') return route.fulfill({ status:200, contentType:'application/json', body:JSON.stringify({ league:{} }) })
    return route.fulfill({ status:200, contentType:'application/json', body:JSON.stringify({ league:{ id:'saved', provider:'sleeper', league_id:'sl-1', season:2026, team_id:'1', league_data:sleeper } }) })
  })
  await page.route('**/api/league-import', (route) => route.fulfill({ status:200, contentType:'application/json', body:JSON.stringify(sleeper) }))
  await page.route('**/api/rankings', (route) => route.fulfill({ status:200, contentType:'application/json', body:JSON.stringify({ players:[
    { id:'p2', name:'Test Runner', team:'DET', bye:null, pos:'RB', posRank:10, adp:20, consensusAdp:20, rank:20, projectedPoints:15, percentStarted:75 },
    { id:'p3', name:'Test Receiver', team:'MIN', bye:null, pos:'WR', posRank:11, adp:22, consensusAdp:22, rank:22, projectedPoints:14, percentStarted:68 },
  ] }) }))
  await page.goto('/')
  await openHomeAddLeague(page)
  await page.getByLabel('League provider').selectOption('sleeper')
  await page.getByLabel('League ID', { exact:true }).fill('sl-1')
  await page.getByRole('button', { name:'Go', exact:true }).click()
  await expect(page.getByText('Shiva Dogs', { exact:true }).first()).toBeVisible()
  await openTeam(page)
  await expect(page.getByText('Test Quarterback', { exact:true })).toBeVisible()
  await expect(page.getByText('Test Runner', { exact:true })).toBeVisible()
  await page.screenshot({ path:testInfo.outputPath('league-lineup.png'), fullPage:true })
})

test('recommendation is scoring-aware and renders confidence vocabulary', () => {
  const [rb, wr] = [sleeper.roster[1], sleeper.roster[2]]
  const evidence = { name:'', pos:'', team:'', games:10, season:2025, ppg:14, floor:8, ceiling:25, rate15:45, boom25:10, bust10:15, recent:16 }
  const recommendation = recommendStart(rb, wr, [
    { id:'p2', name:rb.player, team:'DET', bye:null, pos:'RB', posRank:10, adp:20, consensusAdp:20, rank:20, projectedPoints:14, percentStarted:70 },
    { id:'p3', name:wr.player, team:'MIN', bye:null, pos:'WR', posRank:11, adp:22, consensusAdp:22, rank:22, projectedPoints:14, percentStarted:70 },
  ], evidence, evidence, { rec:1 })
  expect(['Strong Start','Lean','Close Call']).toContain(recommendation.confidence)
  expect(recommendation.explanation).toContain('league reception scoring')
})
