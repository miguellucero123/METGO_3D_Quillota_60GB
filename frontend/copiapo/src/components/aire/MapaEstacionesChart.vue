<template>
  <div class="chart-wrap">
    <v-chart class="chart" :option="option" autoresize @click="onClick" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { ScatterChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, ScatterChart, GridComponent, TooltipComponent])

const props = defineProps({
  // [{ slug, nombre, lat, lon, color, valor, etiqueta, activo }]
  puntos: { type: Array, default: () => [] },
  valorLabel: { type: String, default: 'Índice' },
})
const emit = defineEmits(['select'])

const option = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(17, 24, 39, 0.92)',
    borderColor: 'rgba(251, 191, 36, 0.3)',
    textStyle: { color: '#f3f4f6' },
    formatter: (p) => {
      const d = p.data
      return `<strong>${d.nombre}</strong><br/>${props.valorLabel}: ${
        d.valor ?? '—'
      }<br/>${d.etiqueta || ''}`
    },
  },
  grid: { top: 24, left: 12, right: 12, bottom: 24, containLabel: true },
  xAxis: {
    type: 'value',
    name: 'Long.',
    scale: true,
    axisLabel: { color: '#9ca3af', formatter: (v) => v.toFixed(2) },
    axisLine: { lineStyle: { color: '#374151' } },
    splitLine: { lineStyle: { color: '#1f2937', type: 'dashed' } },
  },
  yAxis: {
    type: 'value',
    name: 'Lat.',
    scale: true,
    axisLabel: { color: '#9ca3af', formatter: (v) => v.toFixed(2) },
    axisLine: { lineStyle: { color: '#374151' } },
    splitLine: { lineStyle: { color: '#1f2937', type: 'dashed' } },
  },
  series: [
    {
      type: 'scatter',
      symbolSize: (val, p) => (p.data.activo ? 34 : 26),
      label: {
        show: true,
        position: 'right',
        formatter: (p) => p.data.nombre,
        color: '#d1d5db',
        fontSize: 11,
      },
      data: props.puntos.map((pt) => ({
        value: [pt.lon, pt.lat],
        name: pt.slug,
        nombre: pt.nombre,
        valor: pt.valor,
        etiqueta: pt.etiqueta,
        activo: pt.activo,
        itemStyle: {
          color: pt.color || '#9ca3af',
          borderColor: pt.activo ? '#f3f4f6' : 'rgba(243,244,246,0.35)',
          borderWidth: pt.activo ? 2.5 : 1,
          shadowBlur: pt.activo ? 12 : 0,
          shadowColor: pt.color || '#9ca3af',
        },
      })),
    },
  ],
}))

function onClick(params) {
  if (params?.data?.name) emit('select', params.data.name)
}
</script>

<style scoped>
.chart-wrap { width: 100%; }
.chart { height: 420px; width: 100%; }
</style>
