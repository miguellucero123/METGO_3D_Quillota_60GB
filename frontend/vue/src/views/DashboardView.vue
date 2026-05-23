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
import { fetchPronostico, fetchAlertas, fetchRecomendacionesAgricolas } from '@/api/metgoApi'
import {
  riesgoHelada,
  necesidadRiego,
  acumuladoPrecipitacion,
} from '@/utils/agroInsights'

const store = useMetgoStore()
const pronostico = ref([])
const alertas = ref([])
const recomendaciones = ref([])
const cargandoExtra = ref(false)

const d = computed(() => store.datosMeteo)
const helada = computed(() => riesgoHelada(d.value?.temperatura_min))
const riego = computed(() => necesidadRiego(d.value?.humedad, d.value?.precipitacion))
const lluvia7d = computed(() => acumuladoPrecipitacion(pronostico.value))

async function cargarResumen() {
  cargandoExtra.value = true
  try {
    const [p, a, r] = await Promise.all([
      fetchPronostico(store.estacionActiva, 7),
      fetchAlertas(store.estacionActiva),
      fetchRecomendacionesAgricolas(store.estacionActiva),
    ])
    pronostico.value = p
    alertas.value = a.slice(0, 4)
    recomendaciones.value = r.slice(0, 3)
  } catch {
    pronostico.value = []
    alertas.value = []
    recomendaciones.value = []
  } finally {
    cargandoExtra.value = false
  }
}

async function actualizarTodo() {
  await store.cargarDatosMeteo()
  await cargarResumen()
}

onMounted(cargarResumen)
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

    <p v-if="store.error" class="alert-banner">{{ store.error }}</p>

    <div v-if="store.cargando" class="skeleton">Cargando condiciones actuales…</div>

    <template v-else-if="d">
      <div class="card-grid card-grid--wide">
        <MetricCard label="Temperatura media" :value="d.temperatura" unit="°C">
          <template #icon><Thermometer /></template>
        </MetricCard>
        <MetricCard label="Máxima" :value="d.temperatura_max" unit="°C">
          <template #icon><ArrowUp /></template>
        </MetricCard>
        <MetricCard label="Mínima" :value="d.temperatura_min" unit="°C" :variant="helada.nivel === 'high' ? 'alert' : 'default'">
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
        <div class="insight-chip" :class="`insight-chip--${helada.nivel}`">
          <strong>Heladas:</strong> {{ helada.label }}
        </div>
        <div class="insight-chip" :class="`insight-chip--${riego.nivel}`">
          <strong>Riego:</strong> {{ riego.label }}
        </div>
        <div class="insight-chip insight-chip--low">
          <strong>Lluvia 7 días:</strong> {{ lluvia7d.toFixed(1) }} mm acum.
        </div>
      </div>

      <div class="layout-split">
        <SectionCard title="Pronóstico próximos días" subtitle="OpenMeteo · 7 días">
          <template #icon><CloudRain /></template>
          <p v-if="cargandoExtra" class="muted">Cargando…</p>
          <table v-else-if="pronostico.length" class="data-table">
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
          <p v-else class="muted">Sin pronóstico disponible.</p>
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
</style>
