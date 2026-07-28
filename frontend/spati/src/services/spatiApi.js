/**
 * Cliente API SPATI — /api/public/spati/*
 */
import site from '@/site.config.js'

const RENDER_API = site.api?.defaultPublicBase || 'https://metgo-api.onrender.com/api'
const TIMEOUT_MS = 90000

function resolveBaseURL() {
  const fromEnv = import.meta.env.VITE_METGO_API || import.meta.env.VITE_API_BASE
  if (fromEnv) return String(fromEnv).replace(/\/$/, '')
  if (typeof window !== 'undefined') {
    const host = window.location.hostname
    if (host.includes('netlify.app') || host.includes('pages.dev')) return RENDER_API
  }
  return site.api?.localBase || RENDER_API
}

async function fetchJson(path, { method = 'GET', body, timeout = TIMEOUT_MS } = {}) {
  const base = resolveBaseURL()
  const ctrl = new AbortController()
  const t = setTimeout(() => ctrl.abort(), timeout)
  try {
    const res = await fetch(`${base}${path}`, {
      method,
      signal: ctrl.signal,
      headers: {
        Accept: 'application/json',
        ...(body ? { 'Content-Type': 'application/json' } : {}),
      },
      body: body ? JSON.stringify(body) : undefined,
    })
    if (!res.ok) {
      let detalle = ''
      try {
        const j = await res.json()
        if (j?.error) detalle = `: ${j.error}`
        if (j?.detalle) detalle += ` (${j.detalle})`
      } catch {
        /* ignore */
      }
      const err = new Error(`HTTP ${res.status}${detalle}`)
      err.status = res.status
      throw err
    }
    return await res.json()
  } finally {
    clearTimeout(t)
  }
}

export async function fetchSpatiSitios({ altaMontana = true } = {}) {
  const q = altaMontana ? '?alta_montana=1' : ''
  const data = await fetchJson(`/public/spati/sitios${q}`)
  return data.sitios || []
}

export async function fetchSpatiPronostico(sitioId) {
  const id = encodeURIComponent(sitioId || site.spatiDefaultSitio)
  return fetchJson(`/public/spati/${id}/pronostico`)
}

export async function fetchSpatiPronosticoConDron(sitioId, perfilDron, tauHoras = 6) {
  const id = encodeURIComponent(sitioId || site.spatiDefaultSitio)
  return fetchJson(`/public/spati/${id}/pronostico`, {
    method: 'POST',
    body: { perfil_dron: perfilDron, tau_horas: tauHoras },
  })
}

export function getApiBase() {
  return resolveBaseURL()
}
