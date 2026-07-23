<template>
  <div class="chart-wrap">
    <v-chart class="chart" :option="option" autoresize />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent])

const props = defineProps({
  labels: { type: Array, default: () => [] },
  series: { type: Array, default: () => [] }, // [{ name, data, type? }]
  yName: { type: String, default: '' },
})

const option = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(17, 24, 39, 0.92)',
    borderColor: 'rgba(251, 191, 36, 0.3)',
    textStyle: { color: '#f3f4f6' },
  },
  legend: {
    data: props.series.map((s) => s.name),
    textStyle: { color: '#9ca3af' },
    top: 0,
  },
  grid: { top: 40, left: 48, right: 16, bottom: 32 },
  xAxis: {
    type: 'category',
    data: props.labels,
    axisLabel: { color: '#9ca3af' },
    axisLine: { lineStyle: { color: '#374151' } },
  },
  yAxis: {
    type: 'value',
    name: props.yName,
    nameTextStyle: { color: '#9ca3af' },
    axisLabel: { color: '#9ca3af' },
    splitLine: { lineStyle: { color: '#1f2937', type: 'dashed' } },
  },
  series: props.series.map((s, i) => ({
    name: s.name,
    type: s.type || 'line',
    smooth: true,
    data: s.data,
    itemStyle: {
      color: s.color || (i === 0 ? '#fbbf24' : '#fb923c'),
    },
    areaStyle: s.type === 'bar' ? undefined : { opacity: 0.12 },
  })),
}))
</script>

<style scoped>
.chart-wrap { width: 100%; }
.chart { height: 320px; width: 100%; }
</style>
