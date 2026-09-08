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

async function openHomeAddLeague(page:any){await page.locator('.og-bottom').getByRole('button',{name:'Leagues',exact:true}).click();await expect(page.getByLabel('League provider')).toBeVisible()}
async function openTeam(page:any){await page.locator('.og-bottom').getByRole('button',{name:'My Team',exact:true}).click();await expect(page.getByText(/My Team|Lineup/i).first()).toBeVisible()}

test('provider adapters normalize ESPN and Sleeper into the same league model',()=>{
  expect(sleeper.league.provider).toBe('sleeper');expect(sleeper.league.scoringSettings.rec).toBe(1);expect(sleeper.teams[0].name).toBe('Shiva Dogs');expect(sleeper.roster.find(row=>row.player==='Test Runner')?.eligibleSlots).toContain('FLEX')
  const espn=normalizeEspnLeague({id:'e1',seasonId:2026,settings:{name:'ESPN Test',rosterSettings:{lineupSlotCounts:{0:1,2:2,20:5}}},status:{currentScoringPeriod:1},teams:[{id:1,location:'Shiva',nickname:'Team',roster:{entries:[]}}],schedule:[{matchupPeriodId:1,home:{teamId:1,totalPoints:101.2,totalProjectedPointsLive:119.4},away:{teamId:2,totalPoints:98.7,totalProjectedPointsLive:114.1}}]},'e1',2026)
  expect(espn.league.provider).toBe('espn');expect(espn.league.rosterSlots).toEqual(['QB','RB','RB','BE','BE','BE','BE','BE']);expect(espn.matchups?.[0]).toMatchObject({period:1,homeTeamId:1,awayTeamId:2,homeScore:101.2,awayScore:98.7})
})

test('signed-out Go preserves provider and league id while opening account gate',async({page})=>{
  await page.route('**/api/auth/session',route=>route.fulfill({status:401,contentType:'application/json',body:JSON.stringify({error:'Sign in required.'})}));await page.goto('/');await openHomeAddLeague(page);await page.getByLabel('League provider').selectOption('sleeper');await page.getByLabel('League ID',{exact:true}).fill('123456789');await page.getByRole('button',{name:'Go',exact:true}).click();await expect(page.getByRole('dialog',{name:'Shiva account'})).toBeVisible();await expect(page.getByText('It will continue automatically.')).toBeVisible();await expect(page.getByLabel('League provider')).toHaveValue('sleeper');await expect(page.getByLabel('League ID',{exact:true})).toHaveValue('123456789')
})

test('authentication resumes the pending import and persists it',async({page})=>{
  await page.route('**/api/auth/session',route=>route.fulfill({status:401,contentType:'application/json',body:'{}'}));await page.route('**/api/auth/signin',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({user:{id:'u',email:'u@test.dev'}})}));await page.route('**/api/league-import',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(sleeper)}));let saved=false;await page.route('**/api/leagues',async route=>{if(route.request().method()==='POST'){saved=true;return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({league:{id:'saved',team_id:'1'}})})}return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({leagues:[]})})});await page.goto('/');await openHomeAddLeague(page);await page.getByLabel('League provider').selectOption('sleeper');await page.getByLabel('League ID',{exact:true}).fill('sl-1');await page.getByRole('button',{name:'Go',exact:true}).click();await page.getByRole('button',{name:'Sign In',exact:true}).click();await page.getByLabel('Email').fill('u@test.dev');await page.getByLabel('Password').fill('password123');await page.getByRole('button',{name:'Sign In',exact:true}).last().click();await expect.poll(()=>saved).toBeTruthy()
})

