<script setup>
import { ref, computed, watch } from 'vue'
import { useMetgoStore } from '@/stores/metgo'
import { fetchPrecipitacionCalibrada } from '@/api/metgoApi'
import { precipColor, popColor, etiquetaIntensidad, severidadAlertaColor } from '@/utils/colorScale'
import { exportarDatosCSV } from '@/utils/exportData'

const store = useMetgoStore()
const cargando = ref(false)
const modo = ref('precip')
const resolucion = ref('3h')
const datos = ref(null)
const errorMsg = ref(null)
const tooltip = ref(null)

async function cargar() {
  cargando.value = true
  errorMsg.value = null
  try {
    datos.value = await fetchPrecipitacionCalibrada(
      store.estacionActiva,
      7,
      resolucion.value
    )
  } catch (err) {
    datos.value = null
    errorMsg.value = err.message
  } finally {
    cargando.value = false
  }
}

watch([() => store.estacionActiva, resolucion], cargar, { immediate: true })

const es3h = computed(() => resolucion.value === '3h' || datos.value?.resolucion === '3h')

const fechas = computed(() => datos.value?.fechas ?? [])
const precip = computed(() => datos.value?.precipitacion_calibrada ?? datos.value?.datos?.precipitacion ?? [])
const pop = computed(() => datos.value?.pop ?? datos.value?.datos?.pop ?? [])
const p10 = computed(() => datos.value?.precipitacion_p10 ?? [])
const p90 = computed(() => datos.value?.precipitacion_p90 ?? [])
const intensidad = computed(() => datos.value?.intensidad ?? datos.value?.datos?.intensidad ?? [])

const acumulado = computed(() => {
  let s = 0
  return precip.value.map((p) => {
    s += p || 0
    return Math.round(s * 10) / 10
  })
})

const maxY = computed(() => Math.max(es3h.value ? 2 : 5, ...precip.value, ...p90.value, ...acumulado.value))

function fmtEje(f) {
  const s = String(f)
  if (es3h.value && s.includes('T')) {
    const [d, t] = s.split('T')
    const hh = t?.slice(0, 2) ?? ''
    const [, mm, dd] = d.split('-')
    return `${dd}/${mm} ${hh}h`
  }
  return s.slice(5)
}

const barras = computed(() => {
  const n = fechas.value.length || 1
  const barW = es3h.value ? 3.2 : 100 / n
  const gap = es3h.value ? 0.35 : 0
  return fechas.value.map((f, i) => ({
    fecha: f,
    x: es3h.value ? 4 + i * (barW + gap) : i * (100 / n) + (100 / n) * 0.15,
    w: es3h.value ? barW : (100 / n) * 0.7,
    h: ((precip.value[i] || 0) / maxY.value) * 70,
    color: precipColor(precip.value[i]),
    val: precip.value[i],
    pop: pop.value[i],
    int: intensidad.value[i],
    p10: p10.value[i],
    p90: p90.value[i],
    label: fmtEje(f),
    showLabel: es3h.value ? i % 4 === 0 : true,
  }))
})

const chartWidth = computed(() => (es3h.value ? Math.max(100, barras.value.length * 3.55 + 8) : 100))

const stats = computed(() => ({
  total: precip.value.reduce((a, b) => a + (b || 0), 0).toFixed(1),
  max: Math.max(0, ...precip.value).toFixed(1),
  ventanasLluvia: precip.value.filter((p) => p > (es3h.value ? 0.2 : 1)).length,
  calibrado: datos.value?.metadatos?.calibrado ?? false,
}))

function showTip(evt, b) {
  tooltip.value = {
    x: evt.clientX,
    y: evt.clientY,
    html: `${b.label}: ${b.val} mm · PoP ${b.pop ?? 0}% · ${etiquetaIntensidad(b.val)}${
      es3h.value ? ` · ${b.int ?? 0} mm/h` : ''
    }`,
  }
}

function exportCsv() {
  const rows = fechas.value.map((f, i) => ({
    fecha: f,
    precipitacion_mm: precip.value[i],
    pop_pct: pop.value[i],
    intensidad_mm_h: intensidad.value[i],
    p10: p10.value[i],
    p90: p90.value[i],
    resolucion: resolucion.value,
  }))
  exportarDatosCSV(rows, `precip_${resolucion.value}_${store.estacionActiva}`)
}
</script>

