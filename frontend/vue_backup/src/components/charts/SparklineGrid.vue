<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { formatoDiaCorto } from '@/utils/meteoDates'
import { CHART_COLORS } from '@/utils/echartsTheme'

use([CanvasRenderer, LineChart, GridComponent])

const props = defineProps({
  /** [{ id, nombre, fechas: [], valores: [], unidad }] */
  series: { type: Array, default: () => [] },
  kind: { type: String, default: 'temp' },
})

const stroke = computed(() => (props.kind === 'precip' ? CHART_COLORS.azul : CHART_COLORS.ambar))

function optionFor(vals) {
  return {
    backgroundColor: 'transparent',
    animation: false,
    grid: { left: 2, right: 2, top: 4, bottom: 2 },
    xAxis: { type: 'category', show: false, data: vals.map((_, i) => i) },
    yAxis: { type: 'value', show: false, scale: true },
    series: [
      {
        type: 'line',
        data: vals,
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2, color: stroke.value },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: props.kind === 'precip' ? 'rgba(2,132,199,0.35)' : 'rgba(245,158,11,0.3)' },
              { offset: 1, color: 'rgba(0,0,0,0)' },
            ],
          },
        },
      },
    ],
  }
}
</script>

<template>
  <div class="spark-grid">
    <article v-for="s in series" :key="s.id" class="spark-card">
      <header>
        <strong>{{ s.nombre }}</strong>
        <span v-if="s.valores?.length">{{ s.valores[s.valores.length - 1] }}{{ s.unidad }}</span>
      </header>
      <div v-if="s.valores?.length > 1" class="spark-chart">
        <v-chart class="chart" :option="optionFor(s.valores)" autoresize />
      </div>
      <p v-else class="no-data">Sin serie</p>
      <footer v-if="s.fechas?.length">
        {{ formatoDiaCorto(s.fechas[0]) }} — {{ formatoDiaCorto(s.fechas[s.fechas.length - 1]) }}
      </footer>
    </article>
  </div>
</template>

<style scoped>
.spark-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.65rem;
}
.spark-card {
  border: 1px solid var(--color-border, #334155);
  border-radius: 8px;
  padding: 0.45rem 0.55rem;
  background: var(--color-surface, #1e293b);
}
.spark-card header {
  display: flex;
  justify-content: space-between;
  font-size: 0.72rem;
  margin-bottom: 0.2rem;
  color: var(--color-text, #f1f5f9);
}
.spark-card footer {
  font-size: 0.62rem;
  color: var(--color-text-muted, #94a3b8);
  margin-top: 0.15rem;
}
.spark-chart { width: 100%; height: 48px; }
.chart { width: 100%; height: 100%; }
.no-data { font-size: 0.7rem; color: #94a3b8; text-align: center; margin: 0.5rem 0; }
</style>
