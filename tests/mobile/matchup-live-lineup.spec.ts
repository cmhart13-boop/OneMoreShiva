import { expect, test } from '@playwright/test'

function league(qbStarter:'Old Quarterback'|'New Quarterback'){
  const oldSlot=qbStarter==='Old Quarterback'?'QB':'BE'
  const newSlot=qbStarter==='New Quarterback'?'QB':'BE'
  return {
    league:{id:'12345',provider:'espn',season:2026,name:'Shiva One',scoringPeriod:1,matchupPeriod:1,rosterSlots:['QB','RB','WR','TE'],scoringSettings:{}},
    teams:[{id:'1',name:'My Selected Team',owners:[],wins:0,losses:0},{id:'2',name:'Opponent Team',owners:[],wins:0,losses:0}],
    roster:[
      {teamId:'1',team:'My Selected Team',playerId:'old',player:'Old Quarterback',slotId:oldSlot==='QB'?'0':'20',slot:oldSlot,proTeamId:1,position:'QB',eligibleSlots:['QB'],injuryStatus:'',percentOwned:90,percentStarted:55,projectedPoints:17},
      {teamId:'1',team:'My Selected Team',playerId:'new',player:'New Quarterback',slotId:newSlot==='QB'?'0':'20',slot:newSlot,proTeamId:2,position:'QB',eligibleSlots:['QB'],injuryStatus:'',percentOwned:91,percentStarted:56,projectedPoints:18},
      {teamId:'1',team:'My Selected Team',playerId:'rb',player:'Starting Runner',slotId:'2',slot:'RB',proTeamId:3,position:'RB',eligibleSlots:['RB','FLEX'],injuryStatus:'',percentOwned:92,percentStarted:80,projectedPoints:15},
      {teamId:'1',team:'My Selected Team',playerId:'wr',player:'Starting Receiver',slotId:'4',slot:'WR',proTeamId:4,position:'WR',eligibleSlots:['WR','FLEX'],injuryStatus:'',percentOwned:93,percentStarted:82,projectedPoints:16},
      {teamId:'1',team:'My Selected Team',playerId:'te',player:'Starting Tight End',slotId:'6',slot:'TE',proTeamId:5,position:'TE',eligibleSlots:['TE','FLEX'],injuryStatus:'',percentOwned:85,percentStarted:70,projectedPoints:11},
      {teamId:'2',team:'Opponent Team',playerId:'opp',player:'Opponent Quarterback',slotId:'0',slot:'QB',proTeamId:6,position:'QB',eligibleSlots:['QB'],injuryStatus:'',percentOwned:99,percentStarted:95,projectedPoints:20}
    ],
    freeAgents:[],
    matchups:[{period:1,homeTeamId:'1',awayTeamId:'2',homeScore:null,awayScore:null,homeProjected:59,awayProjected:70}]
  }
}

test('My Matchup keeps helmets separated and refreshes ESPN starting lineup on focus',async({page})=>{
  const stale=league('Old Quarterback')
  const fresh=league('New Quarterback')
  let returnFresh=false
  const importBodies:any[]=[]

  await page.addInitScript(({league})=>{sessionStorage.setItem('shiva-league',JSON.stringify(league));sessionStorage.setItem('shiva-team-id','1')},{league:stale})
  await page.route('**/api/auth/session',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({user:{id:'u1',email:'owner@example.com'}})}))
  await page.route('**/api/leagues',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({leagues:[{id:'saved',provider:'espn',league_id:'12345',season:2026,team_id:'1',league_name:'Shiva One',team_name:'My Selected Team',league_data:stale}]})}))
  await page.route('**/api/league-import',async route=>{importBodies.push(route.request().postDataJSON());await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(returnFresh?fresh:stale)})})
  await page.route('**/api/scoreboard*',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({games:[]})}))
  await page.route('**/api/defense-matchups*',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({baselineSeason:2025,methodology:'test',source:'test',defenses:{}})}))
  await page.route('**/api/rankings*',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({players:[
    {id:'old',espnId:'old',name:'Old Quarterback',team:'ATL',pos:'QB',rank:20,percentStarted:55,projectedPoints:17},
    {id:'new',espnId:'new',name:'New Quarterback',team:'BUF',pos:'QB',rank:18,percentStarted:56,projectedPoints:18},
    {id:'rb',espnId:'rb',name:'Starting Runner',team:'KC',pos:'RB',rank:10,percentStarted:80,projectedPoints:15},
    {id:'wr',espnId:'wr',name:'Starting Receiver',team:'DET',pos:'WR',rank:9,percentStarted:82,projectedPoints:16},
    {id:'te',espnId:'te',name:'Starting Tight End',team:'LV',pos:'TE',rank:15,percentStarted:70,projectedPoints:11}
  ]})}))
  await page.route('https://a.espncdn.com/**',route=>route.fulfill({status:200,contentType:'image/png',body:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADElEQVR42mNk+M/wHwAF/gL+NqFrWQAAAABJRU5ErkJggg==','base64')}))

  await page.goto('/',{waitUntil:'networkidle'})
  const matchup=page.locator('.og-my-matchup').first()
  const lineup=matchup.locator('.og-starting-lineup')
  await expect(lineup).toBeVisible()
  await expect(lineup.getByText('Old Quarterback',{exact:true})).toBeVisible()
  await expect(lineup.getByText('New Quarterback',{exact:true})).toHaveCount(0)
  await expect(lineup.getByText('Starting Runner',{exact:true})).toBeVisible()
  await expect(matchup.getByText('ESPN synced live',{exact:true})).toBeVisible()

  const left=await matchup.locator('.live-helmet.left').boundingBox()
  const versus=await matchup.locator('.og-helmet-clash>i').boundingBox()
  const right=await matchup.locator('.live-helmet.right').boundingBox()
  expect(left).not.toBeNull();expect(versus).not.toBeNull();expect(right).not.toBeNull()
  expect(left!.x+left!.width).toBeLessThan(versus!.x)
  expect(versus!.x+versus!.width).toBeLessThan(right!.x)
  expect(left!.width).toBeLessThanOrEqual(63.5)
  expect(right!.width).toBeLessThanOrEqual(63.5)

  returnFresh=true
  await page.evaluate(()=>window.dispatchEvent(new Event('focus')))
  await expect(lineup.getByText('New Quarterback',{exact:true})).toBeVisible()
  await expect(lineup.getByText('Old Quarterback',{exact:true})).toHaveCount(0)
  expect(importBodies.some(body=>body?.provider==='espn'&&body?.leagueId==='12345'&&body?.season===2026)).toBeTruthy()
})