test('signed-in import saves, activates real roster and switches to team view',async({page},testInfo)=>{
  await page.route('**/api/auth/session',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({user:{id:'u',email:'u@test.dev'}})}));await page.route('**/api/leagues',async route=>{if(route.request().method()==='GET')return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({leagues:[{id:'saved',provider:'sleeper',league_id:'sl-1',season:2026,team_id:'1',league_name:'Sleeper Test',league_data:sleeper},{id:'saved-2',provider:'sleeper',league_id:'sl-2',season:2026,team_id:'2',league_name:'Second League',league_data:sleeperTwo}]})});if(route.request().method()==='PATCH')return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({league:{}})});return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({league:{id:'saved',provider:'sleeper',league_id:'sl-1',season:2026,team_id:'1',league_data:sleeper}})})});await page.route('**/api/league-import',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(sleeper)}));await page.route('**/api/rankings',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({players:[{id:'p2',name:'Test Runner',team:'DET',bye:null,pos:'RB',posRank:10,adp:20,consensusAdp:20,rank:20,projectedPoints:15,percentStarted:75},{id:'p3',name:'Test Receiver',team:'MIN',bye:null,pos:'WR',posRank:11,adp:22,consensusAdp:22,rank:22,projectedPoints:14,percentStarted:68}]})}));await page.goto('/');await expect(page.locator('.og-snapshot-page')).toHaveCount(2);const snapshotTrack=page.locator('.og-snapshot-track');await snapshotTrack.evaluate((element:HTMLElement)=>element.scrollTo({left:element.clientWidth+8,behavior:'instant'}));await expect(page.locator('.og-snapshot-dots button').nth(1)).toHaveClass(/active/);await openHomeAddLeague(page);await page.getByLabel('League provider').selectOption('sleeper');await page.getByLabel('League ID',{exact:true}).fill('sl-1');await page.getByRole('button',{name:'Go',exact:true}).click();await expect(page.getByLabel('Active team',{exact:true})).toHaveValue('1');await expect(page.getByRole('heading',{name:'Sleeper Test is connected.',exact:true})).toBeVisible();await openTeam(page);await expect(page.getByText('Test Quarterback',{exact:true})).toBeVisible();await expect(page.getByText('Test Runner',{exact:true})).toBeVisible();await page.screenshot({path:testInfo.outputPath('league-lineup.png'),fullPage:true})
})

