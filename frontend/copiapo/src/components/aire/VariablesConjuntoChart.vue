<template>
  <div class="chart-wrap" role="img" :aria-label="ariaLabel">
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
  seriesMap: { type: Object, default: () => ({}) },
  slots: { type: Array, default: () => [] },
})

const ariaLabel = computed(() => {
  const names = (props.slots || []).map((s) => s.nombre).join(', ')
  return `Gráfico conjunto: ${names || 'sin series'}`
})

const option = computed(() => {
  const slots = props.slots || []
  const ejesUsados = []
  const yAxis = []
  const ejeIndex = {}

  for (const s of slots) {
    const eje = s.eje || s.id
    if (!(eje in ejeIndex)) {
      const pos = ejesUsados.length % 2 === 0 ? 'left' : 'right'
      const offset = Math.floor(ejesUsados.length / 2) * 48
      ejeIndex[eje] = ejesUsados.length
      ejesUsados.push(eje)
      yAxis.push({
        type: 'value',
        name: s.unidad || '',
        position: pos,
        offset,
        axisLine: { show: true, lineStyle: { color: s.color || '#64748b' } },
        splitLine: { show: ejesUsados.length === 1 },
        axisLabel: { color: '#64748b', fontSize: 10 },
        nameTextStyle: { color: '#64748b', fontSize: 10 },
      })
    }
  }

  const series = slots.map((s) => {
    const data = props.seriesMap[s.id] || []
    const tipo = s.tipo === 'bar' ? 'bar' : 'line'
    return {
      name: s.nombre,
      type: tipo,
      yAxisIndex: ejeIndex[s.eje || s.id] || 0,
      data,
      showSymbol: false,
      step: s.tipo === 'step' ? 'end' : undefined,
      itemStyle: { color: s.color || '#64748b' },
      lineStyle: { width: 2, color: s.color || '#64748b' },
      barMaxWidth: 8,
      emphasis: { focus: 'series' },
    }
  })

  const labels = (props.labels || []).map((l) => {
    const m = String(l || '').match(/T(\d{2}):/)
    return m ? `${m[1]}h` : String(l || '').slice(5, 16)
  })

  return {
    animationDuration: 400,
    tooltip: { trigger: 'axis' },
    legend: { top: 0, type: 'scroll', textStyle: { fontSize: 11 } },
    grid: { left: 48 + Math.floor(ejesUsados.length / 2) * 40, right: 48 + Math.ceil(ejesUsados.length / 2) * 40, top: 40, bottom: 36 },
    xAxis: { type: 'category', data: labels, axisLabel: { fontSize: 10, color: '#64748b' } },
    yAxis: yAxis.length ? yAxis : [{ type: 'value' }],
    series,
  }
})
</script>

<style scoped>
.chart-wrap {
  width: 100%;
  min-height: 320px;
}
.chart {
  width: 100%;
  height: 360px;
}
</style>
