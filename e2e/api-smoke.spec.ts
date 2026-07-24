import { test, expect } from '@playwright/test'

/**
 * Smoke E10 — no requiere SPA desplegada (Netlify créditos bajos).
 * Valida API multi-sitio + health SLO.
 */
test.describe('METGO API smoke E10', () => {
  test('health global', async ({ request }) => {
    const res = await request.get('/api/health')
    expect(res.ok()).toBeTruthy()
    const body = await res.json()
    expect(body.fase).toBe('10')
  })

  test('health sitios', async ({ request }) => {
    const res = await request.get('/api/health/sitios')
    expect(res.ok()).toBeTruthy()
    const body = await res.json()
    expect(body.fase).toBe('E10')
    const slugs = (body.sitios || []).map((s: { sitio: string }) => s.sitio)
    expect(slugs).toContain('quillota')
    expect(slugs).toContain('copiapo')
  })

  test('metrics prometheus', async ({ request }) => {
    const res = await request.get('/api/metrics')
    expect(res.ok()).toBeTruthy()
    const text = await res.text()
    expect(text).toContain('metgo_uptime_seconds')
  })

  test('public sitios', async ({ request }) => {
    const res = await request.get('/api/public/sitios')
    expect(res.ok()).toBeTruthy()
    const list = await res.json()
    expect(Array.isArray(list)).toBeTruthy()
  })
})
