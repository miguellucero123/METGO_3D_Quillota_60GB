<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import {
  Thermometer,
  Droplets,
  Wind,
  CloudRain,
  Gauge,
  ArrowUp,
  ArrowDown,
  RefreshCw,
} from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useMetgoStore } from '@/stores/metgo'
import { Grid3x3 } from 'lucide-vue-next'

const router = useRouter()
import MetricCard from '@/components/ui/MetricCard.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import WeatherScene from '@/components/meteo/WeatherScene.vue'
import FrostBadge from '@/components/meteo/FrostBadge.vue'
import MlProjectionChart from '@/components/charts/MlProjectionChart.vue'
import TimeSeriesChart from '@/components/charts/TimeSeriesChart.vue'
import { fetchPronostico, fetchAlertas, fetchRecomendacionesAgricolas, mlPredictBatch } from '@/api/metgoApi'
import { mapMlProjectionItems, ML_VARS_DASHBOARD } from '@/utils/mlProjection'
import { diaDeFila } from '@/utils/meteoDates'
import {
  riesgoHelada,
  necesidadRiego,
  acumuladoPrecipitacion,
} from '@/utils/agroInsights'
import { useFormatTemp } from '@/composables/useFormatTemp'

const store = useMetgoStore()
const { formatTemperatura, unit: tempUnit } = useFormatTemp()
const pronostico = ref([])
const alertas = ref([])
const recomendaciones = ref([])
const cargandoExtra = ref(false)
const mlProyecciones = ref([])
const cargandoMl = ref(false)
const pronosticoError = ref('')

const labelsPron = computed(() =>
  pronostico.value.map((r) => diaDeFila(r) || String(r.fecha ?? '').slice(0, 10))
)
const tempsPronMax = computed(() => pronostico.value.map((r) => r.temperatura_max))
const tempsPronMin = computed(() => pronostico.value.map((r) => r.temperatura_min))

const d = computed(() => store.datosMeteo)
const helada = computed(() => riesgoHelada(d.value?.temperatura_min))
const riego = computed(() => necesidadRiego(d.value?.humedad, d.value?.precipitacion))
const lluvia7d = computed(() => acumuladoPrecipitacion(pronostico.value))

async function cargarResumen() {
  cargandoExtra.value = true
  cargandoMl.value = true
  const [pRes, aRes, rRes] = await Promise.allSettled([
    fetchPronostico(store.estacionActiva, 7),
    fetchAlertas(store.estacionActiva),
    fetchRecomendacionesAgricolas(store.estacionActiva),
  ])
  pronostico.value = pRes.status === 'fulfilled' ? pRes.value : []
  if (pRes.status === 'rejected') {
    pronosticoError.value = pRes.reason?.message || 'Error al cargar pronóstico'
  } else if (!pronostico.value.length) {
    pronosticoError.value =
      'La API no devolvió días futuros (OpenMeteo o caché; pruebe Actualizar)'
  } else {
    pronosticoError.value = ''
  }
  alertas.value =
    aRes.status === 'fulfilled' ? (aRes.value || []).slice(0, 4) : []
  recomendaciones.value =
    rRes.status === 'fulfilled' ? (rRes.value || []).slice(0, 3) : []
  cargandoExtra.value = false

  try {
    const batch = await mlPredictBatch(
      ML_VARS_DASHBOARD.map((v) => v.variable),
      store.estacionActiva
    )
    mlProyecciones.value = mapMlProjectionItems(batch, store.datosMeteo)
  } catch {
    mlProyecciones.value = []
  } finally {
    cargandoMl.value = false
  }
}

async function actualizarTodo() {
  await store.cargarDatosMeteo()
  await cargarResumen()
}

