<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { RadarChart } from 'echarts/charts'
import { RadarComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { CHART_COLORS, tooltipOscuro } from '@/utils/echartsTheme'

use([CanvasRenderer, RadarChart, RadarComponent, TooltipComponent, LegendComponent])

const props = defineProps({
  directions: { type: Array, default: () => [] },
  speeds: { type: Array, default: () => [] },
  unit: { type: String, default: 'm/s' },
  size: { type: Number, default: 280 },
})

const SECTORS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

const countUnit = computed(() => (props.directions.length > 15 ? 'h' : 'd'))

const buckets = computed(() => {
  const counts = SECTORS.map(() => 0)
  const speedSum = SECTORS.map(() => 0)
  props.directions.forEach((deg, i) => {
    const d = Number(deg)
    const s = Number(props.speeds[i]) || 0
    if (Number.isNaN(d)) return
    const idx = Math.round(d / 45) % 8
    counts[idx] += 1
    speedSum[idx] += s
  })
  const max = Math.max(1, ...counts)
  return SECTORS.map((label, i) => ({
    label,
    count: counts[i],
    avgSpeed: counts[i] ? Math.round((speedSum[i] / counts[i]) * 10) / 10 : 0,
    ratio: counts[i] / max,
  }))
})

const chartOption = computed(() => {
  const maxCount = Math.max(1, ...buckets.value.map((b) => b.count))
  return {
    backgroundColor: 'transparent',
    tooltip: {
      ...tooltipOscuro(),
      trigger: 'item',
    },
    radar: {
      indicator: SECTORS.map((name) => ({ name, max: maxCount })),
      center: ['50%', '52%'],
      radius: '68%',
      axisName: { color: CHART_COLORS.texto, fontSize: 11 },
      splitLine: { lineStyle: { color: CHART_COLORS.grilla } },
      splitArea: {
        areaStyle: {
          color: ['rgba(15,23,42,0.2)', 'rgba(30,41,59,0.35)'],
        },
      },
      axisLine: { lineStyle: { color: CHART_COLORS.eje } },
    },
    series: [
      {
        type: 'radar',
        name: 'Frecuencia',
        data: [
          {
            value: buckets.value.map((b) => b.count),
            name: 'Frecuencia',
            areaStyle: { color: 'rgba(56, 189, 248, 0.25)' },
            lineStyle: { color: CHART_COLORS.celeste, width: 2 },
            itemStyle: { color: CHART_COLORS.celeste },
          },
        ],
      },
    ],
  }
})
</script>

<template>
  <div class="wind-rose" role="img" aria-label="Rosa de vientos">
    <div v-if="!directions.length" class="empty">Sin datos de dirección de viento</div>
    <template v-else>
      <div class="chart-wrap" :style="{ height: size + 'px', width: '100%', maxWidth: size + 40 + 'px' }">
        <v-chart class="chart" :option="chartOption" autoresize />
      </div>
      <ul class="legend">
        <li v-for="b in buckets.filter((x) => x.count)" :key="b.label">
          <strong>{{ b.label }}</strong> {{ b.count }}{{ countUnit }} · {{ b.avgSpeed }} {{ unit }}
        </li>
      </ul>
    </template>
  </div>
</template>

<style scoped>
.wind-rose { display: flex; flex-wrap: wrap; gap: 1rem; align-items: flex-start; }
.chart-wrap {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  padding: 0.5rem;
}
.chart { width: 100%; height: 100%; }
.legend {
  list-style: none;
  margin: 0;
  padding: 0;
  font-size: 0.75rem;
  color: var(--color-text-muted, #94a3b8);
  display: grid;
  gap: 0.25rem;
}
.empty { font-size: 0.8rem; color: var(--color-text-muted, #94a3b8); margin: 0; }
</style>
