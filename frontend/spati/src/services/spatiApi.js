/**
 * Cliente API SPATI — /api/public/spati/*
 */
import site from '@/site.config.js'

const RENDER_API = site.api?.defaultPublicBase || 'https://metgo-api.onrender.com/api'
const TIMEOUT_MS = 120000

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
  const t = setTimeout(() => ctrl.abort('timeout'), timeout)
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
        if (j?.sugerencia) detalle += ` — ${j.sugerencia}`
      } catch {
        /* ignore */
      }
      const err = new Error(`HTTP ${res.status}${detalle}`)
      err.status = res.status
      throw err
    }
    return await res.json()
  } catch (e) {
    if (e?.name === 'AbortError' || e?.message === 'timeout' || String(e).includes('aborted')) {
      const err = new Error(
        'La API tardó demasiado (Open-Meteo o Render en frío). Espere unos segundos y reintente.',
      )
      err.code = 'TIMEOUT'
      throw err
    }
    throw e
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

/** Catálogo multi-faena (operaciones M1/M2). */
export async function fetchFaenas({ incluirIzaje = true } = {}) {
  const q = incluirIzaje ? '' : '?incluir_izaje=0'
  const data = await fetchJson(`/public/operaciones/faenas${q}`)
  return data.faenas || []
}

export async function fetchPaqueteAmbiental(faenaId, { horas = 72 } = {}) {
  const id = encodeURIComponent(faenaId || site.spatiDefaultSitio)
  return fetchJson(`/public/operaciones/faena/${id}/paquete-ambiental?horas=${horas}`)
}

export async function fetchEstacionesArea(faenaId) {
  const id = encodeURIComponent(faenaId || site.spatiDefaultSitio)
  return fetchJson(`/public/operaciones/faena/${id}/estaciones-area`)
}

export async function fetchModeloVsObservado(faenaId, { dias = 14 } = {}) {
  const id = encodeURIComponent(faenaId || site.spatiDefaultSitio)
  return fetchJson(`/public/operaciones/faena/${id}/modelo-vs-observado?dias=${dias}`)
}

export async function fetchObservadoStatus(faenaId, { dias = 14 } = {}) {
  const id = encodeURIComponent(faenaId || site.spatiDefaultSitio)
  return fetchJson(`/public/operaciones/faena/${id}/observado-status?dias=${dias}`)
}

export async function fetchSpatiUmbrales(sitioId) {
  const id = encodeURIComponent(sitioId || site.spatiDefaultSitio)
  return fetchJson(`/public/spati/${id}/umbrales`)
}

export function urlInformeFaena(faenaId, formato = 'pdf') {
  const id = encodeURIComponent(faenaId || site.spatiDefaultSitio)
  const fmt = ['csv', 'pdf', 'html'].includes(formato) ? formato : 'pdf'
  return `${resolveBaseURL()}/public/operaciones/faena/${id}/informe?formato=${fmt}`
}

export function urlModeloVsObservadoCsv(faenaId, dias = 14) {
  const id = encodeURIComponent(faenaId || site.spatiDefaultSitio)
  return `${resolveBaseURL()}/public/operaciones/faena/${id}/modelo-vs-observado?formato=csv&dias=${dias}`
}
