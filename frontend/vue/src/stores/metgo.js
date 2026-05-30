import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fetchEstaciones, fetchResumenMeteo, fetchHealth, wakeApi } from '@/api/metgoApi'

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

  const estacionNombre = computed(() =>
    estaciones.value.find((e) => e.id === estacionActiva.value)?.nombre ?? 'Quillota'
  )

  async function cargarDatosMeteo() {
    cargando.value = true
    error.value = null
    try {
      datosMeteo.value = await fetchResumenMeteo(estacionActiva.value, tipoAnalisis.value)
    } catch (e) {
      error.value = e.message ?? 'Error al cargar datos'
      datosMeteo.value = null
    } finally {
      cargando.value = false
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
          /* cold start Render: reintento en fetchHealth */
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
    cargando,
    error,
    apiOnline,
    tipoAnalisis,
    estacionNombre,
    cargarDatosMeteo,
    inicializar,
  }
})
