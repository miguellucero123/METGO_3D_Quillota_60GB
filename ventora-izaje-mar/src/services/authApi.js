/**
 * Auth JWT metgo-api (E9) — sitio Mantos Blancos.
 */
import site from '@/site.config.js'

const RENDER_API = site.api?.defaultPublicBase || 'https://metgo-api.onrender.com/api'
const TOKEN_KEY = `${site.storagePrefix || 'metgo'}_access_token`
const USER_KEY = `${site.storagePrefix || 'metgo'}_user`
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

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function getStoredUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || 'null')
  } catch {
    return null
  }
}

export function setSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

async function request(path, { method = 'GET', body, auth = false, timeout = TIMEOUT_MS } = {}) {
  const ctrl = new AbortController()
  const t = setTimeout(() => ctrl.abort(), timeout)
  const headers = { Accept: 'application/json' }
  if (body != null) headers['Content-Type'] = 'application/json'
  if (auth) {
    const token = getToken()
    if (token) headers.Authorization = `Bearer ${token}`
  }
  try {
    const res = await fetch(`${resolveBaseURL()}${path}`, {
      method,
      headers,
      body: body != null ? JSON.stringify(body) : undefined,
      signal: ctrl.signal,
    })
    let data = await res.json().catch(() => ({}))
    
    // Rewrite escondida -> ventanas_muelle
    const dataStr = JSON.stringify(data).replace(/escondida/g, 'ventanas_muelle').replace(/Escondida/g, 'ventanas_muelle')
    data = JSON.parse(dataStr)

    if (!res.ok) {
      const err = new Error(data.error || `HTTP ${res.status}`)
      err.status = res.status
      err.data = data
      err.code = data.code
      // JWT inválido/expirado o sesión reemplazada
      if (res.status === 401 && auth) {
        clearSession()
        if (typeof window !== 'undefined' && data.code === 'session_replaced') {
          try {
            sessionStorage.setItem(
              'metgo_session_msg',
              'Su sesión se cerró porque inició sesión en otro dispositivo.',
            )
          } catch {
            /* ignore */
          }
        }
      }
      throw err
    }
    return data
  } finally {
    clearTimeout(t)
  }
}

export async function login(username, password, { faena, sitio } = {}) {
  // --- MOCK BYPASS FOR LOCAL DEVELOPMENT ---
  if (username === 'miguel.lucero@metgo3d.com') {
    return {
      access_token: 'mock-jwt-token-12345',
      user: {
        id: 1,
        email: username,
        username: 'Miguel Lucero',
        role: 'admin',
        sitio: sitio || SITIO,
        faenas: [{ slug: faena || 'ventanas_muelle' }]
      }
    }
  }
  // -----------------------------------------

  return request('/auth/login', {
    method: 'POST',
    body: {
      username,
      password,
      sitio: sitio || SITIO,
      ...(faena ? { faena } : {}),
    },
  })
}

export async function fetchMe() {
  const token = getToken()
  if (token === 'mock-jwt-token-12345') {
    return {
      id: 1,
      email: 'miguel.lucero@metgo3d.com',
      username: 'Miguel Lucero',
      role: 'admin',
      sitio: SITIO,
      faenas: [{ slug: 'ventanas_muelle' }]
    }
  }
  return request('/auth/me', { auth: true })
}

export async function wakeApi() {
  try {
    await request('/health', { timeout: 25000 })
    return true
  } catch {
    return false
  }
}

export async function validateRegistro(body) {
  try {
    return await request('/auth/validate-registro', { method: 'POST', body })
  } catch (e) {
    if (e.data && typeof e.data.ok === 'boolean') return e.data
    throw e
  }
}

export async function registerV2(body) {
  return request('/auth/register-v2', { method: 'POST', body })
}

export async function reenviarVerificacion(body) {
  return request('/auth/reenviar-verificacion', { method: 'POST', body })
}

export async function fetchAccess({ sitio, faena, tab } = {}) {
  const token = getToken()
  if (token === 'mock-jwt-token-12345') {
    return { tab_allowed: true }
  }
  const q = new URLSearchParams()
  if (sitio) q.set('sitio', sitio)
  if (faena) q.set('faena', faena)
  if (tab) q.set('tab', tab)
  const qs = q.toString()
  try {
    return await request(`/auth/access${qs ? `?${qs}` : ''}`, { auth: true })
  } catch (e) {
    if (e.status === 403 && e.data && typeof e.data === 'object' && e.data.tabs) {
      return { ...e.data, tab_allowed: false }
    }
    throw e
  }
}

export async function fetchPlanes(sitio = 'spati', faena) {
  const q = new URLSearchParams({ sitio })
  if (faena) q.set('faena', faena)
  return request(`/public/planes?${q}`)
}

export async function fetchFaenaReglas(faena) {
  return request(`/public/faenas/${encodeURIComponent(faena)}/reglas`)
}

export async function fetchCuenta(faena) {
  const token = getToken()
  if (token === 'mock-jwt-token-12345') {
    return {
      usuario: {
        email: 'miguel.lucero@metgo3d.com',
        status: 'active',
        email_verified: true,
        sitio: SITIO,
        faena: faena || 'ventanas_muelle'
      },
      suscripcion: {
        plan_code: 'pro',
        status: 'active',
        current_period_end: '2099-12-31'
      },
      access: {
        tabs: {
          resumen: true,
          meteo: true,
          mareas: true,
          experto: true,
          informes: true
        }
      },
      planes: {
        planes: [
          { plan_code: 'pro', nombre: 'Pro', precio_mensual_usd: 100, descripcion: 'Acceso completo' },
          { plan_code: 'enterprise', nombre: 'Enterprise', precio_mensual_usd: 500, descripcion: 'Multifaena' }
        ]
      }
    }
  }
  const q = faena ? `?faena=${encodeURIComponent(faena)}` : ''
  return request(`/auth/cuenta${q}`, { auth: true })
}

export async function fetchMisFaenas() {
  const token = getToken()
  if (token === 'mock-jwt-token-12345') {
    return { faenas: [{ slug: 'ventanas_muelle' }] }
  }
  return request('/auth/mis-faenas', { auth: true })
}

/** M10 — board ops multi-faena (admin / multi_faena / ≥2 faenas). */
export async function fetchOpsBoard({ refresh = false } = {}) {
  const q = refresh ? '?refresh=1' : ''
  // Board multi-faena puede regenerar Open-Meteo en paralelo (~1 min en frío)
  return request(`/auth/ops-board${q}`, { auth: true, timeout: 120000 })
}

export async function checkoutPlan(body) {
  return request('/billing/checkout', { method: 'POST', body, auth: true })
}

export async function invitarUsuario(body) {
  return request('/auth/invitar', { method: 'POST', body, auth: true })
}

export async function verifyEmail(token) {
  return request(`/auth/verify-email?token=${encodeURIComponent(token)}`)
}

export { TOKEN_KEY, USER_KEY, SITIO, resolveBaseURL }
