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
} from 'echarts/components'
import VChart from 'vue-echarts'
import { useMetgoStore } from '@/stores/metgo'
import { fetchPrecipitacionHistorico } from '@/api/metgoApi'
import { exportarDatosCSV } from '@/utils/exportData'
import {
  CHART_COLORS,
  tooltipOscuro,
  leyendaSuperior,
  zoomSlider,
  grillaBase,
  ejeCategoria,
  ejeValor,
  serieBarrasAzules,
  serieLineaVerde,
} from '@/utils/echartsTheme'

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
])

const store = useMetgoStore()
const diasRango = ref(30)
const cargando = ref(false)
const datos = ref([])
const estadisticas = ref(null)
const errorMsg = ref(null)

async function cargar() {
  cargando.value = true
  errorMsg.value = null
  const hasta = new Date()
  const desde = new Date()
  desde.setDate(desde.getDate() - diasRango.value)
  try {
    const res = await fetchPrecipitacionHistorico(
      store.estacionActiva,
      desde.toISOString().slice(0, 10),
      hasta.toISOString().slice(0, 10)
    )
    datos.value = res.datos ?? []
    estadisticas.value = res.estadisticas ?? null
  } catch (err) {
    datos.value = []
    estadisticas.value = null
    errorMsg.value = err.message
  } finally {
    cargando.value = false
  }
}

watch(() => store.estacionActiva, cargar, { immediate: true })
watch(diasRango, cargar)

function fmt(f) {
  return new Date(f).toLocaleDateString('es-CL', { month: 'short', day: 'numeric' })
}

const chartOption = computed(() => {
  const labels = datos.value.map((d) => fmt(d.fecha))
  const precip = datos.value.map((d) => d.precipitacion)
  let s = 0
  const acumulado = precip.map((p) => {
    s += p || 0
    return Math.round(s * 10) / 10
  })

  return {
    backgroundColor: 'transparent',
    tooltip: tooltipOscuro((params) => {
      let html = `<div style="font-weight:bold;margin-bottom:5px;border-bottom:1px solid #4b5563;padding-bottom:5px;">${params[0].axisValue}</div>`
      params.forEach((p) => {
        html += `<div style="display:flex;justify-content:space-between;margin-top:2px;">
                   <span style="color:${p.color};margin-right:15px;">● ${p.seriesName}</span>
                   <b>${p.value ?? 0} mm</b>
                 </div>`
      })
      return html
    }),
    legend: leyendaSuperior(['Precipitación diaria', 'Acumulado']),
    dataZoom: zoomSlider(),
    grid: grillaBase(),
    xAxis: [ejeCategoria(labels)],
    yAxis: [
      ejeValor('Lluvia (mm)', CHART_COLORS.azul, {
        position: 'left',
        axisLabel: { formatter: '{value} mm', color: CHART_COLORS.texto },
      }),
      ejeValor('Acumulado (mm)', CHART_COLORS.verde, {
        position: 'right',
        splitLine: { show: false },
        axisLabel: { formatter: '{value} mm', color: CHART_COLORS.texto },
      }),
    ],
    series: [
      serieBarrasAzules('Precipitación diaria', precip, { yAxisIndex: 0 }),
      serieLineaVerde('Acumulado', acumulado, { yAxisIndex: 1, symbolSize: 4 }),
    ],
  }
})
</script>

<template>
  <div class="hist-precip">
    <div class="hist-precip__ctrl">
      <div class="rango">
        <button v-for="d in [7, 30, 90]" :key="d" type="button" :class="{ active: diasRango === d }" @click="diasRango = d">
          {{ d }}d
        </button>
      </div>
      <button type="button" @click="exportarDatosCSV(datos, `hist_precip_${store.estacionActiva}`)">CSV</button>
    </div>

    <div v-if="cargando" class="loading">Cargando histórico…</div>
    <div v-else-if="errorMsg" class="loading error-msg">{{ errorMsg }}</div>
    <div v-else-if="datos.length > 0" class="chart-wrap">
      <v-chart class="chart" :option="chartOption" autoresize />
    </div>
    <div v-else class="loading">Sin datos de precipitación en el rango</div>

    <div v-if="estadisticas" class="stats">
      <div><span>Total</span><strong>{{ estadisticas.precipitacion_total }} mm</strong></div>
      <div><span>Días lluvia</span><strong>{{ estadisticas.dias_con_lluvia }}</strong></div>
      <div><span>Máximo</span><strong>{{ estadisticas.precipitacion_max_dia }} mm</strong></div>
    </div>
  </div>
</template>

<style scoped>
.hist-precip { padding: 0.5rem 0; }
.hist-precip__ctrl { display: flex; justify-content: space-between; margin-bottom: 0.75rem; }
.rango { display: flex; gap: 0.35rem; }
.rango button, .hist-precip__ctrl > button {
  padding: 0.35rem 0.6rem;
  border: 1px solid var(--color-border, #334155);
  border-radius: 6px;
  background: var(--color-surface, #1e293b);
  color: var(--color-text, #f1f5f9);
  font-size: 0.78rem;
  cursor: pointer;
}
.rango button.active { background: #0284c7; color: #fff; border-color: #0284c7; }
.chart-wrap {
  width: 100%;
  height: 380px;
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  padding: 0.75rem;
}
.chart { width: 100%; height: 100%; }
.stats {
  display: flex; gap: 1rem; margin-top: 1rem;
  font-size: 0.8rem;
  background: var(--color-background, rgba(15, 23, 42, 0.4));
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--color-border);
}
.stats div span { color: var(--color-text-muted); }
.stats strong { display: block; font-size: 1.1rem; color: #38bdf8; margin-top: 0.2rem; }
.loading {
  padding: 2.5rem; text-align: center; color: var(--color-text-muted, #94a3b8);
  background: var(--color-surface, #1e293b);
  border-radius: 8px;
  border: 1px dashed var(--color-border);
}
</style>
