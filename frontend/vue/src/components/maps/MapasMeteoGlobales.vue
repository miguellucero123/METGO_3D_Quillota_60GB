<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useMetgoStore } from '@/stores/metgo'
import { fetchMapaGlobal, fetchMapaRegionalAnimacion } from '@/api/metgoApi'
import MapaMeteoRelieve from '@/components/maps/MapaMeteoRelieve.vue'

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
const grilla = ref(null)
const reproduciendo = ref(false)
let timer = null

const nombreVar = computed(() => variables.find((v) => v.id === variable.value)?.nombre ?? '')
const unidadVar = computed(() => variables.find((v) => v.id === variable.value)?.unidad ?? '')
const fechaFrame = computed(() => grilla.value?.fecha_frame?.slice?.(0, 10) ?? '')

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
  } catch {
    grilla.value = null
    animacion.value = null
  }
}

function setFrame(idx) {
  if (!animacion.value?.frames?.length) return
  frameIdx.value = Math.max(0, Math.min(idx, animacion.value.frames.length - 1))
  grilla.value = animacion.value.frames[frameIdx.value]
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
        {{
          ambito === 'regional'
            ? 'Valle de Aconcagua · mapa interactivo con relieve (zoom, capas, estaciones)'
            : 'Vista global · modelo físico simplificado'
        }}
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

    <MapaMeteoRelieve
      v-if="grilla"
      :key="`${ambito}-${variable}`"
      :grilla="grilla"
      :variable="variable"
      :unidad="unidadVar"
      :nombre-var="nombreVar"
      :fecha-frame="fechaFrame"
      :ambito="ambito"
    />
    <p v-else class="muted">Sin datos de mapa para esta variable.</p>

    <p class="fuente">
      Base cartográfica OpenTopoMap / OpenStreetMap · Capa meteo IDW sobre relieve · Clic en estación para detalle
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
.muted { color: #6b7280; font-size: 0.85rem; }
.fuente { font-size: 0.72rem; color: #0c4a6e; margin-top: 0.5rem; background: #f0f9ff; padding: 0.5rem; border-radius: 6px; }
</style>
