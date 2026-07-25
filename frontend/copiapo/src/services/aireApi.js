/**
 * Cliente público metgo-api — sitio Copiapó (E7).
 * Endpoints /api/public/aire/* y /api/public/estaciones
 */
import site from '@/site.config.js'

const RENDER_API = site.api?.defaultPublicBase || 'https://metgo-api.onrender.com/api'
const SITIO = site.sitio
const TIMEOUT_MS = 60000

function resolveBaseURL() {
  const fromEnv = import.meta.env.VITE_METGO_API || import.meta.env.VITE_API_BASE
  if (fromEnv) return String(fromEnv).replace(/\/$/, '')
  if (typeof window !== 'undefined') {
    const host = window.location.hostname
    if (host.includes('netlify.app') || host.includes('pages.dev')) {
      return RENDER_API
    }
  }
  return site.api?.localBase || RENDER_API
}

async function fetchJson(path, { timeout = TIMEOUT_MS } = {}) {
  const base = resolveBaseURL()
  const ctrl = new AbortController()
  const t = setTimeout(() => ctrl.abort(), timeout)
  try {
    const res = await fetch(`${base}${path}`, {
      signal: ctrl.signal,
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = new Error(`HTTP ${res.status}`)
      err.status = res.status
      throw err
    }
    return await res.json()
  } finally {
    clearTimeout(t)
  }
}

export async function wakeApi() {
  try {
    await fetchJson('/health', { timeout: 25000 })
    return true
  } catch {
    return false
  }
}

export async function fetchEstacionesSitio() {
  const data = await fetchJson(`/public/estaciones?sitio=${encodeURIComponent(SITIO)}`)
  if (Array.isArray(data)) return data
  if (Array.isArray(data?.estaciones)) return data.estaciones
  return []
}

export async function fetchAireActual(estacionId) {
  const id = String(estacionId || '').trim()
  if (!id || id === 'undefined') {
    throw new Error('estacion_id_requerido')
  }
  return fetchJson(`/public/aire/${encodeURIComponent(id)}`)
}

export async function fetchAirePronostico(estacionId, dias = 5) {
  const id = String(estacionId || '').trim()
  if (!id || id === 'undefined') {
    throw new Error('estacion_id_requerido')
  }
  return fetchJson(
    `/public/aire/${encodeURIComponent(id)}/pronostico?dias=${dias}`
  )
}

export async function fetchAireHistorico(estacionId, dias = 7) {
  const id = String(estacionId || '').trim()
  if (!id || id === 'undefined') {
    throw new Error('estacion_id_requerido')
  }
  return fetchJson(
    `/public/aire/${encodeURIComponent(id)}/historico?dias=${dias}`
  )
}

export async function fetchAireAlertas(sitio = SITIO) {
  return fetchJson(`/public/aire/alertas?sitio=${encodeURIComponent(sitio)}`)
}

export async function fetchDispersionHoraria(estacionId, horas = 72) {
  const id = String(estacionId || '').trim()
  if (!id || id === 'undefined') {
    throw new Error('estacion_id_requerido')
  }
  return fetchJson(
    `/public/aire/${encodeURIComponent(id)}/dispersion?horas=${horas}`
  )
}

export async function fetchDispersionDiaria(estacionId, dias = 7) {
  const id = String(estacionId || '').trim()
  if (!id || id === 'undefined') {
    throw new Error('estacion_id_requerido')
  }
  return fetchJson(
    `/public/aire/${encodeURIComponent(id)}/dispersion/diaria?dias=${dias}`
  )
}

export async function fetchDispersionProyeccion(estacionId) {
  const id = String(estacionId || '').trim()
  if (!id || id === 'undefined') {
    throw new Error('estacion_id_requerido')
  }
  return fetchJson(
    `/public/aire/${encodeURIComponent(id)}/dispersion/proyeccion`
  )
}

export async function fetchDispersionAlertas(horizonte = 'horaria', sitio = SITIO) {
  return fetchJson(
    `/public/aire/dispersion/alertas?sitio=${encodeURIComponent(sitio)}&horizonte=${horizonte}`
  )
}

export function getApiBase() {
  return resolveBaseURL()
}

export { SITIO }
