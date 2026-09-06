import { expect, test } from '@playwright/test'

test('defense vs position model can flip a close RB start sit decision',async({page})=>{
  const leagueData={league:{id:'dvp',provider:'espn',season:2026,name:'Defense Test',scoringPeriod:1,matchupPeriod:1,rosterSlots:['RB','RB','WR','TE','QB'],scoringSettings:{}},teams:[{id:'1',name:'Matchup Team',owners:[],wins:0,losses:0},{id:'2',name:'Opponent',owners:[],wins:0,losses:0}],roster:[
    {teamId:'1',team:'Matchup Team',playerId:'s',player:'Slightly Higher Projection',slotId:'2',slot:'RB',proTeamId:1,proTeam:'ATL',position:'RB',eligibleSlots:['RB','FLEX'],injuryStatus:'',percentOwned:90,percentStarted:70,projectedPoints:12},
    {teamId:'1',team:'Matchup Team',playerId:'b',player:'Better Matchup Back',slotId:'20',slot:'BE',proTeamId:2,proTeam:'BUF',position:'RB',eligibleSlots:['RB','FLEX'],injuryStatus:'',percentOwned:88,percentStarted:68,projectedPoints:11.8},
    {teamId:'1',team:'Matchup Team',playerId:'w',player:'Receiver',slotId:'4',slot:'WR',proTeamId:12,proTeam:'KC',position:'WR',eligibleSlots:['WR','FLEX'],injuryStatus:'',percentOwned:95,percentStarted:90,projectedPoints:18},
    {teamId:'1',team:'Matchup Team',playerId:'t',player:'Tight End',slotId:'6',slot:'TE',proTeamId:8,proTeam:'DET',position:'TE',eligibleSlots:['TE','FLEX'],injuryStatus:'',percentOwned:85,percentStarted:72,projectedPoints:13},
    {teamId:'1',team:'Matchup Team',playerId:'q',player:'Quarterback',slotId:'0',slot:'QB',proTeamId:13,proTeam:'LV',position:'QB',eligibleSlots:['QB'],injuryStatus:'',percentOwned:99,percentStarted:95,projectedPoints:21}
  ],freeAgents:[],matchups:[{period:1,homeTeamId:'1',awayTeamId:'2',homeScore:null,awayScore:null,homeProjected:75,awayProjected:73}]}
  await page.addInitScript(({league})=>{sessionStorage.setItem('shiva-league',JSON.stringify(league));sessionStorage.setItem('shiva-team-id','1')},{league:leagueData})
  await page.route('**/api/auth/session',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({user:{id:'u1'}})}))
  await page.route('**/api/leagues',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({leagues:[{id:'saved',provider:'espn',league_id:'dvp',season:2026,team_id:'1',league_data:leagueData}]})}))
  await page.route('**/api/scoreboard*',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({games:[
    {id:'1',name:'ATL at BAL',date:'',status:'',teams:[{abbreviation:'ATL',homeAway:'away'},{abbreviation:'BAL',homeAway:'home'}]},
    {id:'2',name:'BUF vs CAR',date:'',status:'',teams:[{abbreviation:'BUF',homeAway:'home'},{abbreviation:'CAR',homeAway:'away'}]}
  ]})}))
  await page.route('**/api/rankings*',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({players:[
    {id:'s',espnId:'s',name:'Slightly Higher Projection',team:'ATL',pos:'RB',rank:30,percentStarted:70,projectedPoints:12},
    {id:'b',espnId:'b',name:'Better Matchup Back',team:'BUF',pos:'RB',rank:35,percentStarted:68,projectedPoints:11.8},
    {id:'w',espnId:'w',name:'Receiver',team:'KC',pos:'WR',rank:10,percentStarted:90,projectedPoints:18},
    {id:'t',espnId:'t',name:'Tight End',team:'DET',pos:'TE',rank:20,percentStarted:72,projectedPoints:13},
    {id:'q',espnId:'q',name:'Quarterback',team:'LV',pos:'QB',rank:5,percentStarted:95,projectedPoints:21}
  ]})}))
  await page.route('**/api/defense-matchups',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({baselineSeason:2025,methodology:'test',source:'nflverse',defenses:{BAL:{RB:{rank:1,pointsAllowed:15,leagueAverage:24,factor:.88}},CAR:{RB:{rank:32,pointsAllowed:32,leagueAverage:24,factor:1.12}}}})}))
  await page.goto('/',{waitUntil:'networkidle'})
  const keyPlayers=page.locator('.og-key-players')
  const starter=keyPlayers.locator('.og-key-list>div').filter({hasText:'Slightly Higher Projection'})
  const bench=keyPlayers.locator('.og-key-list>div').filter({hasText:'Better Matchup Back'})
  await expect(starter).toContainText('Tough D #1')
  await expect(bench).toContainText('Favorable D #32')
  await expect(starter).toHaveAttribute('data-recommendation','sit')
  await expect(starter.getByText('SIT',{exact:true})).toBeVisible()
  await expect(bench).toHaveAttribute('data-recommendation','start')
  await expect(bench.getByText('START',{exact:true})).toBeVisible()
})