<template>
  <div class="precip-chart">
    <header class="precip-chart__head">
      <div>
        <h3>Pronóstico de precipitación</h3>
        <p v-if="datos" class="meta">
          {{ es3h ? 'Ventanas de 3 h' : 'Acumulado diario' }} ·
          Fuente: {{ datos.metadatos?.fuente ?? 'openmeteo' }}
          <span v-if="stats.calibrado" class="badge badge--cal">Calibrado local</span>
          <span v-if="datos.factor_bias"> · bias {{ datos.factor_bias }}</span>
        </p>
      </div>
      <div class="controls">
        <button type="button" :class="{ active: resolucion === '3h' }" @click="resolucion = '3h'">
          Cada 3 h
        </button>
        <button type="button" :class="{ active: resolucion === 'dia' }" @click="resolucion = 'dia'">
          Por día
        </button>
        <button type="button" :class="{ active: modo === 'precip' }" @click="modo = 'precip'">Lluvia</button>
        <button type="button" :class="{ active: modo === 'acum' }" @click="modo = 'acum'">Acumulado</button>
        <button type="button" :class="{ active: modo === 'pop' }" @click="modo = 'pop'">PoP</button>
        <button type="button" class="export" @click="exportCsv">CSV</button>
      </div>
    </header>

    <div v-if="cargando" class="skeleton">Cargando pronóstico…</div>
    <div v-else-if="errorMsg" class="empty error-msg">{{ errorMsg }}</div>
    <div v-else-if="!datos" class="empty">Sin datos de precipitación</div>

    <template v-else>
      <div class="chart-scroll" :class="{ 'chart-scroll--wide': es3h }">
        <svg
          :viewBox="`0 0 ${chartWidth} 85`"
          class="chart-svg"
          :style="{ minWidth: es3h ? `${Math.max(320, barras.length * 14)}px` : '100%' }"
          role="img"
          aria-label="Gráfico precipitación"
        >
          <line x1="8" y1="75" :x2="chartWidth - 2" y2="75" stroke="var(--color-border, #334155)" stroke-width="0.3" />
          <template v-if="modo === 'precip'">
            <rect
              v-for="(b, i) in barras"
              :key="'b' + i"
              :x="b.x"
              :y="75 - b.h"
              :width="b.w"
              :height="b.h"
              :fill="b.color"
              rx="1.5"
              @mouseenter="showTip($event, b)"
              @mouseleave="tooltip = null"
            />
            <polyline
              v-if="p10.length"
              :points="barras.map((b, i) => `${b.x + b.w / 2},${75 - (p10[i] / maxY) * 70}`).join(' ')"
              fill="none"
              stroke="var(--color-text-muted, #94a3b8)"
              stroke-width="0.5"
              stroke-dasharray="2 2"
            />
            <polyline
              v-if="p90.length"
              :points="barras.map((b, i) => `${b.x + b.w / 2},${75 - (p90[i] / maxY) * 70}`).join(' ')"
              fill="none"
              stroke="var(--color-text, #e2e8f0)"
              stroke-width="0.5"
              stroke-dasharray="2 2"
            />
          </template>
          <template v-else-if="modo === 'acum'">
            <polyline
              :points="barras.map((b, i) => `${b.x + b.w / 2},${75 - (acumulado[i] / maxY) * 70}`).join(' ')"
              fill="none"
              stroke="#0284c7"
              stroke-width="0.8"
            />
          </template>
          <template v-else>
            <rect
              v-for="(b, i) in barras"
              :key="'p' + i"
              :x="b.x"
              :y="75 - ((pop[i] || 0) / 100) * 70"
              :width="b.w"
              :height="((pop[i] || 0) / 100) * 70"
              :fill="popColor(pop[i])"
              opacity="0.85"
            />
          </template>
          <text
            v-for="(b, i) in barras"
            v-show="b.showLabel"
            :key="'l' + i"
            :x="b.x + b.w / 2"
            y="82"
            text-anchor="middle"
            :font-size="es3h ? '2.5' : '2.8'"
            fill="var(--color-text-muted, #94a3b8)"
          >
            {{ b.label }}
          </text>
        </svg>
      </div>

      <div class="stats">
        <div class="stat">
          <span>Total 7d</span><strong>{{ stats.total }} mm</strong>
        </div>
        <div class="stat">
          <span>{{ es3h ? 'Máx. ventana 3 h' : 'Máximo día' }}</span><strong>{{ stats.max }} mm</strong>
        </div>
        <div class="stat">
          <span>{{ es3h ? 'Ventanas con lluvia' : 'Días lluvia' }}</span
          ><strong>{{ stats.ventanasLluvia }}</strong>
        </div>
        <div v-if="datos.alerta_lluvia_fuerte" class="stat stat--alert">
          <span>Alerta</span><strong>Lluvia fuerte próxima</strong>
        </div>
      </div>

      <div class="leyenda">
        <span><i style="background:#bfdbfe" /> 0–2 mm</span>
        <span><i style="background:#60a5fa" /> 2–10 mm</span>
        <span><i style="background:#1e40af" /> 10–25 mm</span>
        <span><i :style="{ background: severidadAlertaColor('rojo') }" /> &gt;25 mm</span>
        <span v-if="es3h" class="hint-scroll">Desplaza horizontalmente para ver todas las ventanas</span>
      </div>
    </template>

    <div v-if="tooltip" class="tip" :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
      {{ tooltip.html }}
    </div>
  </div>
