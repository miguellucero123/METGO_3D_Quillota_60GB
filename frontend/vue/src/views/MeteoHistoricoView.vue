<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { History } from 'lucide-vue-next'
import { useMetgoStore } from '@/stores/metgo'
import SectionCard from '@/components/ui/SectionCard.vue'
import TimeSeriesChart from '@/components/charts/TimeSeriesChart.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import WindRoseChart from '@/components/charts/WindRoseChart.vue'
import { useApiCall } from '@/composables/useApiCall'
import { fetchHistorico, syncDatosEtl, fetchMeteoStore } from '@/api/metgoApi'
import { hoyChile, seriesHistoricoPorDia } from '@/utils/meteoDates'
import { exportarDatosCSV, exportarDatosJSON } from '@/utils/exportData'

const store = useMetgoStore()
const dias = ref(30)
const storeInfo = ref(null)
const etlMsg = ref('')
const etlBusy = ref(false)

const { data: historico, loading, error, run } = useApiCall(() =>
  fetchHistorico(store.estacionActiva, dias.value)
)

const serie = computed(() => seriesHistoricoPorDia(historico.value, dias.value))

const filasExport = computed(() =>
  serie.value.map((r) => ({
    estacion: store.estacionActiva,
    fecha: r.fecha,
    temperatura: r.temperatura,
    temperatura_max: r.temperatura_max,
    temperatura_min: r.temperatura_min,
    precipitacion: r.precipitacion,
    viento: r.viento,
    humedad: r.humedad,
    presion: r.presion,
    direccion_viento: r.direccion_viento,
    fuente: r.fuente,
  }))
)

function exportNombre() {
  return `historico_${store.estacionActiva}_${dias.value}d`
}

function exportarCsv() {
  exportarDatosCSV(filasExport.value, exportNombre())
}

function exportarJson() {
  exportarDatosJSON(filasExport.value, exportNombre())
}

const vientoDirs = computed(() =>
  serie.value.map((r) => r.direccion_viento).filter((v) => v != null)
)
const vientoSpeeds = computed(() =>
  serie.value.filter((r) => r.direccion_viento != null).map((r) => r.viento)
)

const labels = computed(() => serie.value.map((r) => r.fecha))
const tempsMax = computed(() => serie.value.map((r) => r.temperatura_max))
const tempsMin = computed(() => serie.value.map((r) => r.temperatura_min))
const lluvia = computed(() => serie.value.map((r) => r.precipitacion))

async function cargarStore() {
  try {
    storeInfo.value = await fetchMeteoStore()
  } catch {
    storeInfo.value = null
  }
}

async function sincronizarEtl() {
  etlBusy.value = true
  etlMsg.value = ''
  try {
    // Sync corto: no redescargar Archive (eso es job aparte)
    const ventanaSync = Math.min(Number(dias.value) || 14, 30)
    const r = await syncDatosEtl(ventanaSync, false)
    etlMsg.value = `Sync OK: ${r.store?.registros ?? '?'} registros en store`
    await run()
    await cargarStore()
  } catch (e) {
    etlMsg.value = e.message
  } finally {
    etlBusy.value = false
  }
}

onMounted(async () => {
  await run()
  await cargarStore()
})
watch(() => store.estacionActiva, async () => {
  await run()
})
watch(dias, async () => {
  await run()
})
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Histórico meteorológico</h2>
      <p class="page-subtitle">
        Histórico hasta hoy ({{ hoyChile() }}) · {{ store.estacionNombre }}
        <span class="badge badge--neutral">Store Supabase · OpenMeteo Archive</span>
      </p>
      <label class="range-sel">
        Ventana:
        <select v-model.number="dias">
          <option :value="7">7 días</option>
          <option :value="14">14 días</option>
          <option :value="30">30 días</option>
          <option :value="90">90 días</option>
          <option :value="365">1 año</option>
          <option :value="1825">5 años</option>
        </select>
      </label>
      <button type="button" class="btn btn-sm btn-primary" :disabled="etlBusy" @click="sincronizarEtl">
        Sincronizar recientes (ETL)
      </button>
      <button
        type="button"
        class="btn btn-sm"
        :disabled="!serie.length"
        title="Exportar CSV"
        @click="exportarCsv"
      >
        CSV
      </button>
      <button
        type="button"
        class="btn btn-sm"
        :disabled="!serie.length"
        title="Exportar JSON"
        @click="exportarJson"
      >
        JSON
      </button>
      <p v-if="storeInfo" class="muted small">
        Store global: {{ storeInfo.registros }} registros · {{ storeInfo.estaciones }} estaciones
      </p>
      <p v-if="etlMsg" class="small">{{ etlMsg }}</p>
    </header>

    <SectionCard
      title="Rango térmico diario"
      :subtitle="`${serie.length} días con datos · máx y mín`"
    >
      <template #icon><History /></template>
      <SkeletonLoader v-if="loading" :height="220" />
      <p v-else-if="error" class="error-text">{{ error }}</p>
      <TimeSeriesChart
        v-else-if="labels.length"
        :labels="labels"
        :values="tempsMax"
        :values-min="tempsMin"
        unit="°C"
        :show-band="true"
        :show-area="false"
        :height="240"
        y-axis-title="T° máx / mín"
        color="var(--color-primary)"
        fill-color="rgba(26, 95, 74, 0.15)"
      />
      <p v-else class="muted">Sin datos históricos. Use sincronizar ETL o revise la estación.</p>
    </SectionCard>

    <SectionCard
      v-if="vientoDirs.length"
      title="Rosa de vientos"
      :subtitle="`Dirección dominante · ${vientoDirs.length} días con dato`"
    >
      <WindRoseChart :directions="vientoDirs" :speeds="vientoSpeeds" />
    </SectionCard>

    <SectionCard title="Precipitación diaria" :subtitle="`${serie.length} días · mm acumulados por día`">
      <TimeSeriesChart
        v-if="labels.length && !loading"
        :labels="labels"
        :values="lluvia"
        unit=" mm"
        :height="200"
        y-axis-title="Precipitación"
        color="var(--color-sky)"
        fill-color="rgba(56, 142, 192, 0.2)"
      />
    </SectionCard>

    <SectionCard title="Tabla completa" subtitle="Registro diario ordenado">
      <div v-if="serie.length" class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Media</th>
              <th>Máx</th>
              <th>Mín</th>
              <th>Lluvia</th>
              <th>Viento</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in [...serie].reverse()" :key="row.fecha">
              <td>{{ row.fecha }}</td>
              <td>{{ row.temperatura }}°</td>
              <td>{{ row.temperatura_max }}°</td>
              <td>{{ row.temperatura_min }}°</td>
              <td>{{ row.precipitacion }} mm</td>
              <td>{{ row.viento }} m/s</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else-if="!loading" class="muted">Sin filas para mostrar.</p>
    </SectionCard>
  </div>
</template>

<style scoped>
.error-text {
  color: var(--color-danger, #b91c1c);
}
.small {
  font-size: 0.75rem;
  margin-top: 0.35rem;
}
.range-sel {
  display: inline-block;
  font-size: 0.85rem;
  margin-right: 0.75rem;
}
.range-sel select {
  margin-left: 0.35rem;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
}
.table-wrap {
  overflow-x: auto;
  max-height: 360px;
  overflow-y: auto;
}
</style>
