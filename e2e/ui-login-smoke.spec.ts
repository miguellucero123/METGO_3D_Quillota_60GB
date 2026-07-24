import { test, expect } from '@playwright/test'

/**
 * Smoke E10 UI — login Quillota.
 * Requiere METGO_UI_BASE (ej. http://127.0.0.1:5173 o URL Netlify).
 * Si no está definido, los tests se saltan (API-only CI sigue con api-smoke).
 */
const UI = process.env.METGO_UI_BASE || ''

test.describe('METGO UI login smoke', () => {
  test.skip(!UI, 'Define METGO_UI_BASE para smoke UI')

  test('login page renders', async ({ page }) => {
    await page.goto(`${UI.replace(/\/$/, '')}/login`)
    await expect(page.getByRole('heading', { name: /METGO/i })).toBeVisible()
    await expect(page.locator('input[autocomplete="username"]')).toBeVisible()
  })

  test('login demo admin', async ({ page }) => {
    test.setTimeout(120_000)
    await page.goto(`${UI.replace(/\/$/, '')}/login`)
    await page.locator('input[autocomplete="username"]').fill('admin')
    await page.locator('input[autocomplete="current-password"]').fill('admin123')
    await page.getByRole('button', { name: /Entrar|Sign in|Iniciar|Signing/i }).click()
    await expect(page).not.toHaveURL(/\/login/, { timeout: 90_000 })
  })
})
