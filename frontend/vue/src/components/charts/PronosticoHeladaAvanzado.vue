<script setup>
import { ref, computed, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  MarkLineComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { useMetgoStore } from '@/stores/metgo'
import { fetchPronosticoHeladaAvanzado } from '@/api/metgoApi'
import {
  CHART_COLORS,
  tooltipOscuro,
  leyendaSuperior,
  grillaBase,
  ejeCategoria,
  ejeValor,
  serieLineaVerde,
} from '@/utils/echartsTheme'

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  MarkLineComponent,
])

const store = useMetgoStore()
const cargando = ref(false)
const datos = ref([])
const resumen = ref(null)
const expandidoIdx = ref(-1)
const cultivo = ref('palto')

async function cargar() {
  cargando.value = true
  try {
    const res = await fetchPronosticoHeladaAvanzado(store.estacionActiva, 7, cultivo.value)
    datos.value = res.pronosticos_helada ?? []
    resumen.value = res.resumen ?? null
  } catch {
    datos.value = []
    resumen.value = null
  } finally {
    cargando.value = false
  }
}

watch([() => store.estacionActiva, cultivo], cargar, { immediate: true })

function fmt(fechaStr) {
  return new Date(fechaStr).toLocaleDateString('es-CL', { weekday: 'short', day: 'numeric', month: 'short' })
}

function tempClass(t) {
  if (t < -5) return 'ext'
  if (t < 0) return 'crit'
  if (t < 5) return 'riesgo'
  return 'ok'
}

function popColor(p) {
  if (p > 70) return CHART_COLORS.rojo
  if (p > 40) return '#f97316'
  if (p > 20) return CHART_COLORS.ambar
  return '#22c55e'
}

const chartOption = computed(() => {
  const labels = datos.value.map((d) => fmt(d.fecha_pronostico || d.fecha))
  const pops = datos.value.map((d) => d.probabilidad_helada)
  const tmins = datos.value.map((d) => d.temperatura_minima_esperada)
  return {
    backgroundColor: 'transparent',
    tooltip: tooltipOscuro((params) => {
      let html = `<div style="font-weight:bold;margin-bottom:4px;">${params[0].axisValue}</div>`
      params.forEach((p) => {
        const u = p.seriesName.includes('Prob') ? '%' : ' °C'
        html += `<div><span style="color:${p.color}">● ${p.seriesName}</span> <b>${p.value ?? '—'}${u}</b></div>`
      })
      return html
    }),
    legend: leyendaSuperior(['Prob. helada', 'T. mínima']),
    grid: grillaBase(),
    xAxis: [ejeCategoria(labels)],
    yAxis: [
      ejeValor('Prob (%)', CHART_COLORS.rojo, {
        max: 100,
        position: 'left',
        axisLabel: { formatter: '{value}%', color: CHART_COLORS.texto },
      }),
      ejeValor('Temp (°C)', CHART_COLORS.verde, {
        position: 'right',
        splitLine: { show: false },
        axisLabel: { formatter: '{value} °C', color: CHART_COLORS.texto },
      }),
    ],
    series: [
      {
        name: 'Prob. helada',
        type: 'bar',
        yAxisIndex: 0,
        data: pops.map((v) => ({
          value: v,
          itemStyle: { color: popColor(v), borderRadius: [4, 4, 0, 0] },
        })),
        barMaxWidth: 28,
      },
      serieLineaVerde('T. mínima', tmins, {
        yAxisIndex: 1,
        markLine: {
          silent: true,
          data: [{ yAxis: 0 }],
          lineStyle: { color: CHART_COLORS.rojo, type: 'dashed' },
          label: { formatter: '0°C', color: CHART_COLORS.texto },
        },
      }),
    ],
  }
})
</script>

