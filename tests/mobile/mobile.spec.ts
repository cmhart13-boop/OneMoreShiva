import { expect, test } from '@playwright/test'

async function assertMobileShell(page:any){
  const body=page.locator('body');await expect(body).toBeVisible()
  const overflow=await page.evaluate(()=>({width:document.documentElement.scrollWidth,viewport:window.innerWidth}))
  expect(overflow.width).toBeLessThanOrEqual(overflow.viewport+2)
  const nav=page.locator('.og-bottom');await expect(nav).toBeVisible();await expect(nav.getByRole('button')).toHaveCount(5)
  const bg=await body.evaluate((el:HTMLElement)=>getComputedStyle(el).backgroundColor);expect(bg).not.toBe('rgb(255, 255, 255)')
}

async function assertApprovedHome(page:any){
  const sections=await page.locator('.og-home').evaluate((home:HTMLElement)=>Array.from(home.children).map(child=>child.className))
  expect(sections).toEqual(['live-hero','og-home-ask','og-shortcuts','og-snapshots'])
  const hero=page.locator('.live-hero');await expect(hero).toBeVisible();await expect(hero.locator('.live-hero-wordmark')).toContainText('Shiva');await expect(hero.locator('.live-hero-wordmark')).toContainText('FANTASY IQ');await expect(hero.locator('.live-hero-logo-mark img')).toBeVisible();await expect(hero.getByRole('button',{name:'Notifications',exact:true})).toHaveCount(0);await expect(hero.locator('.live-profile')).toBeVisible();await expect(hero.locator('.live-week')).toHaveCount(0);await expect(hero).not.toContainText('WEEK')
  const viewportWidth=await page.evaluate(()=>window.innerWidth);await expect(hero).toHaveCSS('height',viewportWidth>=700?'154px':'111px')
  const heroBox=await hero.boundingBox();const wordmarkBox=await hero.locator('.live-hero-wordmark').boundingBox();expect(heroBox).not.toBeNull();expect(wordmarkBox).not.toBeNull();expect(wordmarkBox!.x-heroBox!.x).toBeLessThanOrEqual(10)
  const stadium=await hero.locator('.live-hero-stadium').evaluate((el:HTMLElement)=>getComputedStyle(el).backgroundImage);expect(stadium).toContain('hero-approved-clean.webp')
  await expect(page.locator('.og-league-strip')).toHaveCount(0)
  const ask=page.locator('.og-home-ask');await expect(ask).toBeVisible();await expect(ask.getByRole('heading',{name:'Ask Shiva',exact:true})).toBeVisible();await expect(ask.locator('.og-home-ask-title img')).toBeVisible();await expect(ask.getByRole('button',{name:'This League',exact:true})).toBeVisible();await expect(ask.getByRole('button',{name:'All My Leagues',exact:true})).toBeVisible();await expect(ask.getByLabel('Ask Shiva home question')).toBeVisible();await expect(ask.getByLabel('Ask Shiva home question')).toHaveValue('');await expect(ask.getByLabel('Ask Shiva home question')).toHaveAttribute('placeholder','Ask Shiva a question…');await expect(ask.getByText('SHIVA SAYS',{exact:true})).toHaveCount(0);await expect(ask.getByRole('button',{name:'Clear home question',exact:true})).toHaveCount(0)
  await expect(page.locator('.og-shortcuts button')).toHaveCount(6)
  for(const label of ['Start / Sit','Waivers','Trade Analyzer','Draft Guide','Power Rankings','Schedule'])await expect(page.locator('.og-shortcuts').getByRole('button',{name:new RegExp(`^${label}`)})).toBeVisible()
  const tileOverflow=await page.locator('.og-shortcuts button').evaluateAll((buttons:HTMLElement[])=>buttons.map(button=>button.scrollWidth>button.clientWidth+1));expect(tileOverflow).not.toContain(true)
  const dashboard=page.locator('.og-snapshot-page').first();await expect(dashboard.locator('.og-snapshot-card')).toHaveCount(2);await expect(dashboard.locator('.live-helmet')).toHaveCount(2)
  await expect(dashboard.getByRole('button',{name:'Connect League',exact:true})).toBeVisible();await expect(page.getByRole('button',{name:/Connect (your )?league/i})).toHaveCount(1)
  await page.evaluate(()=>window.scrollTo(0,document.documentElement.scrollHeight));await page.waitForTimeout(50);const cardBox=await dashboard.locator('.og-snapshot-card').first().boundingBox();const navBox=await page.locator('.og-bottom').boundingBox();expect(cardBox).not.toBeNull();expect(navBox).not.toBeNull();expect(cardBox!.height).toBeGreaterThanOrEqual(260);expect(navBox!.y-(cardBox!.y+cardBox!.height)).toBeGreaterThanOrEqual(0);expect(navBox!.y-(cardBox!.y+cardBox!.height)).toBeLessThanOrEqual(12)
  await expect(dashboard.locator('.live-helmet.left img')).toHaveAttribute('src',/helmet-gold-3d/);await expect(dashboard.locator('.live-helmet.right img')).toHaveAttribute('src',/helmet-red-3d/)
  const labels=await dashboard.locator('.og-snapshot-card > header > b').allTextContents();expect(labels).toEqual(['My Matchup','Key Players']);await expect(dashboard.getByText('My League',{exact:true})).toHaveCount(0);const keyRows=dashboard.locator('.og-key-list>div');await expect(keyRows).toHaveCount(5);await expect(dashboard.getByText('CONSIDER',{exact:true})).toHaveCount(0);for(let i=0;i<5;i++){const row=keyRows.nth(i);await expect(row.locator('em')).toHaveText(/^(START|SIT)$/);const state=await row.getAttribute('data-recommendation');expect(['start','sit']).toContain(state);await expect(row).toHaveClass(new RegExp(`\\b${state}\\b`))}
  await expect(ask.getByRole('heading',{name:'Ask Shiva',exact:true})).toHaveCSS('font-size','26px');await expect(page.locator('.og-shortcut-copy b').first()).toHaveCSS('font-size','10.4px');await expect(page.locator('.og-shortcuts button').first()).toHaveCSS('height','54px');await expect(dashboard.locator('.og-snapshot-card > header > b').first()).toHaveCSS('font-size','14px');await expect(page.locator('.og-bottom button span').first()).toHaveCSS('font-size','11.05px')
  for(const label of ['Home','My Team','Leagues','News','More'])await expect(page.locator('.og-bottom').getByRole('button',{name:label,exact:true})).toBeVisible()
}

