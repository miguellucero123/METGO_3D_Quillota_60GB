<template>
  <div class="page">
    <header class="page-head">
      <h1>Sounding modelado</h1>
      <p>Perfil vertical Open-Meteo (proxy MetPy) · estaciones faena {{ site.faena?.nombre || site.siteLabel }}</p>
    </header>

    <div class="controls">
      <label>
        Estación
        <select v-model="slug">
          <option v-for="est in site.stations" :key="est.slug" :value="est.slug">
            {{ est.nombre }}
          </option>
        </select>
      </label>
      <button type="button" class="btn" @click="cargar" :disabled="loading">Actualizar</button>
    </div>

    <div v-if="loading" class="state">Obteniendo perfil…</div>
    <div v-else-if="error" class="state error">{{ error }}</div>
    <template v-else-if="data">
      <p class="nota">{{ data.nota }}</p>
      <div class="diag" v-if="frame">
        <span
          >Ventilación
          <b class="badge" :class="frame.diagnostico?.ventilacion">{{
            frame.diagnostico?.ventilacion
          }}</b></span
        >
        <span>Inversión: {{ frame.diagnostico?.inversion ? 'sí' : 'no' }}</span>
        <span>Lapse 925–700: {{ frame.diagnostico?.lapse_925_700_c_km ?? '—' }} °C/km</span>
        <span>PBL: {{ frame.diagnostico?.altura_capa_limite ?? '—' }} m</span>
      </div>
      <label class="scrub" v-if="(data.frames || []).length > 1">
        Hora
        <input type="range" min="0" :max="data.frames.length - 1" v-model.number="idx" />
        {{ frame?.fecha_hora }}
      </label>
      <v-chart class="chart" :option="chartOption" autoresize role="img" aria-label="Skew-T lite" />
    </template>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, ref, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { fetchSounding, ESTACION_ANCLA } from '@/services/aireApi'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

const site = inject('site')
const slug = ref(site.faena?.estacionAncla || site.stations?.[0]?.slug || ESTACION_ANCLA)
const loading = ref(true)
const error = ref(null)
const data = ref(null)
const idx = ref(0)

const frame = computed(() => (data.value?.frames || [])[idx.value] || null)

const chartOption = computed(() => {
  const niveles = [...(frame.value?.niveles || [])].filter((n) => n.temp_c != null && n.pressure_hPa)
  const temps = niveles.map((n) => [n.temp_c, n.pressure_hPa])
  const tds = niveles
    .filter((n) => n.dewpoint_c != null)
    .map((n) => [n.dewpoint_c, n.pressure_hPa])
  return {
    animation: false,
    tooltip: { trigger: 'item' },
    legend: { data: ['T', 'Td'], top: 0 },
    grid: { left: 56, right: 24, top: 36, bottom: 40 },
    xAxis: { name: '°C', type: 'value', nameLocation: 'middle', nameGap: 28 },
    yAxis: {
      name: 'hPa',
      type: 'log',
      inverse: true,
      min: 500,
      max: 1050,
      axisLabel: { formatter: (v) => Math.round(v) },
    },
    series: [
      { name: 'T', type: 'line', data: temps, showSymbol: true, symbolSize: 6, lineStyle: { width: 2, color: '#dc2626' }, itemStyle: { color: '#dc2626' } },
      { name: 'Td', type: 'line', data: tds, showSymbol: true, symbolSize: 5, lineStyle: { width: 2, type: 'dashed', color: '#16a34a' }, itemStyle: { color: '#16a34a' } },
    ],
  }
})

async function cargar() {
  loading.value = true
  error.value = null
  try {
    data.value = await fetchSounding(slug.value, 24)
    idx.value = 0
  } catch (e) {
    error.value = e?.message || 'Error sounding'
    data.value = null
  } finally {
    loading.value = false
  }
}

watch(slug, cargar)
onMounted(cargar)
</script>

<style scoped>
.page {
  max-width: 900px;
  margin: 0 auto;
  padding: 1.25rem;
}
.page-head h1 {
  margin: 0 0 0.35rem;
}
.page-head p {
  margin: 0;
  color: var(--color-text-secondary);
}
.controls {
  display: flex;
  gap: 1rem;
  align-items: end;
  margin: 1rem 0;
}
.controls label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.85rem;
}
.controls select {
  padding: 0.4rem 0.55rem;
  border-radius: 8px;
  border: 1px solid var(--color-border);
}
.btn {
  border: none;
  border-radius: 8px;
  padding: 0.45rem 0.9rem;
  background: var(--color-primary);
  font-weight: 600;
  cursor: pointer;
}
.nota {
  font-size: 0.8rem;
  color: var(--color-muted);
}
.diag {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
  margin: 0.75rem 0;
  font-size: 0.85rem;
}
.badge {
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}
.badge.N {
  background: #bbf7d0;
}
.badge.R {
  background: #fde68a;
}
.badge.M {
  background: #fecaca;
}
.scrub {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  font-size: 0.85rem;
}
.scrub input {
  flex: 1;
}
.chart {
  height: 420px;
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  background: var(--color-surface);
}
.state {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-secondary);
}
.state.error {
  color: #b91c1c;
}
</style>
