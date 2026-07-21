<script setup>
import { ref, computed, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
  MarkLineComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { useMetgoStore } from '@/stores/metgo'
import { fetchPrecipitacionCalibrada } from '@/api/metgoApi'
import { exportarDatosCSV } from '@/utils/exportData'

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
  MarkLineComponent,
])

const store = useMetgoStore()
const cargando = ref(false)
const resolucion = ref('3h')
const datos = ref(null)
const errorMsg = ref(null)

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

const stats = computed(() => ({
  total: precip.value.reduce((a, b) => a + (b || 0), 0).toFixed(1),
  max: Math.max(0, ...precip.value).toFixed(1),
  ventanasLluvia: precip.value.filter((p) => p > (es3h.value ? 0.2 : 1)).length,
  calibrado: datos.value?.metadatos?.calibrado ?? false,
}))

const chartOption = computed(() => {
  const labels = fechas.value.map(fmtEje)
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross', animation: false },
      backgroundColor: 'rgba(17, 24, 39, 0.9)',
      borderColor: 'rgba(0, 255, 170, 0.3)',
      textStyle: { color: '#f3f4f6' },
      formatter: (params) => {
        let html = `<div style="font-weight:bold;margin-bottom:5px;border-bottom:1px solid #4b5563;padding-bottom:5px;">${params[0].axisValue}</div>`
        params.forEach((p) => {
          const unit = p.seriesName.includes('Probabilidad') ? '%' : 'mm'
          html += `<div style="display:flex;justify-content:space-between;margin-top:2px;">
                     <span style="color:${p.color};margin-right:15px;">● ${p.seriesName}</span>
                     <b>${p.value ?? 0} ${unit}</b>
                   </div>`
        })
        const i = params[0].dataIndex
        if (es3h.value && intensidad.value[i] != null) {
          html += `<div style="margin-top:4px;color:#9ca3af;font-size:11px;">Intensidad: ${intensidad.value[i]} mm/h</div>`
        }
        return html
      },
    },
    legend: {
      data: ['Precipitación', 'Acumulado', 'Probabilidad Lluvia'],
      textStyle: { color: '#9ca3af' },
      top: 0,
    },
    dataZoom: [
      { type: 'inside', xAxisIndex: 0, filterMode: 'filter' },
      {
        type: 'slider',
        xAxisIndex: 0,
        height: 25,
        bottom: 5,
        borderColor: 'rgba(0, 255, 170, 0.2)',
        textStyle: { color: '#9ca3af' },
      },
    ],
    grid: {
      top: '15%',
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true,
    },
    xAxis: [
      {
        type: 'category',
        data: labels,
        axisLine: { lineStyle: { color: '#374151' } },
        axisLabel: { color: '#9ca3af' },
      },
    ],
    yAxis: [
      {
        type: 'value',
        name: 'Lluvia (mm)',
        position: 'left',
        axisLine: { show: true, lineStyle: { color: '#0ea5e9' } },
        splitLine: { lineStyle: { color: '#1f2937', type: 'dashed' } },
        axisLabel: { formatter: '{value} mm' },
      },
      {
        type: 'value',
        name: 'Acumulado (mm)',
        position: 'right',
        axisLine: { show: true, lineStyle: { color: '#00ffaa' } },
        splitLine: { show: false },
        axisLabel: { formatter: '{value} mm' },
      },
      {
        type: 'value',
        name: 'Prob (%)',
        position: 'right',
        offset: 55,
        max: 100,
        axisLine: { show: true, lineStyle: { color: '#f59e0b' } },
        splitLine: { show: false },
        axisLabel: { show: false },
      },
    ],
    series: [
      {
        name: 'Precipitación',
        type: 'bar',
        yAxisIndex: 0,
        data: precip.value,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: '#38bdf8' },
              { offset: 1, color: '#0284c7' },
            ],
          },
          borderRadius: [4, 4, 0, 0],
        },
        barMaxWidth: 30,
      },
      {
        name: 'Acumulado',
        type: 'line',
        yAxisIndex: 1,
        data: acumulado.value,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: '#00ffaa' },
        lineStyle: { width: 3, shadowColor: 'rgba(0, 255, 170, 0.5)', shadowBlur: 10 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(0, 255, 170, 0.25)' },
              { offset: 1, color: 'rgba(0, 255, 170, 0.0)' },
            ],
          },
        },
      },
      {
        name: 'Probabilidad Lluvia',
        type: 'line',
        yAxisIndex: 2,
        data: pop.value,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#f59e0b', width: 2, type: 'dashed' },
      },
    ],
  }
})

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
        <button type="button" class="export" @click="exportCsv">CSV</button>
      </div>
    </header>

    <div v-if="cargando" class="skeleton">Cargando pronóstico…</div>
    <div v-else-if="errorMsg" class="empty error-msg">{{ errorMsg }}</div>
    <div v-else-if="!datos" class="empty">Sin datos de precipitación</div>

    <template v-else>
      <div class="chart-wrap">
        <v-chart class="chart" :option="chartOption" autoresize />
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
    </template>
  </div>
</template>

<style scoped>
.precip-chart {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: var(--radius-lg, 10px);
  padding: 1rem;
  position: relative;
  box-shadow: var(--shadow-md, none);
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
  color: var(--color-text-muted, #94a3b8);
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
.chart-wrap {
  width: 100%;
  height: 420px;
}
.chart {
  width: 100%;
  height: 100%;
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
</style>
