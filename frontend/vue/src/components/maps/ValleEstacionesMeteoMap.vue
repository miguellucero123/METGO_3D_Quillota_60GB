<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMetgoStore } from '@/stores/metgo'
import { fetchComparativo } from '@/api/metgoApi'
import QuillotaMap3D from '@/components/maps/QuillotaMap3D.vue'

const props = defineProps({
  variable: { type: String, default: 'temperatura' },
})

const router = useRouter()
const store = useMetgoStore()

const estacionesGeo = [
  { id: 'quillota', nombre: 'Quillota' },
  { id: 'los_nogales', nombre: 'Los Nogales' },
  { id: 'hijuelas', nombre: 'Hijuelas' },
  { id: 'limache', nombre: 'Limache' },
  { id: 'olmue', nombre: 'Olmue' },
]

const datos = ref([])

const titulo = computed(() => ({
  temperatura: 'T° máxima hoy',
  precipitacion: 'Precipitación hoy',
  nubosidad: 'Nubosidad hoy',
}[props.variable] || 'Variable'))

const legendMap = computed(() => {
  if (props.variable === 'precipitacion') {
    return { title: 'Precipitación (mm)', gradient: 'linear-gradient(to right, #b0bec5, #2980b9)', labels: ['0mm', '>10mm'] }
  }
  if (props.variable === 'nubosidad') {
    return { title: 'Nubosidad (%)', gradient: 'linear-gradient(to right, #e0e0e0, #555555)', labels: ['0%', '100%'] }
  }
  return { title: 'Temperatura (°C)', gradient: 'linear-gradient(to right, rgb(40,90,140), rgb(215,130,20))', labels: ['8°C', '36°C'] }
})

function valorDe(r) {
  if (props.variable === 'precipitacion') return Number(r.precipitacion) || 0
  if (props.variable === 'nubosidad') return Number(r.cobertura_nubosa) || 0
  return Number(r.temperatura_max) || 0
}

function rgbColorDe(v) {
  if (props.variable === 'precipitacion') {
    return v > 0 ? [41, 128, 185] : [176, 190, 197]
  }
  if (props.variable === 'nubosidad') {
    const l = Math.max(80, 200 - (v * 1.2)); // from 200 down to 80
    return [l, l, l]
  }
  
  // Temperatura
  const n = Math.max(0, Math.min(1, (v - 8) / 28))
  const r = Math.round(40 + n * 175)
  const b = Math.round(140 - n * 120)
  return [r, Math.round(90 + n * 40), b]
}

const puntos = computed(() => {
  const map = new Map((datos.value || []).map((r) => [r.estacion_id, r]))
  return estacionesGeo.map((e) => {
    const r = map.get(e.id) || {}
    const val = valorDe(r)
    const unidad = props.variable === 'precipitacion' ? 'mm' : props.variable === 'nubosidad' ? '%' : '°C'
    return { 
      ...e, 
      value: val, 
      color: rgbColorDe(val),
      text: `${val}${unidad}` 
    }
  })
})

async function cargar() {
  try {
    datos.value = await fetchComparativo()
  } catch {
    datos.value = []
  }
}

function ir(id) {
  store.setEstacion(id)
  store.cargarDatosMeteo()
  router.push('/meteo')
}

onMounted(cargar)
watch(() => props.variable, cargar)
</script>

<template>
  <div class="valle-meteo-map">
    <div class="map-header">
      <h4>{{ titulo }} — Valle de Aconcagua</h4>
      <p class="hint">Clic en estación → detalle meteorológico</p>
    </div>
    
    <div class="map-wrapper">
      <QuillotaMap3D
        :estaciones="puntos"
        :legend="legendMap"
        layerType="column"
        @estacion-click="ir"
      />
    </div>
  </div>
</template>

<style scoped>
.valle-meteo-map { 
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.map-header h4 { margin: 0; font-size: 0.95rem; color: var(--color-text); }
.hint { font-size: 0.75rem; color: var(--color-muted); margin: 0.2rem 0 0; }
.map-wrapper {
  width: 100%;
  border-radius: var(--radius-md);
  overflow: hidden;
}
</style>