onMounted(actualizarTodo)
watch(() => store.estacionActiva, cargarResumen)
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Panel general</h2>
      <p class="page-subtitle">Resumen integrado meteorológico y agrícola — {{ store.estacionNombre }}</p>
      <div class="page-meta">
        <span v-if="d?.fuente" class="badge badge--neutral">{{ d.fuente }}</span>
        <span
          :class="['badge', store.apiOnline ? 'badge--success' : 'badge--danger']"
        >
          API {{ store.apiOnline ? 'conectada' : 'desconectada' }}
        </span>
        <span v-if="d?.actualizado" class="muted">
          Actualizado {{ d.actualizado.slice(0, 16).replace('T', ' ') }}
        </span>
      </div>
    </header>

    <p v-if="store.error" class="alert-banner" role="alert">{{ store.error }}</p>

    <div v-if="store.cargando" class="skeleton">Cargando condiciones actuales…</div>

    <template v-else-if="d">
      <div class="weather-hero">
        <WeatherScene :datos="d" />
        <div class="weather-hero__aside">
          <p class="weather-hero__title">Condición actual</p>
          <p class="weather-hero__temp">
            {{ formatTemperatura(d.temperatura) }} ·
            {{ formatTemperatura(d.temperatura_min) }} / {{ formatTemperatura(d.temperatura_max) }}
          </p>
        </div>
      </div>

      <div class="card-grid card-grid--wide">
        <MetricCard label="Temperatura media" :value="d.temperatura" :temp-celsius="d.temperatura">
          <template #icon><Thermometer /></template>
        </MetricCard>
        <MetricCard
          label="Máxima"
          :value="d.temperatura_max"
          :temp-celsius="d.temperatura_max"
        >
          <template #icon><ArrowUp /></template>
        </MetricCard>
        <MetricCard
          label="Mínima"
          :value="d.temperatura_min"
          :temp-celsius="d.temperatura_min"
          :variant="helada.nivel === 'high' ? 'alert' : 'default'"
        >
          <template #icon><ArrowDown /></template>
        </MetricCard>
        <MetricCard label="Humedad relativa" :value="d.humedad" unit="%">
          <template #icon><Droplets /></template>
        </MetricCard>
        <MetricCard label="Viento máx." :value="d.viento" unit="km/h">
          <template #icon><Wind /></template>
        </MetricCard>
        <MetricCard label="Precipitación" :value="d.precipitacion" unit="mm">
          <template #icon><CloudRain /></template>
        </MetricCard>
        <MetricCard v-if="d.presion" label="Presión" :value="d.presion" unit="hPa">
          <template #icon><Gauge /></template>
        </MetricCard>
      </div>

      <div class="insight-row">
        <div class="insight-chip insight-chip--frost" :class="`insight-chip--${helada.nivel}`">
          <FrostBadge v-if="helada.nivel !== 'low'" size="sm" />
          <strong>Heladas:</strong> {{ helada.label }}
        </div>
        <div class="insight-chip" :class="`insight-chip--${riego.nivel}`">
          <strong>Riego:</strong> {{ riego.label }}
        </div>
        <div class="insight-chip insight-chip--low">
          <strong>Lluvia 7 días:</strong> {{ lluvia7d.toFixed(1) }} mm acum.
        </div>
      </div>

      <SectionCard
        title="Proyecciones ML"
        subtitle="Observado OpenMeteo (misma entrada del modelo) vs predicción ML"
        class="ml-section"
      >
        <p v-if="cargandoMl" class="muted">Calculando proyecciones…</p>
        <MlProjectionChart v-else :items="mlProyecciones" />
      </SectionCard>

      <div class="layout-split">
        <SectionCard title="Pronóstico próximos días" subtitle="OpenMeteo · banda térmica diaria">
          <template #icon><CloudRain /></template>
          <p v-if="cargandoExtra" class="muted">Cargando…</p>
          <template v-else-if="pronostico.length">
            <TimeSeriesChart
              :labels="labelsPron"
              :values="tempsPronMax"
              :values-min="tempsPronMin"
              :unit="tempUnit === 'F' ? '°F' : '°C'"
              :height="220"
              show-band
              :show-area="false"
              y-axis-title="Temperatura"
              color="#c45c26"
              fill-color="rgba(196, 92, 38, 0.15)"
              :export-name="`dashboard_pron_${store.estacionActiva}`"
            />
            <table class="data-table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Media</th>
                  <th>Máx</th>
                  <th>Mín</th>
                  <th>Lluvia</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in pronostico.slice(0, 5)" :key="row.fecha">
                  <td>{{ row.fecha?.slice(0, 10) }}</td>
                  <td>{{ row.temperatura }}°</td>
                  <td>{{ row.temperatura_max }}°</td>
                  <td>{{ row.temperatura_min }}°</td>
                  <td>{{ row.precipitacion }} mm</td>
                </tr>
              </tbody>
            </table>
          </template>
          <p v-else class="muted">
            Sin pronóstico disponible.
            <span v-if="pronosticoError" class="error-hint"> {{ pronosticoError }}</span>
          </p>
        </SectionCard>

        <div class="stack">
          <SectionCard title="Alertas activas" subtitle="Umbrales automáticos">
            <template #icon><Wind /></template>
            <ul v-if="alertas.length" class="alert-list">
              <li v-for="a in alertas" :key="a.id" :class="['alert-item', a.nivel]">
                {{ a.mensaje }}
              </li>
            </ul>
            <p v-else class="muted">Sin alertas críticas.</p>
          </SectionCard>

          <SectionCard title="Recomendaciones agrícolas" subtitle="Según pronóstico local">
            <template #icon><Droplets /></template>
            <ul v-if="recomendaciones.length" class="reco-list">
              <li v-for="(r, i) in recomendaciones" :key="i">
                <span class="reco-cultivo">{{ r.cultivo }}</span>
                <span class="reco-accion">{{ r.accion }}</span>
                <span class="reco-motivo">{{ r.motivo }}</span>
              </li>
            </ul>
            <p v-else class="muted">Sin recomendaciones.</p>
          </SectionCard>
        </div>
      </div>

      <div class="actions-bar">
        <button type="button" class="btn" :disabled="store.cargando || cargandoExtra" @click="actualizarTodo">
          <RefreshCw class="btn-icon" aria-hidden="true" />
          Actualizar datos
        </button>
        <button type="button" class="btn btn--ghost" @click="router.push('/modulos')">
          <Grid3x3 class="btn-icon" aria-hidden="true" />
          Ver todos los módulos
        </button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.page {
  max-width: 1280px;
}

