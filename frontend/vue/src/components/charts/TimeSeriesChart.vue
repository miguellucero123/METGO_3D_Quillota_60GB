<script setup>
import { computed, ref } from 'vue'
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
import { formatoDiaCorto } from '@/utils/meteoDates'
import {
  CHART_COLORS,
  tooltipOscuro,
  leyendaSuperior,
  zoomSlider,
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

const props = defineProps({
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  valuesMin: { type: Array, default: () => [] },
  unit: { type: String, default: '' },
  color: { type: String, default: '' },
  fillColor: { type: String, default: '' },
  height: { type: Number, default: 220 },
  showBand: { type: Boolean, default: false },
  showArea: { type: Boolean, default: true },
  yAxisTitle: { type: String, default: '' },
  seriesMaxLabel: { type: String, default: 'Máxima' },
  seriesMinLabel: { type: String, default: 'Mínima' },
  exportName: { type: String, default: '' },
})

const showMax = ref(true)
const showMin = ref(true)

const axisLabels = computed(() =>
  props.labels.map((l) => {
    try {
      return formatoDiaCorto(l) || String(l)
    } catch {
      return String(l)
    }
  })
)

const lineColor = computed(() => props.color || CHART_COLORS.verde)

const chartOption = computed(() => {
  const series = []
  const legendItems = []

  if (showMax.value) {
    legendItems.push(props.seriesMaxLabel)
    const maxSerie = serieLineaVerde(props.seriesMaxLabel, props.values, {
      itemStyle: { color: lineColor.value },
      lineStyle: {
        width: 3,
        color: lineColor.value,
        shadowColor: 'rgba(0, 255, 170, 0.35)',
        shadowBlur: 8,
      },
      areaStyle: props.showArea
        ? {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: props.fillColor || 'rgba(0, 255, 170, 0.25)' },
                { offset: 1, color: 'rgba(0, 255, 170, 0)' },
              ],
            },
          }
        : undefined,
      symbolSize: 5,
    })
    series.push(maxSerie)
  }

  if (props.showBand && showMin.value && props.valuesMin.length) {
    legendItems.push(props.seriesMinLabel)
    series.push({
      name: props.seriesMinLabel,
      type: 'line',
      data: props.valuesMin,
      smooth: true,
      symbol: 'circle',
      symbolSize: 4,
      itemStyle: { color: CHART_COLORS.celeste },
      lineStyle: { width: 2, color: CHART_COLORS.celeste, type: 'dashed' },
    })
  }

  return {
    backgroundColor: 'transparent',
    tooltip: tooltipOscuro((params) => {
      let html = `<div style="font-weight:bold;margin-bottom:5px;border-bottom:1px solid #4b5563;padding-bottom:5px;">${params[0].axisValue}</div>`
      params.forEach((p) => {
        const u = props.unit ? ` ${props.unit}` : ''
        html += `<div style="display:flex;justify-content:space-between;margin-top:2px;">
          <span style="color:${p.color};margin-right:12px;">● ${p.seriesName}</span>
          <b>${p.value ?? '—'}${u}</b>
        </div>`
      })
      return html
    }),
    legend: leyendaSuperior(legendItems),
    dataZoom: props.labels.length > 14 ? zoomSlider() : [{ type: 'inside', xAxisIndex: 0 }],
    grid: grillaBase(),
    xAxis: [ejeCategoria(axisLabels.value)],
    yAxis: [
      ejeValor(props.yAxisTitle || props.unit || '', lineColor.value, {
        axisLabel: {
          formatter: props.unit ? `{value} ${props.unit}` : '{value}',
          color: CHART_COLORS.texto,
        },
      }),
    ],
    series,
  }
})
</script>

<template>
  <div class="ts-chart">
    <div class="ts-chart__ctrl">
      <label>
        <input v-model="showMax" type="checkbox" />
        {{ seriesMaxLabel }}
      </label>
      <label v-if="showBand">
        <input v-model="showMin" type="checkbox" />
        {{ seriesMinLabel }}
      </label>
    </div>
    <div v-if="!labels.length" class="empty">Sin serie temporal</div>
    <div v-else class="chart-wrap" :style="{ height: height + 'px' }">
      <v-chart class="chart" :option="chartOption" autoresize />
    </div>
  </div>
</template>

<style scoped>
.ts-chart { width: 100%; }
.ts-chart__ctrl {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 0.35rem;
  font-size: 0.75rem;
  color: var(--color-text-muted, #94a3b8);
}
.ts-chart__ctrl label { display: flex; align-items: center; gap: 0.25rem; cursor: pointer; }
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