</template>

<style scoped>
.precip-chart {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  padding: 1rem;
  position: relative;
}
.precip-chart__head {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}
.precip-chart__head h3 {
  margin: 0;
  font-size: 1rem;
}
.meta {
  margin: 0.25rem 0 0;
  font-size: 0.78rem;
  color: #6b7280;
}
.badge--cal {
  background: rgba(29, 78, 216, 0.2);
  color: #60a5fa;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  margin-left: 0.35rem;
}
.controls {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
}
.controls button {
  padding: 0.35rem 0.65rem;
  border: 1px solid var(--color-border, #334155);
  background: var(--color-surface, #1e293b);
  color: var(--color-text, #f1f5f9);
  border-radius: 6px;
  font-size: 0.78rem;
  cursor: pointer;
}
.controls button.active {
  background: #0284c7;
  color: #fff;
  border-color: #0284c7;
}
.controls .export {
  background: var(--color-border, #334155);
}
.chart-scroll {
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 4px;
}
.chart-scroll::-webkit-scrollbar {
  height: 6px;
}
.chart-scroll::-webkit-scrollbar-track {
  background: var(--color-surface);
}
.chart-scroll::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 4px;
}
.chart-scroll--wide {
  border: 1px solid var(--color-border, #334155);
  border-radius: 6px;
  background: var(--color-background, rgba(15, 23, 42, 0.4));
}
.chart-svg {
  display: block;
  height: 220px;
  width: 100%;
}
.skeleton,
.empty {
  padding: 3rem 2rem;
  text-align: center;
  color: var(--color-text-muted, #94a3b8);
  background: var(--color-surface, #1e293b);
  border-radius: 8px;
  border: 1px dashed var(--color-border);
}
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.5rem;
  margin-top: 0.75rem;
}
.stat {
  background: rgba(2, 132, 199, 0.1);
  border-left: 3px solid #0284c7;
  padding: 0.5rem 0.65rem;
  border-radius: 6px;
  font-size: 0.78rem;
}
.stat strong {
  display: block;
  font-size: 1rem;
  color: #38bdf8;
}
.stat--alert {
  background: rgba(239, 68, 68, 0.1);
  border-color: #ef4444;
}
.stat--alert strong {
  color: #f87171;
}
.leyenda {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 0.75rem;
  font-size: 0.72rem;
  color: #4b5563;
  align-items: center;
}
.leyenda i {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 2px;
  margin-right: 4px;
  vertical-align: middle;
}
.hint-scroll {
  color: #9ca3af;
  font-style: italic;
}
.tip {
  position: fixed;
  z-index: 50;
  background: #1f2937;
  color: #fff;
  padding: 0.35rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  pointer-events: none;
  transform: translate(-50%, -120%);
  max-width: 280px;
}
</style>
