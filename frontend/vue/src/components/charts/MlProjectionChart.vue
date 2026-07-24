<script setup>
import { computed, ref } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  MarkLineComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { exportarDatosCSV } from '@/utils/exportData'
import {
  CHART_COLORS,
  tooltipOscuro,
  leyendaSuperior,
} from '@/utils/echartsTheme'

use([
  CanvasRenderer,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  MarkLineComponent,
])

const props = defineProps({
  items: { type: Array, default: () => [] },
  exportName: { type: String, default: 'ml_proyeccion' },
})

/** Facetas: misma escala física por panel (opción 1). */
const FACETS = [
  {
    id: 'temp',
    title: 'Temperatura (°C)',
    keys: ['temperatura_max', 'temperatura_min'],
    unit: '°C',
  },
  {
    id: 'humedad',
    title: 'Humedad (%)',
    keys: ['humedad'],
    unit: '%',
    yMin: 0,
    yMax: 100,
  },
  {
    id: 'presion',
    title: 'Presión (hPa)',
    keys: ['presion'],
    unit: 'hPa',
    yMin: 900,
    yMax: 1100,
  },
  {
    id: 'lluvia_viento',
    title: 'Lluvia (mm) · Viento',
    keys: ['precipitacion', 'viento'],
    unit: '',
  },
]

const DOMAIN = {
  temperatura_max: { label: 'T. máx', unit: '°C', umbralOk: 1.0, umbralWarn: 2.5 },
  temperatura_min: { label: 'T. mín', unit: '°C', umbralOk: 1.0, umbralWarn: 2.5 },
  humedad: { label: 'Humedad', unit: '%', umbralOk: 5, umbralWarn: 12 },
  precipitacion: { label: 'Lluvia', unit: 'mm', umbralOk: 1.5, umbralWarn: 4 },
  presion: { label: 'Presión', unit: 'hPa', umbralOk: 2, umbralWarn: 5 },
  viento: { label: 'Viento', unit: 'km/h', umbralOk: 5, umbralWarn: 12 },
}

const COLOR_OK = '#10b981'
const COLOR_WARN = '#f59e0b'
const COLOR_BAD = '#ef4444'
const COLOR_NA = CHART_COLORS.azul
const COLOR_OBS = '#1a5f4a'

/** @type {import('vue').Ref<'facetas' | 'delta'>} */
const modo = ref('facetas')

function colorPorError(absDelta, umbralOk, umbralWarn) {
  if (absDelta == null || Number.isNaN(absDelta)) return COLOR_NA
  if (absDelta <= umbralOk) return COLOR_OK
  if (absDelta <= umbralWarn) return COLOR_WARN
  return COLOR_BAD
}

function etiquetaDelta(delta, unit) {
  if (delta == null || Number.isNaN(delta)) return '—'
  const sign = delta > 0 ? '+' : ''
  return `${sign}${delta.toFixed(1)}${unit ? ` ${unit}` : ''}`
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
        umbralOk: meta.umbralOk,
        umbralWarn: meta.umbralWarn,
      }
    })
)

const byKey = computed(() => {
  const m = new Map()
  for (const r of rows.value) m.set(r.key, r)
  return m
})

const facetsActivos = computed(() =>
  FACETS.map((f) => ({
    ...f,
    rows: f.keys.map((k) => byKey.value.get(k)).filter(Boolean),
  })).filter((f) => f.rows.length > 0)
)

