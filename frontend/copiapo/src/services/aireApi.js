/**
 * Cliente público metgo-api — sitio Copiapó (E7).
 * Endpoints /api/public/aire/* y /api/public/estaciones
 */
import site from '@/site.config.js'

const RENDER_API = site.api?.defaultPublicBase || 'https://metgo-api.onrender.com/api'
const SITIO = site.sitio
const TIMEOUT_MS = 60000

/** Normaliza id de estación (API a veces solo manda `id`, no `slug`). */
export function estacionSlug(raw) {
  if (raw == null) return null
  if (typeof raw === 'object') {
    const s = raw.slug ?? raw.estacion_id ?? raw.id
    return estacionSlug(s)
  }
  const id = String(raw).trim()
  if (!id || id === 'undefined' || id === 'null') return null
  return id
}

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
  const id = estacionSlug(estacionId)
  if (!id) {
    throw new Error('estacion_id_requerido')
  }
  return fetchJson(`/public/aire/${encodeURIComponent(id)}`)
}

export async function fetchAirePronostico(estacionId, dias = 5) {
  const id = estacionSlug(estacionId)
  if (!id) {
    throw new Error('estacion_id_requerido')
  }
  return fetchJson(
    `/public/aire/${encodeURIComponent(id)}/pronostico?dias=${dias}`
  )
}

export async function fetchAireHistorico(estacionId, dias = 7) {
  const id = estacionSlug(estacionId)
  if (!id) {
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
  const id = estacionSlug(estacionId)
  if (!id) {
    throw new Error('estacion_id_requerido')
  }
  return fetchJson(
    `/public/aire/${encodeURIComponent(id)}/dispersion?horas=${horas}`
  )
}

export async function fetchDispersionDiaria(estacionId, dias = 7) {
  const id = estacionSlug(estacionId)
  if (!id) {
    throw new Error('estacion_id_requerido')
  }
  return fetchJson(
    `/public/aire/${encodeURIComponent(id)}/dispersion/diaria?dias=${dias}`
  )
}

export async function fetchDispersionProyeccion(estacionId) {
  const id = estacionSlug(estacionId)
  if (!id) {
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

/** METGO Airshed Modeler — campo concentración + viento (proxy AERMOD). */
export async function fetchAirshedModel({ sitio = SITIO, nx = 28, ny = 28, frames = 6 } = {}) {
  const q = new URLSearchParams({
    sitio,
    nx: String(nx),
    ny: String(ny),
    frames: String(frames),
  })
  return fetchJson(`/public/aire/modelo/airshed?${q}`)
}

export async function fetchSounding(estacionId, horas = 24) {
  const id = estacionSlug(estacionId)
  if (!id) throw new Error('estacion_id_requerido')
  return fetchJson(`/public/aire/${encodeURIComponent(id)}/sounding?horas=${horas}`)
}

export async function fetchPaipotePaquete(forzar = false) {
  const q = forzar ? '?forzar=1' : ''
  return fetchJson(`/public/operaciones/paipote/paquete${q}`)
}

export async function fetchPaipoteVentilacion(horizonte = 'horaria') {
  return fetchJson(
    `/public/operaciones/paipote/ventilacion?horizonte=${encodeURIComponent(horizonte)}`
  )
}

export async function fetchOlasCalor({ estacion = 'paipote', estacionAno = 'otono', anios = 7 } = {}) {
  const q = new URLSearchParams({
    estacion,
    estacion_ano: estacionAno,
    anios: String(anios),
  })
  return fetchJson(`/public/operaciones/paipote/olas-calor?${q}`)
}

export async function fetchSateliteAtmos({ estacion = 'paipote', bandas = 'vis,ir,wv' } = {}) {
  const q = new URLSearchParams({ estacion, bandas })
  return fetchJson(`/public/operaciones/paipote/satelite?${q}`)
}

export async function fetchConjuntoCatalogo() {
  return fetchJson('/public/operaciones/conjunto/catalogo')
}

export async function fetchConjuntoSeries(estacionId, { horas = 72, series = [] } = {}) {
  const id = estacionSlug(estacionId)
  if (!id) throw new Error('estacion_id_requerido')
  const q = new URLSearchParams({ horas: String(horas) })
  if (series?.length) q.set('series', series.join(','))
  return fetchJson(`/public/operaciones/${encodeURIComponent(id)}/conjunto?${q}`)
}

export function getApiBase() {
  return resolveBaseURL()
}

export { SITIO }