test('approved Shiva home is real interactive UI and matches mobile shell',async({page})=>{
  const consoleErrors:string[]=[];const pageErrors:string[]=[]
  page.on('console',msg=>{if(msg.type()==='error')consoleErrors.push(msg.text())});page.on('pageerror',err=>pageErrors.push(err.message))
  await page.route('**/api/auth/session',route=>route.fulfill({status:401,contentType:'application/json',body:'{}'}))
  await page.route('https://a.espncdn.com/**',route=>route.fulfill({status:200,contentType:'image/png',body:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADElEQVR42mNk+M/wHwAF/gL+NqFrWQAAAABJRU5ErkJggg==','base64')}))
  await page.route('**/api/leagues',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({leagues:[]})}))
  await page.route('**/api/scoreboard*',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({games:[]})}))
  await page.route('**/api/rankings*',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({players:[
    {id:'1',espnId:'1',name:'Alpha Runner',team:'ATL',pos:'RB',rank:1,percentStarted:92,projectedPoints:20},
    {id:'2',espnId:'2',name:'Bravo Receiver',team:'BUF',pos:'WR',rank:2,percentStarted:71,projectedPoints:18},
    {id:'3',espnId:'3',name:'Charlie Tight End',team:'KC',pos:'TE',rank:3,percentStarted:55,projectedPoints:15},
    {id:'4',espnId:'4',name:'Delta Flex',team:'DET',pos:'WR',rank:4,percentStarted:41,projectedPoints:13},
    {id:'5',espnId:'5',name:'Echo Back',team:'LV',pos:'RB',rank:5,percentStarted:10,projectedPoints:8,injuryStatus:'OUT'},
  ]})}))
  await page.goto('/',{waitUntil:'networkidle'});await expect(page.locator('.spec-shell')).toBeVisible();await assertMobileShell(page);await assertApprovedHome(page);await page.screenshot({path:'test-results/mobile-home.png',fullPage:true})
  await heroAuthIsViewportSafe(page)
  await page.locator('.og-bottom').getByRole('button',{name:'My Team',exact:true}).click();await assertMobileShell(page)
  await page.locator('.og-bottom').getByRole('button',{name:'Leagues',exact:true}).click();await assertMobileShell(page)
  await page.locator('.og-bottom').getByRole('button',{name:'More',exact:true}).click();await assertMobileShell(page);await expect(page.getByRole('heading',{name:'More Shiva',exact:true})).toBeVisible()
  expect(pageErrors).toEqual([]);expect(consoleErrors.filter(m=>!/Failed to load resource|ERR_NETWORK_ACCESS_DENIED/.test(m))).toEqual([])
})

