import { chromium } from 'playwright'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { extname, join, normalize } from 'node:path'

const root = process.cwd()
const browser = await chromium.launch({ headless: true })
const page = await browser.newPage({ viewport: { width: 393, height: 852 }, deviceScaleFactor: 1 })
const players = [
  { id:'1',espnId:'1',name:'Alpha Runner',team:'ATL',pos:'RB',rank:1,percentStarted:92,projectedPoints:20 },
  { id:'2',espnId:'2',name:'Bravo Receiver',team:'BUF',pos:'WR',rank:2,percentStarted:71,projectedPoints:18 },
  { id:'3',espnId:'3',name:'Charlie Tight End',team:'KC',pos:'TE',rank:3,percentStarted:55,projectedPoints:15 },
  { id:'4',espnId:'4',name:'Delta Flex',team:'DET',pos:'WR',rank:4,percentStarted:41,projectedPoints:13 },
  { id:'5',espnId:'5',name:'Echo Back',team:'LV',pos:'RB',rank:5,percentStarted:10,projectedPoints:8,injuryStatus:'OUT' },
]
const mime = { '.css':'text/css', '.js':'text/javascript', '.png':'image/png', '.jpg':'image/jpeg', '.jpeg':'image/jpeg', '.webp':'image/webp', '.svg':'image/svg+xml', '.woff2':'font/woff2', '.json':'application/json', '.webmanifest':'application/manifest+json' }
const safe = (base, path) => { const target=normalize(join(base,path)); if(!target.startsWith(base))throw new Error('Unsafe path'); return target }

await page.route('**/*', async route => {
  const url = new URL(route.request().url())
  try {
    if (url.pathname === '/') return route.fulfill({ status:200, contentType:'text/html', body:await readFile(join(root,'.next/server/app/index.html')) })
    if (url.pathname === '/api/auth/session') return route.fulfill({ status:401, contentType:'application/json', body:'{}' })
    if (url.pathname === '/api/leagues') return route.fulfill({ status:200, contentType:'application/json', body:'{"leagues":[]}' })
    if (url.pathname === '/api/rankings') return route.fulfill({ status:200, contentType:'application/json', body:JSON.stringify({players}) })
    if (url.pathname === '/api/ask') return route.fulfill({ status:200, contentType:'application/json', body:'{"answer":"Start Jeanty. Verified response."}' })
    if (url.pathname.startsWith('/_next/image')) { const source=decodeURIComponent(url.searchParams.get('url')||'').replace(/^\//,''); const file=safe(join(root,'public'),source); return route.fulfill({status:200,contentType:mime[extname(file)]||'application/octet-stream',body:await readFile(file)}) }
    if (url.pathname.startsWith('/_next/static/')) { const file=safe(join(root,'.next/static'),url.pathname.slice('/_next/static/'.length)); return route.fulfill({status:200,contentType:mime[extname(file)]||'application/octet-stream',body:await readFile(file)}) }
    const file=safe(join(root,'public'),url.pathname.replace(/^\//,'')); return route.fulfill({status:200,contentType:mime[extname(file)]||'application/octet-stream',body:await readFile(file)})
  } catch { return route.fulfill({status:404,body:'Not found'}) }
})

await page.goto('http://shiva.local/',{waitUntil:'networkidle'})
await page.waitForTimeout(2700)
await page.screenshot({path:'test-results/mobile-home-final.png',fullPage:true})
const result = await page.evaluate(() => {
  const css=(selector,property)=>getComputedStyle(document.querySelector(selector))[property]
  const hero=document.querySelector('.live-hero').getBoundingClientRect()
  const shortcut=document.querySelector('.og-shortcuts button').getBoundingClientRect()
  const card=document.querySelector('.og-snapshot-card').getBoundingClientRect()
  const askTitle=document.querySelector('.og-home-ask-title h2').getBoundingClientRect()
  const askScope=document.querySelector('.og-home-scope').getBoundingClientRect()
  const scopeOverflow=Array.from(document.querySelectorAll('.og-home-scope button')).map(button=>button.scrollWidth-button.clientWidth)
  return {overflow:document.documentElement.scrollWidth-window.innerWidth,hero:hero.height,shortcut:shortcut.height,card:card.height,strip:document.querySelectorAll('.og-league-strip').length,connect:Array.from(document.querySelectorAll('button')).filter(button=>/connect (your )?league/i.test(button.textContent||'')).length,askFont:css('.og-home-ask-title h2','fontSize'),shortcutFont:css('.og-shortcut-copy b','fontSize'),cardFont:css('.og-snapshot-card>header>b','fontSize'),navFont:css('.og-bottom button span','fontSize'),askCollision:askTitle.right-askScope.left,scopeOverflow}
})
await page.evaluate(()=>window.scrollTo(0,document.documentElement.scrollHeight))
await page.waitForTimeout(50)
const alignment = await page.evaluate(() => { const card=document.querySelector('.og-snapshot-card').getBoundingClientRect(); const nav=document.querySelector('.og-bottom').getBoundingClientRect(); return {gap:nav.top-card.bottom,cardBottom:card.bottom,navTop:nav.top} })
console.log(JSON.stringify({...result,...alignment},null,2))
assert.equal(result.overflow,0)
assert.equal(result.hero,111)
assert.equal(result.shortcut,54)
assert.ok(result.card>=260)
assert.equal(result.strip,0)
assert.equal(result.connect,1)
assert.equal(result.askFont,'26px')
assert.equal(result.shortcutFont,'10.4px')
assert.equal(result.cardFont,'11.7px')
assert.equal(result.navFont,'11.05px')
assert.ok(result.askCollision<=0)
assert.ok(result.scopeOverflow.every(value=>value<=0))
assert.ok(alignment.gap>=0&&alignment.gap<=12)
await page.locator('.live-bell').click()
assert.equal(await page.locator('.live-alert-popover').count(),1)
await page.getByRole('button',{name:'Close',exact:true}).click()
await page.locator('.live-profile').getByRole('button',{name:'Login or sign up',exact:true}).click()
const dialog=page.getByRole('dialog',{name:'Shiva account'})
const box=await dialog.boundingBox()
assert.ok(box&&box.x>=0&&box.x+box.width<=393)
await dialog.getByRole('button',{name:'Close',exact:true}).click()
await page.getByRole('button',{name:'All My Leagues',exact:true}).click()
assert.ok((await page.getByRole('button',{name:'All My Leagues',exact:true}).getAttribute('class'))?.includes('active'))
await page.getByLabel('Ask Shiva home question').fill('Jeanty or Skattebo?')
await page.getByRole('button',{name:'Send home question to Shiva',exact:true}).click()
await page.getByText('Start Jeanty. Verified response.',{exact:true}).waitFor()
await page.getByRole('button',{name:'Connect League',exact:true}).click()
await page.getByRole('heading',{name:'Sync Your League',exact:true}).waitFor()
await page.getByLabel('League ID').waitFor()
await browser.close()