test('My Leagues keeps team context, grades the live roster, and player pages remain navigable',async({page})=>{
  const league={league:{id:'grade-1',provider:'espn',season:2026,name:'Shiva Grade League',scoringPeriod:1,matchupPeriod:1,rosterSlots:['QB','RB','WR','TE','FLEX','BE'],scoringSettings:{rec:1}},teams:[{id:'1',name:'Championship Build',owners:[],wins:0,losses:0},{id:'2',name:'Upside Team',owners:[],wins:0,losses:0}],roster:[
    {teamId:'1',team:'Championship Build',playerId:'p1',player:'Alpha Runner',slotId:'2',slot:'RB',proTeamId:1,proTeam:'ATL',position:'RB',eligibleSlots:['RB','FLEX'],injuryStatus:'',percentOwned:95,percentStarted:85,projectedPoints:18},
    {teamId:'1',team:'Championship Build',playerId:'p2',player:'Bravo Receiver',slotId:'4',slot:'WR',proTeamId:2,proTeam:'BUF',position:'WR',eligibleSlots:['WR','FLEX'],injuryStatus:'',percentOwned:92,percentStarted:80,projectedPoints:17},
    {teamId:'1',team:'Championship Build',playerId:'p3',player:'Charlie Tight End',slotId:'6',slot:'TE',proTeamId:12,proTeam:'KC',position:'TE',eligibleSlots:['TE','FLEX'],injuryStatus:'',percentOwned:88,percentStarted:75,projectedPoints:14},
    {teamId:'2',team:'Upside Team',playerId:'p4',player:'Delta Back',slotId:'2',slot:'RB',proTeamId:8,proTeam:'DET',position:'RB',eligibleSlots:['RB','FLEX'],injuryStatus:'',percentOwned:75,percentStarted:55,projectedPoints:12},
    {teamId:'2',team:'Upside Team',playerId:'p5',player:'Echo Back',slotId:'20',slot:'BE',proTeamId:13,proTeam:'LV',position:'RB',eligibleSlots:['RB','FLEX'],injuryStatus:'',percentOwned:65,percentStarted:42,projectedPoints:10},
  ],freeAgents:[],matchups:[]}
  const saved={id:'saved-grade',provider:'espn',league_id:'grade-1',season:2026,team_id:'1',league_name:'Shiva Grade League',team_name:'Championship Build',league_data:league}
  await page.addInitScript(({league})=>{localStorage.setItem('shiva-active-league',JSON.stringify(league));localStorage.setItem('shiva-active-team-id','1');localStorage.setItem('shiva-active-saved-league-id','saved-grade')},{league})
  await page.route('**/api/auth/session',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({user:{id:'u',email:'u@test.dev'}})}))
  await page.route('**/api/defense-matchups*',route=>route.fulfill({status:200,contentType:'application/json',body:'{"teams":[]}'}))
  await page.route('**/api/league-import*',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(league)}))
  await page.route('**/api/leagues*',async route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(route.request().method()==='GET'?{leagues:[saved]}:{league:saved})}))
  await page.route('**/api/rankings*',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({players:[
    {id:'p1',espnId:'p1',name:'Alpha Runner',team:'ATL',pos:'RB',rank:5,posRank:2,adp:6,projectedPoints:18,percentStarted:85},
    {id:'p2',espnId:'p2',name:'Bravo Receiver',team:'BUF',pos:'WR',rank:8,posRank:3,adp:9,projectedPoints:17,percentStarted:80},
    {id:'p3',espnId:'p3',name:'Charlie Tight End',team:'KC',pos:'TE',rank:20,posRank:2,adp:21,projectedPoints:14,percentStarted:75},
    {id:'p4',espnId:'p4',name:'Delta Back',team:'DET',pos:'RB',rank:60,posRank:25,adp:65,projectedPoints:12,percentStarted:55},
    {id:'p5',espnId:'p5',name:'Echo Back',team:'LV',pos:'RB',rank:75,posRank:31,adp:80,projectedPoints:10,percentStarted:42},
  ]})}))
  await page.route('**/api/scoreboard*',route=>route.fulfill({status:200,contentType:'application/json',body:'{"games":[]}'}))
  await page.route('**/api/evidence*',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({evidence:{name:'Alpha Runner',pos:'RB',team:'ATL',games:2,season:2025,ppg:16,floor:11,ceiling:24,rate15:50,boom25:0,bust10:0,recent:16,gameLog:[{season:2025,week:2,opponent:'CAR',points:18,statLine:'92 rush yds · 4 rec'}]}})}))
  await page.route('**/api/news*',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({articles:[{headline:'Alpha Runner earns larger role',description:'Current team update.',published:'2026-09-08',url:'https://example.com/story',image:''}]})}))
  await page.route(/^https?:\/\/(?!127\.0\.0\.1)/,route=>route.abort())
  await page.goto('/',{waitUntil:'networkidle'})
  await page.locator('.og-shortcuts').getByRole('button',{name:/^Draft Grade/}).click()
  await expect(page.getByRole('heading',{name:'My Leagues',exact:true})).toBeVisible()
  await expect(page.getByRole('heading',{name:'Draft Analyzer',exact:true})).toBeVisible()
  await expect(page.locator('.draft-grade-card')).toContainText(/A|B|C|D|F/)
  await page.getByLabel('Active team',{exact:true}).selectOption('2')
  await page.locator('.og-bottom').getByRole('button',{name:'Home',exact:true}).click()
  await page.locator('.og-shortcuts').getByRole('button',{name:/^Start \/ Sit/}).click()
  await expect(page.getByLabel('Active team',{exact:true})).toHaveValue('2')
  await page.locator('.og-bottom').getByRole('button',{name:'Home',exact:true}).click()
  await page.locator('.og-shortcuts').getByRole('button',{name:/^Trade Analyzer/}).click()
  await page.locator('.players-live-list').getByText('Alpha Runner',{exact:true}).click()
  const dialog=page.getByRole('dialog',{name:'Alpha Runner player page'})
  await expect(dialog).toBeVisible()
  await expect(dialog.getByRole('heading',{name:'PLAYER OVERVIEW',exact:true})).toBeVisible()
  await dialog.getByRole('tab',{name:'Stats',exact:true}).click();await expect(dialog.getByText('PPR / Game',{exact:true})).toBeVisible()
  await dialog.getByRole('tab',{name:'Game Log',exact:true}).click();await expect(dialog.getByText('92 rush yds · 4 rec',{exact:true})).toBeVisible()
  await dialog.getByRole('tab',{name:'Projections',exact:true}).click();await expect(dialog.getByText('Current weekly projection',{exact:true})).toBeVisible()
  await dialog.getByRole('tab',{name:'News',exact:true}).click();await expect(dialog.getByText('Alpha Runner earns larger role',{exact:true})).toBeVisible()
  await dialog.getByRole('button',{name:'Close player page',exact:true}).click();await expect(dialog).toHaveCount(0)
})

test('recommendation is scoring-aware and renders confidence vocabulary',()=>{
  const [rb,wr]=[sleeper.roster[1],sleeper.roster[2]];const evidence={name:'',pos:'',team:'',games:10,season:2025,ppg:14,floor:8,ceiling:25,rate15:45,boom25:10,bust10:15,recent:16};const recommendation=recommendStart(rb,wr,[{id:'p2',name:rb.player,team:'DET',bye:null,pos:'RB',posRank:10,adp:20,consensusAdp:20,rank:20,projectedPoints:14,percentStarted:70},{id:'p3',name:wr.player,team:'MIN',bye:null,pos:'WR',posRank:11,adp:22,consensusAdp:22,rank:22,projectedPoints:14,percentStarted:70}],evidence,evidence,{rec:1});expect(['Strong Start','Lean','Close Call']).toContain(recommendation.confidence);expect(recommendation.explanation).toContain('league reception scoring')
})
