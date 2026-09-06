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
  const hero=page.locator('.live-hero');await expect(hero).toBeVisible();await expect(hero.locator('.live-hero-wordmark')).toContainText('Shiva');await expect(hero.locator('.live-hero-wordmark')).toContainText('FANTASY IQ');await expect(hero.getByRole('button',{name:'Notifications',exact:true})).toBeVisible();await expect(hero.getByRole('button',{name:'Notifications',exact:true}).locator('i')).toHaveCount(0);await expect(hero.locator('.live-profile')).toBeVisible();await expect(hero.locator('.live-week')).toHaveCount(0);await expect(hero).not.toContainText('WEEK')
  await expect(hero).toHaveCSS('height','111px')
  const stadium=await hero.locator('.live-hero-stadium').evaluate((el:HTMLElement)=>getComputedStyle(el).backgroundImage);expect(stadium).toContain('hero-approved-clean.webp')
  await hero.getByRole('button',{name:'Notifications',exact:true}).click();await expect(hero.getByText('Notifications',{exact:true})).toBeVisible();await hero.getByRole('button',{name:'Close',exact:true}).click()
  await expect(page.locator('.og-league-strip')).toHaveCount(0)
  const ask=page.locator('.og-home-ask');await expect(ask).toBeVisible();await expect(ask.getByRole('heading',{name:'Ask Shiva',exact:true})).toBeVisible();await expect(ask.locator('.og-home-ask-title img')).toBeVisible();await expect(ask.getByRole('button',{name:'This League',exact:true})).toBeVisible();await expect(ask.getByRole('button',{name:'All My Leagues',exact:true})).toBeVisible();await expect(ask.getByLabel('Ask Shiva home question')).toBeVisible();await expect(ask.getByText('SHIVA SAYS',{exact:true})).toBeVisible()
  await expect(page.locator('.og-shortcuts button')).toHaveCount(6)
  for(const label of ['Start / Sit','Waivers','Trade Analyzer','Draft Guide','Power Rankings','Schedule'])await expect(page.locator('.og-shortcuts').getByRole('button',{name:new RegExp(`^${label}`)})).toBeVisible()
  const tileOverflow=await page.locator('.og-shortcuts button').evaluateAll((buttons:HTMLElement[])=>buttons.map(button=>button.scrollWidth>button.clientWidth+1));expect(tileOverflow).not.toContain(true)
  const dashboard=page.locator('.og-snapshot-page').first();await expect(dashboard.locator('.og-snapshot-card')).toHaveCount(2);await expect(dashboard.locator('.live-helmet')).toHaveCount(2)
  await expect(dashboard.getByRole('button',{name:'Connect League',exact:true})).toBeVisible();await expect(page.getByRole('button',{name:/Connect (your )?league/i})).toHaveCount(1)
  await page.evaluate(()=>window.scrollTo(0,document.documentElement.scrollHeight));await page.waitForTimeout(50);const cardBox=await dashboard.locator('.og-snapshot-card').first().boundingBox();const navBox=await page.locator('.og-bottom').boundingBox();expect(cardBox).not.toBeNull();expect(navBox).not.toBeNull();expect(cardBox!.height).toBeGreaterThanOrEqual(260);expect(navBox!.y-(cardBox!.y+cardBox!.height)).toBeGreaterThanOrEqual(0);expect(navBox!.y-(cardBox!.y+cardBox!.height)).toBeLessThanOrEqual(12)
  await expect(dashboard.locator('.live-helmet.left img')).toHaveAttribute('src',/helmet-gold-3d/);await expect(dashboard.locator('.live-helmet.right img')).toHaveAttribute('src',/helmet-red-3d/)
  const labels=await dashboard.locator('.og-snapshot-card > header > b').allTextContents();expect(labels).toEqual(['My Matchup','Key Players']);await expect(dashboard.getByText('My League',{exact:true})).toHaveCount(0);await expect(dashboard.locator('.og-key-list>div')).toHaveCount(5);await expect(dashboard.getByText('START',{exact:true})).toHaveCount(2);await expect(dashboard.getByText('CONSIDER',{exact:true})).toHaveCount(2);await expect(dashboard.getByText('SIT',{exact:true})).toHaveCount(1)
  await expect(ask.getByRole('heading',{name:'Ask Shiva',exact:true})).toHaveCSS('font-size','26px');await expect(page.locator('.og-shortcut-copy b').first()).toHaveCSS('font-size','10.4px');await expect(page.locator('.og-shortcuts button').first()).toHaveCSS('height','54px');await expect(dashboard.locator('.og-snapshot-card > header > b').first()).toHaveCSS('font-size','11.7px');await expect(page.locator('.og-bottom button span').first()).toHaveCSS('font-size','11.05px')
  for(const label of ['Home','My Team','Leagues','News','More'])await expect(page.locator('.og-bottom').getByRole('button',{name:label,exact:true})).toBeVisible()
}

test('approved Shiva home is real interactive UI and matches mobile shell',async({page})=>{
  const consoleErrors:string[]=[];const pageErrors:string[]=[]
  page.on('console',msg=>{if(msg.type()==='error')consoleErrors.push(msg.text())});page.on('pageerror',err=>pageErrors.push(err.message))
  await page.route('**/api/auth/session',route=>route.fulfill({status:401,contentType:'application/json',body:'{}'}))
  await page.route('https://a.espncdn.com/**',route=>route.fulfill({status:200,contentType:'image/png',body:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADElEQVR42mNk+M/wHwAF/gL+NqFrWQAAAABJRU5ErkJggg==','base64')}))
  await page.route('**/api/leagues',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({leagues:[]})}))
  await page.route('**/api/rankings',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({players:[
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
  const box=await dialogs.boundingBox();expect(box).not.toBeNull();expect(box!.x).toBeGreaterThanOrEqual(0);expect(box!.x+box!.width).toBeLessThanOrEqual(393)
  await dialogs.getByRole('button',{name:'Close',exact:true}).click();await expect(dialogs).toHaveCount(0)
}

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
  const news=await request.get('/api/news');expect(news.ok()).toBeTruthy();const newsData=await news.json();expect(Array.isArray(newsData.articles)).toBeTruthy();expect(newsData.articles.length).toBeGreaterThan(0);expect(newsData.articles.filter((a:any)=>typeof a.url==='string'&&/^https?:\/\//.test(a.url)).length).toBeGreaterThan(0)
  const scores=await request.get('/api/scoreboard');expect(scores.ok()).toBeTruthy();expect(Array.isArray((await scores.json()).games)).toBeTruthy()
  const rankings=await request.get('/api/rankings');expect(rankings.ok()).toBeTruthy();expect(Array.isArray((await rankings.json()).players)).toBeTruthy()
  const edges=await request.get('/api/edges');expect(edges.ok()).toBeTruthy();expect(Array.isArray((await edges.json()).players)).toBeTruthy()
})

test('launch never exposes a white screen on mobile',async({page})=>{await page.goto('/',{waitUntil:'domcontentloaded'});const colors=await page.evaluate(async()=>{const seen:string[]=[];for(let i=0;i<12;i++){seen.push(getComputedStyle(document.body).backgroundColor);await new Promise(r=>setTimeout(r,50))}return seen});expect(colors).not.toContain('rgb(255, 255, 255)')})