.alert-banner {
  background: var(--color-warning-bg);
  color: var(--color-warning);
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.insight-chip--frost {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.weather-hero {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: stretch;
  margin-bottom: 1.25rem;
}

.weather-hero__aside {
  flex: 1;
  min-width: 180px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 1rem 1.25rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.weather-hero__title {
  margin: 0;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-muted);
}

.weather-hero__temp {
  margin: 0.35rem 0 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text);
}

.ml-section {
  margin-bottom: 1.25rem;
}

.insight-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 1.25rem 0;
}

.insight-chip {
  font-size: 0.8rem;
  padding: 0.45rem 0.85rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
}

.insight-chip--low {
  border-color: var(--color-accent-light);
  background: var(--color-primary-subtle);
}

.insight-chip--medium {
  background: var(--color-warning-bg);
  border-color: transparent;
  color: var(--color-warning);
}

.insight-chip--high {
  background: var(--color-danger-bg);
  border-color: transparent;
  color: var(--color-danger);
}

.stack {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.alert-list {
  list-style: none;
}

.alert-item {
  font-size: 0.85rem;
  padding: 0.55rem 0;
  border-bottom: 1px solid var(--color-border);
  padding-left: 0.65rem;
  border-left: 3px solid var(--color-accent);
}

.alert-item.warning {
  border-left-color: var(--color-warning);
}

.alert-item:last-child {
  border-bottom: none;
}

.reco-list {
  list-style: none;
}

.reco-list li {
  padding: 0.65rem 0;
  border-bottom: 1px solid var(--color-border);
  display: grid;
  gap: 0.2rem;
}

.reco-cultivo {
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--color-primary);
}

.reco-accion {
  font-size: 0.85rem;
}

.reco-motivo {
  font-size: 0.75rem;
  color: var(--color-muted);
}

.actions-bar {
  margin-top: 1.5rem;
}

.btn-icon {
  width: 1rem;
  height: 1rem;
}

.error-hint {
  display: block;
  margin-top: 0.35rem;
  font-size: 0.75rem;
  color: #dc2626;
}
</style>
