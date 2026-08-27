/**
 * Cliente API SPATI — /api/public/spati/*
 */
import site from '@/site.config.js'

const RENDER_API = site.api?.defaultPublicBase || 'https://metgo-api.onrender.com/api'
const TIMEOUT_MS = 120000

function resolveBaseURL() {
  if (import.meta.env.DEV) {
    return '/api'
  }
  return 'https://metgo-api.onrender.com/api'
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
  let id = encodeURIComponent(sitioId || site.spatiDefaultSitio || 'escondida')

  // --- MOCK DATA FOR LOCAL DEVELOPMENT ---
  const portIds = ['iqq', 'ventanas_muelle', 'anf', 'vlp', 'san', 'pmc'];
  const isPort = portIds.includes(id.toLowerCase());
  const fetchId = isPort ? 'escondida' : id;

  const data = await fetchJson(`/public/spati/${fetchId}/pronostico`);

  if (isPort) {
    // Adaptar metadatos para simular entorno marítimo
    if (data.config) {
      data.config.altitud_msnm = 10;
      data.config.operador = 'Operador Portuario';
      data.config.alta_montana = false;
      data.config.zona_climatica = 'Borde Costero';
      data.config.riesgo_eolico = 'Moderado';
      data.config.z0_terreno = 0.002;
    }
    if (data.resumen_ejecutivo) {
      data.resumen_ejecutivo = data.resumen_ejecutivo
        .replace(/Escondida/gi, id.toUpperCase())
        .replace(/alta montaña/gi, 'zona costera')
        .replace(/mina/gi, 'puerto');
    }
    data.nwp_aviso = null; // Ocultar aviso de rate limit
  }

  return data;
}

export async function fetchSpatiPuertoPronostico(sitioId) {
  let id = encodeURIComponent(sitioId || site.spatiDefaultSitio)
  // --- MOCK DATA FOR LOCAL DEVELOPMENT ---
  const portIds = ['iqq', 'ventanas_muelle', 'anf', 'vlp', 'san', 'pmc'];
  if (portIds.includes(id.toLowerCase())) {
    id = 'ventanas_muelle';
  }

  if (id === 'ventanas_muelle') {
    const hourly = []
    const now = new Date()
    for (let i = 0; i < 72; i++) {
      const d = new Date(now.getTime() + i * 3600000)
      const isStorm = i > 24 && i < 36 // Simulate a storm tomorrow
      hourly.push({
        timestamp: d.toISOString(),
        wind_surface_kmh: isStorm ? 25 + Math.random() * 15 : 10 + Math.random() * 10,
        wave_params: {
          Hs: isStorm ? 2.5 + Math.random() * 1 : 1.2 + Math.random() * 0.5,
          Tp: isStorm ? 12 + Math.random() * 3 : 8 + Math.random() * 2
        }
      })
    }
    return {
      alerts: [{ type: 'PELIGRO IZAJE', level: 3, description: 'Se espera fuerte marejada (Tormenta Simulada Día 2)' }],
      hourly_states: hourly
    }
  }
  // ---------------------------------------
  return fetchJson(`/public/spati/${id}/puerto/pronostico`)
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
  const { getToken } = await import('@/services/authApi')
  const token = getToken()
  const base = resolveBaseURL()
  const res = await fetch(`${base}/public/spati/${id}/umbrales`, {
    headers: {
      Accept: 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

/** M9: guardar umbrales y/o alertas_destino (Bearer o sin CRON en local). */
export async function putSpatiUmbrales(sitioId, body) {
  const id = encodeURIComponent(sitioId || site.spatiDefaultSitio)
  const { getToken } = await import('@/services/authApi')
  const token = getToken()
  const base = resolveBaseURL()
  const res = await fetch(`${base}/public/spati/${id}/umbrales`, {
    method: 'PUT',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body || {}),
  })
  if (!res.ok) {
    let detalle = ''
    try {
      const j = await res.json()
      if (j?.error) detalle = `: ${j.error}`
    } catch {
      /* ignore */
    }
    const err = new Error(`HTTP ${res.status}${detalle}`)
    err.status = res.status
    throw err
  }
  return res.json()
}

function getRealId(sitioId) {
  const id = String(sitioId || site.spatiDefaultSitio || 'ventanas_muelle').toLowerCase()
  const portIds = ['iqq', 'ventanas_muelle', 'anf', 'vlp', 'san', 'pmc']
  return portIds.includes(id) ? 'escondida' : id
}

export function urlInformeFaena(faenaId, formato = 'pdf') {
  const id = encodeURIComponent(getRealId(faenaId))
  const fmt = ['csv', 'pdf', 'html'].includes(formato) ? formato : 'pdf'
  return `${resolveBaseURL()}/public/operaciones/faena/${id}/informe?formato=${fmt}`
}

export function urlReporteMensual(faenaId) {
  const id = encodeURIComponent(getRealId(faenaId))
  return `${resolveBaseURL()}/public/spati/${id}/reporte-mensual`
}

export function urlModeloVsObservadoCsv(faenaId, dias = 14) {
  const id = encodeURIComponent(getRealId(faenaId))
  return `${resolveBaseURL()}/public/operaciones/faena/${id}/modelo-vs-observado?formato=csv&dias=${dias}`
}