function buildFacetOption() {
  const facets = facetsActivos.value
  const n = facets.length || 1
  const gap = 3
  const topPad = 10
  const bottomPad = 6
  const usable = 100 - topPad - bottomPad - gap * (n - 1)
  const h = usable / n

  const grids = []
  const xAxes = []
  const yAxes = []
  const titles = []
  const series = []

  facets.forEach((facet, i) => {
    const top = topPad + i * (h + gap)
    grids.push({
      left: '12%',
      right: '4%',
      top: `${top}%`,
      height: `${h}%`,
      containLabel: false,
    })
    titles.push({
      text: facet.title,
      left: '12%',
      top: `${top - 2.2}%`,
      textStyle: {
        color: CHART_COLORS.texto,
        fontSize: 11,
        fontWeight: 600,
      },
    })
    xAxes.push({
      type: 'category',
      gridIndex: i,
      data: facet.rows.map((r) => r.label),
      axisLine: { lineStyle: { color: CHART_COLORS.eje } },
      axisLabel: {
        color: CHART_COLORS.texto,
        fontSize: 10,
        interval: 0,
      },
      axisTick: { alignWithLabel: true },
    })
    const yOpt = {
      type: 'value',
      gridIndex: i,
      scale: !(facet.yMin != null && facet.yMax != null),
      axisLine: { show: true, lineStyle: { color: CHART_COLORS.verde } },
      splitLine: { lineStyle: { color: CHART_COLORS.grilla, type: 'dashed' } },
      axisLabel: {
        color: CHART_COLORS.texto,
        fontSize: 10,
        formatter: (v) => (Number.isInteger(v) ? String(v) : Number(v).toFixed(1)),
      },
    }
    if (facet.yMin != null) yOpt.min = facet.yMin
    if (facet.yMax != null) yOpt.max = facet.yMax
    yAxes.push(yOpt)

    series.push({
      name: 'Observado',
      type: 'bar',
      xAxisIndex: i,
      yAxisIndex: i,
      data: facet.rows.map((r) => r.actual),
      itemStyle: { color: COLOR_OBS, borderRadius: [3, 3, 0, 0] },
      barMaxWidth: 22,
      barGap: '20%',
    })
    series.push({
      name: 'Modelo ML',
      type: 'bar',
      xAxisIndex: i,
      yAxisIndex: i,
      data: facet.rows.map((r) => ({
        value: r.prediccion,
        itemStyle: { color: r.colorMl, borderRadius: [3, 3, 0, 0] },
      })),
      barMaxWidth: 22,
      label: {
        show: true,
        position: 'top',
        color: CHART_COLORS.texto,
        fontSize: 9,
        formatter: (p) => {
          const row = facet.rows[p.dataIndex]
          if (!row || row.delta == null) return ''
          const sign = row.delta > 0 ? '+' : ''
          return `${sign}${row.delta.toFixed(1)}`
        },
      },
    })
  })

  return {
    backgroundColor: 'transparent',
    legend: {
      ...leyendaSuperior(['Observado', 'Modelo ML']),
      top: 0,
      right: 8,
    },
    title: titles,
    tooltip: tooltipOscuro((params) => {
      const list = Array.isArray(params) ? params : [params]
      const p0 = list[0]
      // 2 series por faceta (Observado + Modelo ML)
      const facetIdx = Math.floor((p0.seriesIndex ?? 0) / 2)
      const facet = facets[facetIdx] || facets[0]
      const row = facet?.rows?.[p0.dataIndex]
      if (!row) return ''
      let html = `<div style="font-weight:bold;margin-bottom:4px;">${row.label} · ${facet.title}</div>`
      list.forEach((p) => {
        const v = typeof p.value === 'object' && p.value != null ? p.value.value : p.value
        html += `<div><span style="color:${p.color}">● ${p.seriesName}</span> <b>${v ?? '—'} ${row.unit}</b></div>`
      })
      html += `<div style="margin-top:6px;border-top:1px solid #475569;padding-top:4px;">`
      html += `<span style="color:${row.colorMl}">Δ ML−obs</span> <b style="color:${row.colorMl}">${etiquetaDelta(row.delta, row.unit)}</b>`
      html += `</div>`
      return html
    }),
    axisPointer: { link: [{ xAxisIndex: 'all' }] },
    grid: grids,
    xAxis: xAxes,
    yAxis: yAxes,
    series,
  }
}

