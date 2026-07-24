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
  temperatura_max: { label: 'T. máx', unit: '°C', umbralOk: 1.0, umbralWarn: 2.5 },
  temperatura_min: { label: 'T. mín', unit: '°C', umbralOk: 1.0, umbralWarn: 2.5 },
  humedad: { label: 'Humedad', unit: '%', umbralOk: 5, umbralWarn: 12 },
  precipitacion: { label: 'Lluvia', unit: 'mm', umbralOk: 1.5, umbralWarn: 4 },
  presion: { label: 'Presión', unit: 'hPa', umbralOk: 2, umbralWarn: 5 },
  viento: { label: 'Viento', unit: 'm/s', umbralOk: 1.5, umbralWarn: 3.5 },
}

const COLOR_OK = '#10b981'
const COLOR_WARN = '#f59e0b'
const COLOR_BAD = '#ef4444'
const COLOR_NA = CHART_COLORS.azul

function colorPorError(absDelta, umbralOk, umbralWarn) {
  if (absDelta == null || Number.isNaN(absDelta)) return COLOR_NA
  if (absDelta <= umbralOk) return COLOR_OK
  if (absDelta <= umbralWarn) return COLOR_WARN
  return COLOR_BAD
}

function etiquetaDelta(delta, unit) {
  if (delta == null || Number.isNaN(delta)) return '—'
  const sign = delta > 0 ? '+' : ''
  return `${sign}${delta.toFixed(1)} ${unit || ''}`.trim()
}

const rows = computed(() =>
  (props.items || [])
    .filter((r) => r.prediccion != null && !Number.isNaN(Number(r.prediccion)))
    .map((r) => {
      const meta = DOMAIN[r.variable] || {
        label: r.label || r.variable,
        unit: (r.unidad || '').trim() || '',
        umbralOk: 1,
        umbralWarn: 3,
      }
      const actual = Number(r.actual)
      const pred = Number(r.prediccion)
      const actualOk = !Number.isNaN(actual)
      const delta = actualOk ? pred - actual : null
      const absDelta = delta == null ? null : Math.abs(delta)
      return {
        key: r.variable,
        label: meta.label || r.label,
        unit: meta.unit,
        actual: actualOk ? actual : null,
        prediccion: pred,
        delta,
        absDelta,
        colorMl: colorPorError(absDelta, meta.umbralOk, meta.umbralWarn),
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
    const dLabel = etiquetaDelta(row?.delta, row?.unit)
    const dColor = row?.colorMl || COLOR_NA
    html += `<div style="margin-top:6px;border-top:1px solid #475569;padding-top:4px;">`
    html += `<span style="color:${dColor}">Δ ML−obs</span> <b style="color:${dColor}">${dLabel}</b>`
    html += `</div>`
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
      data: rows.value.map((r) => ({
        value: r.prediccion,
        itemStyle: { color: r.colorMl, borderRadius: [4, 4, 0, 0] },
      })),
      barMaxWidth: 28,
      label: {
        show: true,
        position: 'top',
        color: CHART_COLORS.texto,
        fontSize: 10,
        formatter: (p) => {
          const row = rows.value[p.dataIndex]
          if (!row || row.delta == null) return ''
          const sign = row.delta > 0 ? '+' : ''
          return `${sign}${row.delta.toFixed(1)}`
        },
      },
    },
  ],
}))

function exportCsv() {
  exportarDatosCSV(
    rows.value.map((r) => ({
      variable: r.label,
      observado: r.actual,
      prediccion: r.prediccion,
      delta: r.delta,
      unidad: r.unit,
    })),
    props.exportName
  )
}
</script>

<template>
  <div class="ml-proj">
    <div class="ml-proj__ctrl">
      <span class="ml-proj__legend" title="Color de la barra ML según |Δ|">
        <i class="swatch ok" /> ok
        <i class="swatch warn" /> medio
        <i class="swatch bad" /> alto
      </span>
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
.ml-proj__ctrl {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.35rem;
}
.ml-proj__legend {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.72rem;
  color: var(--color-muted, #94a3b8);
}
.swatch {
  display: inline-block;
  width: 0.65rem;
  height: 0.65rem;
  border-radius: 2px;
}
.swatch.ok { background: #10b981; }
.swatch.warn { background: #f59e0b; }
.swatch.bad { background: #ef4444; }
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
