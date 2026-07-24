import { defineConfig } from '@playwright/test'

const API = process.env.METGO_API_BASE || 'https://metgo-api.onrender.com'

export default defineConfig({
  testDir: '.',
  timeout: 90_000,
  retries: 1,
  use: {
    baseURL: API,
  },
  projects: [{ name: 'api-smoke', testMatch: /api-smoke\.spec\.ts/ }],
})