function buildDeltaOption() {
  const list = rows.value.filter((r) => r.delta != null)
  return {
    backgroundColor: 'transparent',
    legend: leyendaSuperior(['Δ ML − observado']),
    tooltip: tooltipOscuro((params) => {
      const i = params[0].dataIndex
      const row = list[i]
      if (!row) return ''
      let html = `<div style="font-weight:bold;margin-bottom:4px;">${row.label}</div>`
      html += `<div>Observado: <b>${row.actual ?? '—'} ${row.unit}</b></div>`
      html += `<div>ML: <b>${row.prediccion} ${row.unit}</b></div>`
      html += `<div style="margin-top:4px;color:${row.colorMl}">Δ: <b>${etiquetaDelta(row.delta, row.unit)}</b></div>`
      return html
    }),
    grid: { left: '10%', right: '4%', top: '14%', bottom: '12%', containLabel: true },
    xAxis: {
      type: 'category',
      data: list.map((r) => r.label),
      axisLine: { lineStyle: { color: CHART_COLORS.eje } },
      axisLabel: { color: CHART_COLORS.texto, rotate: list.length > 4 ? 15 : 0 },
    },
    yAxis: {
      type: 'value',
      name: 'Δ (unidad de cada var.)',
      nameTextStyle: { color: CHART_COLORS.texto, fontSize: 10 },
      axisLine: { show: true, lineStyle: { color: CHART_COLORS.verde } },
      splitLine: { lineStyle: { color: CHART_COLORS.grilla, type: 'dashed' } },
      axisLabel: { color: CHART_COLORS.texto },
    },
    series: [
      {
        name: 'Δ ML − observado',
        type: 'bar',
        data: list.map((r) => ({
          value: Number(r.delta.toFixed(2)),
          itemStyle: { color: r.colorMl, borderRadius: [3, 3, 0, 0] },
        })),
        barMaxWidth: 36,
        markLine: {
          silent: true,
          symbol: 'none',
          data: [{ yAxis: 0, lineStyle: { color: '#94a3b8', type: 'solid', width: 1 } }],
          label: { show: false },
        },
        label: {
          show: true,
          position: 'top',
          color: CHART_COLORS.texto,
          fontSize: 10,
          formatter: (p) => {
            const v = p.value
            const sign = v > 0 ? '+' : ''
            return `${sign}${v}`
          },
        },
      },
    ],
  }
}

const chartOption = computed(() =>
  modo.value === 'delta' ? buildDeltaOption() : buildFacetOption()
)

const chartHeight = computed(() => {
  if (modo.value === 'delta') return 300
  const n = Math.max(facetsActivos.value.length, 1)
  return Math.min(720, 120 + n * 130)
})

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
      <div class="modo-switch" role="group" aria-label="Modo de visualización">
        <button
          type="button"
          :class="{ active: modo === 'facetas' }"
          @click="modo = 'facetas'"
        >
          Por escala
        </button>
        <button
          type="button"
          :class="{ active: modo === 'delta' }"
          @click="modo = 'delta'"
        >
          Solo Δ error
        </button>
      </div>
      <span class="ml-proj__legend" title="Color de la barra ML según |Δ|">
        <i class="swatch ok" /> ok
        <i class="swatch warn" /> medio
        <i class="swatch bad" /> alto
      </span>
      <button type="button" class="csv-btn" @click="exportCsv">CSV</button>
    </div>
    <div v-if="!rows.length" class="empty">Sin proyecciones ML</div>
    <div
      v-else
      class="chart-wrap"
      :style="{ height: chartHeight + 'px' }"
      role="img"
      :aria-label="
        modo === 'delta'
          ? 'Error ML menos observado por variable'
          : 'Proyección ML versus observado en paneles por escala física'
      "
    >
      <v-chart class="chart" :option="chartOption" autoresize />
    </div>
  </div>
</template>

<style scoped>
.ml-proj { width: 100%; }
.ml-proj__ctrl {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.65rem;
  margin-bottom: 0.45rem;
}
.modo-switch {
  display: inline-flex;
  gap: 0.2rem;
  padding: 0.15rem;
  border: 1px solid var(--color-border, #334155);
  border-radius: 8px;
  background: var(--color-bg, #0b1120);
}
.modo-switch button {
  border: none;
  background: transparent;
  color: var(--color-muted, #94a3b8);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.3rem 0.65rem;
  border-radius: 6px;
  cursor: pointer;
  font-family: inherit;
}
.modo-switch button.active {
  background: var(--color-primary-muted, rgba(0, 255, 170, 0.15));
  color: var(--color-primary, #00ffaa);
}
.ml-proj__legend {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.72rem;
  color: var(--color-muted, #94a3b8);
  margin-left: auto;
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
.csv-btn {
  padding: 0.3rem 0.6rem;
  font-size: 0.75rem;
  border-radius: 6px;
  border: 1px solid var(--color-border, #334155);
  background: var(--color-surface, #1e293b);
  color: var(--color-text, #f1f5f9);
  cursor: pointer;
  font-family: inherit;
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
  border: 1px dashed var(--color-border);
  border-radius: 8px;
}
</style>
