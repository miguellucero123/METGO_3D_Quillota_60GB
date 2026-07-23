<script setup>
import { computed, ref } from 'vue'
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
import { formatoDiaCorto } from '@/utils/meteoDates'
import { exportarDatosCSV } from '@/utils/exportData'
import { exportarEchartsPng } from '@/utils/exportChart'
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

const props = defineProps({
  labels: { type: Array, default: () => [] },
  temperaturas: { type: Array, default: () => [] },
  precipitacion: { type: Array, default: () => [] },
  tempUnit: { type: String, default: '°C' },
  height: { type: Number, default: 280 },
  exportName: { type: String, default: 'combo_meteo' },
})

const axisLabels = computed(() =>
  props.labels.map((l) => {
    try {
      return formatoDiaCorto(l) || String(l)
    } catch {
      return String(l)
    }
  })
)

const chartOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: tooltipOscuro((params) => {
    let html = `<div style="font-weight:bold;margin-bottom:5px;border-bottom:1px solid #4b5563;padding-bottom:5px;">${params[0].axisValue}</div>`
    params.forEach((p) => {
      const unit = p.seriesName.includes('Temp') ? ` ${props.tempUnit}` : ' mm'
      html += `<div style="display:flex;justify-content:space-between;margin-top:2px;">
        <span style="color:${p.color};margin-right:12px;">● ${p.seriesName}</span>
        <b>${p.value ?? '—'}${unit}</b>
      </div>`
    })
    return html
  }),
  legend: leyendaSuperior(['Temperatura máx', 'Precipitación']),
  dataZoom: props.labels.length > 10 ? zoomSlider() : [{ type: 'inside', xAxisIndex: 0 }],
  grid: grillaBase(),
  xAxis: [ejeCategoria(axisLabels.value)],
  yAxis: [
    ejeValor(`Temp (${props.tempUnit})`, CHART_COLORS.verde, {
      position: 'left',
      axisLabel: { formatter: `{value} ${props.tempUnit}`, color: CHART_COLORS.texto },
    }),
    ejeValor('Lluvia (mm)', CHART_COLORS.azul, {
      position: 'right',
      splitLine: { show: false },
      axisLabel: { formatter: '{value} mm', color: CHART_COLORS.texto },
    }),
  ],
  series: [
    serieLineaVerde('Temperatura máx', props.temperaturas, { yAxisIndex: 0 }),
    serieBarrasAzules('Precipitación', props.precipitacion, { yAxisIndex: 1 }),
  ],
}))

function exportCsv() {
  const rows = props.labels.map((f, i) => ({
    fecha: f,
    temperatura_max: props.temperaturas[i],
    precipitacion_mm: props.precipitacion[i],
  }))
  exportarDatosCSV(rows, props.exportName)
}

const chartRef = ref(null)

function exportPng() {
  const inst = chartRef.value?.chart || chartRef.value
  exportarEchartsPng(inst, props.exportName || 'combo_meteo')
}
</script>

<template>
  <div class="combo-meteo">
    <div class="combo-meteo__ctrl">
      <button type="button" class="export" @click="exportCsv">CSV</button>
      <button type="button" class="export" @click="exportPng">PNG</button>
    </div>
    <div v-if="!labels.length" class="empty">Sin datos combinados</div>
    <div v-else class="chart-wrap" :style="{ height: height + 'px' }">
      <v-chart ref="chartRef" class="chart" :option="chartOption" autoresize />
    </div>
  </div>
</template>

<style scoped>
.combo-meteo { width: 100%; }
.combo-meteo__ctrl { display: flex; justify-content: flex-end; margin-bottom: 0.35rem; }
.export {
  padding: 0.3rem 0.6rem;
  font-size: 0.75rem;
  border-radius: 6px;
  border: 1px solid var(--color-border, #334155);
  background: var(--color-surface, #1e293b);
  color: var(--color-text, #f1f5f9);
  cursor: pointer;
}
.chart-wrap {
  width: 100%;
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  padding: 0.5rem;
}
.chart { width: 100%; height: 100%; }
.empty {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-muted, #94a3b8);
  border: 1px dashed var(--color-border, #334155);
  border-radius: 8px;
}
</style>
