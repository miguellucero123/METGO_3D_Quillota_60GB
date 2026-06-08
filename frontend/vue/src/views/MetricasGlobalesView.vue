<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Gauge, Thermometer, CloudRain, BellRing, Wind, BarChart3 } from 'lucide-vue-next'
import MetricCard from '@/components/ui/MetricCard.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import HorizontalBarChart from '@/components/charts/HorizontalBarChart.vue'
import { useApiCall } from '@/composables/useApiCall'
import { fetchMetricasGlobales } from '@/api/metgoApi'
import { useMetgoStore } from '@/stores/metgo'
import { hoyChile } from '@/utils/meteoDates'

const router = useRouter()
const metgo = useMetgoStore()
const { data: m, loading, error, run } = useApiCall(fetchMetricasGlobales)

onMounted(run)

const refFecha = computed(() => m.value?.referencia_fecha || hoyChile())
const estacionesDetalle = computed(() => m.value?.detalle_estaciones || [])

const labelsEst = computed(() => estacionesDetalle.value.map((r) => r.estacion))
const tempsMax = computed(() => estacionesDetalle.value.map((r) => r.temperatura_max))
const tempsMin = computed(() => estacionesDetalle.value.map((r) => r.temperatura_min))
const lluvia = computed(() => estacionesDetalle.value.map((r) => r.precipitacion))

const actualizadoLegible = computed(() => {
  const raw = m.value?.actualizado
  if (!raw) return ''
  try {
    return new Date(raw).toLocaleString('es-CL', { timeZone: 'America/Santiago' })
  } catch {
    return raw
  }
})

function irEstacion(estacionId) {
  if (!estacionId) return
  metgo.estacionActiva = estacionId
  metgo.cargarDatosMeteo()
  router.push('/meteo')
}
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Métricas globales</h2>
      <p class="page-subtitle">
        KPIs consolidados del valle · día de referencia {{ refFecha }}
      </p>
    </header>

    <p v-if="loading" class="skeleton">Cargando métricas…</p>
    <p v-else-if="error" class="error-text">{{ error }}</p>
    <template v-else-if="m">
      <div class="card-grid card-grid--wide">
        <MetricCard label="Estaciones activas" :value="m.estaciones_activas" :icon="Gauge" />
        <MetricCard
          label="T° media máx"
          :value="`${m.temperatura_media_max ?? '—'}°C`"
          :icon="Thermometer"
        />
        <MetricCard
          label="T° media mín"
          :value="`${m.temperatura_media_min ?? '—'}°C`"
          :icon="Thermometer"
        />
        <MetricCard
          label="Precip. total"
          :value="`${m.precipitacion_total} mm`"
          :icon="CloudRain"
        />
        <MetricCard label="Viento máx" :value="`${m.viento_max} km/h`" :icon="Wind" />
        <MetricCard label="Alertas" :value="m.alertas_activas" :icon="BellRing" />
      </div>

      <div v-if="estacionesDetalle.length" class="chart-grid">
        <SectionCard title="T° máxima por estación (hoy)" subtitle="Comparación en el valle">
          <template #icon><BarChart3 /></template>
          <HorizontalBarChart :labels="labelsEst" :values="tempsMax" unit="°C" kind="temp" />
        </SectionCard>

        <SectionCard title="T° mínima por estación (hoy)" subtitle="Riesgo de heladas">
          <HorizontalBarChart :labels="labelsEst" :values="tempsMin" unit="°C" kind="temp" />
        </SectionCard>

        <SectionCard title="Precipitación hoy" subtitle="mm acumulados por estación">
          <HorizontalBarChart :labels="labelsEst" :values="lluvia" unit=" mm" kind="precip" />
        </SectionCard>
      </div>

      <SectionCard title="Detalle por estación" :subtitle="actualizadoLegible">
        <div v-if="estacionesDetalle.length" class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Estación</th>
                <th>T° máx</th>
                <th>T° mín</th>
                <th>Lluvia</th>
                <th>Viento</th>
                <th>Humedad</th>
                <th>Fuente</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in estacionesDetalle" :key="r.estacion_id">
                <td>
                  <button type="button" class="link-est" @click="irEstacion(r.estacion_id)">
                    {{ r.estacion }}
                  </button>
                </td>
                <td>{{ r.temperatura_max }}°C</td>
                <td>{{ r.temperatura_min }}°C</td>
                <td>{{ r.precipitacion }} mm</td>
                <td>{{ r.viento }} km/h</td>
                <td>{{ r.humedad }}%</td>
                <td class="muted-cell">{{ r.fuente || 'METGO' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="muted">Sin detalle de estaciones.</p>
        <div class="nav-links">
          <router-link to="/meteo/comparativo">Visualizaciones comparativas →</router-link>
          <router-link to="/meteo/historico">Histórico por estación →</router-link>
        </div>
      </SectionCard>

      <SectionCard
        title="Estaciones incluidas"
        :subtitle="(m.estaciones || []).join(' · ')"
      >
        <p class="muted">
          {{ m.estaciones_activas }} estaciones del Valle de Aconcagua.
          <span v-if="m.humedad_media != null"> · Humedad media {{ m.humedad_media }}%</span>
          <span v-if="m.alertas_warning">
            · {{ m.alertas_warning }} alerta(s) warning
          </span>
        </p>
      </SectionCard>
    </template>
  </div>
</template>

<style scoped>
.error-text {
  color: var(--color-danger, #b91c1c);
}
.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}
.table-wrap {
  overflow-x: auto;
  margin-bottom: 0.75rem;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}
.data-table th,
.data-table td {
  padding: 0.5rem 0.65rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}
.data-table th {
  color: var(--color-muted);
  font-weight: 600;
}
.muted-cell {
  font-size: 0.75rem;
  color: var(--color-muted);
}
.link-est {
  border: none;
  background: none;
  padding: 0;
  font: inherit;
  color: var(--color-primary);
  cursor: pointer;
  text-decoration: underline;
  font-weight: 600;
}
.nav-links {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.85rem;
}
.nav-links a {
  color: var(--color-primary);
}
</style>