async function heroAuthIsViewportSafe(page:any){
  await page.locator('.live-profile').getByRole('button',{name:'Login or sign up',exact:true}).click()
  const dialogs=page.getByRole('dialog',{name:'Shiva account'});await expect(dialogs).toHaveCount(1);await expect(dialogs).toBeVisible()
  const box=await dialogs.boundingBox();const viewportWidth=await page.evaluate(()=>window.innerWidth);expect(box).not.toBeNull();expect(box!.x).toBeGreaterThanOrEqual(0);expect(box!.x+box!.width).toBeLessThanOrEqual(viewportWidth)
  await dialogs.getByRole('button',{name:'Close',exact:true}).click();await expect(dialogs).toHaveCount(0)
}

test('selected league team drives personalized Key Players and roster start sit',async({page})=>{
  const leagueData={league:{id:'12345',provider:'espn',season:2026,name:'Shiva One',scoringPeriod:1,matchupPeriod:1,rosterSlots:['QB','RB','WR','TE','RB'],scoringSettings:{}},teams:[{id:'1',name:'My Selected Team',owners:[],wins:0,losses:0},{id:'2',name:'Other Team',owners:[],wins:0,losses:0}],roster:[
    {teamId:'1',team:'My Selected Team',playerId:'a',player:'Starter Back',slotId:'2',slot:'RB',proTeamId:1,proTeam:'ATL',position:'RB',eligibleSlots:['RB','FLEX'],injuryStatus:'',percentOwned:90,percentStarted:70,projectedPoints:8},
    {teamId:'1',team:'My Selected Team',playerId:'b',player:'Bench Back',slotId:'20',slot:'BE',proTeamId:2,proTeam:'BUF',position:'RB',eligibleSlots:['RB','FLEX'],injuryStatus:'',percentOwned:80,percentStarted:55,projectedPoints:14},
    {teamId:'1',team:'My Selected Team',playerId:'c',player:'Alpha Receiver',slotId:'4',slot:'WR',proTeamId:12,proTeam:'KC',position:'WR',eligibleSlots:['WR','FLEX'],injuryStatus:'',percentOwned:95,percentStarted:86,projectedPoints:18},
    {teamId:'1',team:'My Selected Team',playerId:'d',player:'Alpha Tight End',slotId:'6',slot:'TE',proTeamId:8,proTeam:'DET',position:'TE',eligibleSlots:['TE','FLEX'],injuryStatus:'',percentOwned:85,percentStarted:72,projectedPoints:12},
    {teamId:'1',team:'My Selected Team',playerId:'e',player:'Alpha Quarterback',slotId:'0',slot:'QB',proTeamId:13,proTeam:'LV',position:'QB',eligibleSlots:['QB'],injuryStatus:'',percentOwned:99,percentStarted:92,projectedPoints:20},
    {teamId:'2',team:'Other Team',playerId:'x',player:'Wrong Team Star',slotId:'0',slot:'QB',proTeamId:15,proTeam:'MIA',position:'QB',eligibleSlots:['QB'],injuryStatus:'',percentOwned:99,percentStarted:99,projectedPoints:30}
  ],freeAgents:[],matchups:[{period:1,homeTeamId:'1',awayTeamId:'2',homeScore:null,awayScore:null,homeProjected:72,awayProjected:85}]}
  await page.addInitScript(({league})=>{sessionStorage.setItem('shiva-league',JSON.stringify(league));sessionStorage.setItem('shiva-team-id','1')},{league:leagueData})
  await page.route('**/api/auth/session',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({user:{id:'u1',email:'owner@example.com'}})}))
  await page.route('**/api/leagues',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({leagues:[{id:'saved',provider:'espn',league_id:'12345',season:2026,team_id:'1',league_name:'Shiva One',team_name:'My Selected Team',league_data:leagueData}]})}))
  await page.route('**/api/scoreboard*',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({games:[{id:'g1',name:'ATL at CAR',date:'',status:'',teams:[{abbreviation:'ATL',homeAway:'away'},{abbreviation:'CAR',homeAway:'home'}]},{id:'g2',name:'BUF vs NYJ',date:'',status:'',teams:[{abbreviation:'BUF',homeAway:'home'},{abbreviation:'NYJ',homeAway:'away'}]}]})}))
  await page.route('**/api/rankings*',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({players:[
    {id:'a',espnId:'a',name:'Starter Back',team:'ATL',pos:'RB',rank:50,percentStarted:70,projectedPoints:8},
    {id:'b',espnId:'b',name:'Bench Back',team:'BUF',pos:'RB',rank:40,percentStarted:55,projectedPoints:14},
    {id:'c',espnId:'c',name:'Alpha Receiver',team:'KC',pos:'WR',rank:10,percentStarted:86,projectedPoints:18},
    {id:'d',espnId:'d',name:'Alpha Tight End',team:'DET',pos:'TE',rank:20,percentStarted:72,projectedPoints:12},
    {id:'e',espnId:'e',name:'Alpha Quarterback',team:'LV',pos:'QB',rank:5,percentStarted:92,projectedPoints:20},
    {id:'x',espnId:'x',name:'Wrong Team Star',team:'MIA',pos:'QB',rank:1,percentStarted:99,projectedPoints:30}
  ]})}))
  await page.goto('/',{waitUntil:'networkidle'})
  const dashboard=page.locator('.og-snapshot-page').first();await expect(dashboard.getByText('My Selected Team',{exact:true})).toBeVisible();const keyPlayers=dashboard.locator('.og-key-players');await expect(keyPlayers.getByText('Wrong Team Star',{exact:true})).toHaveCount(0);for(const name of ['Starter Back','Bench Back','Alpha Receiver','Alpha Tight End','Alpha Quarterback'])await expect(keyPlayers.getByText(name,{exact:true})).toBeVisible();const starterRow=keyPlayers.locator('.og-key-list>div').filter({hasText:'Starter Back'});const benchRow=keyPlayers.locator('.og-key-list>div').filter({hasText:'Bench Back'});await expect(starterRow).toHaveAttribute('data-recommendation','sit');await expect(starterRow.getByText('SIT',{exact:true})).toBeVisible();await expect(benchRow).toHaveAttribute('data-recommendation','start');await expect(benchRow.getByText('START',{exact:true})).toBeVisible();await expect(benchRow).toContainText('vs NYJ');await expect(starterRow).toContainText('@ CAR')
})

