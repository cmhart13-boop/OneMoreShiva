import { expect, test } from '@playwright/test'

const pages = ['Draft', 'Guide', 'Coach'] as const

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

async function assertHomepageAcceptance(page: any) {
  await expect(page.locator('.countdown')).toHaveCount(0)

  await expect(page.locator('.brand-trophy')).toBeVisible()
  await expect(page.locator('.brand-name')).toHaveText('Shiva')
  await expect(page.locator('.brand-subtitle')).toHaveText('FANTASY FOOTBALL INTELLIGENCE')

  const topTrophyStyle = await page.locator('.brand-trophy').evaluate((el: HTMLElement) => {
    const style = getComputedStyle(el)
    return { background: style.backgroundColor, border: style.borderStyle, boxShadow: style.boxShadow }
  })
  expect(topTrophyStyle.background).toBe('rgba(0, 0, 0, 0)')
  expect(topTrophyStyle.border).toBe('none')
  expect(topTrophyStyle.boxShadow).toBe('none')

  const shivaNav = page.getByRole('button', { name: 'Shiva', exact: true })
  await expect(shivaNav).toBeVisible()
  await expect(shivaNav.locator('.nav-trophy')).toBeVisible()
  await expect(shivaNav.locator('span').last()).toHaveText('Shiva')
  const navTrophyStyle = await shivaNav.locator('.nav-trophy').evaluate((el: HTMLElement) => {
    const style = getComputedStyle(el)
    return { background: style.backgroundColor, border: style.borderStyle, boxShadow: style.boxShadow }
  })
  expect(navTrophyStyle.background).toBe('rgba(0, 0, 0, 0)')
  expect(navTrophyStyle.border).toBe('none')
  expect(navTrophyStyle.boxShadow).toBe('none')
  const shivaButtonBg = await shivaNav.evaluate((el: HTMLElement) => getComputedStyle(el).backgroundColor)
  expect(shivaButtonBg).toBe('rgba(0, 0, 0, 0)')

  await expect(page.getByRole('heading', { level: 1, name: 'Shiva Edge', exact: true })).toBeVisible()
  await expect(page.getByText('The Shiva Edge', { exact: true })).toHaveCount(0)
  await expect(page.getByText('CURRENT CONTEXT', { exact: true })).toHaveCount(0)
  await expect(page.getByText('LIVE ESPN', { exact: true })).toHaveCount(0)
  await expect(page.getByRole('heading', { level: 2, name: 'Shiva Blast', exact: true })).toBeVisible()

  const edgeTitles = page.locator('.edge-title')
  await expect(edgeTitles).toHaveCount(2)
  await expect(edgeTitles.nth(0)).toHaveText('Raise the Floor')
  await expect(edgeTitles.nth(1)).toHaveText('Keep the Ceiling')

  const floorSizes = await page.locator('.edge-panel').nth(0).evaluate((card: HTMLElement) => {
    const title = card.querySelector('.edge-title') as HTMLElement
    const subtitle = card.querySelector('.edge-subtitle') as HTMLElement
    const metric = card.querySelector('.metric-row b') as HTMLElement
    return {
      title: parseFloat(getComputedStyle(title).fontSize),
      subtitle: parseFloat(getComputedStyle(subtitle).fontSize),
      metric: parseFloat(getComputedStyle(metric).fontSize),
    }
  })
  expect(floorSizes.title).toBeGreaterThan(floorSizes.subtitle)
  expect(floorSizes.metric).toBeLessThanOrEqual(floorSizes.title)

  const blastCards = page.locator('.blast-list .blast-card')
  await expect(blastCards).toHaveCount(4)
  await expect(blastCards.locator('img')).toHaveCount(4)

  const newsResponse = await page.request.get('/api/news')
  expect(newsResponse.ok()).toBeTruthy()
  const newsPayload = await newsResponse.json()
  const expectedHeadlines = newsPayload.articles.slice(0, 4).map((article: any) => article.headline)
  const renderedHeadlines = await blastCards.locator('.blast-copy > b').allTextContents()
  expect(renderedHeadlines).toEqual(expectedHeadlines)
}

test('approved Shiva homepage changes and four-page mobile shell are correct', async ({ page }) => {
  const consoleErrors: string[] = []
  const pageErrors: string[] = []

  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text())
  })
  page.on('pageerror', (err) => pageErrors.push(err.message))

  await page.goto('/', { waitUntil: 'networkidle' })
  await expect(page.locator('.app-shell')).toBeVisible()
  await assertMobileShell(page)
  await assertHomepageAcceptance(page)
  await page.screenshot({ path: 'test-results/mobile-home.png', fullPage: true })

  for (const label of pages) {
    const button = page.getByRole('button', { name: label, exact: true })
    await expect(button).toBeVisible()
    await button.click()
    await page.waitForTimeout(350)
    await assertMobileShell(page)
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
