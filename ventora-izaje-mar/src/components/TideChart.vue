<template>
  <div class="tide-chart">
    <div class="panel-header">
      <Waves class="panel-icon" :size="16" />
      <span class="panel-title">Pronóstico de Marea (24h)</span>
      <span class="panel-unit">metros (NRS)</span>
    </div>
    
    <div class="chart-container">
      <v-chart class="chart-canvas" :option="chartOption" autoresize />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, MarkLineComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { Waves } from 'lucide-vue-next'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, MarkLineComponent])

const props = defineProps({
  tides: {
    type: Array,
    default: () => []
  }
})

const chartOption = computed(() => {
  if (!props.tides.length) return {}
  
  const labels = props.tides.map(t => t.label)
  const data = props.tides.map(t => t.levelM)
  
  return {
    animation: true,
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(10, 20, 40, 0.9)',
      borderColor: 'rgba(100, 160, 255, 0.2)',
      textStyle: { color: '#e2eaf6', fontFamily: 'JetBrains Mono, monospace', fontSize: 12 },
      valueFormatter: (value) => `${value} m`
    },
    grid: { left: 35, right: 15, top: 20, bottom: 25 },
    xAxis: { 
      type: 'category', 
      data: labels,
      axisLabel: { color: 'rgba(120, 160, 220, 0.6)', fontSize: 10, fontFamily: 'JetBrains Mono' },
      axisLine: { lineStyle: { color: 'rgba(100, 160, 255, 0.2)' } }
    },
    yAxis: { 
      type: 'value', 
      min: (value) => Math.floor(value.min * 10) / 10 - 0.2,
      max: (value) => Math.ceil(value.max * 10) / 10 + 0.2,
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)', type: 'dashed' } },
      axisLabel: { color: 'rgba(120, 160, 220, 0.6)', fontSize: 10, fontFamily: 'JetBrains Mono' }
    },
    series: [
      { 
        name: 'Marea', 
        type: 'line', 
        data: data,
        smooth: true, 
        showSymbol: false, 
        lineStyle: { width: 3, color: '#3b82f6' },
        areaStyle: {
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
              { offset: 1, color: 'rgba(59, 130, 246, 0.02)' }
            ]
          }
        },
        markLine: {
          silent: true,
          symbol: 'none',
          label: { position: 'start', color: '#94a3b8', fontSize: 9 },
          lineStyle: { color: '#64748b', type: 'dashed' },
          data: [{ yAxis: 0, name: 'NRS' }]
        }
      }
    ]
  }
})
</script>

<style scoped>
.tide-chart {
  background: rgba(10, 20, 40, 0.72);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(100, 160, 255, 0.15);
  border-radius: 12px;
  padding: 16px;
  color: #e2eaf6;
  font-family: 'JetBrains Mono', 'Fira Mono', monospace;
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #7ab0e8;
  border-bottom: 1px solid rgba(100, 160, 255, 0.1);
  padding-bottom: 8px;
}
.panel-unit { margin-left: auto; color: rgba(120,160,220,0.5); font-size: 0.7rem; }

.chart-container {
  flex: 1;
  min-height: 180px;
  width: 100%;
}

.chart-canvas {
  width: 100%;
  height: 100%;
}
</style>
