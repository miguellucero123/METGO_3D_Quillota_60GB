<template>
  <div class="page">
    <header class="page-head">
      <h1>Ventanas operacionales</h1>
      <p>Serie horaria 48 h · semáforo por actividad en cada punto de faena</p>
    </header>

    <div class="controls">
      <label>
        Punto
        <select v-model="slugActivo">
          <option v-for="est in site.stations" :key="est.slug" :value="est.slug">
            {{ est.nombre }}
          </option>
        </select>
      </label>
    </div>

    <div v-if="loading" class="state">Calculando ventanas…</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button type="button" class="btn" @click="cargar">Reintentar</button>
    </div>

    <template v-else>
      <section v-if="actual" class="ahora" :class="`nivel-${actual.nivel_global || 'verde'}`">
        <div>
          <span class="label">Próxima hora</span>
          <strong>{{ formatearHora(actual.fecha_hora) }}</strong>
        </div>
        <div>
          <span class="label">Nivel global</span>
          <strong :class="`s-${actual.nivel_global}`">{{ etiquetaNivel(actual.nivel_global) }}</strong>
        </div>
        <div>
          <span class="label">Viento</span>
          <strong>{{ actual.viento_sostenido ?? '—' }} m/s
            <em v-if="actual.viento_racha != null">(ráfaga {{ actual.viento_racha }})</em>
          </strong>
        </div>
        <div>
          <span class="label">Visibilidad</span>
          <strong>{{ actual.visibilidad ?? '—' }} km</strong>
        </div>
        <div>
          <span class="label">UV</span>
          <strong :class="`s-${nivelAct(actual, 'exposicion_uv')}`">{{ actual.uv_index ?? '—' }}</strong>
        </div>
        <div v-if="actual.so2 != null">
          <span class="label">SO₂</span>
          <strong>{{ actual.so2 }} µg/m³</strong>
        </div>
      </section>

      <section v-if="labels.length" class="grafico">
        <v-chart class="chart" :option="chartOption" autoresize />
      </section>

      <section class="tabla-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Hora</th>
              <th>Global</th>
              <th>Tronadura</th>
              <th>Transporte</th>
              <th>Izaje</th>
              <th>UV</th>
              <th>Viento</th>
              <th>Visib.</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="f in serie.slice(0, 24)" :key="f.fecha_hora">
              <td>{{ formatearHora(f.fecha_hora) }}</td>
              <td :class="`s-${f.nivel_global}`">{{ etiquetaNivel(f.nivel_global) }}</td>
              <td :class="`s-${nivelAct(f, 'tronadura')}`">{{ etiquetaNivel(nivelAct(f, 'tronadura')) }}</td>
              <td :class="`s-${nivelAct(f, 'transporte')}`">{{ etiquetaNivel(nivelAct(f, 'transporte')) }}</td>
              <td :class="`s-${nivelAct(f, 'izaje')}`">{{ etiquetaNivel(nivelAct(f, 'izaje')) }}</td>
              <td :class="`s-${nivelAct(f, 'exposicion_uv')}`">{{ f.uv_index ?? '—' }}</td>
              <td>{{ f.viento_sostenido ?? '—' }}</td>
              <td>{{ f.visibilidad ?? '—' }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <p class="fuente">Mostrando primeras 24 h de la serie (máx. 48). Fuente: Open-Meteo Forecast.</p>
    </template>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, ref, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { wakeApi, fetchVentanas } from '@/services/operacionesApi'

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent])

const NIVEL_SCORE = { verde: 0, amarillo: 1, rojo: 2 }

const site = inject('site')
const loading = ref(true)
const error = ref(null)
const slugActivo = ref(site.stations[0]?.slug || 'mb_rajo')
const serie = ref([])

const actual = computed(() => serie.value[0] || null)
const labels = computed(() =>
  serie.value.map((f) => String(f.fecha_hora || '').slice(5, 16).replace('T', ' '))
)

const chartOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(17, 24, 39, 0.92)',
    borderColor: 'rgba(251, 146, 60, 0.3)',
    textStyle: { color: '#f3f4f6' },
  },
  legend: {
    data: ['Nivel global', 'Viento (m/s)'],
    textStyle: { color: '#9ca3af' },
    top: 0,
  },
  grid: { top: 40, left: 48, right: 16, bottom: 32 },
  xAxis: {
    type: 'category',
    data: labels.value,
    axisLabel: { color: '#9ca3af' },
    axisLine: { lineStyle: { color: '#374151' } },
  },
  yAxis: [
    {
      type: 'value',
      name: 'Nivel',
      min: 0,
      max: 2,
      interval: 1,
      axisLabel: {
        color: '#9ca3af',
        formatter: (v) => ({ 0: 'V', 1: 'A', 2: 'R' }[v] || v),
      },
      splitLine: { lineStyle: { color: '#1f2937', type: 'dashed' } },
    },
    {
      type: 'value',
      name: 'm/s',
      axisLabel: { color: '#9ca3af' },
      splitLine: { show: false },
    },
  ],
  series: [
    {
      name: 'Nivel global',
      type: 'line',
      step: 'middle',
      data: serie.value.map((f) => NIVEL_SCORE[f.nivel_global] ?? 0),
      itemStyle: { color: '#fb923c' },
      areaStyle: { opacity: 0.12 },
    },
    {
      name: 'Viento (m/s)',
      type: 'bar',
      yAxisIndex: 1,
      data: serie.value.map((f) => f.viento_sostenido),
      itemStyle: { color: '#38bdf8' },
    },
  ],
}))

function nivelAct(f, act) {
  return f?.actividades?.[act]?.nivel || 'verde'
}
function etiquetaNivel(n) {
  return { verde: 'Verde', amarillo: 'Amarillo', rojo: 'Rojo' }[n] || '—'
}
function formatearHora(iso) {
  return String(iso || '').slice(5, 16).replace('T', ' ')
}

async function cargar() {
  loading.value = true
  error.value = null
  serie.value = []
  try {
    await wakeApi()
    serie.value = (await fetchVentanas(slugActivo.value, 48)) || []
  } catch (err) {
    error.value =
      err?.status === 503
        ? 'Servicio de operaciones temporalmente no disponible.'
        : err?.message || 'No se pudieron cargar las ventanas'
  } finally {
    loading.value = false
  }
}

watch(slugActivo, cargar)
onMounted(cargar)
</script>

<style scoped>
.page { max-width: 1100px; }
.page-head { margin-bottom: 1rem; }
.page-head h1 { margin: 0 0 0.25rem; font-size: 1.6rem; }
.page-head p { margin: 0; color: var(--color-text-secondary); }
.controls { margin-bottom: 1rem; }
.controls label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}
.controls select {
  padding: 0.5rem 0.65rem;
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  max-width: 260px;
}
.ahora {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.75rem;
  border: 1px solid var(--color-border);
  border-left: 4px solid var(--color-success);
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 1rem;
}
.ahora.nivel-amarillo { border-left-color: var(--color-warning); }
.ahora.nivel-rojo { border-left-color: var(--color-danger); }
.ahora .label {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  margin-bottom: 0.15rem;
}
.grafico { margin: 0.5rem 0 1rem; }
.chart { height: 300px; width: 100%; }
.tabla-wrap { overflow-x: auto; }
.s-verde { color: var(--color-success); }
.s-amarillo { color: var(--color-warning); }
.s-rojo { color: var(--color-danger); }
.state { padding: 2rem; text-align: center; color: var(--color-text-secondary); }
.state.error { color: var(--color-danger); }
.btn {
  margin-top: 0.75rem;
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-primary);
  background: var(--color-primary-muted);
  color: var(--color-primary);
  border-radius: 6px;
  cursor: pointer;
}
.fuente { margin-top: 1rem; font-size: 0.8rem; color: var(--color-muted); }
</style>
