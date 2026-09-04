import { expect, test } from '@playwright/test'

const pages = ['Draft', 'Guide', 'Scores'] as const

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

async function assertCoachHome(page: any) {
  await expect(page.getByRole('heading', { level: 1, name: 'Shiva Coach', exact: true })).toBeVisible()
  await expect(page.getByText('Your roster, current ESPN context and Shiva’s historical evidence in one place.', { exact: true })).toHaveCount(0)
  await expect(page.getByText('SHIVA SAYS', { exact: true })).toHaveCount(0)
  await expect(page.getByRole('heading', { level: 2, name: /Connect your ESPN league to fully unlock Shiva|is connected/ })).toBeVisible()

  const coachTabs = ['Overview', 'League', 'Start / Sit', 'Waivers', 'Lineup', 'Player Watch', 'Ask Shiva']
  for (const label of coachTabs) await expect(page.getByRole('button', { name: label, exact: true })).toBeVisible()
  const tabs = page.locator('.coach-tabs button')
  await expect(tabs).toHaveCount(7)
  const positions = await tabs.evaluateAll((els: HTMLElement[]) => els.map((el) => ({ x: el.getBoundingClientRect().x, y: el.getBoundingClientRect().y })))
  expect(new Set(positions.map((item) => Math.round(item.y))).size).toBeGreaterThanOrEqual(2)
  expect(Math.max(...positions.map((item) => item.x))).toBeLessThan(await page.evaluate(() => window.innerWidth))

  await expect(page.getByLabel('ESPN League ID')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Connect ESPN League', exact: true })).toBeVisible()
  await expect(page.getByText('The app still works without ESPN, but league sync turns Shiva from a general tool into your team’s decision room.', { exact: true })).toHaveCount(0)

  await expect(page.getByText('LINEUP EDGE', { exact: true })).toBeHidden()
  await expect(page.getByText('DRAFT EDGE', { exact: true })).toBeHidden()

  const edgeCards = page.locator('.home-edge-cards .edge-panel')
  await expect(edgeCards).toHaveCount(2)
  await expect(edgeCards.nth(0).locator('.edge-title')).toHaveText('Raise the Floor')
  await expect(edgeCards.nth(1).locator('.edge-title')).toHaveText('Keep the Ceiling')

  for (const title of await page.locator('.home-edge-cards .edge-title').all()) {
    expect(await title.evaluate((el: HTMLElement) => getComputedStyle(el).color)).toBe('rgb(230, 204, 120)')
  }
  for (const button of await page.locator('.home-edge-cards .edge-action').all()) {
    expect(await button.evaluate((el: HTMLElement) => getComputedStyle(el).backgroundColor)).toBe('rgb(230, 204, 120)')
  }

  await page.getByRole('button', { name: 'Floor Rankings →', exact: true }).click()
  await expect(page.getByRole('heading', { level: 1, name: 'Raise the Floor', exact: true })).toBeVisible()
  await expect(page.locator('.edge-filter-pills button')).toHaveCount(5)
  const edgeApi = await page.request.get('/api/edges')
  expect(edgeApi.ok()).toBeTruthy()
  const edgePayload = await edgeApi.json()
  expect(edgePayload.players.length).toBeGreaterThan(0)
  await expect(page.locator('.edge-rank-row').first()).toBeVisible()
  await page.getByRole('button', { name: 'RB', exact: true }).click()
  await expect(page.locator('.edge-rank-row .pos-RB').first()).toBeVisible()
  await page.getByRole('button', { name: '← Shiva Coach', exact: true }).click()

  await page.getByRole('button', { name: 'Ceiling Rankings →', exact: true }).click()
  await expect(page.getByRole('heading', { level: 1, name: 'Keep the Ceiling', exact: true })).toBeVisible()
  await expect(page.locator('.edge-rank-row').first()).toBeVisible()
  await page.getByRole('button', { name: '← Shiva Coach', exact: true }).click()

  await page.getByRole('button', { name: 'League', exact: true }).click()
  await expect(page.getByText(/Connect your ESPN league from Overview|League Standings/)).toBeVisible()
  await page.getByRole('button', { name: 'Start / Sit', exact: true }).click()
  await expect(page.getByRole('heading', { level: 2, name: 'Start / Sit', exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Overview', exact: true }).click()
}

async function assertScoresPage(page: any) {
  await expect(page.getByRole('heading', { level: 1, name: 'Scores', exact: true })).toBeVisible()
  await expect(page.getByRole('heading', { level: 2, name: 'NFL Scores', exact: true })).toBeVisible()
  await expect(page.getByRole('heading', { level: 2, name: 'Latest ESPN', exact: true })).toBeVisible()
  const scoreboardResponse = await page.request.get('/api/scoreboard')
  expect(scoreboardResponse.ok()).toBeTruthy()
  const scoreboard = await scoreboardResponse.json()
  expect(Array.isArray(scoreboard.games)).toBeTruthy()
  if (scoreboard.games.length) await expect(page.locator('.score-list .score-card')).toHaveCount(scoreboard.games.length)
  const newsResponse = await page.request.get('/api/news')
  expect(newsResponse.ok()).toBeTruthy()
  const newsPayload = await newsResponse.json()
  await expect(page.locator('.blast-list .blast-card')).toHaveCount(newsPayload.articles.slice(0, 4).length)
}

test('approved Coach controls, Edge rankings and mobile shell are correct', async ({ page }) => {
  const consoleErrors: string[] = []
  const pageErrors: string[] = []
  page.on('console', (msg) => { if (msg.type() === 'error') consoleErrors.push(msg.text()) })
  page.on('pageerror', (err) => pageErrors.push(err.message))
  await page.goto('/', { waitUntil: 'networkidle' })
  await expect(page.locator('.app-shell')).toBeVisible()
  await assertMobileShell(page)
  await expect(page.locator('.brand-trophy')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Shiva', exact: true })).toBeVisible()
  await assertCoachHome(page)
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
  expect(consoleErrors).toEqual([])
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
