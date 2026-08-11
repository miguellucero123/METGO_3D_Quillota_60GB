<script setup>
import { computed, ref, watch, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { useMetgoStore } from '@/stores/metgo'
import { fetchComparacionModelos } from '@/api/metgoApi'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import {
  CHART_COLORS,
  tooltipOscuro,
  leyendaSuperior,
  zoomSlider,
  zoomInside,
  grillaBase,
  ejeCategoria,
  ejeValor,
  serieLineaVerde,
} from '@/utils/echartsTheme'

use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
])

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

const filas = computed(() => datos.value?.comparacion ?? [])
const unidad = computed(() => variables.find((v) => v.id === variable.value)?.unidad ?? '')
const nota = computed(() => datos.value?.nota ?? '')

const chartOption = computed(() => {
  const labels = filas.value.map((r) => String(r.fecha || '').slice(5))
  return {
    backgroundColor: 'transparent',
    tooltip: tooltipOscuro((params) => {
      let html = `<div style="font-weight:bold;margin-bottom:4px;">${params[0].axisValue}</div>`
      params.forEach((p) => {
        html += `<div><span style="color:${p.color}">● ${p.seriesName}</span> <b>${p.value ?? '—'} ${unidad.value}</b></div>`
      })
      return html
    }),
    legend: leyendaSuperior(['GFS', 'ECMWF']),
    dataZoom: filas.value.length > 8 ? zoomSlider() : [zoomInside()],
    grid: grillaBase(),
    xAxis: [ejeCategoria(labels)],
    yAxis: [
      ejeValor(unidad.value, CHART_COLORS.verde, {
        axisLabel: { formatter: `{value} ${unidad.value}`, color: CHART_COLORS.texto },
      }),
    ],
    series: [
      serieLineaVerde(
        'GFS',
        filas.value.map((r) => r.gfs),
        { symbolSize: 6 }
      ),
      {
        name: 'ECMWF',
        type: 'line',
        data: filas.value.map((r) => r.ecmwf),
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: CHART_COLORS.celeste },
        lineStyle: { width: 3, color: CHART_COLORS.celeste, type: 'dashed' },
      },
    ],
  }
})

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

watch([variable, () => store.estacionActiva], cargar)
onMounted(cargar)
</script>

<template>
  <div class="cmp-modelos">
    <header>
      <h3>Comparación GFS vs ECMWF</h3>
      <p>Pronóstico diario · OpenMeteo gfs_seamless vs ecmwf_ifs04</p>
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

    <SkeletonLoader v-if="cargando" :rows="4" />
    <p v-else-if="error" class="err">{{ error }}</p>
    <div v-else-if="filas.length" class="chart-wrap">
      <v-chart class="chart" :option="chartOption" autoresize />
    </div>
    <p v-else class="empty">Sin comparación disponible</p>
    <p v-if="nota" class="nota">{{ nota }}</p>
  </div>
</template>

<style scoped>
.cmp-modelos {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  padding: 1rem;
}
.cmp-modelos header h3 { margin: 0; font-size: 1rem; }
.cmp-modelos header p { margin: 0.25rem 0 0.75rem; font-size: 0.78rem; color: var(--color-text-muted, #94a3b8); }
.vars { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 0.75rem; }
.vars button {
  padding: 0.3rem 0.65rem;
  border-radius: 6px;
  border: 1px solid var(--color-border, #334155);
  background: transparent;
  color: var(--color-text, #f1f5f9);
  font-size: 0.78rem;
  cursor: pointer;
}
.vars button.active { background: #0284c7; border-color: #0284c7; color: #fff; }
.chart-wrap { width: 100%; height: 320px; }
.chart { width: 100%; height: 100%; }
.err, .empty { text-align: center; padding: 1.5rem; color: var(--color-text-muted, #94a3b8); }
.nota { font-size: 0.72rem; color: #94a3b8; margin: 0.5rem 0 0; }
</style>
