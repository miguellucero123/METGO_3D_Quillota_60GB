/**
 * Auth JWT metgo-api (E9) — sitio Copiapó.
 */
import site from '@/site.config.js'

const RENDER_API = site.api?.defaultPublicBase || 'https://metgo-api.onrender.com/api'
const TOKEN_KEY = `${site.storagePrefix || 'metgo'}_access_token`
const USER_KEY = `${site.storagePrefix || 'metgo'}_user`
const SITIO = site.sitio
const TIMEOUT_MS = 90000

const COLD_START_MSG =
  'La API en Render está iniciando o tardó demasiado (plan gratuito). ' +
  'Espere 60 s, abra https://metgo-api.onrender.com/api/health en otra pestaña y vuelva a intentar.'

function resolveBaseURL() {
  const fromEnv = import.meta.env.VITE_METGO_API || import.meta.env.VITE_API_BASE
  if (fromEnv) return String(fromEnv).replace(/\/$/, '')
  // Local sin API en 8080: Render directo (CORS permite localhost).
  // API local: VITE_METGO_API=http://127.0.0.1:8080/api
  return RENDER_API
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

function mapNetworkError(err) {
  if (err?.name === 'AbortError' || err?.message?.includes('aborted')) {
    return new Error(COLD_START_MSG)
  }
  if (err?.message === 'Failed to fetch' || err?.message?.includes('NetworkError')) {
    return new Error(COLD_START_MSG)
  }
  return err instanceof Error ? err : new Error(String(err || 'Error de red'))
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
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      const err = new Error(data.error || `HTTP ${res.status}`)
      err.status = res.status
      err.data = data
      throw err
    }
    return data
  } catch (err) {
    if (err?.status) throw err
    throw mapNetworkError(err)
  } finally {
    clearTimeout(t)
  }
}

export async function login(username, password) {
  return request('/auth/login', {
    method: 'POST',
    body: { username, password, sitio: SITIO },
    timeout: 90000,
  })
}

export async function fetchMe() {
  return request('/auth/me', { auth: true })
}

/** Despierta Render (cold start free) antes del login. */
export async function wakeApi(maxRetries = 10) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      await request('/health', { timeout: 15000 })
      return true
    } catch {
      if (i === maxRetries - 1) {
        throw new Error(COLD_START_MSG)
      }
      await new Promise((r) => setTimeout(r, 4000))
    }
  }
  return false
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
  return request('/auth/register-v2', { method: 'POST', body, timeout: 90000 })
}

export async function verifyEmail(token) {
  return request(`/auth/verify-email?token=${encodeURIComponent(token)}`)
}

export async function fetchPlanes(sitio = SITIO, faena) {
  const q = new URLSearchParams({ sitio })
  if (faena) q.set('faena', faena)
  return request(`/public/planes?${q}`)
}

export async function fetchCuenta(faena) {
  const q = faena ? `?faena=${encodeURIComponent(faena)}` : ''
  return request(`/auth/cuenta${q}`, { auth: true })
}

export async function checkoutPlan(body) {
  return request('/billing/checkout', { method: 'POST', body, auth: true })
}

export { TOKEN_KEY, USER_KEY, SITIO, resolveBaseURL, RENDER_API, COLD_START_MSG }
