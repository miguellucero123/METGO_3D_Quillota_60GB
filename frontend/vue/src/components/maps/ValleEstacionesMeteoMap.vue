<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMetgoStore } from '@/stores/metgo'
import { fetchComparativo } from '@/api/metgoApi'
import ChartTooltip from '@/components/charts/ChartTooltip.vue'

const props = defineProps({
  variable: { type: String, default: 'temperatura' },
})

const router = useRouter()
const store = useMetgoStore()

const estacionesGeo = [
  { id: 'quillota', nombre: 'Quillota', x: 48, y: 52 },
  { id: 'los_nogales', nombre: 'Los Nogales', x: 62, y: 28 },
  { id: 'hijuelas', nombre: 'Hijuelas', x: 78, y: 42 },
  { id: 'limache', nombre: 'Limache', x: 35, y: 72 },
  { id: 'olmue', nombre: 'Olmue', x: 70, y: 68 },
]

const datos = ref([])
const tip = ref({ visible: false, x: 0, y: 0, p: null })

const titulo = computed(() => ({
  temperatura: 'T° máxima hoy',
  precipitacion: 'Precipitación hoy',
  nubosidad: 'Nubosidad hoy',
}[props.variable] || 'Variable'))

function valorDe(r) {
  if (props.variable === 'precipitacion') return Number(r.precipitacion) || 0
  if (props.variable === 'nubosidad') return Number(r.cobertura_nubosa) || 0
  return Number(r.temperatura_max) || 0
}

function colorTemp(t) {
  const n = Math.max(0, Math.min(1, (t - 8) / 28))
  const r = Math.round(40 + n * 175)
  const b = Math.round(140 - n * 120)
  return `rgb(${r}, ${Math.round(90 + n * 40)}, ${b})`
}

function colorDe(v) {
  if (props.variable === 'precipitacion') return v > 0 ? '#2980b9' : '#b0bec5'
  if (props.variable === 'nubosidad') return `hsl(210, ${30 + v * 0.5}%, ${70 - v * 0.35}%)`
  return colorTemp(v)
}

const puntos = computed(() => {
  const map = new Map((datos.value || []).map((r) => [r.estacion_id, r]))
  return estacionesGeo.map((e) => {
    const r = map.get(e.id) || {}
    const val = valorDe(r)
    return { ...e, val, color: colorDe(val), unidad: props.variable === 'precipitacion' ? 'mm' : props.variable === 'nubosidad' ? '%' : '°C' }
  })
})

async function cargar() {
  try {
    datos.value = await fetchComparativo()
  } catch {
    datos.value = []
  }
}

function ir(p) {
  store.setEstacion(p.id)
  store.cargarDatosMeteo()
  router.push('/meteo')
}

function onEnter(e, p) {
  tip.value = { visible: true, x: e.clientX, y: e.clientY, p }
}
function onLeave() {
  tip.value.visible = false
}

onMounted(cargar)
watch(() => props.variable, cargar)
</script>

<template>
  <div class="valle-meteo-map">
    <h4>{{ titulo }} — Valle de Aconcagua</h4>
    <svg viewBox="0 0 100 100" class="map-svg" role="img">
      <rect width="100" height="100" fill="#f0f9ff" rx="4" />
      <ellipse cx="55" cy="50" rx="38" ry="32" fill="#dbeafe" opacity="0.5" />
      <g v-for="p in puntos" :key="p.id">
        <circle
          :cx="p.x"
          :cy="p.y"
          r="7"
          :fill="p.color"
          stroke="#fff"
          stroke-width="1.2"
          class="pin"
          @click="ir(p)"
          @mouseenter="onEnter($event, p)"
          @mouseleave="onLeave"
        />
        <text :x="p.x" :y="p.y + 13" text-anchor="middle" font-size="3.2" fill="#374151">{{ p.nombre }}</text>
        <text :x="p.x" :y="p.y - 10" text-anchor="middle" font-size="3.5" font-weight="600" fill="#111827">
          {{ p.val }}{{ p.unidad }}
        </text>
      </g>
    </svg>
    <p class="hint">Clic en estación → detalle meteorológico</p>
    <ChartTooltip :x="tip.x" :y="tip.y" :visible="tip.visible && tip.p">
      <strong>{{ tip.p?.nombre }}</strong>
      {{ tip.p?.val }}{{ tip.p?.unidad }}
    </ChartTooltip>
  </div>
</template>

<style scoped>
.valle-meteo-map { position: relative; }
.valle-meteo-map h4 { margin: 0 0 0.5rem; font-size: 0.9rem; }
.map-svg { width: 100%; max-height: 280px; border-radius: 8px; border: 1px solid #e5e7eb; }
.pin { cursor: pointer; }
.hint { font-size: 0.68rem; color: #6b7280; margin: 0.35rem 0 0; }
</style>
