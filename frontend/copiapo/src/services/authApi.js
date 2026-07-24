/**
 * Auth JWT metgo-api (E9) — sitio Copiapó.
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
  if (typeof window !== 'undefined' && window.location.hostname.includes('netlify.app')) {
    return RENDER_API
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
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      const err = new Error(data.error || `HTTP ${res.status}`)
      err.status = res.status
      err.data = data
      throw err
    }
    return data
  } finally {
    clearTimeout(t)
  }
}

export async function login(username, password) {
  return request('/auth/login', {
    method: 'POST',
    body: { username, password, sitio: SITIO },
  })
}

export async function fetchMe() {
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

export { TOKEN_KEY, USER_KEY, SITIO, resolveBaseURL }
