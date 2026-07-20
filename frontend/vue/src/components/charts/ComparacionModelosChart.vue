<script setup>
import { computed, ref, watch, onMounted } from 'vue'
import { useMetgoStore } from '@/stores/metgo'
import { fetchComparacionModelos } from '@/api/metgoApi'
import ChartTooltip from '@/components/charts/ChartTooltip.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'

const store = useMetgoStore()

const variables = [
  { id: 'temperatura', nombre: 'T° máx', unidad: '°C' },
  { id: 'precipitacion', nombre: 'Lluvia', unidad: 'mm' },
  { id: 'humedad', nombre: 'Humedad', unidad: '%' },
  { id: 'nubosidad', nombre: 'Nubes', unidad: '%' },
]

const variable = ref('temperatura')
const datos = ref(null)
const cargando = ref(false)
const error = ref('')
const tip = ref({ visible: false, x: 0, y: 0, i: -1 })

const filas = computed(() => datos.value?.comparacion ?? [])
const unidad = computed(() => variables.find((v) => v.id === variable.value)?.unidad ?? '')
const nota = computed(() => datos.value?.nota ?? '')

const W = 640
const H = 200
const pad = { t: 16, r: 12, b: 36, l: 40 }

const yRange = computed(() => {
  const vals = filas.value.flatMap((r) => [r.gfs, r.ecmwf]).map(Number)
  if (!vals.length) return { min: 0, max: 1 }
  let lo = Math.min(...vals)
  let hi = Math.max(...vals)
  if (lo === hi) { lo -= 1; hi += 1 }
  const m = (hi - lo) * 0.1 || 0.5
  return { min: lo - m, max: hi + m }
})

const innerW = computed(() => W - pad.l - pad.r)
const innerH = computed(() => H - pad.t - pad.b)

function xAt(i, n) {
  if (n <= 1) return pad.l + innerW.value / 2
  return pad.l + (i / (n - 1)) * innerW.value
}

function yAt(v) {
  const { min, max } = yRange.value
  return pad.t + innerH.value * (1 - (Number(v) - min) / (max - min))
}

function pathFor(key) {
  const n = filas.value.length
  if (!n) return ''
  return filas.value
    .map((r, i) => `${i ? 'L' : 'M'} ${xAt(i, n).toFixed(1)} ${yAt(r[key]).toFixed(1)}`)
    .join(' ')
}

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    datos.value = await fetchComparacionModelos(store.estacionActiva, variable.value)
  } catch (e) {
    datos.value = null
    error.value = e?.message || 'Error cargando comparación'
  } finally {
    cargando.value = false
  }
}

function onEnter(e, i) {
  tip.value = { visible: true, x: e.clientX, y: e.clientY, i }
}
function onMove(e) {
  if (tip.value.visible) { tip.value.x = e.clientX; tip.value.y = e.clientY }
}
function onLeave() {
  tip.value.visible = false
}

watch([variable, () => store.estacionActiva], cargar)
onMounted(cargar)
</script>

<template>
  <div class="cmp-modelos">
    <header>
      <h3>Comparación GFS vs ECMWF</h3>
      <p>Pronóstico diario · OpenMeteo <code>gfs_seamless</code> vs <code>ecmwf_ifs04</code></p>
    </header>

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

    <SkeletonLoader v-if="cargando" :height="220" />
    <p v-else-if="error" class="error">{{ error }}</p>
    <template v-else-if="filas.length">
      <div class="legend">
        <span><i class="swatch gfs" /> GFS</span>
        <span><i class="swatch ecmwf" /> ECMWF</span>
      </div>
      <svg
        class="cmp-svg"
        :viewBox="`0 0 ${W} ${H}`"
        preserveAspectRatio="xMidYMid meet"
        @mouseleave="onLeave"
      >
        <path :d="pathFor('gfs')" class="line gfs" fill="none" />
        <path :d="pathFor('ecmwf')" class="line ecmwf" fill="none" />
        <g v-for="(r, i) in filas" :key="r.fecha">
          <circle
            :cx="xAt(i, filas.length)"
            :cy="yAt(r.gfs)"
            r="4"
            class="dot gfs"
            @mouseenter="onEnter($event, i)"
            @mousemove="onMove"
          />
          <circle
            :cx="xAt(i, filas.length)"
            :cy="yAt(r.ecmwf)"
            r="4"
            class="dot ecmwf"
            @mouseenter="onEnter($event, i)"
            @mousemove="onMove"
          />
          <text
            :x="xAt(i, filas.length)"
            :y="H - 8"
            text-anchor="middle"
            class="xlab"
          >
            {{ r.fecha?.slice(5) }}
          </text>
        </g>
      </svg>
      <ChartTooltip :x="tip.x" :y="tip.y" :visible="tip.visible && tip.i >= 0">
        <strong>{{ filas[tip.i]?.fecha }}</strong><br />
        GFS: {{ filas[tip.i]?.gfs }}{{ unidad }}<br />
        ECMWF: {{ filas[tip.i]?.ecmwf }}{{ unidad }}<br />
        Δ {{ filas[tip.i]?.diferencia }}{{ unidad }} · {{ filas[tip.i]?.concordancia }}
      </ChartTooltip>
      <p v-if="nota" class="nota">{{ nota }}</p>
    </template>
    <p v-else class="muted">Sin datos de comparación.</p>
  </div>
</template>

<style scoped>
.cmp-modelos { background: var(--color-surface, #1e293b); border-radius: 8px; padding: 1rem; }
.cmp-modelos header h3 { margin: 0; font-size: 1rem; }
.cmp-modelos header p { margin: 0.25rem 0 0.75rem; font-size: 0.75rem; color: #6b7280; }
.vars { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 0.75rem; }
.vars button {
  padding: 0.35rem 0.65rem;
  border: 1px solid var(--color-border, #334155);
  border-radius: 6px;
  background: var(--color-surface, #1e293b);
  font-size: 0.75rem;
  cursor: pointer;
}
.vars button.active { background: #0284c7; color: #fff; border-color: #0284c7; }
.legend { display: flex; gap: 1rem; font-size: 0.72rem; color: #6b7280; margin-bottom: 0.35rem; }
.swatch { display: inline-block; width: 12px; height: 3px; margin-right: 0.35rem; vertical-align: middle; }
.swatch.gfs, .line.gfs, .dot.gfs { stroke: #22d3ee; fill: #22d3ee; }
.swatch.ecmwf, .line.ecmwf, .dot.ecmwf { stroke: #a78bfa; fill: #a78bfa; }
.line { stroke-width: 2.5; }
.cmp-svg { width: 100%; height: auto; display: block; }
.xlab { font-size: 9px; fill: #9ca3af; }
.nota, .muted { font-size: 0.72rem; color: #6b7280; margin-top: 0.5rem; }
.error { color: #dc2626; font-size: 0.85rem; }
</style>