test('Ask Shiva scope, composer and answer actions are interactive',async({page})=>{
  await page.route('**/api/ask',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({answer:'Start Jeanty. Better volume and matchup.'})}))
  await page.goto('/',{waitUntil:'networkidle'})
  const ask=page.locator('.og-home-ask')
  await ask.getByRole('button',{name:'All My Leagues',exact:true}).click()
  await expect(ask.getByRole('button',{name:'All My Leagues',exact:true})).toHaveClass(/active/)
  await ask.getByLabel('Ask Shiva home question').fill('Jeanty or Skattebo?')
  await ask.getByRole('button',{name:'Send home question to Shiva',exact:true}).click()
  await expect(ask.getByText('Start Jeanty. Better volume and matchup.',{exact:true})).toBeVisible()
  await ask.getByRole('button',{name:/Ask Why/}).click()
  await expect(ask.getByLabel('Ask Shiva home question')).toHaveValue(/^Why\? /)
  await ask.getByRole('button',{name:'Send home question to Shiva',exact:true}).click()
  await expect(ask.getByText('Start Jeanty. Better volume and matchup.',{exact:true})).toBeVisible()
  await ask.getByRole('button',{name:/Fix Lineup/}).click()
  await expect(page.getByText(/My Team|Lineup/i).first()).toBeVisible()
})

