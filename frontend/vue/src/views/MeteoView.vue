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
  Star,
  Cloud,
  Eye,
} from 'lucide-vue-next'
import { useMetgoStore } from '@/stores/metgo'
import { useFavoritesStore } from '@/stores/favorites'
import { useFormatTemp } from '@/composables/useFormatTemp'
import MetricCard from '@/components/ui/MetricCard.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import WeatherScene from '@/components/meteo/WeatherScene.vue'
import FrostBadge from '@/components/meteo/FrostBadge.vue'
import PronosticoHeladasPanel from '@/components/meteo/PronosticoHeladasPanel.vue'
import { riesgoHelada } from '@/utils/agroInsights'
import { fetchPronostico, fetchHistorico, fetchVientoHorario } from '@/api/metgoApi'
import { condicionViento, acumuladoPrecipitacion } from '@/utils/agroInsights'
import { hoyChile, seriesHistoricoPorDia, diaDeFila } from '@/utils/meteoDates'
import ComboMeteoChart from '@/components/charts/ComboMeteoChart.vue'
import WindRoseChart from '@/components/charts/WindRoseChart.vue'
import EnsemblePredictivoPanel from '@/components/meteo/EnsemblePredictivoPanel.vue'
import { usePreferencesStore } from '@/stores/preferences'

const store = useMetgoStore()
const favorites = useFavoritesStore()
const prefs = usePreferencesStore()
const { formatTemperatura } = useFormatTemp()
const pronostico = ref([])
const historico = ref([])
const cargandoPron = ref(false)
const cargandoHist = ref(false)
const vientoHorario = ref(null)
const cargandoViento = ref(false)

const estacionInfo = computed(() =>
  store.estaciones.find((e) => e.id === store.estacionActiva)
)

const d = computed(() => store.datosMeteo)
const helada = computed(() => riesgoHelada(d.value?.temperatura_min))
const viento = computed(() => condicionViento(d.value?.viento))
const historicoFiltrado = computed(() => seriesHistoricoPorDia(historico.value, 14))
const lluviaHist = computed(() => acumuladoPrecipitacion(historicoFiltrado.value))
const lluviaPron = computed(() => acumuladoPrecipitacion(pronostico.value))
const rangoTermico = computed(() => {
  if (!d.value) return '—'
  return `${formatTemperatura(d.value.temperatura_min)} / ${formatTemperatura(d.value.temperatura_max)}`
})

const tempUnit = computed(() => (prefs.tempUnit === 'F' ? '°F' : '°C'))
const labelsPron = computed(() =>
  pronostico.value.map((r) => diaDeFila(r) || String(r.fecha ?? '').slice(0, 10))
)
const tempsPronMax = computed(() => pronostico.value.map((r) => r.temperatura_max))
const tempsPronMin = computed(() => pronostico.value.map((r) => r.temperatura_min))
const precipPron = computed(() => pronostico.value.map((r) => r.precipitacion))
const labelsHist = computed(() =>
  historicoFiltrado.value.map((r) => diaDeFila(r) || String(r.fecha ?? '').slice(0, 10))
)
const tempsHistMax = computed(() => historicoFiltrado.value.map((r) => r.temperatura_max))
const tempsHistMin = computed(() => historicoFiltrado.value.map((r) => r.temperatura_min))
const lluviaHistSerie = computed(() => historicoFiltrado.value.map((r) => r.precipitacion))
const nubosidadSerie = computed(() => pronostico.value.map((r) => r.cobertura_nubosa ?? 0))
const vientoDirsPron = computed(() =>
  Array.isArray(vientoHorario.value?.direcciones) && vientoHorario.value.direcciones.length
    ? vientoHorario.value.direcciones
    : pronostico.value.map((r) => r.direccion_viento).filter((v) => v != null)
)
const vientoSpeedsPron = computed(() =>
  Array.isArray(vientoHorario.value?.velocidades) && vientoHorario.value.velocidades.length
    ? vientoHorario.value.velocidades
    : pronostico.value.filter((r) => r.direccion_viento != null).map((r) => r.viento)
)

