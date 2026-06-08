<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useMetgoStore } from '@/stores/metgo'
import { fetchMapaGlobal, fetchMapaRegionalAnimacion } from '@/api/metgoApi'
import { colorMapa, rangoMapa, valorANormalizado } from '@/utils/mapColorScale'

const store = useMetgoStore()

const variables = [
  { id: 'temperatura', nombre: 'Temperatura', unidad: '°C' },
  { id: 'humedad', nombre: 'Humedad', unidad: '%' },
  { id: 'precipitacion', nombre: 'Precipitación', unidad: 'mm' },
  { id: 'radiacion', nombre: 'Radiación', unidad: 'W/m²' },
  { id: 'nubosidad', nombre: 'Nubosidad', unidad: '%' },
  { id: 'viento_velocidad', nombre: 'Viento', unidad: 'm/s' },
]

const variable = ref('temperatura')
const ambito = ref('regional')
const frameIdx = ref(0)
const animacion = ref(null)
const canvasRef = ref(null)
const grilla = ref(null)
const hoverVal = ref('Pase el cursor sobre el mapa')
const reproduciendo = ref(false)
let timer = null

const nombreVar = computed(() => variables.find((v) => v.id === variable.value)?.nombre ?? '')
const unidadVar = computed(() => variables.find((v) => v.id === variable.value)?.unidad ?? '')
const fechaFrame = computed(() => grilla.value?.fecha_frame?.slice?.(0, 10) ?? '')
const escala = computed(() => rangoMapa(variable.value))

function latLonToXY(lat, lon, bounds, w, h) {
  const { lat_min, lat_max, lon_min, lon_max } = bounds
  const x = ((lon - lon_min) / (lon_max - lon_min || 1)) * w
  const y = ((lat_max - lat) / (lat_max - lat_min || 1)) * h
  return { x, y }
}

async function cargar() {
  stopAnim()
  frameIdx.value = 0
  try {
    if (ambito.value === 'regional') {
      animacion.value = await fetchMapaRegionalAnimacion(
        store.estacionActiva,
        variable.value,
        { resolucion: '0.02', dias: 7 }
      )
      grilla.value = animacion.value?.frames?.[0] ?? null
    } else {
      animacion.value = null
      grilla.value = await fetchMapaGlobal(variable.value, { resolucion: '1.0' })
    }
    render()
  } catch {
    grilla.value = null
    animacion.value = null
  }
}

function render() {
  const canvas = canvasRef.value
  const data = grilla.value
  if (!canvas || !data) return
  const ctx = canvas.getContext('2d')
  const { lats, lons, valores } = data
  const w = canvas.width
  const h = canvas.height
  ctx.fillStyle = '#0f172a'
  ctx.fillRect(0, 0, w, h)

  const nLat = lats.length
  const nLon = lons.length
  const cellW = w / nLon
  const cellH = h / nLat

  for (let i = 0; i < nLat; i++) {
    for (let j = 0; j < nLon; j++) {
      const val = valores[i]?.[j]
      if (val == null) continue
      const n = valorANormalizado(variable.value, val)
      ctx.fillStyle = colorMapa(variable.value, n)
      ctx.fillRect(j * cellW, i * cellH, cellW + 1, cellH + 1)
    }
  }

  const bounds = data.bounds || {
    lat_min: Math.min(...lats),
    lat_max: Math.max(...lats),
    lon_min: Math.min(...lons),
    lon_max: Math.max(...lons),
  }

  for (const p of data.puntos_estacion || []) {
    const { x, y } = latLonToXY(p.lat, p.lon, bounds, w, h)
    ctx.beginPath()
    ctx.arc(x, y, 6, 0, Math.PI * 2)
    ctx.fillStyle = '#fff'
    ctx.fill()
    ctx.strokeStyle = '#111827'
    ctx.lineWidth = 2
    ctx.stroke()
    ctx.fillStyle = '#fff'
    ctx.font = 'bold 11px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText(String(p.valor), x, y - 10)
  }
}

function onMove(e) {
  const data = grilla.value
  const canvas = canvasRef.value
  if (!data || !canvas) return
  const rect = canvas.getBoundingClientRect()
  const li = Math.min(
    data.lats.length - 1,
    Math.max(0, Math.floor(((e.clientY - rect.top) / rect.height) * data.lats.length))
  )
  const lj = Math.min(
    data.lons.length - 1,
    Math.max(0, Math.floor(((e.clientX - rect.left) / rect.width) * data.lons.length))
  )
  const val = data.valores[li]?.[lj]
  if (val != null) hoverVal.value = `${val.toFixed(1)} ${unidadVar.value}`
}

