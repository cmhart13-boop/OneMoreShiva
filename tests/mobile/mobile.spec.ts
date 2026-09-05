import { expect, test } from '@playwright/test'

async function assertMobileShell(page: any) {
  const body = page.locator('body')
  await expect(body).toBeVisible()
  const overflow = await page.evaluate(() => ({ width: document.documentElement.scrollWidth, viewport: window.innerWidth }))
  expect(overflow.width).toBeLessThanOrEqual(overflow.viewport + 2)
  const nav = page.locator('.spec-bottom')
  await expect(nav).toBeVisible()
  await expect(nav.getByRole('button')).toHaveCount(6)
  const bg = await body.evaluate((el: HTMLElement) => getComputedStyle(el).backgroundColor)
  expect(bg).not.toBe('rgb(255, 255, 255)')
}

async function assertSpecHome(page: any) {
  await expect(page.locator('.og-hero')).toBeVisible()
  const heroBg = await page.locator('.og-hero').evaluate((el: HTMLElement) => getComputedStyle(el).backgroundImage)
  expect(heroBg).toContain('og-home-hero.jpg')
  await expect(page.locator('.og-shortcuts button')).toHaveCount(6)
  for (const label of ['Start / Sit','Waivers','Trade Analyzer','Draft Guide','Power Rankings','Schedule']) {
    await expect(page.locator('.og-shortcuts').getByRole('button', { name:new RegExp(`^${label}`) })).toBeVisible()
  }
  const tileOverflow = await page.locator('.og-shortcuts button').evaluateAll((buttons:HTMLElement[]) => buttons.map(button => button.scrollWidth > button.clientWidth + 1))
  expect(tileOverflow).not.toContain(true)
  const clippedTileText = await page.locator('.og-shortcut-copy b, .og-shortcut-copy small').evaluateAll((labels:HTMLElement[]) => labels.map(label => label.scrollWidth > label.clientWidth + 1))
  expect(clippedTileText).not.toContain(true)
  await expect(page.locator('.og-dashboard .og-panel')).toHaveCount(2)
  await expect(page.locator('.og-news-card')).toHaveCount(3)
  await expect(page.locator('.og-snapshot-page').first().locator('.og-snapshot-card')).toHaveCount(3)
  await expect(page.locator('.og-helmet')).toHaveCount(2)
  for (const label of ['Leagues','Ask Shiva','Players','Tools','More']) await expect(page.locator('.spec-bottom').getByRole('button', { name:label, exact:true })).toBeVisible()
}

test('approved Shiva home structure and mobile shell are correct', async ({ page }) => {
  const consoleErrors:string[] = []
  const pageErrors:string[] = []
  page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()) })
  page.on('pageerror', err => pageErrors.push(err.message))
  await page.route('**/api/auth/session', route => route.fulfill({ status:401, contentType:'application/json', body:'{}' }))
  await page.route('**/api/leagues', route => route.fulfill({ status:200, contentType:'application/json', body:JSON.stringify({ leagues:[] }) }))
  await page.route('**/api/rankings', route => route.fulfill({ status:200, contentType:'application/json', body:JSON.stringify({ players:[] }) }))
  await page.route('**/api/news', route => route.fulfill({ status:200, contentType:'application/json', body:JSON.stringify({ articles:[] }) }))
  await page.goto('/', { waitUntil:'networkidle' })
  await expect(page.locator('.spec-shell')).toBeVisible()
  await assertMobileShell(page)
  await assertSpecHome(page)
  await page.screenshot({ path:'test-results/mobile-home.png', fullPage:true })
  await page.locator('.spec-bottom').getByRole('button', { name:'Players', exact:true }).click()
  await assertMobileShell(page)
  await page.locator('.spec-bottom').getByRole('button', { name:'Leagues', exact:true }).click()
  await assertMobileShell(page)
  await page.locator('.spec-bottom').getByRole('button', { name:'More', exact:true }).click()
  await assertMobileShell(page)
  await expect(page.getByRole('heading', { name:'More Shiva', exact:true })).toBeVisible()
  expect(pageErrors).toEqual([])
  expect(consoleErrors.filter(m => !/Failed to load resource|ERR_NETWORK_ACCESS_DENIED/.test(m))).toEqual([])
})

