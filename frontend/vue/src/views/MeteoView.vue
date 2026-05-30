<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import {
  Thermometer,
  Droplets,
  Wind,
  CloudRain,
  Gauge,
  MapPin,
  Sun,
} from 'lucide-vue-next'
import { useMetgoStore } from '@/stores/metgo'
import MetricCard from '@/components/ui/MetricCard.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import WeatherScene from '@/components/meteo/WeatherScene.vue'
import FrostBadge from '@/components/meteo/FrostBadge.vue'
import { riesgoHelada } from '@/utils/agroInsights'
import { fetchPronostico, fetchHistorico } from '@/api/metgoApi'
import { condicionViento, acumuladoPrecipitacion } from '@/utils/agroInsights'

const store = useMetgoStore()
const pronostico = ref([])
const historico = ref([])
const cargandoPron = ref(false)
const cargandoHist = ref(false)

const estacionInfo = computed(() =>
  store.estaciones.find((e) => e.id === store.estacionActiva)
)

const d = computed(() => store.datosMeteo)
const helada = computed(() => riesgoHelada(d.value?.temperatura_min))
const viento = computed(() => condicionViento(d.value?.viento))
const lluviaHist = computed(() => acumuladoPrecipitacion(historico.value))
const lluviaPron = computed(() => acumuladoPrecipitacion(pronostico.value))

async function cargar() {
  cargandoPron.value = true
  cargandoHist.value = true
  try {
    const [p, h] = await Promise.all([
      fetchPronostico(store.estacionActiva, 7),
      fetchHistorico(store.estacionActiva, 14),
    ])
    pronostico.value = p
    historico.value = h
  } catch {
    pronostico.value = []
    historico.value = []
  } finally {
    cargandoPron.value = false
    cargandoHist.value = false
  }
}

onMounted(cargar)
watch(() => store.estacionActiva, cargar)
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Meteorología</h2>
      <p class="page-subtitle">
        Condiciones y pronóstico · {{ store.estacionNombre }}
        <span v-if="d?.fuente" class="badge badge--neutral">{{ d.fuente }}</span>
      </p>
      <div class="page-meta">
        <label class="inline-select">
          Análisis:
          <select v-model="store.tipoAnalisis" @change="store.cargarDatosMeteo()">
            <option value="pronostico">Pronóstico</option>
            <option value="historico">Histórico</option>
          </select>
        </label>
        <router-link to="/configuracion" class="link-config">Configuración avanzada</router-link>
      </div>
      <p v-if="estacionInfo?.lat" class="coords">
        <MapPin class="coords__icon" aria-hidden="true" />
        {{ estacionInfo.lat.toFixed(4) }}°, {{ estacionInfo.lon.toFixed(4) }}° · America/Santiago
      </p>
    </header>

    <div v-if="d" class="weather-hero">
      <WeatherScene :datos="d" />
      <div class="weather-hero__aside">
        <p class="weather-hero__title">Valle de Aconcagua</p>
        <p class="weather-hero__temp">{{ d.temperatura }}°C · humedad {{ d.humedad }}%</p>
        <div v-if="helada.nivel !== 'low'" class="frost-row">
          <FrostBadge size="sm" show-label />
          <span>{{ helada.label }}</span>
        </div>
      </div>
    </div>

    <div v-if="d" class="card-grid card-grid--wide">
      <MetricCard label="Temp. media" :value="d.temperatura" unit="°C">
        <template #icon><Thermometer /></template>
      </MetricCard>
      <MetricCard label="Rango térmico" :value="`${d.temperatura_min} / ${d.temperatura_max}`" unit="°C">
        <template #icon><Sun /></template>
      </MetricCard>
      <MetricCard label="Humedad" :value="d.humedad" unit="%">
        <template #icon><Droplets /></template>
      </MetricCard>
      <MetricCard label="Viento" :value="d.viento" unit="km/h">
        <template #icon><Wind /></template>
      </MetricCard>
      <MetricCard label="Precipitación día" :value="d.precipitacion" unit="mm">
        <template #icon><CloudRain /></template>
      </MetricCard>
      <MetricCard v-if="d.presion" label="Presión" :value="d.presion" unit="hPa">
        <template #icon><Gauge /></template>
      </MetricCard>
    </div>

    <div class="insight-row">
      <span class="insight-chip">{{ viento.label }}</span>
      <span class="insight-chip">Pronóstico 7d: {{ lluviaPron.toFixed(1) }} mm</span>
      <span class="insight-chip">Histórico 14d: {{ lluviaHist.toFixed(1) }} mm</span>
    </div>

    <div class="layout-split">
      <SectionCard title="Pronóstico 7 días" subtitle="Temperatura, humedad, viento y lluvia">
        <template #icon><CloudRain /></template>
        <p v-if="cargandoPron" class="skeleton">Cargando pronóstico…</p>
        <div v-else-if="pronostico.length" class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Media</th>
                <th>Máx</th>
                <th>Mín</th>
                <th>Humedad</th>
                <th>Lluvia</th>
                <th>Viento</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in pronostico" :key="row.fecha">
                <td>{{ row.fecha?.slice(0, 10) }}</td>
                <td>{{ row.temperatura }}°</td>
                <td>{{ row.temperatura_max }}°</td>
                <td>{{ row.temperatura_min }}°</td>
                <td>{{ row.humedad }}%</td>
                <td>{{ row.precipitacion }} mm</td>
                <td>{{ row.viento }} km/h</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="muted">Sin datos de pronóstico.</p>
      </SectionCard>

      <SectionCard title="Histórico reciente" subtitle="Últimos 14 días">
        <template #icon><Thermometer /></template>
        <p v-if="cargandoHist" class="skeleton">Cargando histórico…</p>
        <div v-else-if="historico.length" class="table-wrap table-wrap--scroll">
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
              <tr v-for="row in historico.slice(-10)" :key="row.fecha">
                <td>{{ row.fecha?.slice(0, 10) }}</td>
                <td>{{ row.temperatura }}°</td>
                <td>{{ row.temperatura_max }}°</td>
                <td>{{ row.temperatura_min }}°</td>
                <td>{{ row.precipitacion }} mm</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="muted">Sin histórico disponible.</p>
      </SectionCard>
    </div>
  </div>
</template>

<style scoped>
.page {
  max-width: 1280px;
}

.weather-hero {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.weather-hero__aside {
  flex: 1;
  min-width: 180px;
  padding: 1rem 1.25rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.35rem;
}

.weather-hero__title {
  margin: 0;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-muted);
}

.weather-hero__temp {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
}

.frost-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  color: var(--color-sky-deep);
  font-weight: 600;
}

.coords {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  color: var(--color-muted);
  margin-top: 0.35rem;
}

.coords__icon {
  width: 0.9rem;
  height: 0.9rem;
}

.insight-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 1rem 0 1.25rem;
}

.insight-chip {
  font-size: 0.78rem;
  padding: 0.4rem 0.75rem;
  background: var(--color-primary-subtle);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
}

.table-wrap {
  overflow-x: auto;
}

.table-wrap--scroll {
  max-height: 320px;
  overflow-y: auto;
}

.inline-select {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--color-muted);
}

.inline-select select {
  padding: 0.3rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: inherit;
}

.link-config {
  font-size: 0.85rem;
  color: var(--color-primary);
  text-decoration: none;
}

.link-config:hover {
  text-decoration: underline;
}
</style>
