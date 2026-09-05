import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/mobile',
  timeout: 45_000,
  expect: { timeout: 10_000 },
  retries: 1,
  reporter: [['list'], ['html', { outputFolder: 'playwright-report', open: 'never' }]],
  webServer: process.env.SHIVA_BASE_URL ? undefined : {
    command: 'npx next dev -H 127.0.0.1',
    url: 'http://127.0.0.1:3000',
    reuseExistingServer: true,
    timeout: 120_000,
  },
  use: {
    baseURL: process.env.SHIVA_BASE_URL || 'http://127.0.0.1:3000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'iPhone 15 Pro',
      use: {
        ...devices['iPhone 15 Pro'],
        browserName: 'chromium',
        viewport: { width: 393, height: 852 },
      },
    },
    {
      name: 'Desktop Chrome',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1440, height: 1000 },
      },
    },
  ],
})