async function cargar() {
  cargandoPron.value = true
  cargandoHist.value = true
  cargandoViento.value = true
  const [pRes, hRes, vRes] = await Promise.allSettled([
    fetchPronostico(store.estacionActiva, 7),
    fetchHistorico(store.estacionActiva, 14),
    fetchVientoHorario(store.estacionActiva, 7),
  ])
  pronostico.value = pRes.status === 'fulfilled' ? pRes.value : []
  historico.value = hRes.status === 'fulfilled' ? hRes.value : []
  vientoHorario.value = vRes.status === 'fulfilled' ? vRes.value : null
  cargandoPron.value = false
  cargandoHist.value = false
  cargandoViento.value = false
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
        <button
          type="button"
          class="btn-fav"
          :class="{ 'btn-fav--on': favorites.isFavorite(store.estacionActiva) }"
          :title="favorites.isFavorite(store.estacionActiva) ? 'Quitar favorita' : 'Añadir favorita'"
          @click="favorites.toggle(store.estacionActiva)"
        >
          <Star aria-hidden="true" />
        </button>
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
        <p class="weather-hero__temp">
          {{ formatTemperatura(d.temperatura) }} · humedad {{ d.humedad }}%
        </p>
        <div v-if="helada.nivel !== 'low'" class="frost-row">
          <FrostBadge size="sm" show-label />
          <span>{{ helada.label }}</span>
        </div>
      </div>
    </div>

    <div v-if="d" class="card-grid card-grid--wide">
      <MetricCard label="Temp. media" :value="d.temperatura" :temp-celsius="d.temperatura">
        <template #icon><Thermometer /></template>
      </MetricCard>
      <MetricCard label="Rango térmico" :value="rangoTermico">
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
      <MetricCard v-if="d.cobertura_nubosa != null" label="Nubosidad" :value="d.cobertura_nubosa" unit="%">
        <template #icon><Cloud /></template>
      </MetricCard>
      <MetricCard v-if="d.radiacion_solar != null" label="Radiación solar" :value="d.radiacion_solar" unit="W/m²">
        <template #icon><Sun /></template>
      </MetricCard>
      <MetricCard v-if="d.visibilidad != null" label="Visibilidad" :value="d.visibilidad" unit="km">
        <template #icon><Eye /></template>
      </MetricCard>
    </div>

    <div class="insight-row">
      <span class="insight-chip">{{ viento.label }}</span>
      <span class="insight-chip">Pronóstico 7d: {{ lluviaPron.toFixed(1) }} mm</span>
      <span class="insight-chip">Histórico 14d: {{ lluviaHist.toFixed(1) }} mm</span>
      <span v-if="d?.pop != null || d?.probabilidad_lluvia != null" class="insight-chip">
        PoP: {{ d.pop ?? d.probabilidad_lluvia }}%
      </span>
      <router-link to="/meteo/precipitacion" class="insight-link">Precipitación →</router-link>
      <router-link to="/meteo/avanzado" class="insight-link">Meteo avanzada →</router-link>
    </div>

    <SectionCard
      title="Motor Predictivo Multi-Modelo (Ensemble)"
      subtitle="Consenso de ECMWF, GFS, ICON, GEM y MeteoFrance (Medianas y Probabilidades)"
    >
      <template #icon><CloudRain /></template>
      <EnsemblePredictivoPanel />
    </SectionCard>

    <SectionCard
      title="Combo lluvia + temperatura · 7 días"
      subtitle="Doble escala: barras (mm) y línea (T° máx) (Modelo Simple)"
    >
      <template #icon><CloudRain /></template>
      <p v-if="cargandoPron" class="skeleton">Cargando…</p>
      <ComboMeteoChart
        v-else-if="labelsPron.length"
        :labels="labelsPron"
        :temperaturas="tempsPronMax"
        :precipitacion="precipPron"
        :temp-unit="tempUnit"
        :export-name="`combo_${store.estacionActiva}`"
      />
    </SectionCard>

    <SectionCard
      title="Banda térmica · pronóstico 7 días"
      subtitle="Máxima y mínima diaria (OpenMeteo)"
    >
      <template #icon><Thermometer /></template>
      <p v-if="cargandoPron" class="skeleton">Cargando…</p>
      <TimeSeriesChart
        v-else-if="labelsPron.length"
        :labels="labelsPron"
        :values="tempsPronMax"
        :values-min="tempsPronMin"
        :unit="tempUnit"
        :height="240"
        show-band
        :show-area="false"
        y-axis-title="Temperatura"
        color="#c45c26"
        fill-color="rgba(196, 92, 38, 0.12)"
        :export-name="`banda_${store.estacionActiva}`"
      />
      <p v-else class="muted">Sin pronóstico.</p>
    </SectionCard>

    <SectionCard
      v-if="nubosidadSerie.some((v) => v > 0)"
      title="Nubosidad y radiación · pronóstico"
      subtitle="Cobertura nubosa diaria (OpenMeteo)"
    >
      <template #icon><Cloud /></template>
      <TimeSeriesChart
        v-if="labelsPron.length && !cargandoPron"
        :labels="labelsPron"
        :values="nubosidadSerie"
        unit=" %"
        :height="180"
        y-axis-title="Nubosidad"
        color="#60a5fa"
      />
    </SectionCard>

    <SectionCard
      title="Histórico observado"
      :subtitle="`${labelsHist.length} días hasta ${hoyChile()}`"
    >
      <template #icon><Sun /></template>
      <p v-if="cargandoHist" class="skeleton">Cargando histórico…</p>
      <TimeSeriesChart
        v-else-if="labelsHist.length"
        :labels="labelsHist"
        :values="tempsHistMax"
        :values-min="tempsHistMin"
        unit="°C"
        :height="240"
        show-band
        :show-area="false"
        y-axis-title="T° máx / mín"
        :export-name="`historico_${store.estacionActiva}`"
      />
      <p v-else class="muted">Sin histórico.</p>
    </SectionCard>

    <div class="layout-split">
      <PronosticoHeladasPanel />
      <SectionCard
        v-if="vientoDirsPron.length"
        title="Rosa de vientos · pronóstico"
        :subtitle="
          Array.isArray(vientoHorario?.direcciones) && vientoHorario?.direcciones?.length
            ? 'Serie horaria (OpenMeteo)'
            : 'Dirección dominante 7 días'
        "
      >
        <template #icon><Wind /></template>
        <WindRoseChart :directions="vientoDirsPron" :speeds="vientoSpeedsPron" />
      </SectionCard>
    </div>

    <SectionCard title="Precipitación histórica" subtitle="mm por día">
      <TimeSeriesChart
        v-if="labelsHist.length && !cargandoHist"
        :labels="labelsHist"
        :values="lluviaHistSerie"
        unit=" mm"
        :height="200"
        y-axis-title="Lluvia"
        color="var(--color-sky)"
      />
    </SectionCard>

    <div class="layout-split">
      <SectionCard title="Pronóstico 7 días" subtitle="Tabla detallada">
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
                <th>Nubes</th>
                <th>Visib.</th>
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
                <td>{{ row.viento }} m/s</td>
                <td>{{ row.cobertura_nubosa ?? '—' }}%</td>
                <td>{{ row.visibilidad ?? '—' }} km</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="muted">Sin datos de pronóstico.</p>
      </SectionCard>

      <SectionCard
        title="Histórico reciente"
        :subtitle="`Últimos 14 días hasta hoy (${hoyChile()})`"
      >
        <template #icon><Thermometer /></template>
        <p v-if="cargandoHist" class="skeleton">Cargando histórico…</p>
        <div v-else-if="historicoFiltrado.length" class="table-wrap table-wrap--scroll">
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
              <tr v-for="row in [...historicoFiltrado].reverse()" :key="row.fecha">
                <td>{{ row.fecha }}</td>
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

.insight-link {
  font-size: 0.78rem;
  padding: 0.4rem 0.75rem;
  color: var(--color-sky-deep, #0284c7);
  text-decoration: none;
  font-weight: 600;
}
.insight-link:hover { text-decoration: underline; }

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

.btn-fav {
  margin-left: 0.35rem;
  padding: 0.15rem 0.35rem;
  border: none;
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  vertical-align: middle;
}

.btn-fav svg {
  width: 1rem;
  height: 1rem;
}

.btn-fav--on {
  color: var(--color-warning);
  fill: var(--color-warning);
}

.link-config:hover {
  text-decoration: underline;
}
</style>
