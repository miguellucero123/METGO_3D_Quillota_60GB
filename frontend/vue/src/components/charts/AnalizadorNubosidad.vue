<script setup>
import { ref, computed, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { useMetgoStore } from '@/stores/metgo'
import { fetchAnalisisNubosidad } from '@/api/metgoApi'
import {
  CHART_COLORS,
  tooltipOscuro,
  leyendaSuperior,
  grillaBase,
  ejeCategoria,
  ejeValor,
  serieBarrasAzules,
  serieLineaVerde,
} from '@/utils/echartsTheme'

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent])

const store = useMetgoStore()
const cargando = ref(false)
const datos = ref([])

async function cargar() {
  cargando.value = true
  try {
    const res = await fetchAnalisisNubosidad(store.estacionActiva, 7)
    datos.value = res.datos ?? []
  } catch {
    datos.value = []
  } finally {
    cargando.value = false
  }
}

watch(() => store.estacionActiva, cargar, { immediate: true })

function fmt(f) {
  return new Date(f).toLocaleDateString('es-CL', { weekday: 'short', day: 'numeric', month: 'short' })
}

const chartOption = computed(() => {
  const labels = datos.value.map((d) => fmt(d.fecha))
  const cob = datos.value.map((d) => d.cobertura)
  const rad = datos.value.map((d) => d.radiacion || 0)
  return {
    backgroundColor: 'transparent',
    tooltip: tooltipOscuro((params) => {
      let html = `<div style="font-weight:bold;margin-bottom:4px;">${params[0].axisValue}</div>`
      params.forEach((p) => {
        const u = p.seriesName.includes('Radiación') ? ' W/m²' : '%'
        html += `<div><span style="color:${p.color}">● ${p.seriesName}</span> <b>${p.value ?? 0}${u}</b></div>`
      })
      return html
    }),
    legend: leyendaSuperior(['Cobertura nubosa', 'Radiación']),
    grid: { ...grillaBase(), bottom: '8%', top: '18%' },
    xAxis: [ejeCategoria(labels)],
    yAxis: [
      ejeValor('Cobertura (%)', CHART_COLORS.azul, {
        max: 100,
        position: 'left',
        axisLabel: { formatter: '{value}%', color: CHART_COLORS.texto },
      }),
      ejeValor('Radiación', CHART_COLORS.ambar, {
        position: 'right',
        splitLine: { show: false },
        axisLabel: { formatter: '{value}', color: CHART_COLORS.texto },
      }),
    ],
    series: [
      serieBarrasAzules('Cobertura nubosa', cob, { yAxisIndex: 0 }),
      serieLineaVerde('Radiación', rad, {
        yAxisIndex: 1,
        itemStyle: { color: CHART_COLORS.ambar },
        lineStyle: { color: CHART_COLORS.ambar, width: 3 },
        areaStyle: undefined,
      }),
    ],
  }
})
</script>

<template>
  <div class="nub-panel">
    <h3>Nubosidad y radiación solar</h3>
    <div v-if="cargando" class="loading">Cargando…</div>
    <template v-else-if="datos.length">
      <div class="chart-wrap">
        <v-chart class="chart" :option="chartOption" autoresize />
      </div>
      <table class="tabla">
        <thead>
          <tr><th>Fecha</th><th>Cobertura</th><th>Tipo</th><th>Radiación</th><th>ΔT día</th><th>ΔT noche</th></tr>
        </thead>
        <tbody>
          <tr v-for="(d, i) in datos" :key="i">
            <td>{{ fmt(d.fecha) }}</td>
            <td>{{ d.cobertura }}%</td>
            <td>{{ d.tipo_nube }}</td>
            <td>{{ d.radiacion }} W/m²</td>
            <td :class="d.impacto_temp_dia < 0 ? 'neg' : ''">{{ d.impacto_temp_dia }}°C</td>
            <td :class="d.impacto_temp_noche > 0 ? 'pos' : ''">+{{ d.impacto_temp_noche }}°C</td>
          </tr>
        </tbody>
      </table>
      <div class="info-grid">
        <div class="info"><strong>Día</strong> Nubes reducen radiación → días más frescos.</div>
        <div class="info"><strong>Noche</strong> Nubes atrapan calor → menos riesgo de helada radiativa.</div>
      </div>
    </template>
    <p v-else class="empty">Sin datos de nubosidad</p>
  </div>
</template>

<style scoped>
.nub-panel { background: var(--color-surface, #1e293b); border-radius: 8px; padding: 1rem; border: 1px solid var(--color-border, #334155); }
.nub-panel h3 { margin: 0 0 0.75rem; font-size: 1rem; }
.chart-wrap { width: 100%; height: 280px; margin-bottom: 0.75rem; }
.chart { width: 100%; height: 100%; }
.tabla { width: 100%; font-size: 0.78rem; border-collapse: collapse; }
.tabla th, .tabla td { padding: 0.4rem; border-bottom: 1px solid var(--color-border, #334155); }
.neg { color: #ef4444; }
.pos { color: #10b981; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 0.75rem; }
.info { font-size: 0.75rem; background: rgba(2, 132, 199, 0.1); padding: 0.5rem; border-radius: 6px; border-left: 3px solid #0284c7; }
.loading, .empty { text-align: center; padding: 1.5rem; color: var(--color-text-muted, #94a3b8); }
</style>
