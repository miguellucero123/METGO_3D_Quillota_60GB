import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  fetchEstaciones,
  fetchResumenMeteo,
  fetchHealth,
  wakeApi,
  fetchComparativo,
  fetchCronogramaRiego,
  fetchAgricolaRiego,
  fetchRecomendacionesAgricolas,
} from '@/api/metgoApi'
import { CULTIVOS_CATALOG } from '@/utils/agroColors'

export const useMetgoStore = defineStore('metgo', () => {
  const estaciones = ref([
    { id: 'quillota', nombre: 'Quillota', activa: true },
    { id: 'los_nogales', nombre: 'Los Nogales', activa: true },
    { id: 'hijuelas', nombre: 'Hijuelas', activa: true },
    { id: 'limache', nombre: 'Limache', activa: true },
    { id: 'olmue', nombre: 'Olmué', activa: true },
  ])
  const estacionActiva = ref('quillota')
  const datosMeteo = ref(null)
  const cargando = ref(false)
  const error = ref(null)
  const apiOnline = ref(false)
  const tipoAnalisis = ref('pronostico')

  const comparativoEstaciones = ref({})
  const riegoPorCultivo = ref({})
  const recomendacionesAgricolas = ref([])
  const cronogramaRiego = ref(null)
  const loadingCronograma = ref(false)

  const estacionNombre = computed(() =>
    estaciones.value.find((e) => e.id === estacionActiva.value)?.nombre ?? 'Quillota'
  )

  const resumenMeteo = computed(() => datosMeteo.value)

  function setEstacion(id) {
    if (id && estacionActiva.value !== id) {
      estacionActiva.value = id
      cargarDatosMeteo()
    }
  }

  async function cargarDatosMeteo(retry = true) {
    cargando.value = true
    error.value = null
    try {
      datosMeteo.value = await fetchResumenMeteo(estacionActiva.value, tipoAnalisis.value)
    } catch (e) {
      const msg = e.message ?? 'Error al cargar datos'
      // Retry automático si Render está en cold start (404 transitorio)
      if (retry && msg.includes('iniciando')) {
        await new Promise((r) => setTimeout(r, 3000))
        return cargarDatosMeteo(false)
      }
      error.value = msg
      datosMeteo.value = null
    } finally {
      cargando.value = false
    }
  }

  async function fetchComparativoEstaciones() {
    try {
      const rows = await fetchComparativo()
      const map = {}
      for (const r of rows || []) {
        const id = r.estacion_id || r.id
        if (id) map[id] = r
      }
      comparativoEstaciones.value = map
      return map
    } catch {
      comparativoEstaciones.value = {}
      return {}
    }
  }

  async function fetchRiegoPorCultivo(estacionId = estacionActiva.value) {
    const out = {}
    for (const c of CULTIVOS_CATALOG) {
      try {
        const r = await fetchAgricolaRiego(estacionId, c.slug)
        out[c.slug] = Number(r.mm_sugeridos_hoy) || 0
      } catch {
        out[c.slug] = 0
      }
    }
    riegoPorCultivo.value = out
    return out
  }

  async function fetchRecomendaciones(estacionId = estacionActiva.value) {
    try {
      recomendacionesAgricolas.value = await fetchRecomendacionesAgricolas(estacionId)
    } catch {
      recomendacionesAgricolas.value = []
    }
    return recomendacionesAgricolas.value
  }

  async function fetchCronograma(estacionId, cultivoSlug) {
    loadingCronograma.value = true
    try {
      const data = await fetchCronogramaRiego(estacionId, cultivoSlug)
      cronogramaRiego.value = data
      return data
    } catch (e) {
      console.error('fetchCronograma error:', e)
      cronogramaRiego.value = { cronograma: [] }
      return { cronograma: [] }
    } finally {
      loadingCronograma.value = false
    }
  }

  async function inicializar() {
    const token = localStorage.getItem('metgo_access_token')
    if (!token) {
      apiOnline.value = false
      return
    }
    try {
      const esPublico =
        typeof window !== 'undefined' && window.location.hostname.includes('netlify.app')
      if (esPublico) {
        try {
          await wakeApi()
        } catch {
          /* cold start Render */
        }
      }
      const health = await fetchHealth()
      apiOnline.value = health.status === 'ok' || health.status === 'degraded'
    } catch {
      apiOnline.value = false
      error.value =
        'API REST no disponible. Ejecute: python 10_Deployment_Produccion/scripts/iniciar_api_rest.py'
    }
    try {
      const remoto = await fetchEstaciones()
      if (remoto?.length) estaciones.value = remoto
    } catch (e) {
      if (!error.value) error.value = e.message
    }
    await cargarDatosMeteo()
  }

  return {
    estaciones,
    estacionActiva,
    datosMeteo,
    resumenMeteo,
    cargando,
    error,
    apiOnline,
    tipoAnalisis,
    estacionNombre,
    comparativoEstaciones,
    riegoPorCultivo,
    recomendacionesAgricolas,
    cronogramaRiego,
    loadingCronograma,
    cargarDatosMeteo,
    setEstacion,
    inicializar,
    fetchComparativoEstaciones,
    fetchRiegoPorCultivo,
    fetchRecomendaciones,
    fetchCronograma,
  }
})
