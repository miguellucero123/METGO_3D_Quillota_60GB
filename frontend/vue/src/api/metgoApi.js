import axios from 'axios'

const TOKEN_KEY = 'metgo_access_token'

/** API en Render; en Netlify el proxy /api suele dar 504 si el servicio está dormido (>26 s). */
const RENDER_API_BASE = 'https://metgo-api.onrender.com/api'

function resolveApiBaseURL() {
  const fromEnv = import.meta.env.VITE_METGO_API
  if (fromEnv) return fromEnv
  if (typeof window !== 'undefined' && window.location.hostname.includes('netlify.app')) {
    return RENDER_API_BASE
  }
  return '/api'
}

const api = axios.create({
  baseURL: resolveApiBaseURL(),
  timeout: 90000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/** Redirige a login sin recargar la página (evita error de iframe en preview de Cursor/Chrome). */
let onUnauthorized = null

export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler
}

api.interceptors.response.use(
  (r) => r,
  (err) => {
    const status = err.response?.status
    if (status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem('metgo_user')
      if (onUnauthorized) {
        onUnauthorized()
      } else if (window.self === window.top && !window.location.pathname.includes('/login')) {
        window.location.assign('/login')
      }
    }
    let msg =
      err.response?.data?.error ??
      err.message ??
      'Error de conexion con la API METGO'
    if (status === 504 || err.code === 'ECONNABORTED') {
      msg =
        'La API en Render está iniciando o tardó demasiado (plan gratuito). ' +
        'Espere 60 s, abra https://metgo-api.onrender.com/api/health en otra pestaña y vuelva a intentar.'
    }
    return Promise.reject(new Error(msg))
  }
)

/** Despierta el servicio en Render antes del login (cold start). */
export async function wakeApi() {
  await api.get('/health', { timeout: 120000 })
}

export async function login(username, password) {
  const { data } = await api.post('/auth/login', { username, password })
  return data
}

export async function fetchMe() {
  const { data } = await api.get('/auth/me')
  return data
}

export async function fetchHealth() {
  const { data } = await api.get('/health', { timeout: 120000 })
  return data
}

export async function fetchEstaciones() {
  const { data } = await api.get('/estaciones')
  return data
}

export async function fetchResumenMeteo(estacionId, tipo = 'pronostico') {
  const { data } = await api.get(`/meteo/${estacionId}`, { params: { tipo } })
  return data
}

export async function fetchPronostico(estacionId, dias = 7) {
  const { data } = await api.get(`/meteo/${estacionId}/pronostico`, {
    params: { dias },
  })
  return data
}

export async function fetchHistorico(estacionId, dias = 30) {
  const { data } = await api.get(`/meteo/${estacionId}/historico`, {
    params: { dias },
  })
  return data
}

export async function fetchAlertas(estacionId) {
  const { data } = await api.get('/alertas', {
    params: estacionId ? { estacion: estacionId } : {},
  })
  return data
}

export async function fetchRecomendacionesAgricolas(estacionId) {
  const { data } = await api.get(`/agricola/${estacionId}`)
  return data
}

export async function fetchSistemaResumen() {
  const { data } = await api.get('/sistema/resumen')
  return data
}

export async function fetchModulos(categoria) {
  const { data } = await api.get('/modulos', {
    params: categoria ? { categoria } : {},
  })
  return data
}

export async function fetchModulo(id) {
  const { data } = await api.get(`/modulos/${id}`)
  return data
}

export async function fetchConfiguracionEstacion(estacionId) {
  const { data } = await api.get(`/configuracion/estacion/${estacionId}`)
  return data
}

export async function fetchServiciosStreamlit() {
  const { data } = await api.get('/servicios/streamlit')
  return data
}

export async function iniciarServicioStreamlit(moduloId) {
  const { data } = await api.post(`/servicios/streamlit/${moduloId}/iniciar`)
  return data
}

export async function detenerServicioStreamlit(moduloId) {
  const { data } = await api.post(`/servicios/streamlit/${moduloId}/detener`)
  return data
}

export async function detenerTodosStreamlit() {
  const { data } = await api.post('/servicios/streamlit/detener-todos')
  return data
}

/** URL embed del Visor de Puertos (iframe en /puertos). */
export async function fetchVisorPuerto(moduloId) {
  const { data } = await api.get(`/servicios/streamlit/${moduloId}/visor`)
  return data
}