test('league auth stays inline, in viewport, and resumes the saved import',async({page})=>{
  const leagueData={league:{id:'12345',provider:'espn',season:2026,name:'The League',scoringPeriod:1,matchupPeriod:1,rosterSlots:[],scoringSettings:{}},teams:[{id:'1',name:'Gridiron Gods',owners:[],wins:0,losses:0}],roster:[],freeAgents:[],matchups:[]}
  await page.route('**/api/auth/session',route=>route.fulfill({status:401,contentType:'application/json',body:'{}'}))
  await page.route('**/api/auth/signin',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({user:{id:'u1',email:'owner@example.com',firstName:'Chris'}})}))
  await page.route('**/api/league-import',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(leagueData)}))
  await page.route('**/api/leagues*',async route=>{if(route.request().method()==='POST')await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({league:{id:'saved',provider:'espn',league_id:'12345',season:2026,team_id:'1',league_data:leagueData}})});else await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({leagues:[]})})})
  await page.goto('/',{waitUntil:'networkidle'});await page.locator('.og-bottom').getByRole('button',{name:'Leagues',exact:true}).click();await page.getByLabel('League ID').fill('12345');await page.getByRole('button',{name:'Go',exact:true}).click()
  const dialog=page.getByRole('dialog',{name:'Shiva account'});await expect(dialog).toHaveCount(1);await dialog.getByRole('button',{name:'Close',exact:true}).click();const inline=page.getByRole('button',{name:'Sign Up / Sign In',exact:true});await expect(inline).toBeVisible();await inline.click();await expect(dialog).toHaveCount(1)
  await dialog.getByRole('button',{name:'Sign In',exact:true}).click();await dialog.getByLabel('Email').fill('owner@example.com');await dialog.getByLabel('Password').fill('password123');await dialog.getByRole('button',{name:'Sign In',exact:true}).last().click();await expect(dialog).toHaveCount(0)
  await expect.poll(()=>page.evaluate(()=>Boolean(sessionStorage.getItem('shiva-league')))).toBe(true);expect(await page.evaluate(()=>localStorage.getItem('shiva-pending-league-import'))).toBeNull()
})

test('Guide remains native and expandable',async({page})=>{
  await page.goto('/',{waitUntil:'networkidle'});await page.locator('.og-shortcuts').getByRole('button',{name:/^Draft Guide/}).click();await expect(page.getByRole('heading',{level:1,name:'Shiva’s Draft Guide',exact:true})).toBeVisible();await expect(page.locator('iframe')).toHaveCount(0);await expect(page.getByRole('link',{name:/Full Draft Guide PDF/i})).toBeVisible();const topics=page.locator('.guide-topic-pills');await topics.getByRole('button',{name:'Charts',exact:true}).click();await expect(page.getByRole('heading',{level:1,name:'Charts',exact:true})).toBeVisible();await expect(page.locator('.guide-chart-image-button img')).toHaveCount(6)
})

test('live football APIs return usable data and article links',async({request})=>{
  const health=await request.get('/api/health');expect(health.ok()).toBeTruthy();expect((await health.json()).ok).toBe(true)
  const authHealth=await request.get('/api/auth/health');expect(authHealth.ok()).toBeTruthy();expect((await authHealth.json()).ok).toBe(true)
  const news=await request.get('/api/news');expect(news.ok()).toBeTruthy();const newsData=await news.json();expect(Array.isArray(newsData.articles)).toBeTruthy();expect(newsData.articles.length).toBeGreaterThan(0);expect(newsData.articles.filter((a:any)=>typeof a.url==='string'&&/^https?:\/\//.test(a.url)).length).toBeGreaterThan(0)
  const scores=await request.get('/api/scoreboard');expect(scores.ok()).toBeTruthy();expect(Array.isArray((await scores.json()).games)).toBeTruthy()
  const rankings=await request.get('/api/rankings');expect(rankings.ok()).toBeTruthy();expect(Array.isArray((await rankings.json()).players)).toBeTruthy()
  const edges=await request.get('/api/edges');expect(edges.ok()).toBeTruthy();expect(Array.isArray((await edges.json()).players)).toBeTruthy()
})

test('launch never exposes a white screen on mobile',async({page})=>{await page.goto('/',{waitUntil:'domcontentloaded'});const colors=await page.evaluate(async()=>{const seen:string[]=[];for(let i=0;i<12;i++){seen.push(getComputedStyle(document.body).backgroundColor);await new Promise(r=>setTimeout(r,50))}return seen});expect(colors).not.toContain('rgb(255, 255, 255)')})