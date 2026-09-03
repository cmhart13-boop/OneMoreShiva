import { expect, test } from '@playwright/test'

const pages = ['Home', 'Draft', 'Guide', 'Coach'] as const

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

test('mobile app renders cleanly and navigation stays attached to phone bottom', async ({ page }) => {
  const consoleErrors: string[] = []
  const pageErrors: string[] = []

  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text())
  })
  page.on('pageerror', (err) => pageErrors.push(err.message))

  await page.goto('/', { waitUntil: 'networkidle' })
  await expect(page.locator('.app-shell')).toBeVisible()
  await assertMobileShell(page)
  await page.screenshot({ path: 'test-results/mobile-home.png', fullPage: true })

  for (const label of pages.slice(1)) {
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
