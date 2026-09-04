import { expect, test } from '@playwright/test'

const pages = ['Draft', 'Guide', 'Scores'] as const

async function assertMobileShell(page: any) {
  const body = page.locator('body')
  await expect(body).toBeVisible()

  const overflow = await page.evaluate(() => ({
    width: document.documentElement.scrollWidth,
    viewport: window.innerWidth,
  }))
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
  await expect(page.getByText('Historical evidence, not a mystery score.', { exact: true })).toHaveCount(0)
  await expect(page.getByText('SHIVA EDGE', { exact: true })).toHaveCount(0)

  const coachTabs = ['Overview', 'League', 'Start / Sit', 'Waivers', 'Lineup', 'Player Watch', 'Ask Shiva']
  for (const label of coachTabs) await expect(page.getByRole('button', { name: label, exact: true })).toBeVisible()

  await expect(page.getByText('LINEUP EDGE', { exact: true })).toBeHidden()
  await expect(page.getByText('DRAFT EDGE', { exact: true })).toBeHidden()

  const edgeCards = page.locator('.home-edge-cards .edge-panel')
  await expect(edgeCards).toHaveCount(2)
  await expect(edgeCards.nth(0).locator('.edge-title')).toHaveText('Raise the Floor')
  await expect(edgeCards.nth(1).locator('.edge-title')).toHaveText('Keep the Ceiling')

  for (const title of await page.locator('.home-edge-cards .edge-title').all()) {
    const color = await title.evaluate((el: HTMLElement) => getComputedStyle(el).color)
    expect(color).toBe('rgb(230, 204, 120)')
  }

  const edgeButtons = page.locator('.home-edge-cards .edge-action')
  await expect(edgeButtons).toHaveCount(2)
  for (const button of await edgeButtons.all()) {
    const background = await button.evaluate((el: HTMLElement) => getComputedStyle(el).backgroundColor)
    expect(background).toBe('rgb(230, 204, 120)')
  }

  await page.getByRole('button', { name: 'Start / Sit', exact: true }).click()
  await expect(page.getByRole('heading', { level: 2, name: 'Start / Sit', exact: true })).toBeVisible()
  await expect(page.locator('.home-edge-cards')).toBeHidden()
  await page.getByRole('button', { name: 'Overview', exact: true }).click()
  await expect(edgeCards.nth(0)).toBeVisible()
}

async function assertScoresPage(page: any) {
  await expect(page.getByRole('heading', { level: 1, name: 'Scores', exact: true })).toBeVisible()
  await expect(page.getByRole('heading', { level: 2, name: 'NFL Scores', exact: true })).toBeVisible()
  await expect(page.getByRole('heading', { level: 2, name: 'Latest ESPN', exact: true })).toBeVisible()

  const scoreboardResponse = await page.request.get('/api/scoreboard')
  expect(scoreboardResponse.ok()).toBeTruthy()
  const scoreboard = await scoreboardResponse.json()
  expect(Array.isArray(scoreboard.games)).toBeTruthy()
  if (scoreboard.games.length) {
    expect(scoreboard.games[0]).toHaveProperty('status')
    expect(scoreboard.games[0].teams?.[0]).toHaveProperty('score')
    await expect(page.locator('.score-list .score-card')).toHaveCount(scoreboard.games.length)
  }

  const newsResponse = await page.request.get('/api/news')
  expect(newsResponse.ok()).toBeTruthy()
  const newsPayload = await newsResponse.json()
  const expectedHeadlines = newsPayload.articles.slice(0, 4).map((article: any) => article.headline)
  const blastCards = page.locator('.blast-list .blast-card')
  await expect(blastCards).toHaveCount(expectedHeadlines.length)
  const renderedHeadlines = await blastCards.locator('.blast-copy > b').allTextContents()
  expect(renderedHeadlines).toEqual(expectedHeadlines)
}

test('Coach-first Shiva home, Scores page and mobile shell are correct', async ({ page }) => {
  const consoleErrors: string[] = []
  const pageErrors: string[] = []

  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text())
  })
  page.on('pageerror', (err) => pageErrors.push(err.message))

  await page.goto('/', { waitUntil: 'networkidle' })
  await expect(page.locator('.app-shell')).toBeVisible()
  await assertMobileShell(page)

  await expect(page.locator('.brand-trophy')).toBeVisible()
  await expect(page.locator('.brand-name')).toHaveText('Shiva')
  await expect(page.locator('.brand-subtitle')).toHaveText('FANTASY FOOTBALL INTELLIGENCE')
  await expect(page.getByRole('button', { name: 'Shiva', exact: true })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Scores', exact: true })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Coach', exact: true })).toHaveCount(0)

  await assertCoachHome(page)
  await page.screenshot({ path: 'test-results/mobile-home.png', fullPage: true })

  for (const label of pages) {
    const button = page.getByRole('button', { name: label, exact: true })
    await expect(button).toBeVisible()
    await button.click()
    await page.waitForTimeout(350)
    await assertMobileShell(page)
    if (label === 'Scores') await assertScoresPage(page)
    await page.screenshot({ path: `test-results/mobile-${label.toLowerCase()}.png`, fullPage: true })
  }

  expect(pageErrors, `Page errors: ${pageErrors.join(' | ')}`).toEqual([])
  expect(consoleErrors, `Console errors: ${consoleErrors.join(' | ')}`).toEqual([])
})

test('launch never exposes a white screen on mobile', async ({ page }) => {
  await page.goto('/', { waitUntil: 'domcontentloaded' })
  const colors = await page.evaluate(async () => {
    const seen: string[] = []
    for (let i = 0; i < 12; i += 1) {
      seen.push(getComputedStyle(document.body).backgroundColor)
      await new Promise((resolve) => setTimeout(resolve, 50))
    }
    return seen
  })
  expect(colors).not.toContain('rgb(255, 255, 255)')
})
