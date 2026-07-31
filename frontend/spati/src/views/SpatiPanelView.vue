<template>
  <div class="page">
    <header class="page-head">
      <h1>Panel técnico · Pronóstico de izaje</h1>
      <p>72 h · Δt 15 min · física de pluma + alertas 0–3 · vista experta</p>
    </header>

    <div class="controls">
      <p class="faena-fija">
        Faena:
        <strong>{{ faenaMeta?.nombre || sitioId }}</strong>
        <span v-if="faenaMeta?.region" class="muted"> · {{ faenaMeta.region }}</span>
        <span v-if="faenaMeta?.altitud_msnm" class="muted"> ({{ faenaMeta.altitud_msnm }} m)</span>
      </p>
      <button type="button" class="btn" :disabled="loading" @click="cargar">Actualizar</button>
    </div>

    <div v-if="loading" class="state">Actualizando pronóstico…</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button type="button" class="btn" @click="cargar">Reintentar</button>
    </div>

    <template v-else-if="data">
      <p v-if="data.nwp_aviso" class="aviso-nwp" role="status">{{ data.nwp_aviso }}</p>
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

      <section v-if="data.variables_zona_izaje" class="zona-ops">
        <h2>Variables de zona de izaje (ahora)</h2>
        <div class="ops-grid">
          <div><span class="lbl">Condición</span><strong>{{ data.variables_zona_izaje.condicion_izaje }}</strong></div>
          <div><span class="lbl">v 10 m</span><strong>{{ n(data.variables_zona_izaje.v_10m_kmh) }} km/h</strong></div>
          <div><span class="lbl">v 80 m</span><strong>{{ n(data.variables_zona_izaje.v_80m_kmh) }} km/h</strong></div>
          <div><span class="lbl">v 100 m</span><strong>{{ n(data.variables_zona_izaje.v_100m_kmh) }} km/h</strong></div>
          <div><span class="lbl">v pluma {{ data.config?.altura_pluma_m }} m</span><strong>{{ n(data.variables_zona_izaje.v_pluma_kmh) }} km/h</strong></div>
          <div><span class="lbl">Ráfaga 10 m</span><strong>{{ n(data.variables_zona_izaje.rafaga_10m_kmh) }} km/h</strong></div>
          <div><span class="lbl">Cizalladura 10–100</span><strong>{{ n(data.variables_zona_izaje.cizalladura_10_100?.delta_v_kmh) }} km/h</strong></div>
          <div><span class="lbl">Turbulencia</span><strong>{{ n(data.variables_zona_izaje.indice_turbulencia, 3) }}</strong></div>
          <div><span class="lbl">Fuerza carga</span><strong>{{ n(data.variables_zona_izaje.fuerza_carga_n, 0) }} N</strong></div>
          <div><span class="lbl">% límite</span><strong>{{ n(data.variables_zona_izaje.pct_limite_diseno, 0) }} %</strong></div>
          <div><span class="lbl">Visibilidad</span><strong>{{ n(data.variables_zona_izaje.visibilidad_km, 1) }} km</strong></div>
          <div><span class="lbl">RH / precip</span><strong>{{ n(data.variables_zona_izaje.rh_pct, 0) }} % · {{ n(data.variables_zona_izaje.precip_mmh, 1) }} mm/h</strong></div>
        </div>
      </section>

      <section class="perfil-sec">
        <h2>Perfil vertical de viento (10–200 m AGL)</h2>
        <p class="muted">
          Anclas NWP 10 / 80 / 100 m · niveles intermedios y 200 m por perfil logarítmico (z₀={{ data.config?.z0_terreno }})
          · pluma marcada a {{ data.config?.altura_pluma_m }} m
        </p>
        <div class="perfil-charts">
          <v-chart class="chart-perfil" :option="perfilAhoraOption" autoresize role="img" aria-label="Perfil ahora" />
          <v-chart class="chart-perfil" :option="perfilPicoOption" autoresize role="img" aria-label="Perfil pico" />
        </div>
        <div class="perfil-tables" v-if="nivelesAhora.length">
          <table>
            <thead>
              <tr><th>Altura (m)</th><th>Ahora (km/h)</th><th>F (N)</th><th>Pico (km/h)</th><th>Fuente</th></tr>
            </thead>
            <tbody>
              <tr v-for="row in tablaPerfil" :key="row.h" :class="{ pluma: row.esPluma }">
                <td>{{ row.h }}{{ row.esPluma ? ' · pluma' : '' }}</td>
                <td>{{ n(row.vAhora) }}</td>
                <td>{{ n(row.fAhora, 0) }}</td>
                <td>{{ n(row.vPico) }}</td>
                <td class="mono">{{ row.fuente }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <h2 class="serie-title">Serie 72 h</h2>
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
import { useRoute } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, ScatterChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, MarkLineComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { fetchSpatiPronostico, getApiBase } from '@/services/spatiApi'
import { wakeApi } from '@/services/authApi'

use([CanvasRenderer, LineChart, ScatterChart, GridComponent, TooltipComponent, LegendComponent, MarkLineComponent])

const site = inject('site')
const route = useRoute()
const injectedFaena = inject('faena', null)
const injectedMeta = inject('faenaMeta', null)

const sitioId = computed(
  () =>
    (injectedFaena && injectedFaena.value) ||
    String(route.params.faena || site.spatiDefaultSitio || 'escondida').toLowerCase(),
)
const faenaMeta = computed(
  () =>
    (injectedMeta && injectedMeta.value) ||
    (site.stations || []).find((s) => s.slug === sitioId.value) || {
      slug: sitioId.value,
      nombre: sitioId.value,
    },
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

function n(v, nd = 1) {
  if (v == null || Number.isNaN(Number(v))) return '—'
  return Number(v).toFixed(nd)
}

const nivelesAhora = computed(() => data.value?.perfil_vertical_ahora?.niveles || [])
const nivelesPico = computed(() => data.value?.perfil_vertical_pico?.niveles || [])

const tablaPerfil = computed(() => {
  const ahora = Object.fromEntries((nivelesAhora.value || []).map((p) => [p.altura_m, p]))
  const pico = Object.fromEntries((nivelesPico.value || []).map((p) => [p.altura_m, p]))
  const hs = data.value?.config?.alturas_perfil_m || [10, 20, 30, 40, 50, 60, 70, 80, 100, 200]
  const pluma = Number(data.value?.config?.altura_pluma_m || 55)
  return hs.map((h) => ({
    h,
    vAhora: ahora[h]?.v_kmh,
    fAhora: ahora[h]?.fuerza_n,
    vPico: pico[h]?.v_kmh,
    fuente: ahora[h]?.fuente || pico[h]?.fuente || '—',
    esPluma: Math.abs(h - pluma) < 6,
  }))
})

function perfilChart(niveles, titulo) {
  const pts = (niveles || []).map((p) => [p.v_kmh, p.altura_m])
  const pluma = Number(data.value?.config?.altura_pluma_m || 55)
  return {
    animation: false,
    title: { text: titulo, left: 0, top: 0, textStyle: { fontSize: 12, color: '#94a3b8', fontWeight: 500 } },
    tooltip: {
      trigger: 'item',
      formatter: (p) => `${p.value[1]} m AGL · ${p.value[0]} km/h`,
    },
    grid: { left: 48, right: 16, top: 32, bottom: 40 },
    xAxis: { type: 'value', name: 'km/h', min: 0 },
    yAxis: { type: 'value', name: 'm AGL', min: 0, max: 220 },
    series: [
      {
        type: 'line',
        data: pts,
        symbolSize: 7,
        lineStyle: { width: 2, color: '#14b8a6' },
        itemStyle: { color: '#5eead4' },
        markLine: {
          symbol: 'none',
          data: [
            {
              yAxis: pluma,
              lineStyle: { color: '#3b82f6', type: 'dashed' },
              label: { formatter: `pluma ${pluma} m`, position: 'insideEndTop' },
            },
            {
              xAxis: 36,
              lineStyle: { color: '#ef4444', type: 'dotted' },
              label: { formatter: '36' },
            },
          ],
        },
      },
    ],
  }
}

const perfilAhoraOption = computed(() =>
  perfilChart(nivelesAhora.value, `Ahora · ${fmt(data.value?.perfil_vertical_ahora?.valid_time)}`)
)
const perfilPicoOption = computed(() =>
  perfilChart(
    nivelesPico.value,
    `Pico 72 h · ${fmt(data.value?.perfil_vertical_pico?.valid_time)} · ${n(data.value?.perfil_vertical_pico?.v_final_kmh)} km/h`
  )
)

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
    await wakeApi()
    data.value = await fetchSpatiPronostico(sitioId.value)
  } catch (e) {
    const msg = e?.message || 'Error al calcular el pronóstico'
    error.value =
      e?.code === 'TIMEOUT'
        ? msg
        : `${msg}. API: ${getApiBase()}`
    data.value = null
  } finally {
    loading.value = false
  }
}

