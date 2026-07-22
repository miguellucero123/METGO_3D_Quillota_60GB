import axios from 'axios'
import { seriesHistoricoPorDia, seriePronosticoPorDia } from '@/utils/meteoDates'

const TOKEN_KEY = 'metgo_access_token'

/** API en Render; en Netlify el proxy /api suele dar 504 si el servicio está dormido (>26 s). */
const RENDER_API_BASE = 'https://metgo-api.onrender.com/api'

function resolveApiBaseURL() {
  if (typeof window !== 'undefined' && window.location.hostname.includes('netlify.app')) {
    return RENDER_API_BASE
  }
  const fromEnv = import.meta.env.VITE_METGO_API
  if (fromEnv) return fromEnv
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
let onForbidden = null

export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler
}

export function setForbiddenHandler(handler) {
  onForbidden = handler
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
    if (status === 403 && onForbidden) {
      onForbidden()
    }
    const url = err.config?.url ?? ''
    let msg =
      err.response?.data?.error ??
      err.message ??
      'Error de conexion con la API METGO'
    if (status === 504 || err.code === 'ECONNABORTED') {
      msg =
        'La API en Render está iniciando o tardó demasiado (plan gratuito). ' +
        'Espere 60 s, abra https://metgo-api.onrender.com/api/health en otra pestaña y vuelva a intentar.'
    } else if (status === 404 && url.includes('/meteo/')) {
      // Render (plan free) devuelve 404 durante cold start antes de que Flask arranque.
      // Si el body tiene "estacion_id" es un 404 real de validación; si no, es cold start.
      const esRealNotFound = err.response?.data?.estacion_id
      if (!esRealNotFound) {
        msg =
          'La API en Render aún está iniciando (plan gratuito). ' +
          'Recargue la página en 30 segundos.'
      }
    } else if (status === 503) {
      msg = err.response?.data?.error ?? 'El servicio meteorológico (OpenMeteo) no está disponible temporalmente. Recargue en unos minutos.'
    }
    return Promise.reject(new Error(msg))
  }
)

/** Despierta el servicio en Render antes del login (cold start). */
export async function wakeApi(maxRetries = 12) {
  const baseUrl = resolveApiBaseURL()
  for (let i = 0; i < maxRetries; i++) {
    try {
      await axios.get(`${baseUrl}/health`, { timeout: 10000 })
      return true
    } catch (err) {
      if (i === maxRetries - 1) {
        throw new Error(
          'La API en Render está iniciando o tardó demasiado (plan gratuito). ' +
          'Espere 60 s, abra https://metgo-api.onrender.com/api/health en otra pestaña y vuelva a intentar.'
        )
      }
      await new Promise(r => setTimeout(r, 5000))
    }
  }
}

export async function login(username, password) {
  const { data } = await api.post('/auth/login', { username, password })
  return data
}