<template>
  <div class="helada-av">
    <header class="helada-av__head">
      <h3>Pronóstico de helada radiativa</h3>
      <select v-model="cultivo" class="cultivo-sel">
        <option value="palto">Palto</option>
        <option value="vid">Vid</option>
        <option value="citricos">Cítricos</option>
        <option value="tomate">Tomate</option>
        <option value="lechuga">Lechuga</option>
      </select>
    </header>

    <div v-if="cargando" class="loading">Cargando…</div>
    <template v-else-if="datos.length">
      <div v-if="resumen" class="resumen">
        <div class="card sev"><strong>{{ resumen.dias_riesgo_severo }}</strong><span>Severo</span></div>
        <div class="card mod"><strong>{{ resumen.dias_riesgo_moderado }}</strong><span>Moderado</span></div>
        <div class="card min"><strong>{{ resumen.temperatura_minima_7d }}°C</strong><span>T° mín 7d</span></div>
      </div>

      <div class="chart-wrap">
        <v-chart class="chart" :option="chartOption" autoresize />
      </div>

      <table class="tabla">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>T° mín</th>
            <th>PoP</th>
            <th>Nubes</th>
            <th>Viento</th>
            <th>Riesgo</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(d, i) in datos" :key="i">
            <tr
              :class="{ alto: d.riesgo_severo }"
              @click="expandidoIdx = expandidoIdx === i ? -1 : i"
            >
              <td>{{ fmt(d.fecha_pronostico || d.fecha) }}</td>
              <td>
                <span class="badge" :class="tempClass(d.temperatura_minima_esperada)">
                  {{ d.temperatura_minima_esperada }}°C
                </span>
              </td>
              <td>{{ d.probabilidad_helada }}%</td>
              <td>{{ d.cobertura_nubosa ?? '—' }}%</td>
              <td>{{ d.velocidad_viento ?? '—' }} m/s</td>
              <td>{{ d.nivel_riesgo || (d.riesgo_severo ? 'Severo' : '—') }}</td>
            </tr>
            <tr v-if="expandidoIdx === i" class="detalle-row">
              <td colspan="6">
                {{ d.recomendacion || d.descripcion || 'Sin detalle adicional' }}
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </template>
    <p v-else class="empty">Sin pronóstico de helada</p>
  </div>
</template>

<style scoped>
.helada-av {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  padding: 1rem;
}
.helada-av__head { display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.75rem; }
.helada-av__head h3 { margin: 0; font-size: 1rem; }
.cultivo-sel { font-size: 0.8rem; padding: 0.3rem 0.5rem; border-radius: 6px; border: 1px solid var(--color-border); background: var(--color-surface); color: var(--color-text); }
.resumen { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; margin-bottom: 0.75rem; }
.card { background: rgba(15, 23, 42, 0.5); border-radius: 8px; padding: 0.5rem; text-align: center; border-left: 3px solid #0284c7; }
.card strong { display: block; font-size: 1.1rem; color: #38bdf8; }
.card span { font-size: 0.72rem; color: #94a3b8; }
.card.sev { border-color: #ef4444; }
.card.mod { border-color: #f59e0b; }
.chart-wrap { width: 100%; height: 300px; margin-bottom: 0.75rem; }
.chart { width: 100%; height: 100%; }
.tabla { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
.tabla th, .tabla td { padding: 0.4rem 0.35rem; border-bottom: 1px solid var(--color-border, #334155); text-align: left; }
.tabla th { color: #94a3b8; font-weight: 500; }
.tabla tr { cursor: pointer; }
.tabla tr.alto { background: rgba(239, 68, 68, 0.08); }
.detalle-row td { font-size: 0.75rem; color: #94a3b8; }
.badge { padding: 0.1rem 0.35rem; border-radius: 4px; font-weight: 600; }
.badge.ok { color: #22c55e; }
.badge.riesgo { color: #fbbf24; }
.badge.crit { color: #f87171; }
.badge.ext { color: #ef4444; }
.loading, .empty { text-align: center; padding: 1.5rem; color: #94a3b8; }
</style>