watch(sitioId, cargar)
onMounted(() => cargar())
</script>

<style scoped>
.page { max-width: 960px; margin: 0 auto; padding: 1.25rem; }
.page-head h1 { margin: 0 0 0.35rem; }
.page-head p { margin: 0; color: var(--color-muted); }
.controls { display: flex; gap: 0.75rem; align-items: center; margin: 1.25rem 0; flex-wrap: wrap; }
.faena-fija { margin: 0; font-size: 0.9rem; color: var(--color-text-secondary); }
.faena-fija strong { color: var(--color-text); }
.btn { padding: 0.5rem 1rem; border-radius: var(--radius-md); border: none; background: var(--color-primary); color: #0f172a; font-weight: 700; cursor: pointer; }
.btn:disabled { opacity: 0.6; }
.state { padding: 1.5rem; color: var(--color-muted); }
.state.error { color: #fca5a5; }
.aviso-nwp {
  margin: 0 0 1rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  border: 1px solid #f59e0b66;
  background: #f59e0b14;
  color: #fde68a;
  font-size: 0.88rem;
}
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
.zona-ops, .perfil-sec { margin: 1.25rem 0; }
.zona-ops h2, .perfil-sec h2, .serie-title { font-size: 1rem; margin: 0 0 0.5rem; }
.ops-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.65rem; padding: 0.85rem; border: 1px solid var(--color-border); border-radius: var(--radius-md); background: var(--color-surface); }
.ops-grid .lbl { display: block; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--color-muted); }
.perfil-charts { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 0.75rem; }
.chart-perfil { height: 320px; width: 100%; border: 1px solid var(--color-border); border-radius: var(--radius-md); padding: 0.35rem; }
.perfil-tables { margin-top: 0.75rem; overflow-x: auto; }
.perfil-tables table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.perfil-tables th, .perfil-tables td { padding: 0.4rem 0.55rem; border-bottom: 1px solid var(--color-border); text-align: left; }
.perfil-tables tr.pluma { background: rgba(59, 130, 246, 0.08); }
.perfil-tables .mono { font-family: ui-monospace, Consolas, monospace; font-size: 0.72rem; color: var(--color-muted); }
.chart { height: 360px; width: 100%; margin-top: 0.5rem; }
.legend { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.75rem; }
.chip { font-size: 0.75rem; padding: 0.2rem 0.5rem; border-radius: 4px; border: 1px solid var(--color-border); }
.chip.n0 { color: #86efac; }
.chip.n1 { color: #fde68a; }
.chip.n2 { color: #fdba74; }
.chip.n3 { color: #fca5a5; }
</style>
