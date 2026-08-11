<script setup>
import { ref, computed, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  MarkLineComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { useMetgoStore } from '@/stores/metgo'
import { fetchPronosticoHeladas } from '@/api/metgoApi'
import { riesgoHeladaPorCultivo } from '@/utils/agroInsights'
import { severidadAlertaColor } from '@/utils/colorScale'
import FrostBadge from '@/components/meteo/FrostBadge.vue'
import {
  CHART_COLORS,
  tooltipOscuro,
  grillaBase,
  ejeCategoria,
  ejeValor,
  serieLineaVerde,
} from '@/utils/echartsTheme'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent, MarkLineComponent])

const store = useMetgoStore()
const data = ref(null)
const cargando = ref(false)
const cultivoSel = ref('palto')

async function cargar() {
  cargando.value = true
  try {
    data.value = await fetchPronosticoHeladas(store.estacionActiva, 7)
  } catch {
    data.value = null
  } finally {
    cargando.value = false
  }
}

watch(() => store.estacionActiva, cargar, { immediate: true })

const diasFiltrados = computed(() => {
  const dias = data.value?.dias ?? []
  return dias.map((d) => ({
    ...d,
    riesgo: riesgoHeladaPorCultivo(d.temperatura_min, cultivoSel.value),
    sevCultivo: d.por_cultivo?.[cultivoSel.value] ?? 'bajo',
  }))
})

const peor = computed(() => data.value?.peor_dia)

const chartOption = computed(() => {
  const dias = data.value?.dias ?? []
  const labels = dias.map((d) => d.fecha)
  const tmins = dias.map((d) => d.temperatura_min)
  return {
    backgroundColor: 'transparent',
    tooltip: tooltipOscuro((params) => {
      const p = params[0]
      return `<div style="font-weight:bold;margin-bottom:5px;border-bottom:1px solid #4b5563;padding-bottom:5px;">${p.axisValue}</div>
              <div style="display:flex;justify-content:space-between;">
                <span style="color:${p.color};margin-right:15px;">● T. Mínima</span>
                <b>${p.value} °C</b>
              </div>`
    }),
    grid: { ...grillaBase(), bottom: '8%' },
    xAxis: [ejeCategoria(labels)],
    yAxis: [
      ejeValor('Temperatura (°C)', CHART_COLORS.verde, {
        position: 'left',
        axisLabel: { formatter: '{value} °C', color: CHART_COLORS.texto },
      }),
    ],
    series: [
      serieLineaVerde('T. Mínima', tmins, {
        symbolSize: 8,
        markLine: {
          silent: true,
          data: [{ yAxis: 0, name: 'Helada' }],
          lineStyle: { color: CHART_COLORS.rojo, type: 'dashed' },
          label: { position: 'start', formatter: 'Helada (0°C)', color: CHART_COLORS.texto },
        },
      }),
    ],
  }
})
</script>

<template>
  <div class="heladas-panel">
    <header class="heladas-panel__head">
      <div class="title-row">
        <FrostBadge size="sm" />
        <h3>Pronóstico de heladas — 7 días</h3>
      </div>
      <select v-model="cultivoSel" class="cultivo-sel">
        <option value="palto">Palto</option>
        <option value="vid">Vid</option>
        <option value="citricos">Cítricos</option>
        <option value="tomate">Tomate</option>
        <option value="lechuga">Lechuga</option>
      </select>
    </header>

    <div v-if="cargando" class="loading">Cargando…</div>
    <div v-else-if="!data" class="empty">Sin pronóstico de heladas</div>
    <template v-else>
      <div v-if="data.alerta_activa && peor" class="alerta-helada">
        <strong>Alerta activa:</strong> mín {{ peor.temperatura_min }}°C el {{ peor.fecha }}
      </div>
      <div class="chart-wrap">
        <v-chart class="chart" :option="chartOption" autoresize />
      </div>
      <ul class="dias-list">
        <li v-for="d in diasFiltrados" :key="d.fecha" class="dia-item">
          <span class="fecha">{{ d.fecha }}</span>
          <span class="temp">{{ d.temperatura_min }}°C</span>
          <span
            class="badge"
            :style="{ background: severidadAlertaColor(d.sevCultivo) + '22', color: severidadAlertaColor(d.sevCultivo) }"
          >
            {{ d.riesgo.label }}
          </span>
        </li>
      </ul>
      <p class="fuente">Fuente: {{ data.fuente }} · {{ data.tipo_dato }}</p>
    </template>
  </div>
</template>

<style scoped>
.heladas-panel {
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  padding: 1rem;
  background: var(--color-surface, #1e293b);
}
.heladas-panel__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}
.title-row { display: flex; align-items: center; gap: 0.5rem; }
.title-row h3 { margin: 0; font-size: 0.95rem; }
.cultivo-sel { font-size: 0.8rem; padding: 0.3rem 0.5rem; border-radius: 6px; border: 1px solid var(--color-border, #334155); }
.alerta-helada {
  background: var(--color-alert-bg, rgba(239, 68, 68, 0.1));
  border-left: 3px solid #ef4444;
  padding: 0.5rem 0.65rem;
  border-radius: 6px;
  font-size: 0.82rem;
  margin-bottom: 0.65rem;
}
.chart-wrap { width: 100%; height: 300px; margin-bottom: 0.75rem; }
.chart { width: 100%; height: 100%; }
.dias-list { list-style: none; margin: 0; padding: 0; }
.dia-item {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 0.5rem;
  padding: 0.4rem 0;
  border-bottom: 1px solid var(--color-border, #334155);
  font-size: 0.82rem;
}
.badge { padding: 0.15rem 0.45rem; border-radius: 4px; font-weight: 600; font-size: 0.72rem; }
.fuente { margin: 0.5rem 0 0; font-size: 0.72rem; color: #9ca3af; }
.loading, .empty { padding: 1rem; text-align: center; color: #6b7280; }
</style>
