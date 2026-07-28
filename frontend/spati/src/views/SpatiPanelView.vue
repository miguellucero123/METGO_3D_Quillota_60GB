<template>
  <div class="page">
    <header class="page-head">
      <h1>Pronóstico de izaje</h1>
      <p>72 h · Δt 15 min · física de pluma + alertas 0–3</p>
    </header>

    <div class="controls">
      <label>
        Sitio / grúa
        <select v-model="sitioId">
          <option v-for="s in sitios" :key="s.sitio_id || s.slug" :value="s.sitio_id || s.slug">
            {{ s.nombre }}{{ s.region ? ` · ${s.region}` : '' }}{{ s.altitud_msnm ? ` (${s.altitud_msnm} m)` : '' }}
          </option>
        </select>
      </label>
      <button type="button" class="btn" :disabled="loading" @click="cargar">Actualizar</button>
    </div>

    <div v-if="loading" class="state">Calculando SPATI (Open-Meteo + física)…</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button type="button" class="btn" @click="cargar">Reintentar</button>
    </div>

    <template v-else-if="data">
      <section class="hero-nivel" :class="'n' + data.nivel_maximo">
        <div>
          <span class="lbl">Nivel máximo 72 h</span>
          <strong>{{ data.nivel_maximo_nombre }}</strong>
        </div>
        <div>
          <span class="lbl">Intervalos</span>
          <strong>{{ data.n_intervalos }}</strong>
        </div>
        <div>
          <span class="lbl">MOS</span>
          <strong>{{ data.modo_sin_mos ? 'sin calibración ML' : 'activo' }}</strong>
        </div>
        <div v-if="data.config?.altitud_msnm">
          <span class="lbl">Altitud</span>
          <strong>{{ data.config.altitud_msnm }} m s.n.m.</strong>
        </div>
        <div v-if="data.config?.operador">
          <span class="lbl">Operador</span>
          <strong>{{ data.config.operador }}</strong>
        </div>
        <div v-if="data.config?.factor_reduccion != null">
          <span class="lbl">FR densidad</span>
          <strong>{{ Number(data.config.factor_reduccion).toFixed(3) }}</strong>
        </div>
        <div v-if="data.config?.rho_isa_kg_m3 != null">
          <span class="lbl">ρ ISA</span>
          <strong>{{ Number(data.config.rho_isa_kg_m3).toFixed(3) }} kg/m³</strong>
        </div>
        <div v-if="data.config?.v_equiv_36_kmh != null">
          <span class="lbl">v equiv. 36 km/h</span>
          <strong>{{ data.config.v_equiv_36_kmh }} km/h</strong>
        </div>
        <div v-if="data.config?.gust_factor != null">
          <span class="lbl">Factor ráfaga</span>
          <strong>{{ Number(data.config.gust_factor).toFixed(2) }}</strong>
        </div>
        <div v-if="data.config?.z0_terreno != null">
          <span class="lbl">z₀</span>
          <strong>{{ data.config.z0_terreno }} m</strong>
        </div>
        <div v-if="data.config?.requiere_autorizacion_dgac">
          <span class="lbl">Dron</span>
          <strong>Requiere DGAC</strong>
        </div>
        <div v-if="data.sesgo_dron_kmh != null">
          <span class="lbl">Sesgo dron</span>
          <strong>{{ data.sesgo_dron_kmh.toFixed(1) }} km/h</strong>
        </div>
      </section>

      <p v-if="data.config?.alta_montana" class="muted ha-note">
        Alta montaña activo · umbral crítico 36 km/h constante · control por fuerza F=½ρv²ACd
        <template v-if="data.config.zona_climatica"> · zona {{ data.config.zona_climatica }}</template>
        <template v-if="data.config.riesgo_eolico"> · riesgo {{ data.config.riesgo_eolico }}</template>
      </p>

      <pre class="resumen">{{ data.resumen_ejecutivo }}</pre>

      <section class="ventanas" v-if="(data.ventanas_seguras || []).length">
        <h2>Ventanas seguras (≥ 2 h VERDE)</h2>
        <ul>
          <li v-for="(v, i) in data.ventanas_seguras" :key="i">
            {{ fmt(v.inicio) }} → {{ fmt(v.fin) }}
            <span class="muted">({{ v.duracion_horas }} h · máx {{ v.rafaga_max_en_ventana ?? '—' }} km/h)</span>
          </li>
        </ul>
      </section>
      <p v-else class="muted">Sin ventanas seguras ≥ 2 h en el horizonte.</p>

      <v-chart class="chart" :option="chartOption" autoresize role="img" aria-label="Serie SPATI" />

      <div class="legend">
        <span class="chip n0">0 Verde &lt;26</span>
        <span class="chip n1">1 Amarillo 26–29</span>
        <span class="chip n2">2 Naranja 30–34</span>
        <span class="chip n3">3 Rojo ≥35 (flag 36)</span>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, ref, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, ScatterChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, MarkLineComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { fetchSpatiPronostico, fetchSpatiSitios } from '@/services/spatiApi'

use([CanvasRenderer, LineChart, ScatterChart, GridComponent, TooltipComponent, LegendComponent, MarkLineComponent])

