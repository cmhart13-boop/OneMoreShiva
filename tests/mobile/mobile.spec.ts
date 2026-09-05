import { expect, test } from '@playwright/test'

const pages = ['Coach', 'Guide', 'Scores'] as const

async function assertMobileShell(page: any) {
  const body = page.locator('body')
  await expect(body).toBeVisible()
  const overflow = await page.evaluate(() => ({ width: document.documentElement.scrollWidth, viewport: window.innerWidth }))
  expect(overflow.width).toBeLessThanOrEqual(overflow.viewport + 2)
  const nav = page.locator('.bottom-nav')
  await expect(nav).toBeVisible()
  const navBox = await nav.boundingBox()
  expect(navBox).not.toBeNull()
  if (navBox) {
    const viewportHeight = await page.evaluate(() => window.innerHeight)
    const gap = viewportHeight - (navBox.y + navBox.height)
    expect(gap).toBeGreaterThanOrEqual(0)
    expect(gap).toBeLessThanOrEqual(24)
  }
  const bg = await body.evaluate((el: HTMLElement) => getComputedStyle(el).backgroundColor)
  expect(bg).not.toBe('rgb(255, 255, 255)')
}

async function assertOverviewHome(page: any) {
  await expect(page.getByText('YOUR HOME BASE', { exact: true })).toBeVisible()
  await expect(page.getByRole('heading', { level: 1, name: /Welcome back|Hey,/ })).toBeVisible()

  const askHero = page.locator('.home-ask-hero')
  await expect(askHero.getByRole('heading', { level: 2, name: 'Ask Shiva', exact: true })).toBeVisible()
  await expect(askHero.locator('.ask-box')).toBeVisible()
  await expect(askHero.getByRole('button', { name: 'Ask Shiva', exact: true })).toBeVisible()

  const syncBanner = page.locator('.home-sync-banner')
  if (await syncBanner.count()) {
    const syncToggle = syncBanner.getByRole('button', { name: /Sync Your League/i })
    await expect(syncToggle).toBeVisible()
    await expect(page.getByLabel('League provider')).toHaveCount(0)
    await syncToggle.click()
    await expect(page.getByLabel('League provider')).toBeVisible()
    await expect(page.getByLabel('League ID', { exact: true })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Go', exact: true })).toBeVisible()
    await syncToggle.click()
  }

  const edgeCards = page.locator('.home-edge-cards .edge-panel')
  await expect(edgeCards).toHaveCount(2)
  await expect(edgeCards.nth(0).locator('.edge-title')).toHaveText('Raise the Floor')
  await expect(edgeCards.nth(1).locator('.edge-title')).toHaveText('Keep the Ceiling')
  for (const title of await page.locator('.home-edge-cards .edge-title').all()) {
    expect(await title.evaluate((el: HTMLElement) => getComputedStyle(el).textAlign)).toBe('left')
    expect(await title.evaluate((el: HTMLElement) => getComputedStyle(el).color)).toBe('rgb(230, 204, 120)')
  }
  for (const button of await page.locator('.home-edge-cards .edge-action').all()) {
    expect(await button.evaluate((el: HTMLElement) => getComputedStyle(el).backgroundColor)).toBe('rgb(234, 217, 142)')
  }

  await page.getByRole('button', { name: 'See Floor Rankings →', exact: true }).click()
  await expect(page.getByRole('button', { name: 'See Floor Rankings →', exact: true })).toHaveAttribute('aria-expanded', 'true')
  await expect(page.locator('.edge-filter-pills button')).toHaveCount(6)
  await page.getByRole('button', { name: 'See Ceiling Rankings →', exact: true }).click()
  await expect(page.getByRole('button', { name: 'See Ceiling Rankings →', exact: true })).toHaveAttribute('aria-expanded', 'true')

  const homeNews = page.locator('.home-news')
  await expect(homeNews.getByRole('heading', { level: 2, name: 'Latest ESPN', exact: true })).toBeVisible()
}

async function assertScoresPage(page: any) {
  await expect(page.getByRole('heading', { level: 1, name: 'Scores', exact: true })).toBeVisible()
  await expect(page.getByRole('heading', { level: 2, name: 'NFL Scores', exact: true })).toBeVisible()
  await expect(page.getByRole('heading', { level: 2, name: 'Latest ESPN', exact: true })).toBeVisible()
  await expect(page.locator('.score-list')).toBeVisible()
}

test('approved Overview hierarchy, Edge rankings and mobile shell are correct', async ({ page }) => {
  const consoleErrors: string[] = []
  const pageErrors: string[] = []
  page.on('console', (msg) => { if (msg.type() === 'error') consoleErrors.push(msg.text()) })
  page.on('pageerror', (err) => pageErrors.push(err.message))
  await page.goto('/', { waitUntil: 'networkidle' })
  await expect(page.locator('.app-shell')).toBeVisible()
  await assertMobileShell(page)
  await expect(page.locator('.brand-trophy')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Shiva', exact: true })).toBeVisible()
  await assertOverviewHome(page)
  await page.screenshot({ path: 'test-results/mobile-home.png', fullPage: true })
  for (const label of pages) {
    const button = page.getByRole('button', { name: label, exact: true })
    await button.click()
    await page.waitForTimeout(350)
    await assertMobileShell(page)
    if (label === 'Scores') await assertScoresPage(page)
    await page.screenshot({ path: `test-results/mobile-${label.toLowerCase()}.png`, fullPage: true })
  }
  expect(pageErrors).toEqual([])
  expect(consoleErrors.filter((message) => !/Failed to load resource|ERR_NETWORK_ACCESS_DENIED/.test(message))).toEqual([])
})

test('Guide is native, wrapped, visual and expandable', async ({ page }) => {
  await page.goto('/', { waitUntil: 'networkidle' })
  await page.locator('.bottom-nav').getByRole('button', { name: 'Guide', exact: true }).click()
  await expect(page.getByRole('heading', { level: 1, name: 'Shiva’s Draft Guide', exact: true })).toBeVisible()
  await expect(page.getByText(/Organized by topic instead of PDF page/i)).toHaveCount(0)
  await expect(page.locator('iframe')).toHaveCount(0)
  await expect(page.getByRole('link', { name: /Full Draft Guide PDF/i })).toBeVisible()

  const topics = page.locator('.guide-topic-pills')
  const pillOverflow = await topics.evaluate((el: HTMLElement) => ({ scrollWidth:el.scrollWidth, clientWidth:el.clientWidth }))
  expect(pillOverflow.scrollWidth).toBeLessThanOrEqual(pillOverflow.clientWidth + 2)

  await topics.getByRole('button', { name:'Charts', exact:true }).click()
  await expect(page.getByRole('heading', { level:1, name:'Charts', exact:true })).toBeVisible()
  await expect(page.locator('.guide-chart-card')).toHaveCount(7)
  await expect(page.locator('.guide-chart-image-button img')).toHaveCount(6)
  await expect(page.getByText('Graph coming soon in the published source.', { exact:true })).toBeVisible()
  for (const title of ['QB Volume','RB Efficiency','WR Efficiency','QB Rushing','Fantasy Shootout',"RB's Dream QB"]) {
    await expect(page.locator('.guide-chart-card').getByRole('heading', { name:title, exact:true })).toBeVisible()
  }
  expect(await page.locator('body').innerText()).not.toMatch(/\bJoel\b/i)

  await page.getByRole('button', { name:'Expand QB Volume', exact:true }).click()
  await expect(page.getByRole('dialog', { name:'QB Volume expanded' })).toBeVisible()
  await expect(page.getByRole('dialog', { name:'QB Volume expanded' }).locator('img')).toBeVisible()
  await page.getByRole('button', { name:'Close expanded chart', exact:true }).click()
  await expect(page.getByRole('dialog', { name:'QB Volume expanded' })).toHaveCount(0)
})

test('launch never exposes a white screen on mobile', async ({ page }) => {
  await page.goto('/', { waitUntil: 'domcontentloaded' })
  const colors = await page.evaluate(async () => {
    const seen: string[] = []
    for (let i = 0; i < 12; i += 1) { seen.push(getComputedStyle(document.body).backgroundColor); await new Promise((resolve) => setTimeout(resolve, 50)) }
    return seen
  })
  expect(colors).not.toContain('rgb(255, 255, 255)')
})