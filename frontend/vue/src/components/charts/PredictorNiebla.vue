<script setup>
import { ref, computed, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { useMetgoStore } from '@/stores/metgo'
import { fetchPronosticoNiebla } from '@/api/metgoApi'
import {
  CHART_COLORS,
  tooltipOscuro,
  grillaBase,
  ejeCategoria,
  ejeValor,
} from '@/utils/echartsTheme'

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent])

const store = useMetgoStore()
const cargando = ref(false)
const datos = ref([])
const resumen = ref(null)

async function cargar() {
  cargando.value = true
  try {
    const res = await fetchPronosticoNiebla(store.estacionActiva, 7)
    datos.value = res.pronosticos_niebla ?? []
    resumen.value = res.resumen ?? null
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

function popColor(p) {
  if (p > 70) return CHART_COLORS.rojo
  if (p > 40) return '#f97316'
  if (p > 20) return CHART_COLORS.ambar
  return '#22c55e'
}

function tipoLabel(t) {
  return { radiativa: 'Radiativa', advectiva: 'Advectiva', rocio_cerro: 'Rocío' }[t] || t
}

const chartOption = computed(() => {
  const labels = datos.value.map((d) => fmt(d.fecha_pronostico))
  const pops = datos.value.map((d) => d.probabilidad_niebla)
  return {
    backgroundColor: 'transparent',
    tooltip: tooltipOscuro((params) => {
      const p = params[0]
      const i = p.dataIndex
      const d = datos.value[i]
      return `<div style="font-weight:bold;margin-bottom:4px;">${p.axisValue}</div>
        <div>Probabilidad: <b>${p.value}%</b></div>
        <div style="color:#9ca3af;font-size:11px;">${tipoLabel(d?.tipo_niebla)} · vis ${d?.visibilidad_esperada} km</div>`
    }),
    grid: { ...grillaBase(), bottom: '8%', top: '8%' },
    xAxis: [ejeCategoria(labels)],
    yAxis: [
      ejeValor('Prob. niebla (%)', CHART_COLORS.celeste, {
        max: 100,
        axisLabel: { formatter: '{value}%', color: CHART_COLORS.texto },
      }),
    ],
    series: [
      {
        name: 'Probabilidad niebla',
        type: 'bar',
        data: pops.map((v) => ({
          value: v,
          itemStyle: { color: popColor(v), borderRadius: [4, 4, 0, 0] },
        })),
        barMaxWidth: 36,
      },
    ],
  }
})
</script>

<template>
  <div class="niebla-panel">
    <h3>Nieblas y visibilidad</h3>
    <div v-if="cargando" class="loading">Cargando…</div>
    <template v-else-if="datos.length">
      <p v-if="resumen" class="resumen">
        Días con niebla: <strong>{{ resumen.dias_con_niebla }}</strong> ·
        Visibilidad mín: <strong>{{ resumen.visibilidad_minima }} km</strong>
      </p>
      <div class="chart-wrap">
        <v-chart class="chart" :option="chartOption" autoresize />
      </div>
      <table class="tabla">
        <thead>
          <tr><th>Fecha</th><th>PoP</th><th>Tipo</th><th>Severidad</th><th>Visibilidad</th><th>Alerta</th></tr>
        </thead>
        <tbody>
          <tr v-for="(d, i) in datos" :key="i" :class="{ crit: d.severidad === 'muy_densa' }">
            <td>{{ fmt(d.fecha_pronostico) }}</td>
            <td>{{ d.probabilidad_niebla }}%</td>
            <td>{{ tipoLabel(d.tipo_niebla) }}</td>
            <td>{{ d.severidad.replace('_', ' ') }}</td>
            <td>{{ d.visibilidad_esperada }} km</td>
            <td>{{ d.severidad === 'muy_densa' ? 'Critica' : d.severidad === 'densa' ? 'Alta' : 'Baja' }}</td>
          </tr>
        </tbody>
      </table>
      <div class="seguridad">
        <strong>Seguridad vial:</strong> &lt; 1 km precaución · &lt; 500 m alerta · &lt; 100 m crítica
      </div>
    </template>
    <p v-else class="empty">Sin pronóstico de niebla</p>
  </div>
</template>

<style scoped>
.niebla-panel { background: var(--color-surface, #1e293b); border-radius: 8px; padding: 1rem; border: 1px solid var(--color-border, #334155); }
.niebla-panel h3 { margin: 0 0 0.75rem; font-size: 1rem; }
.resumen { font-size: 0.8rem; color: var(--color-text-muted, #94a3b8); margin-bottom: 0.5rem; }
.chart-wrap { width: 100%; height: 240px; margin-bottom: 0.75rem; }
.chart { width: 100%; height: 100%; }
.tabla { width: 100%; font-size: 0.78rem; border-collapse: collapse; }
.tabla th, .tabla td { padding: 0.4rem; border-bottom: 1px solid var(--color-border, #334155); }
.tabla tr.crit { background: rgba(239, 68, 68, 0.12); }
.seguridad { margin-top: 0.75rem; font-size: 0.75rem; background: rgba(239, 68, 68, 0.1); padding: 0.5rem; border-radius: 6px; border-left: 3px solid #ef4444; }
.loading, .empty { text-align: center; padding: 1.5rem; color: var(--color-text-muted, #94a3b8); }
</style>
