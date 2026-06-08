<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { History } from 'lucide-vue-next'
import { useMetgoStore } from '@/stores/metgo'
import SectionCard from '@/components/ui/SectionCard.vue'
import TimeSeriesChart from '@/components/charts/TimeSeriesChart.vue'
import { useApiCall } from '@/composables/useApiCall'
import { fetchHistorico, syncDatosEtl, fetchMeteoStore } from '@/api/metgoApi'
import { hoyChile, seriesHistoricoPorDia } from '@/utils/meteoDates'

const store = useMetgoStore()
const dias = 30
const storeInfo = ref(null)
const etlMsg = ref('')
const etlBusy = ref(false)

const { data: historico, loading, error, run } = useApiCall(() =>
  fetchHistorico(store.estacionActiva, dias)
)

const serie = computed(() => seriesHistoricoPorDia(historico.value, dias))

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
    const r = await syncDatosEtl(dias, true)
    etlMsg.value = `Sync OK: ${r.store?.registros ?? '?'} registros en BD local`
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
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Histórico meteorológico</h2>
      <p class="page-subtitle">
        Últimos {{ dias }} días hasta hoy ({{ hoyChile() }}) · {{ store.estacionNombre }}
        <span class="badge badge--neutral">Fase 4A · ETL local</span>
      </p>
      <button type="button" class="btn btn-sm btn-primary" :disabled="etlBusy" @click="sincronizarEtl">
        Sincronizar OpenMeteo + CSV → store
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
      <p v-if="loading" class="skeleton">Cargando histórico…</p>
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
              <td>{{ row.viento }} km/h</td>
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
.table-wrap {
  overflow-x: auto;
  max-height: 360px;
  overflow-y: auto;
}
</style>
