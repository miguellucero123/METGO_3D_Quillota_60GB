<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { GitCompare, BarChart3, Star } from 'lucide-vue-next'
import SectionCard from '@/components/ui/SectionCard.vue'
import SimpleBarChart from '@/components/charts/SimpleBarChart.vue'
import { useApiCall } from '@/composables/useApiCall'
import { fetchComparativo, fetchComparativoHistorico } from '@/api/metgoApi'
import { useFavoritesStore } from '@/stores/favorites'
import { useMetgoStore } from '@/stores/metgo'
import { useFormatTemp } from '@/composables/useFormatTemp'

const router = useRouter()
const favorites = useFavoritesStore()
const metgo = useMetgoStore()
const { formatTemperatura, unit } = useFormatTemp()

const { data: resumen, loading, error, run: runResumen } = useApiCall(fetchComparativo)
const {
  data: historico,
  loading: loadingHist,
  error: errorHist,
  run: runHistorico,
} = useApiCall(() => fetchComparativoHistorico(14))

async function cargar() {
  await Promise.all([runResumen(), runHistorico()])
}

onMounted(cargar)

const estacionesResumen = computed(() => resumen.value || [])

const labelsTempMax = computed(() =>
  estacionesResumen.value.map((r) => r.estacion || r.estacion_id)
)
const valuesTempMax = computed(() =>
  estacionesResumen.value.map((r) => r.temperatura_max)
)
const valuesPrecip = computed(() =>
  estacionesResumen.value.map((r) => r.precipitacion)
)

/** Promedio T° máx últimas 2 semanas por estación. */
const promedioHistPorEstacion = computed(() => {
  const porEst = new Map()
  for (const r of historico.value || []) {
    const id = r.estacion_id || r.estacion
    if (!id) continue
    if (!porEst.has(id)) porEst.set(id, { nombre: r.estacion, sum: 0, n: 0 })
    const acc = porEst.get(id)
    acc.sum += Number(r.temperatura_max) || 0
    acc.n += 1
  }
  return [...porEst.values()]
    .map((x) => ({
      nombre: x.nombre,
      promedio: x.n ? Math.round((x.sum / x.n) * 10) / 10 : 0,
    }))
    .sort((a, b) => a.nombre.localeCompare(b.nombre))
})

const labelsHist = computed(() => promedioHistPorEstacion.value.map((x) => x.nombre))
const valuesHist = computed(() => promedioHistPorEstacion.value.map((x) => x.promedio))
const tempUnitLabel = computed(() => (unit.value === 'F' ? '°F' : '°C'))

function irEstacion(id) {
  metgo.estacionActiva = id
  metgo.cargarDatosMeteo()
  router.push('/meteo')
}
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Visualizaciones avanzadas</h2>
      <p class="page-subtitle">
        Valle de Aconcagua · 5 estaciones principales
        <span class="badge badge--neutral">Migrado desde puerto 8506</span>
      </p>
    </header>

    <SectionCard
      title="Resumen actual por estación"
      subtitle="Pronóstico del día · Quillota, Los Nogales, Hijuelas, Limache, Olmué"
    >
      <template #icon><GitCompare /></template>
      <p v-if="loading" class="skeleton">Cargando estaciones…</p>
      <p v-else-if="error" class="error-text">{{ error }}</p>
      <template v-else>
        <p v-if="!estacionesResumen.length" class="muted">Sin datos comparativos.</p>
        <div v-else class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th aria-label="Favorito" />
                <th>Estación</th>
                <th>T° máx</th>
                <th>T° mín</th>
                <th>Lluvia</th>
                <th>Viento</th>
                <th>Humedad</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in estacionesResumen" :key="r.estacion_id">
                <td>
                  <button
                    type="button"
                    class="fav-cell"
                    :class="{ 'fav-cell--on': favorites.isFavorite(r.estacion_id) }"
                    @click="favorites.toggle(r.estacion_id)"
                  >
                    <Star aria-hidden="true" />
                  </button>
                </td>
                <td>
                  <button type="button" class="link-est" @click="irEstacion(r.estacion_id)">
                    {{ r.estacion }}
                  </button>
                </td>
                <td>{{ formatTemperatura(r.temperatura_max) }}</td>
                <td>{{ formatTemperatura(r.temperatura_min) }}</td>
                <td>{{ r.precipitacion }} mm</td>
                <td>{{ r.viento }} km/h</td>
                <td>{{ r.humedad }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </SectionCard>

    <SectionCard
      title="Comparativo T° máxima (hoy)"
      subtitle="Todas las estaciones del valle"
    >
      <template #icon><BarChart3 /></template>
      <SimpleBarChart
        v-if="labelsTempMax.length && !loading"
        :labels="labelsTempMax"
        :values="valuesTempMax"
        :unit="tempUnitLabel"
      />
    </SectionCard>

    <SectionCard title="Precipitación (hoy)" subtitle="mm por estación">
      <SimpleBarChart
        v-if="labelsTempMax.length && !loading"
        :labels="labelsTempMax"
        :values="valuesPrecip"
        unit=" mm"
        color="var(--color-sky)"
      />
    </SectionCard>

    <SectionCard
      title="T° máxima promedio · 2 semanas"
      subtitle="Histórico multi-estación vía API"
    >
      <p v-if="loadingHist" class="skeleton">Cargando histórico…</p>
      <p v-else-if="errorHist" class="error-text">{{ errorHist }}</p>
      <SimpleBarChart
        v-else-if="labelsHist.length"
        :labels="labelsHist"
        :values="valuesHist"
        :unit="tempUnitLabel"
        color="var(--color-accent, #5a9b72)"
      />
      <p v-else class="muted">Sin histórico multi-estación.</p>
    </SectionCard>
  </div>
</template>

<style scoped>
.table-wrap {
  overflow-x: auto;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}
.data-table th,
.data-table td {
  padding: 0.55rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}
.data-table th {
  color: var(--color-muted);
  font-weight: 600;
}
.error-text {
  color: var(--color-danger, #b91c1c);
}
.fav-cell {
  border: none;
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  padding: 0.15rem;
}
.fav-cell svg {
  width: 0.95rem;
  height: 0.95rem;
}
.fav-cell--on {
  color: var(--color-warning);
  fill: var(--color-warning);
}
.link-est {
  border: none;
  background: none;
  padding: 0;
  font: inherit;
  color: var(--color-primary);
  cursor: pointer;
  text-decoration: underline;
}
</style>
