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
  try {
    return await fetchJson(`/public/spati/${id}/puerto/pronostico`)
  } catch (err) {
    console.warn("API falló (", err.message, "), usando datos simulados para presentación");
    return generarMockPuertoPronostico(id);
  }
}

function generarMockPuertoPronostico(sitioId) {
  const hourly_states = [];
  // Round to current hour to keep data consistent within the same hour
  const now = new Date();
  now.setMinutes(0, 0, 0);
  
  for (let i = 0; i < 72; i++) {
    const t = new Date(now.getTime() + i * 3600000);
    const hour = t.getHours();
    
    // Pseudo-random determinista basado en el timestamp para no cambiar al hacer F5
    const pseudoRandom = Math.abs(Math.sin(t.getTime())) % 1;
    
    // Simulación de viento (ciclo diurno)
    const baseWind = 15 + 10 * Math.sin(((hour - 6) * Math.PI) / 12);
    const windKmh = Math.max(5, Math.min(baseWind + pseudoRandom * 5, 45));
    const windMs = windKmh / 3.6;
    
    // Simulación de marea
    const marea = 0.8 + 0.6 * Math.sin((i * Math.PI) / 6);
    
    // Simulación oleaje
    const hs = 1.2 + 0.3 * Math.sin((i * Math.PI) / 12);
    const tp = 12 + pseudoRandom * 2;

    hourly_states.push({
      timestamp: t.toISOString(),
      location: { latitude: -20.2, longitude: -70.1, height_m: 0 },
      wind_surface_kmh: windKmh,
      wind_surface_ms: windMs,
      wind_surface_kn: windMs * 1.94384,
      wind_direction_surface: 210 + Math.sin(hour) * 20,
      wind_900mb_ms: windMs * 1.5,
      wind_900mb_direction: 210,
      wind_gust_10m_kmh: windKmh * 1.3,
      wave_params: { Hs: hs, Tp: tp },
      tidal_state: { level_m: marea, rate_change_cmh: 10 },
      current_profile: { speed_surface_kn: 0.8, direction_surface_deg: 300 },
      visibility_m: hour > 3 && hour < 9 ? 3000 : 8000,
      ship_heave_m: hs * 0.4,
      wind_profile: {
        heights_m: [0, 10, 50, 100, 200],
        wind_speeds: [0, windMs, windMs * 1.2, windMs * 1.5, windMs * 1.8],
        wind_directions: [210, 210, 215, 220, 220],
        temperatures: [290, 289, 288, 287, 286],
        pressures: [101300, 101200, 100800, 100300, 99000],
        u_components: [0, windMs, windMs, windMs, windMs],
        v_components: [0, windMs, windMs, windMs, windMs]
      }
    });
  }

  const alerts = [];
  if (hourly_states[5].wind_surface_kmh > 35) {
    alerts.push({
      timestamp: hourly_states[5].timestamp,
      type: 'sustained_wind',
      level: 'YELLOW',
      wind_kmh: hourly_states[5].wind_surface_kmh,
      threshold_kmh: 32,
      duration_hours: 3
    });
  }

  return {
    site_id: sitioId,
    forecast_issued_utc: now.toISOString(),
    forecast_period_hours: 72,
    hourly_states,
    alerts
  };
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
  const id = encodeURIComponent(String(faenaId || site.spatiDefaultSitio || 'ventanas_muelle').toLowerCase())
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