const site = inject('site')
const sitioId = ref(site.spatiDefaultSitio || 'escondida')
const sitios = ref(
  (site.stations || []).map((s) => ({
    sitio_id: s.slug,
    nombre: s.nombre,
    region: s.region,
    altitud_msnm: s.altitud_msnm,
  }))
)
const loading = ref(true)
const error = ref(null)
const data = ref(null)

function fmt(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('es-CL', { dateStyle: 'short', timeStyle: 'short' })
  } catch {
    return iso
  }
}

const chartOption = computed(() => {
  const serie = data.value?.serie || []
  const times = serie.map((r) => r.valid_time)
  const vfinal = serie.map((r) => r.v_final_kmh)
  const vfisica = serie.map((r) => r.v_fisica_grua)
  const veas = serie.map((r) => r.v_eas_kmh)
  const niveles = serie.map((r) => r.nivel_alerta)
  return {
    animation: false,
    tooltip: { trigger: 'axis' },
    legend: { data: ['v final', 'v física pluma', 'v EAS'], top: 0 },
    grid: { left: 48, right: 24, top: 40, bottom: 56 },
    xAxis: { type: 'category', data: times, axisLabel: { formatter: (v) => fmt(v).split(',')[1] || v } },
    yAxis: { type: 'value', name: 'km/h', min: 0 },
    series: [
      {
        name: 'v final',
        type: 'line',
        data: vfinal,
        showSymbol: false,
        lineStyle: { width: 2, color: '#3b82f6' },
        markLine: {
          symbol: 'none',
          data: [
            { yAxis: 26, lineStyle: { color: '#eab308', type: 'dashed' }, label: { formatter: '26' } },
            { yAxis: 36, lineStyle: { color: '#ef4444', type: 'dashed' }, label: { formatter: '36' } },
          ],
        },
      },
      {
        name: 'v física pluma',
        type: 'line',
        data: vfisica,
        showSymbol: false,
        lineStyle: { width: 1.5, type: 'dotted', color: '#94a3b8' },
      },
      {
        name: 'v EAS',
        type: 'line',
        data: veas,
        showSymbol: false,
        lineStyle: { width: 1.5, color: '#a78bfa' },
      },
      {
        name: 'nivel',
        type: 'scatter',
        data: niveles.map((n, i) => [i, n]),
        symbolSize: 0,
      },
    ],
  }
})

async function cargar() {
  loading.value = true
  error.value = null
  try {
    data.value = await fetchSpatiPronostico(sitioId.value)
  } catch (e) {
    error.value = e?.message || 'Error SPATI'
    data.value = null
  } finally {
    loading.value = false
  }
}

watch(sitioId, cargar)
onMounted(async () => {
  try {
    const list = await fetchSpatiSitios()
    if (list?.length) {
      sitios.value = list.map((s) => ({
        sitio_id: s.sitio_id,
        nombre: s.nombre,
        region: s.region,
        altitud_msnm: s.altitud_msnm,
      }))
    }
  } catch {
    /* seed local */
  }
  await cargar()
})
</script>

<style scoped>
.page { max-width: 960px; margin: 0 auto; padding: 1.25rem; }
.page-head h1 { margin: 0 0 0.35rem; }
.page-head p { margin: 0; color: var(--color-muted); }
.controls { display: flex; gap: 0.75rem; align-items: end; margin: 1.25rem 0; flex-wrap: wrap; }
.controls label { display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.85rem; }
.controls select { min-width: 220px; padding: 0.45rem 0.6rem; border-radius: var(--radius-md); border: 1px solid var(--color-border); background: var(--color-surface); color: var(--color-text); }
.btn { padding: 0.5rem 1rem; border-radius: var(--radius-md); border: none; background: var(--color-primary); color: #0b1120; font-weight: 600; cursor: pointer; }
.btn:disabled { opacity: 0.6; }
.state { padding: 1.5rem; color: var(--color-muted); }
.state.error { color: #fca5a5; }
.hero-nivel { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.75rem; padding: 1rem; border-radius: var(--radius-md); border: 1px solid var(--color-border); margin-bottom: 1rem; }
.hero-nivel .lbl { display: block; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--color-muted); }
.hero-nivel.n0 { border-color: #22c55e55; }
.hero-nivel.n1 { border-color: #eab30855; }
.hero-nivel.n2 { border-color: #f9731655; }
.hero-nivel.n3 { border-color: #ef444455; background: #ef444411; }
.resumen { white-space: pre-wrap; background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-md); padding: 0.85rem 1rem; font-size: 0.85rem; margin-bottom: 1rem; }
.ventanas h2 { font-size: 1rem; margin: 0 0 0.5rem; }
.ventanas ul { margin: 0; padding-left: 1.1rem; }
.muted { color: var(--color-muted); font-size: 0.85rem; }
.ha-note { margin: 0 0 1rem; padding: 0.5rem 0; border-bottom: 1px solid var(--color-border); }
.chart { height: 360px; width: 100%; margin-top: 1rem; }
.legend { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.75rem; }
.chip { font-size: 0.75rem; padding: 0.2rem 0.5rem; border-radius: 4px; border: 1px solid var(--color-border); }
.chip.n0 { color: #86efac; }
.chip.n1 { color: #fde68a; }
.chip.n2 { color: #fdba74; }
.chip.n3 { color: #fca5a5; }
</style>
