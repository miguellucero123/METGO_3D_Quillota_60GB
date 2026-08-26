<template>
  <div class="premium-page">
    <div class="premium-bg-glow"></div>
    <div class="premium-bg-glow secondary"></div>

    <header class="premium-header">
      <div class="title-area">
        <h1>Panel Portuario · WRF + ERA5</h1>
        <p>Inteligencia Oceanográfica Hiperlocal (72 h)</p>
      </div>
      <div class="controls-area">
        <div class="faena-badge">
          <span>Puerto Activo</span>
          <strong>{{ faenaMeta?.nombre || sitioId }}</strong>
        </div>
        <button type="button" class="btn-premium" :disabled="loading" @click="cargar">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Actualizar Datos</span>
        </button>
      </div>
    </header>

    <div v-if="loading" class="state-loader">
      <div class="wave-loader"></div>
      <p>Sincronizando con modelo ERA5...</p>
    </div>
    
    <div v-else-if="error" class="state-error glass-card">
      <div class="error-icon">⚠️</div>
      <p>{{ error }}</p>
      <button type="button" class="btn-premium alert-btn" @click="cargar">Reintentar Conexión</button>
    </div>

    <template v-else-if="data">
      <!-- ALERTAS -->
      <section v-if="alertasActivas.length" class="alert-section">
        <h2 class="section-title">Niveles de Riesgo y Alertas</h2>
        <div class="alerts-grid">
          <div v-for="(alerta, index) in alertasActivas" :key="index" :class="['alert-card glass-card', alerta.level]">
            <div class="alert-icon" v-if="alerta.level === 'RED' || alerta.level === 'CRITICAL'">🔴</div>
            <div class="alert-icon" v-else>🟡</div>
            <div class="alert-content">
              <span class="alert-badge">{{ alerta.level }}</span>
              <strong class="alert-type">{{ alerta.type }}</strong>
              <span class="alert-time">{{ formatoFecha(alerta.timestamp) }}</span>
              <p class="alert-desc" v-if="alerta.type === 'sustained_wind'">Viento: {{ n(alerta.wind_kmh) }} km/h (Umbral: {{ alerta.threshold_kmh }})</p>
              <p class="alert-desc" v-else-if="alerta.type === 'ship_heave'">Cabeceo crítico: {{ n(alerta.heave_m, 2) }} m</p>
              <p class="alert-desc" v-else-if="alerta.type === 'swell_long_period'">Tp: {{ n(alerta.Tp_s, 1) }} s, Hs: {{ n(alerta.Hs_m, 1) }}m</p>
            </div>
          </div>
        </div>
      </section>
      
      <!-- WIDGETS CONDICIONES ACTUALES -->
      <section v-if="estadoActual" class="widgets-section">
        <h2 class="section-title">Condiciones de Izaje y Fondeo</h2>
        <div class="widgets-grid">
          <div class="widget glass-card">
            <div class="widget-icon">💨</div>
            <div class="widget-info">
              <span class="lbl">Viento Base (10m)</span>
              <strong class="val">{{ n(estadoActual.wind_surface_kmh) }} <small>km/h</small></strong>
              <span class="sub">Dir: {{ n(estadoActual.wind_direction_surface, 0) }}°</span>
            </div>
          </div>
          <div class="widget glass-card highlight">
            <div class="widget-icon">🏗️</div>
            <div class="widget-info">
              <span class="lbl">Viento Izaje (40m)</span>
              <strong class="val">{{ n(vientoActualAlturas[40]) }} <small>km/h</small></strong>
              <span class="sub">Ráfagas: {{ n(estadoActual.wind_gust_10m_kmh * 1.15) }} km/h</span>
            </div>
          </div>
          <div class="widget glass-card danger">
            <div class="widget-icon">⚓</div>
            <div class="widget-info">
              <span class="lbl">Tensión Espigas (ITE)</span>
              <strong class="val">{{ estadoActualIte.value }} <small>idx</small></strong>
              <span class="sub" :class="estadoActualIte.level">{{ estadoActualIte.level }}</span>
            </div>
          </div>
          <div class="widget glass-card ocean">
            <div class="widget-icon">🌊</div>
            <div class="widget-info">
              <span class="lbl">Swell (Energía)</span>
              <strong class="val">{{ estadoActualIte.waveEnergyFlux_kWm }} <small>kW/m</small></strong>
              <span class="sub">Hs: {{ estadoActual.wave_params ? n(estadoActual.wave_params.Hs, 2) : '—' }}m</span>
            </div>
          </div>
          <div class="widget glass-card">
            <div class="widget-icon">🌔</div>
            <div class="widget-info">
              <span class="lbl">Nivel de Marea</span>
              <strong class="val">{{ n(mareaActual) }} <small>m</small></strong>
              <span class="sub">Ref: Nivel de Reducción</span>
            </div>
          </div>
        </div>
      </section>

      <!-- GRAFICOS -->
      <section class="charts-section">
        <div class="chart-container glass-card chart-large">
          <h3 class="chart-title">Perfil Vertical de Vientos en Grúas (10m a 200m)</h3>
          <v-chart class="chart-canvas large" :option="chartVientoOption" autoresize />
        </div>
        
        <div class="chart-container glass-card chart-large">
          <h3 class="chart-title">Oceanografía Física y Resonancia en Espigas (ITE)</h3>
          <v-chart class="chart-canvas large" :option="chartOlaOption" autoresize />
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, MarkLineComponent, MarkAreaComponent, DataZoomComponent, VisualMapComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { fetchSpatiPuertoPronostico, getApiBase } from '@/services/spatiApi'
import { wakeApi } from '@/services/authApi'
import { calculateWindProfile, calculateSpudStressIndex, generateSyntheticTide } from '@/utils/oceanPhysics'

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent, MarkLineComponent, MarkAreaComponent, DataZoomComponent, VisualMapComponent])

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

