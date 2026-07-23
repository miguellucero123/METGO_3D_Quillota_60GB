<script setup>
import { computed, ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { GitCompare, BarChart3, Star } from 'lucide-vue-next'
import SectionCard from '@/components/ui/SectionCard.vue'
import EstacionCard from '@/components/ui/EstacionCard.vue'
import HorizontalBarChart from '@/components/charts/HorizontalBarChart.vue'
import TimeSeriesChart from '@/components/charts/TimeSeriesChart.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import ValleEstacionesMeteoMap from '@/components/maps/ValleEstacionesMeteoMap.vue'
import SparklineGrid from '@/components/charts/SparklineGrid.vue'
import { useApiCall } from '@/composables/useApiCall'
import { fetchComparativo, fetchComparativoHistorico } from '@/api/metgoApi'
import { useFavoritesStore } from '@/stores/favorites'
import { useMetgoStore } from '@/stores/metgo'
import { useFormatTemp } from '@/composables/useFormatTemp'
import { hoyChile } from '@/utils/meteoDates'

const router = useRouter()
const favorites = useFavoritesStore()
const metgo = useMetgoStore()
const { formatTemperatura, unit } = useFormatTemp()

const diasHist = ref(14)

const { data: resumen, loading, error, run: runResumen } = useApiCall(fetchComparativo)
const {
  data: historico,
  loading: loadingHist,
  error: errorHist,
  run: runHistorico,
} = useApiCall(() => fetchComparativoHistorico(diasHist.value))

async function cargar() {
  await Promise.all([runResumen(), runHistorico()])
}

onMounted(cargar)
watch(diasHist, () => runHistorico())

const estacionesResumen = computed(() => resumen.value || [])

const labelsTempMax = computed(() =>
  estacionesResumen.value.map((r) => r.estacion || r.estacion_id)
)
const valuesTempMax = computed(() =>
  estacionesResumen.value.map((r) => Number(r.temperatura_max) || 0)
)
const valuesPrecip = computed(() =>
  estacionesResumen.value.map((r) => Number(r.precipitacion) || 0)
)
const stationIds = computed(() =>
  estacionesResumen.value.map((r) => r.estacion_id)
)
const barHints = computed(() =>
  estacionesResumen.value.map(
    (r) => `Fuente: ${r.fuente || 'openmeteo'} · ${String(r.fecha || '').slice(0, 10)}`
  )
)
const valuesNubosidad = computed(() =>
  estacionesResumen.value.map((r) => Number(r.cobertura_nubosa) || 0)
)

/** Promedio T° máx por estación en ventana histórica (solo días ≤ hoy). */
const promedioHistPorEstacion = computed(() => {
  const porEst = new Map()
  for (const r of historico.value || []) {
    const id = r.estacion_id || r.estacion
    if (!id) continue
    const dia = String(r.fecha ?? '').slice(0, 10)
    if (dia > hoyChile()) continue
    if (!porEst.has(id)) porEst.set(id, { nombre: r.estacion, sum: 0, n: 0 })
    const acc = porEst.get(id)
    acc.sum += Number(r.temperatura_max) || 0
    acc.n += 1
  }
  return [...porEst.values()]
    .map((x) => ({
      nombre: x.nombre,
      promedio: x.n ? Math.round((x.sum / x.n) * 10) / 10 : 0,
      dias: x.n,
    }))
    .sort((a, b) => a.nombre.localeCompare(b.nombre))
})

const labelsHist = computed(() => promedioHistPorEstacion.value.map((x) => x.nombre))
const valuesHist = computed(() => promedioHistPorEstacion.value.map((x) => x.promedio))

/** Serie diaria del valle: promedio T° máx de las 5 estaciones por día. */
const serieValle = computed(() => {
  const porDia = new Map()
  for (const r of historico.value || []) {
    const dia = String(r.fecha ?? '').slice(0, 10)
    if (!dia || dia > hoyChile()) continue
    if (!porDia.has(dia)) porDia.set(dia, { sum: 0, n: 0 })
    const acc = porDia.get(dia)
    acc.sum += Number(r.temperatura_max) || 0
    acc.n += 1
  }
  return [...porDia.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([fecha, acc]) => ({
      fecha,
      temperatura_max: acc.n ? Math.round((acc.sum / acc.n) * 10) / 10 : 0,
    }))
})

const labelsValle = computed(() => serieValle.value.map((r) => r.fecha))
const tempsValle = computed(() => serieValle.value.map((r) => r.temperatura_max))

const mapaVariable = ref('temperatura')

/** Small multiples: serie T° máx por estación desde histórico multi-estación. */
const sparkSeries = computed(() => {
  const porEst = new Map()
  for (const r of historico.value || []) {
    const id = r.estacion_id
    const dia = String(r.fecha ?? '').slice(0, 10)
    if (!id || dia > hoyChile()) continue
    if (!porEst.has(id)) {
      porEst.set(id, { id, nombre: r.estacion, fechas: [], valores: [], unidad: '°C' })
    }
    const acc = porEst.get(id)
    acc.fechas.push(dia)
    acc.valores.push(Number(r.temperatura_max) || 0)
  }
  return [...porEst.values()].sort((a, b) => a.nombre.localeCompare(b.nombre))
})

const tempUnitLabel = computed(() => (unit.value === 'F' ? '°F' : '°C'))

function irEstacion(id) {
  if (!id) return
  metgo.setEstacion(id)
  metgo.cargarDatosMeteo()
  router.push('/meteo')
}

function onBarClick({ id }) {
  irEstacion(id)
}
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Visualizaciones avanzadas</h2>
      <p class="page-subtitle">
        Valle de Aconcagua · comparación por estación · hoy {{ hoyChile() }}
      </p>
    </header>

    <SectionCard
      title="Resumen actual por estación"
      subtitle="Condiciones del día en las 5 estaciones principales"
    >
      <template #icon><GitCompare /></template>
      <SkeletonLoader v-if="loading" :height="160" :lines="5" />
      <p v-else-if="error" class="error-text">{{ error }}</p>
      <template v-else>
        <p v-if="!estacionesResumen.length" class="muted">Sin datos comparativos.</p>
        <template v-else>
          <div class="estaciones-grid">
            <EstacionCard
              v-for="r in estacionesResumen"
              :key="r.estacion_id"
              :id="r.estacion_id"
              :nombre="r.estacion || r.estacion_id"
              :temperatura="r.temperatura ?? r.temperatura_max"
              :temperatura-max="r.temperatura_max"
              :temperatura-min="r.temperatura_min"
              :precipitacion="r.precipitacion"
              :humedad="r.humedad"
              :viento="r.viento"
              :activa="r.estacion_id === metgo.estacionActiva"
              @select="irEstacion"
            />
          </div>
          <div class="table-wrap table-wrap--compact">
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
                  <td>{{ r.viento }} m/s</td>
                  <td>{{ r.humedad }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </template>
    </SectionCard>

    <SectionCard title="Mapa del valle" subtitle="Pins por estación · clic para detalle">
      <div class="mapa-vars">
        <button type="button" :class="{ active: mapaVariable === 'temperatura' }" @click="mapaVariable = 'temperatura'">T°</button>
        <button type="button" :class="{ active: mapaVariable === 'precipitacion' }" @click="mapaVariable = 'precipitacion'">Lluvia</button>
        <button type="button" :class="{ active: mapaVariable === 'nubosidad' }" @click="mapaVariable = 'nubosidad'">Nubes</button>
      </div>
      <ValleEstacionesMeteoMap :variable="mapaVariable" />
    </SectionCard>

    <div class="chart-grid">
      <SectionCard title="T° máxima hoy" subtitle="Comparación horizontal entre estaciones">
        <template #icon><BarChart3 /></template>
        <HorizontalBarChart
          v-if="labelsTempMax.length && !loading"
          :labels="labelsTempMax"
          :values="valuesTempMax"
          :station-ids="stationIds"
          :hints="barHints"
          :unit="tempUnitLabel"
          kind="temp"
          clickable
          @bar-click="onBarClick"
        />
      </SectionCard>

      <SectionCard title="Precipitación hoy" subtitle="mm por estación">
        <HorizontalBarChart
          v-if="labelsTempMax.length && !loading"
          :labels="labelsTempMax"
          :values="valuesPrecip"
          :station-ids="stationIds"
          :hints="barHints"
          unit=" mm"
          kind="precip"
          clickable
          @bar-click="onBarClick"
        />
      </SectionCard>

      <SectionCard
        v-if="valuesNubosidad.some((v) => v > 0)"
        title="Nubosidad hoy"
        subtitle="% cobertura por estación"
      >
        <HorizontalBarChart
          v-if="labelsTempMax.length && !loading"
          :labels="labelsTempMax"
          :values="valuesNubosidad"
          :station-ids="stationIds"
          :hints="barHints"
          unit=" %"
          kind="humedad"
          clickable
          @bar-click="onBarClick"
        />
      </SectionCard>
    </div>

    <SectionCard
      title="Evolución del valle (T° máx media)"
      :subtitle="`${labelsValle.length} días · promedio de las estaciones activas`"
    >
      <div class="range-sel">
        <label>
          Ventana:
          <select v-model.number="diasHist">
            <option :value="7">7 días</option>
            <option :value="14">14 días</option>
            <option :value="30">30 días</option>
          </select>
        </label>
      </div>
      <SkeletonLoader v-if="loadingHist" :height="200" />
      <p v-else-if="errorHist" class="error-text">{{ errorHist }}</p>
      <TimeSeriesChart
        v-else-if="labelsValle.length"
        :labels="labelsValle"
        :values="tempsValle"
        :unit="tempUnitLabel"
        :height="220"
        y-axis-title="T° máx media"
        export-name="comparativo_valle"
      />
      <p v-else class="muted">Sin histórico multi-estación.</p>
    </SectionCard>

    <SectionCard
      v-if="sparkSeries.length"
      title="Small multiples · T° máx por estación"
      :subtitle="`Tendencia ${diasHist} días`"
    >
      <SparklineGrid :series="sparkSeries" kind="temp" />
    </SectionCard>

    <SectionCard
      :title="`T° máxima promedio · ${diasHist} días`"
      subtitle="Por estación (barras relativas al rango del período)"
    >
      <HorizontalBarChart
        v-if="labelsHist.length && !loadingHist"
        :labels="labelsHist"
        :values="valuesHist"
        :unit="tempUnitLabel"
        kind="temp"
      />
      <p v-else-if="!loadingHist" class="muted">Sin histórico multi-estación.</p>
    </SectionCard>
  </div>
</template>

<style scoped>
.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}
.estaciones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.table-wrap {
  overflow-x: auto;
}
.table-wrap--compact {
  margin-top: 0.25rem;
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
.range-sel {
  margin-bottom: 0.65rem;
  font-size: 0.8rem;
}
.mapa-vars {
  display: flex;
  gap: 0.35rem;
  margin-bottom: 0.5rem;
}
.mapa-vars button {
  padding: 0.3rem 0.55rem;
  border: 1px solid var(--color-border, #334155);
  border-radius: 6px;
  background: var(--color-surface, #1e293b);
  font-size: 0.75rem;
  cursor: pointer;
}
.mapa-vars button.active {
  background: #0284c7;
  color: #fff;
  border-color: #0284c7;
}
.range-sel select {
  margin-left: 0.35rem;
  padding: 0.2rem 0.45rem;
  border-radius: 6px;
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