test('Ask Shiva scope toggle, composer, clear control and answer actions are interactive', async ({ page }) => {
  await page.route('**/api/ask', route => route.fulfill({ status:200, contentType:'application/json', body:JSON.stringify({ answer:'Start Jeanty. Better volume and matchup.' }) }))
  await page.goto('/', { waitUntil:'networkidle' })
  await page.locator('.spec-bottom').getByRole('button', { name:'Ask Shiva', exact:true }).click()
  await page.getByRole('button', { name:'All My Leagues', exact:true }).click()
  await expect(page.getByRole('button', { name:'All My Leagues', exact:true })).toHaveClass(/active/)
  await page.getByLabel('Ask Shiva question').fill('Jeanty or Skattebo?')
  await expect(page.getByRole('button', { name:'Clear question', exact:true })).toBeVisible()
  await page.getByRole('button', { name:'Send to Shiva', exact:true }).click()
  await expect(page.getByText('SHIVA SAYS', { exact:true })).toBeVisible()
  await expect(page.getByText('Start Jeanty. Better volume and matchup.', { exact:true })).toBeVisible()
})

test('Guide remains native and expandable', async ({ page }) => {
  await page.goto('/', { waitUntil:'networkidle' })
  await page.locator('.spec-bottom').getByRole('button', { name:'More', exact:true }).click()
  await page.getByRole('button', { name:'Draft Guide', exact:true }).click()
  await expect(page.getByRole('heading', { level:1, name:'Shiva’s Draft Guide', exact:true })).toBeVisible()
  await expect(page.locator('iframe')).toHaveCount(0)
  await expect(page.getByRole('link', { name:/Full Draft Guide PDF/i })).toBeVisible()
  const topics = page.locator('.guide-topic-pills')
  await topics.getByRole('button', { name:'Charts', exact:true }).click()
  await expect(page.getByRole('heading', { level:1, name:'Charts', exact:true })).toBeVisible()
  await expect(page.locator('.guide-chart-image-button img')).toHaveCount(6)
})

test('live football APIs return usable data and article links', async ({ request }) => {
  const health = await request.get('/api/health')
  expect(health.ok()).toBeTruthy()
  expect((await health.json()).ok).toBe(true)

  const news = await request.get('/api/news')
  expect(news.ok()).toBeTruthy()
  const newsData = await news.json()
  expect(Array.isArray(newsData.articles)).toBeTruthy()
  expect(newsData.articles.length).toBeGreaterThan(0)
  const linked = newsData.articles.filter((a:any) => typeof a.url === 'string' && /^https?:\/\//.test(a.url))
  expect(linked.length).toBeGreaterThan(0)

  const scores = await request.get('/api/scoreboard')
  expect(scores.ok()).toBeTruthy()
  const scoreData = await scores.json()
  expect(Array.isArray(scoreData.games)).toBeTruthy()

  const rankings = await request.get('/api/rankings')
  expect(rankings.ok()).toBeTruthy()
  expect(Array.isArray((await rankings.json()).players)).toBeTruthy()

  const edges = await request.get('/api/edges')
  expect(edges.ok()).toBeTruthy()
  expect(Array.isArray((await edges.json()).players)).toBeTruthy()
})

test('launch never exposes a white screen on mobile', async ({ page }) => {
  await page.goto('/', { waitUntil:'domcontentloaded' })
  const colors = await page.evaluate(async () => { const seen:string[] = []; for (let i=0;i<12;i++){ seen.push(getComputedStyle(document.body).backgroundColor); await new Promise(r => setTimeout(r,50)) } return seen })
  expect(colors).not.toContain('rgb(255, 255, 255)')
})