const estados = computed(() => data.value?.hourly_states || [])
const alertasActivas = computed(() => data.value?.alerts || [])

// --- MODELOS OCEANOGRÁFICOS ---
const z0 = computed(() => faenaMeta.value?.z0 || 0.05) // Rugosidad
const alturas = [40, 100, 150, 200]

const estadosFisicos = computed(() => {
  if (!estados.value.length) return []
  const times = estados.value.map(s => s.timestamp)
  const mareas = generateSyntheticTide(times)
  
  return estados.value.map((s, i) => {
    const v10 = s.wind_surface_kmh || 0
    const hs = s.wave_params?.Hs || 0
    const tp = s.wave_params?.Tp || 0
    
    return {
      ...s,
      vientosAltura: calculateWindProfile(v10, z0.value, alturas),
      ite: calculateSpudStressIndex(hs, tp, v10),
      marea_m: mareas[i]?.level_m || 0.8
    }
  })
})

const estadoActual = computed(() => estadosFisicos.value.length > 0 ? estadosFisicos.value[0] : null)
const vientoActualAlturas = computed(() => estadoActual.value?.vientosAltura || {})
const estadoActualIte = computed(() => estadoActual.value?.ite || { value: 0, level: 'SEGURO', waveEnergyFlux_kWm: 0 })
const mareaActual = computed(() => estadoActual.value?.marea_m || 0)

function formatoFecha(iso) {
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

const chartVientoOption = computed(() => {
  if (!estadosFisicos.value.length) return {}
  const times = estadosFisicos.value.map(s => s.timestamp)
  const v10 = estadosFisicos.value.map(s => s.wind_surface_kmh)
  const v40 = estadosFisicos.value.map(s => s.vientosAltura[40])
  const v100 = estadosFisicos.value.map(s => s.vientosAltura[100])
  const v150 = estadosFisicos.value.map(s => s.vientosAltura[150])
  const v200 = estadosFisicos.value.map(s => s.vientosAltura[200])
  
  return {
    animation: true,
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15, 23, 42, 0.9)', borderColor: '#334155', textStyle: { color: '#f8fafc' } },
    legend: { data: ['Base (10m)', 'Grúa (40m)', 'Pilar (100m)', 'Cima (200m)'], top: 0, textStyle: { color: '#94a3b8' } },
    grid: { left: 45, right: 20, top: 40, bottom: 50 },
    xAxis: { type: 'category', data: times, axisLabel: { color: '#64748b', formatter: (v) => formatoFecha(v).split(',')[1] || v } },
    yAxis: { type: 'value', name: 'km/h', min: 0, max: 70, nameTextStyle: { color: '#64748b' }, splitLine: { lineStyle: { color: '#334155', type: 'dashed' } }, axisLabel: { color: '#64748b' } },
    dataZoom: [{ type: 'inside' }, { type: 'slider', bottom: 0, height: 16, borderColor: 'transparent', fillerColor: 'rgba(56, 189, 248, 0.2)' }],
    series: [
      { name: 'Base (10m)', type: 'line', data: v10, showSymbol: false, smooth: true, lineStyle: { width: 2, color: '#94a3b8', type: 'dashed' } },
      { name: 'Grúa (40m)', type: 'line', data: v40, showSymbol: false, smooth: true, lineStyle: { width: 3, color: '#38bdf8' }, areaStyle: { color: 'rgba(56, 189, 248, 0.1)' },
        markArea: { itemStyle: { color: 'rgba(239, 68, 68, 0.1)' }, data: [[{ yAxis: 35, name: 'Prohibición Izaje (>35)', label: {position: 'insideTopLeft', color: '#ef4444'} }, { yAxis: 70 }]] }
      },
      { name: 'Pilar (100m)', type: 'line', data: v100, showSymbol: false, smooth: true, lineStyle: { width: 2, color: '#818cf8' } },
      { name: 'Cima (200m)', type: 'line', data: v200, showSymbol: false, smooth: true, lineStyle: { width: 2, color: '#c084fc' } }
    ]
  }
})

