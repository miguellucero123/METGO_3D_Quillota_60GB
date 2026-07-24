import { defineConfig } from '@playwright/test'

const API = process.env.METGO_API_BASE || 'https://metgo-api.onrender.com'
const UI = process.env.METGO_UI_BASE || ''

export default defineConfig({
  testDir: '.',
  timeout: 90_000,
  retries: 1,
  use: {
    baseURL: API,
  },
  projects: [
    { name: 'api-smoke', testMatch: /api-smoke\.spec\.ts/ },
    {
      name: 'ui-login-smoke',
      testMatch: /ui-login-smoke\.spec\.ts/,
      use: { baseURL: UI || 'http://127.0.0.1:5173' },
    },
  ],
})
