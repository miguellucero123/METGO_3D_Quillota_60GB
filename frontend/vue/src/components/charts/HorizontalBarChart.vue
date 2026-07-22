<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import {
  CHART_COLORS,
  tooltipOscuro,
  grillaBase,
  ejeValor,
} from '@/utils/echartsTheme'

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent])

const props = defineProps({
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  stationIds: { type: Array, default: () => [] },
  unit: { type: String, default: '' },
  color: { type: String, default: '' },
  kind: { type: String, default: 'default' },
  clickable: { type: Boolean, default: false },
  hints: { type: Array, default: () => [] },
})

const emit = defineEmits(['bar-click'])

function barColor(v, i) {
  if (props.color) return props.color
  const n = Number(v)
  if (Number.isNaN(n)) return CHART_COLORS.verde
  const nums = props.values.map(Number).filter((x) => !Number.isNaN(x))
  const min = nums.length ? Math.min(...nums) : 0
  const max = nums.length ? Math.max(...nums) : 1
  const t = max === min ? 0.5 : (n - min) / (max - min)
  if (props.kind === 'temp') {
    const r = Math.round(40 + t * 175)
    const b = Math.round(140 - t * 120)
    return `rgb(${r}, ${Math.round(90 + t * 40)}, ${b})`
  }
  if (props.kind === 'precip') return n > 0 ? CHART_COLORS.azul : '#64748b'
  if (props.kind === 'humedad') return `hsl(200, ${55 + t * 25}%, ${42 + t * 18}%)`
  const hues = [CHART_COLORS.verde, '#34d399', CHART_COLORS.celeste, '#5a9b72']
  return hues[i % hues.length]
}

const chartOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: tooltipOscuro((params) => {
    const p = params[0]
    const i = p.dataIndex
    const hint = props.hints[i] ? `<div style="color:#9ca3af;margin-top:4px;font-size:11px;">${props.hints[i]}</div>` : ''
    const u = props.unit ? ` ${props.unit}` : ''
    return `<div style="font-weight:bold;margin-bottom:4px;">${p.name}</div>
      <b>${p.value ?? '—'}${u}</b>${hint}`
  }),
  grid: { ...grillaBase(), left: '2%', right: '8%', top: '4%', bottom: '4%' },
  xAxis: [
    ejeValor('', CHART_COLORS.texto, {
      type: 'value',
      splitLine: { lineStyle: { color: CHART_COLORS.grilla, type: 'dashed' } },
      axisLabel: {
        formatter: props.unit ? `{value} ${props.unit}` : '{value}',
        color: CHART_COLORS.texto,
      },
    }),
  ],
  yAxis: [
    {
      type: 'category',
      data: props.labels,
      axisLine: { lineStyle: { color: CHART_COLORS.eje } },
      axisLabel: { color: CHART_COLORS.texto },
      inverse: true,
    },
  ],
  series: [
    {
      type: 'bar',
      data: props.values.map((v, i) => ({
        value: v,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 1,
            y2: 0,
            colorStops: [
              { offset: 0, color: barColor(v, i) },
              { offset: 1, color: CHART_COLORS.azul },
            ],
          },
          borderRadius: [0, 4, 4, 0],
        },
      })),
      barMaxWidth: 22,
    },
  ],
}))

function onClick(params) {
  if (!props.clickable) return
  const i = params.dataIndex
  emit('bar-click', { index: i, id: props.stationIds[i], label: props.labels[i] })
}
</script>

<template>
  <div class="hbar">
    <div v-if="!labels.length" class="empty">Sin datos</div>
    <div v-else class="chart-wrap">
      <v-chart class="chart" :option="chartOption" autoresize @click="onClick" />
    </div>
  </div>
</template>

<style scoped>
.hbar { width: 100%; }
.chart-wrap {
  width: 100%;
  height: 280px;
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  padding: 0.5rem;
}
.chart { width: 100%; height: 100%; }
.empty {
  padding: 1.5rem;
  text-align: center;
  color: var(--color-text-muted, #94a3b8);
}
</style>