const chartOlaOption = computed(() => {
  if (!estadosFisicos.value.length) return {}
  const times = estadosFisicos.value.map(s => s.timestamp)
  const hs = estadosFisicos.value.map(s => s.wave_params?.Hs || 0)
  const mareas = estadosFisicos.value.map(s => s.marea_m)
  const iteSeries = estadosFisicos.value.map(s => s.ite.value)
  
  return {
    animation: true,
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15, 23, 42, 0.9)', borderColor: '#334155', textStyle: { color: '#f8fafc' } },
    legend: { data: ['Oleaje Hs (m)', 'Marea (m)', 'ITE (Resonancia Espigas)'], top: 0, textStyle: { color: '#94a3b8' } },
    grid: { left: 45, right: 45, top: 40, bottom: 50 },
    visualMap: {
      show: false,
      seriesIndex: 2, // Aplicar al ITE
      pieces: [{ gt: 0, lte: 0.99, color: '#10b981' }, { gt: 1.0, lte: 1.49, color: '#f59e0b' }, { gt: 1.5, color: '#ef4444' }]
    },
    xAxis: { type: 'category', data: times, axisLabel: { color: '#64748b', formatter: (v) => formatoFecha(v).split(',')[1] || v } },
    yAxis: [
      { type: 'value', name: 'Metros', min: 0, position: 'left', nameTextStyle: { color: '#64748b' }, splitLine: { lineStyle: { color: '#334155', type: 'dashed' } }, axisLabel: { color: '#64748b' } },
      { type: 'value', name: 'Índice (ITE)', min: 0, position: 'right', nameTextStyle: { color: '#64748b' }, splitLine: { show: false }, axisLabel: { color: '#64748b' } }
    ],
    dataZoom: [{ type: 'inside' }, { type: 'slider', bottom: 0, height: 16, borderColor: 'transparent', fillerColor: 'rgba(56, 189, 248, 0.2)' }],
    series: [
      { name: 'Oleaje Hs (m)', type: 'bar', yAxisIndex: 0, data: hs, itemStyle: { color: 'rgba(56, 189, 248, 0.4)', borderRadius: [4, 4, 0, 0] } },
      { name: 'Marea (m)', type: 'line', yAxisIndex: 0, data: mareas, smooth: true, showSymbol: false, lineStyle: { width: 3, color: '#3b82f6' }, areaStyle: { color: 'rgba(59, 130, 246, 0.15)' } },
      { name: 'ITE (Resonancia Espigas)', type: 'line', yAxisIndex: 1, data: iteSeries, smooth: true, showSymbol: false, lineStyle: { width: 4 }, markLine: { data: [{ yAxis: 1.5, name: 'Crítico', lineStyle: { color: '#ef4444', type: 'solid' }, label: { formatter: 'Falla Espiga', color: '#ef4444' } }] } }
    ]
  }
})

async function cargar() {
  loading.value = true
  error.value = null
  try {
    await wakeApi()
    data.value = await fetchSpatiPuertoPronostico(sitioId.value)
  } catch (e) {
    const msg = e?.message || 'Error al calcular el pronóstico portuario'
    error.value = e?.code === 'TIMEOUT' ? msg : `${msg}. API: ${getApiBase()}`
    data.value = null
  } finally {
    loading.value = false
  }
}

watch(sitioId, cargar)
onMounted(() => cargar())
</script>

<style scoped>
/* ESTILOS PREMIUM GLASSMORPHISM */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

.premium-page {
  font-family: 'Outfit', sans-serif;
  min-height: 100vh;
  background-color: #0b0f19;
  color: #f8fafc;
  padding: 2rem;
  position: relative;
  overflow: hidden;
}

/* Efectos de luces de fondo */
.premium-bg-glow {
  position: absolute;
  top: -100px;
  left: -100px;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.15) 0%, rgba(11, 15, 25, 0) 70%);
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
}
.premium-bg-glow.secondary {
  top: 40%;
  right: -150px;
  left: auto;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.1) 0%, rgba(11, 15, 25, 0) 70%);
}

.premium-page > * {
  position: relative;
  z-index: 1;
}