export async function register({ username, password, email }) {
  const { data } = await api.post('/auth/register', { username, password, email })
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

export async function fetchPrecipitacionCalibrada(estacionId, dias = 7, intervalo = '3h') {
  const { data } = await api.get(`/meteo/${estacionId}/precipitacion-calibrada`, {
    params: { dias, intervalo },
  })
  return data
}

export async function fetchPrecipitacionBruta(estacionId, dias = 7) {
  const { data } = await api.get(`/precip/${estacionId}/pronostico`, { params: { dias } })
  return data
}

export async function fetchAlertasPrecipitacion(estacionId) {
  const { data } = await api.get(`/precip/${estacionId}/alertas`)
  return data
}

export async function fetchAlertasPrecipitacionGlobal(estacionId) {
  const { data } = await api.get('/alertas/precipitacion', {
    params: estacionId ? { estacion: estacionId } : {},
  })
  return data
}

export async function fetchPronosticoHeladas(estacionId, dias = 7) {
  const { data } = await api.get(`/meteo/${estacionId}/heladas`, { params: { dias } })
  return data
}

export async function fetchPronosticoHeladaAvanzado(
  estacionId,
  dias = 7,
  cultivo = 'palto',
  extras = {},
) {
  const { data } = await api.get(`/meteo/${estacionId}/helada`, {
    params: { dias, cultivo, ...extras },
  })
  return data
}

export async function fetchAnalisisNubosidad(estacionId, dias = 7) {
  const { data } = await api.get(`/meteo/${estacionId}/nubosidad`, { params: { dias } })
  return data
}

export async function fetchPronosticoNiebla(estacionId, dias = 7) {
  const { data } = await api.get(`/meteo/${estacionId}/niebla`, { params: { dias } })
  return data
}

export async function fetchVariablesMeteoCompletas(estacionId, dias = 7) {
  const { data } = await api.get(`/meteo/${estacionId}/variables-completas`, { params: { dias } })
  return data
}

export async function fetchMapaGlobal(variable, params = {}) {
  const { data } = await api.get(`/mapas/global/${variable}`, { params })
  return data
}

export async function fetchMapaRegional(estacionId, variable, params = {}) {
  const { data } = await api.get(`/mapas/regional/${estacionId}/${variable}`, { params })
  return data
}

export async function fetchMapaRegionalAnimacion(estacionId, variable, params = {}) {
  const { data } = await api.get(`/mapas/regional/${estacionId}/${variable}/animacion`, { params })
  return data
}

export async function fetchComparacionModelos(estacionId, variable, dias = 7) {
  const { data } = await api.get(`/mapas/comparacion-modelos/${estacionId}/${variable}`, {
    params: { dias },
  })
  return data
}

export async function fetchAlertasHelada(estacionId) {
  const { data } = await api.get('/alertas/helada', {
    params: estacionId ? { estacion: estacionId } : {},
  })
  return data
}

export async function fetchPrecipitacionHistorico(estacionId, desde, hasta) {
  const { data } = await api.get(`/precip/${estacionId}/historico`, {
    params: { desde, hasta, include_stats: true },
  })
  return data
}

export async function fetchPrecipitacionAcumulado(estacionId, rango = '7d') {
  const { data } = await api.get(`/precip/${estacionId}/acumulado`, { params: { rango } })
  return data
}

export async function fetchCronogramaRiego(estacionId, cultivo = 'palto') {
  const slug = cultivo === 'uva' ? 'vid' : cultivo
  const { data } = await api.get(`/agricola/${estacionId}/${slug}/cronograma`)
  return data
}

export async function fetchPronostico(estacionId, dias = 7) {
  const { data } = await api.get(`/meteo/${estacionId}/pronostico`, {
    params: { dias },
  })
  return seriePronosticoPorDia(data, dias)
}

export async function fetchVientoHorario(estacionId, dias = 7) {
  const { data } = await api.get(`/meteo/${estacionId}/viento-horario`, { params: { dias } })
  return data
}

/** Una fila por YYYY-MM-DD; excluye días futuros (OpenMeteo forecast mezclado). */
export function dedupeHistoricoPorDia(rows, dias = 30) {
  if (!Array.isArray(rows)) return rows
  return seriesHistoricoPorDia(rows, dias)
}

export async function fetchHistorico(estacionId, dias = 30) {
  const { data } = await api.get(`/meteo/${estacionId}/historico`, {
    params: { dias },
  })
  return dedupeHistoricoPorDia(data, dias)
}

export async function fetchAlertas(estacionId) {
  const { data } = await api.get('/alertas', {
    params: estacionId ? { estacion: estacionId } : {},
  })
  return data
}

export async function fetchComparativo() {
  const { data } = await api.get('/meteo/comparativo')
  return data
}

export async function fetchComparativoHistorico(dias = 14) {
  const { data } = await api.get('/meteo/comparativo/historico', {
    params: { dias },
  })
  return data
}

export async function fetchMetricasGlobales() {
  const { data } = await api.get('/metricas/globales')
  return data
}

export async function fetchAlertasConfig() {
  const { data } = await api.get('/alertas/config')
  return data
}

export async function crearAlertaConfig(payload) {
  const { data } = await api.post('/alertas/config', payload)
  return data
}

export async function eliminarAlertaConfig(id) {
  const { data } = await api.delete(`/alertas/config/${id}`)
  return data
}

export async function fetchTenantMe() {
  const { data } = await api.get('/tenants/me')
  return data
}

export async function fetchIotSensores() {
  const { data } = await api.get('/iot/sensores')
  return data
}

export async function fetchIotLecturas(estacionId) {
  const { data } = await api.get('/iot/lecturas', {
    params: estacionId ? { estacion: estacionId } : {},
  })
  return data
}

export async function simularIot() {
  const { data } = await api.post('/iot/simular')
  return data
}

export async function fetchMlModelos(soloServibles = false) {
  const { data } = await api.get('/ml/modelos', {
    params: soloServibles ? { solo_servibles: '1' } : {},
  })
  return data
}

export async function fetchMlResumen() {
  const { data } = await api.get('/ml/resumen')
  return data
}

export async function fetchMlRegistry() {
  const { data } = await api.get('/ml/registry')
  return data
}

export async function syncMlRegistry() {
  const { data } = await api.post('/ml/registry/sync')
  return data
}

export async function fetchMlPrediccion(variable, estacionId) {
  const { data } = await api.get(`/ml/prediccion/${variable}`, {
    params: { estacion: estacionId },
  })
  return data
}

export async function fetchIntegracionEstado() {
  const { data } = await api.get('/integracion/estado')
  return data
}

export async function syncDatosEtl(dias = 14, incluirCsv = true) {
  const { data } = await api.post('/datos/etl/sync', { dias, incluir_csv: incluirCsv })
  return data
}

export async function fetchEtlStatus() {
  const { data } = await api.get('/datos/etl/status')
  return data
}

export async function fetchAgricolaRiego(estacionId, cultivo = 'palto') {
  const { data } = await api.get(`/agricola/${estacionId}/riego`, { params: { cultivo } })
  return data
}

export async function fetchStreamlitCobertura() {
  const { data } = await api.get('/modulos/streamlit/cobertura')
  return data
}

export async function fetchAgricolaAvanzado(estacionId) {
  const { data } = await api.get(`/agricola/${estacionId}/avanzado`)
  return data
}

export async function fetchAlertasHistorial(estacionId) {
  const { data } = await api.get('/alertas/historial', {
    params: estacionId ? { estacion: estacionId } : {},
  })
  return data
}

export async function fetchReportesUltimos(limite = 10) {
  const { data } = await api.get('/reportes/ultimos', { params: { limite } })
  return data
}

export async function fetchReporteDetalle(nombre) {
  const { data } = await api.get(`/reportes/${encodeURIComponent(nombre)}`)
  return data
}

export async function fetchDatosFuentes() {
  const { data } = await api.get('/datos/fuentes')
  return data
}

export async function fetchMeteoStore() {
  const { data } = await api.get('/datos/meteo/store')
  return data
}

export async function fetchAgricolaCultivos() {
  const { data } = await api.get('/agricola/cultivos')
  return data
}

export async function fetchAgricolaEconomico(estacionId) {
  const { data } = await api.get(`/agricola/${estacionId}/economico`)
  return data
}

export async function fetchNotificacionesConfig() {
  const { data } = await api.get('/notificaciones/config')
  return data
}

export async function guardarNotificacionesConfig(payload) {
  const { data } = await api.put('/notificaciones/config', payload)
  return data
}

export async function probarNotificaciones(mensaje = 'Prueba METGO') {
  const { data } = await api.post('/notificaciones/probar', { mensaje })
  return data
}

export async function fetchNotificacionesStatus() {
  const { data } = await api.get('/notificaciones/status')
  return data
}

export async function fetchNotificacionesOutbox(limite = 20) {
  const { data } = await api.get('/notificaciones/outbox', { params: { limite } })
  return data
}

export async function reintentarNotificacionesOutbox(max = 10) {
  const { data } = await api.post('/notificaciones/outbox/retry', { max })
  return data
}

export async function fetchIotDrones() {
  const { data } = await api.get('/iot/drones')
  return data
}

export async function fetchIotSatelital() {
  const { data } = await api.get('/iot/satelital')
  return data
}

export async function fetchMqttStatus() {
  const { data } = await api.get('/iot/mqtt/status')
  return data
}

export async function ingestarMqtt(topic, payload) {
  const { data } = await api.post('/iot/mqtt/ingestar', { topic, payload })
  return data
}

export async function fetchMlTrainStatus() {
  const { data } = await api.get('/ml/train/status')
  return data
}

export async function encolarMlTrain(
  variables = [],
  estacionId = 'quillota',
  notas = '',
  modo = 'sync'
) {
  const { data } = await api.post('/ml/train/queue', {
    variables,
    estacion_id: estacionId,
    notas,
    modo,
  })
  return data
}

export async function fetchWorkersStatus() {
  const { data } = await api.get('/workers/status')
  return data
}

export async function entrenarMlQuillota(estacionId = 'quillota', variables = null, diasDatos = 365) {
  const { data } = await api.post('/ml/train/run', {
    estacion_id: estacionId,
    variables,
    dias_datos: diasDatos,
  })
  return data
}

export async function procesarColaMl(max = 1) {
  const { data } = await api.post('/ml/train/process-queue', { max })
  return data
}

export async function ejecutarMlTrainSiguiente() {
  const { data } = await api.post('/ml/train/run-next')
  return data
}

export async function fetchDeployInfo() {
  const { data } = await api.get('/deploy/info')
  return data
}

export async function fetchDocsIndice() {
  const { data } = await api.get('/docs/indice')
  return data
}

export async function fetchTestingResumen() {
  const { data } = await api.get('/testing/resumen')
  return data
}

export async function mlPredictBatch(variables, estacionId = 'quillota') {
  const { data } = await api.post('/ml/predict/batch', {
    variables,
    estacion_id: estacionId,
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
