<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { exportarDatosCSV } from '@/utils/exportData'
import {
  CHART_COLORS,
  tooltipOscuro,
  leyendaSuperior,
  grillaBase,
} from '@/utils/echartsTheme'

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent, LegendComponent])

const props = defineProps({
  items: { type: Array, default: () => [] },
  exportName: { type: String, default: 'ml_proyeccion' },
})

const DOMAIN = {
  temperatura_max: { label: 'T. máx', unit: '°C' },
  temperatura_min: { label: 'T. mín', unit: '°C' },
  humedad: { label: 'Humedad', unit: '%' },
  precipitacion: { label: 'Lluvia', unit: 'mm' },
  presion: { label: 'Presión', unit: 'hPa' },
  viento: { label: 'Viento', unit: 'm/s' },
}

const rows = computed(() =>
  (props.items || [])
    .filter((r) => r.prediccion != null && !Number.isNaN(Number(r.prediccion)))
    .map((r) => {
      const meta = DOMAIN[r.variable] || {
        label: r.label || r.variable,
        unit: (r.unidad || '').trim() || '',
      }
      const actual = Number(r.actual)
      const pred = Number(r.prediccion)
      return {
        key: r.variable,
        label: meta.label || r.label,
        unit: meta.unit,
        actual: Number.isNaN(actual) ? null : actual,
        prediccion: pred,
      }
    })
)

const chartOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: tooltipOscuro((params) => {
    const i = params[0].dataIndex
    const row = rows.value[i]
    let html = `<div style="font-weight:bold;margin-bottom:4px;">${row?.label}</div>`
    params.forEach((p) => {
      html += `<div><span style="color:${p.color}">● ${p.seriesName}</span> <b>${p.value ?? '—'} ${row?.unit || ''}</b></div>`
    })
    return html
  }),
  legend: leyendaSuperior(['Observado', 'Modelo ML']),
  grid: grillaBase(),
  xAxis: [
    {
      type: 'category',
      data: rows.value.map((r) => r.label),
      axisLine: { lineStyle: { color: CHART_COLORS.eje } },
      axisLabel: { color: CHART_COLORS.texto, rotate: rows.value.length > 4 ? 20 : 0 },
    },
  ],
  yAxis: [
    {
      type: 'value',
      axisLine: { show: true, lineStyle: { color: CHART_COLORS.verde } },
      splitLine: { lineStyle: { color: CHART_COLORS.grilla, type: 'dashed' } },
      axisLabel: { color: CHART_COLORS.texto },
    },
  ],
  series: [
    {
      name: 'Observado',
      type: 'bar',
      data: rows.value.map((r) => r.actual),
      itemStyle: { color: '#1a5f4a', borderRadius: [4, 4, 0, 0] },
      barMaxWidth: 28,
    },
    {
      name: 'Modelo ML',
      type: 'bar',
      data: rows.value.map((r) => r.prediccion),
      itemStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: CHART_COLORS.celeste },
            { offset: 1, color: CHART_COLORS.azul },
          ],
        },
        borderRadius: [4, 4, 0, 0],
      },
      barMaxWidth: 28,
    },
  ],
}))

function exportCsv() {
  exportarDatosCSV(
    rows.value.map((r) => ({
      variable: r.label,
      observado: r.actual,
      prediccion: r.prediccion,
      unidad: r.unit,
    })),
    props.exportName
  )
}
</script>

<template>
  <div class="ml-proj">
    <div class="ml-proj__ctrl">
      <button type="button" @click="exportCsv">CSV</button>
    </div>
    <div v-if="!rows.length" class="empty">Sin proyecciones ML</div>
    <div v-else class="chart-wrap">
      <v-chart class="chart" :option="chartOption" autoresize />
    </div>
  </div>
</template>

<style scoped>
.ml-proj { width: 100%; }
.ml-proj__ctrl { display: flex; justify-content: flex-end; margin-bottom: 0.35rem; }
.ml-proj__ctrl button {
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
  height: 320px;
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
  border: 1px dashed var(--color-border);
  border-radius: 8px;
}
</style>