function setFrame(idx) {
  if (!animacion.value?.frames?.length) return
  frameIdx.value = Math.max(0, Math.min(idx, animacion.value.frames.length - 1))
  grilla.value = animacion.value.frames[frameIdx.value]
  render()
}

function stopAnim() {
  reproduciendo.value = false
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

function toggleAnim() {
  if (!animacion.value?.frames?.length) return
  if (reproduciendo.value) {
    stopAnim()
    return
  }
  reproduciendo.value = true
  timer = setInterval(() => {
    const next = (frameIdx.value + 1) % animacion.value.frames.length
    setFrame(next)
  }, 500)
}

watch([variable, ambito, () => store.estacionActiva], cargar)
onMounted(cargar)
</script>

<template>
  <div class="mapas-glob">
    <header>
      <h3>🌍 Mapas meteorológicos</h3>
      <p>
        {{ ambito === 'regional' ? 'Valle de Aconcagua (IDW 5 estaciones)' : 'Vista global simplificada' }}
      </p>
    </header>

    <div class="ambito">
      <button type="button" :class="{ active: ambito === 'regional' }" @click="ambito = 'regional'">Regional</button>
      <button type="button" :class="{ active: ambito === 'global' }" @click="ambito = 'global'">Global</button>
    </div>

    <div class="vars">
      <button
        v-for="v in variables"
        :key="v.id"
        type="button"
        :class="{ active: variable === v.id }"
        @click="variable = v.id"
      >
        {{ v.nombre }}
      </button>
    </div>

    <div v-if="ambito === 'regional' && animacion" class="anim-controls">
      <button type="button" @click="toggleAnim">{{ reproduciendo ? 'Pausar' : '▶ Animar 7 días' }}</button>
      <input
        type="range"
        min="0"
        :max="(animacion.frames?.length ?? 1) - 1"
        :value="frameIdx"
        @input="setFrame(Number($event.target.value))"
      />
      <span class="fecha-frame">{{ fechaFrame || '—' }}</span>
    </div>

    <div class="mapa-wrap">
      <canvas ref="canvasRef" width="800" height="400" @mousemove="onMove" />
      <div class="overlay">
        <span>{{ nombreVar }}</span>
        <strong>{{ hoverVal }}</strong>
        <span v-if="fechaFrame">Día: {{ fechaFrame }}</span>
      </div>
      <div class="colorbar">
        <span>{{ escala.min }}{{ unidadVar }}</span>
        <div class="bar" />
        <span>{{ escala.max }}{{ unidadVar }}</span>
      </div>
    </div>
    <p class="fuente">
      Regional: pronóstico OpenMeteo interpolado (IDW) · Puntos blancos = estaciones METGO
    </p>
  </div>
</template>

<style scoped>
.mapas-glob { background: #fff; border-radius: 8px; padding: 1rem; }
.mapas-glob header h3 { margin: 0; font-size: 1rem; }
.mapas-glob header p { margin: 0.25rem 0 0.75rem; font-size: 0.78rem; color: #6b7280; }
.ambito { display: flex; gap: 0.35rem; margin-bottom: 0.5rem; }
.ambito button, .anim-controls button {
  padding: 0.35rem 0.65rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fff;
  font-size: 0.75rem;
  cursor: pointer;
}
.ambito button.active { background: #0284c7; color: #fff; border-color: #0284c7; }
.vars { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 0.75rem; }
.vars button {
  padding: 0.35rem 0.65rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fff;
  font-size: 0.75rem;
  cursor: pointer;
}
.vars button.active { background: #0284c7; color: #fff; border-color: #0284c7; }
.anim-controls { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; font-size: 0.75rem; }
.anim-controls input { flex: 1; }
.fecha-frame { font-family: monospace; color: #4b5563; }
.mapa-wrap { position: relative; border-radius: 8px; overflow: hidden; }
canvas { display: block; width: 100%; height: auto; max-height: 400px; }
.overlay {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.75);
  color: #fff;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.colorbar {
  position: absolute;
  bottom: 8px;
  left: 8px;
  right: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.68rem;
  color: #e5e7eb;
  background: rgba(0, 0, 0, 0.55);
  padding: 0.35rem 0.5rem;
  border-radius: 6px;
}
.colorbar .bar {
  flex: 1;
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(to right, #1e40af, #22c55e, #eab308, #ef4444);
}
.fuente { font-size: 0.72rem; color: #0c4a6e; margin-top: 0.5rem; background: #f0f9ff; padding: 0.5rem; border-radius: 6px; }
</style>