/* HEADER */
.premium-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}
.title-area h1 { margin: 0; font-size: 2.2rem; font-weight: 800; background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.title-area p { margin: 0.2rem 0 0; color: #94a3b8; font-size: 1.1rem; }

.controls-area { display: flex; align-items: center; gap: 1.5rem; }
.faena-badge { background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(51, 65, 85, 0.8); padding: 0.5rem 1.2rem; border-radius: 20px; display: flex; flex-direction: column; align-items: flex-end; }
.faena-badge span { font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
.faena-badge strong { font-size: 1.1rem; color: #38bdf8; }

.btn-premium { background: linear-gradient(135deg, #0ea5e9, #3b82f6); color: white; border: none; padding: 0.8rem 1.5rem; border-radius: 12px; font-weight: 600; font-size: 1rem; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3); font-family: inherit; }
.btn-premium:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(14, 165, 233, 0.5); }
.btn-premium.alert-btn { background: linear-gradient(135deg, #ef4444, #b91c1c); box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3); }

/* CARDS GLASSMORPHISM */
.glass-card {
  background: rgba(30, 41, 59, 0.4);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
}

/* SECTION TITLES */
.section-title { font-size: 1.3rem; font-weight: 600; color: #e2e8f0; margin-bottom: 1.2rem; border-left: 4px solid #38bdf8; padding-left: 0.8rem; }

/* ALERTAS */
.alert-section { margin-bottom: 3rem; }
.alerts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }
.alert-card { padding: 1.2rem; display: flex; gap: 1rem; align-items: flex-start; transition: transform 0.2s; border-left: 4px solid; }
.alert-card:hover { transform: translateY(-2px); }
.alert-card.RED, .alert-card.CRITICAL { border-left-color: #ef4444; background: linear-gradient(90deg, rgba(239,68,68,0.1) 0%, rgba(30,41,59,0.4) 100%); }
.alert-card.YELLOW { border-left-color: #f59e0b; background: linear-gradient(90deg, rgba(245,158,11,0.1) 0%, rgba(30,41,59,0.4) 100%); }
.alert-icon { font-size: 1.5rem; margin-top: 0.2rem; }
.alert-content { display: flex; flex-direction: column; gap: 0.3rem; }
.alert-badge { font-size: 0.65rem; font-weight: 800; padding: 0.2rem 0.5rem; border-radius: 4px; display: inline-block; width: max-content; }
.RED .alert-badge, .CRITICAL .alert-badge { background: #ef4444; color: white; }
.YELLOW .alert-badge { background: #f59e0b; color: white; }
.alert-type { font-size: 1.1rem; color: #f8fafc; }
.alert-time { font-size: 0.8rem; color: #94a3b8; }
.alert-desc { margin: 0; font-size: 0.95rem; color: #cbd5e1; }

/* WIDGETS */
.widgets-section { margin-bottom: 3rem; }
.widgets-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.2rem; }
.widget { padding: 1.5rem; display: flex; align-items: center; gap: 1.2rem; transition: transform 0.3s ease, border-color 0.3s; }
.widget:hover { transform: scale(1.02); border-color: rgba(255,255,255,0.15); }
.widget.highlight { border-bottom: 2px solid #f59e0b; }
.widget.ocean { border-bottom: 2px solid #38bdf8; }
.widget.danger { border-bottom: 2px solid #ef4444; }
.widget-icon { font-size: 2.2rem; opacity: 0.8; }
.widget-info { display: flex; flex-direction: column; }
.widget-info .lbl { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
.widget-info .val { font-size: 1.8rem; font-weight: 800; color: #f8fafc; line-height: 1.1; margin: 0.3rem 0; }
.widget-info .val small { font-size: 0.9rem; font-weight: 400; color: #64748b; }
.widget-info .sub { font-size: 0.85rem; color: #64748b; }

/* CHARTS */
.charts-section { display: grid; grid-template-columns: 1fr; gap: 2rem; }
.chart-container { padding: 1.5rem; }
.chart-title { margin: 0 0 1.5rem; font-size: 1.1rem; font-weight: 600; color: #cbd5e1; text-align: center; }
.chart-canvas { height: 400px; width: 100%; }
.chart-canvas.large { height: 480px; }

/* COLORES ESTADO ITE */
.SEGURO { color: #10b981 !important; }
.PRECAUCION { color: #facc15 !important; }
.ALERTA { color: #f59e0b !important; font-weight: 800; }
.CRITICO { color: #ef4444 !important; font-weight: 800; animation: pulse 2s infinite; }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.6; } 100% { opacity: 1; } }

/* LOADER */
.state-loader { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; color: #38bdf8; }
.wave-loader { width: 50px; height: 50px; border: 3px solid rgba(56,189,248,0.3); border-top-color: #38bdf8; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1rem; }
@keyframes spin { to { transform: rotate(360deg); } }
.state-error { padding: 3rem; text-align: center; color: #fca5a5; max-width: 500px; margin: 2rem auto; }
.state-error .error-icon { font-size: 3rem; margin-bottom: 1rem; }
.state-error p { font-size: 1.1rem; margin-bottom: 1.5rem; }
</style>
