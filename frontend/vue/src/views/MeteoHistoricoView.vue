<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { History } from 'lucide-vue-next'
import { useMetgoStore } from '@/stores/metgo'
import SectionCard from '@/components/ui/SectionCard.vue'
import SimpleBarChart from '@/components/charts/SimpleBarChart.vue'
import { useApiCall } from '@/composables/useApiCall'
import { fetchHistorico, syncDatosEtl, fetchMeteoStore } from '@/api/metgoApi'

const store = useMetgoStore()
const dias = 30
const storeInfo = ref(null)
const etlMsg = ref('')
const etlBusy = ref(false)

const { data: historico, loading, error, run } = useApiCall(() =>
  fetchHistorico(store.estacionActiva, dias)
)

/** Una fila por día (últimos N), evita duplicados si la API mezcla fuentes. */
function ultimosDiasUnicos(rows, n = 14) {
  const porDia = new Map()
  for (const r of rows || []) {
    const dia = String(r.fecha ?? '').slice(0, 10)
    if (dia) porDia.set(dia, r)
  }
  return [...porDia.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .slice(-n)
    .map(([, r]) => r)
}

const ultimas2Semanas = computed(() => ultimosDiasUnicos(historico.value, 14))

const labels = computed(() =>
  ultimas2Semanas.value.map((r) => {
    const d = r.fecha || r.actualizado || ''
    return d.slice(5, 10) || d.slice(0, 10)
  })
)
const tempsMax = computed(() =>
  ultimas2Semanas.value.map((r) => r.temperatura_max)
)
const lluvia = computed(() =>
  ultimas2Semanas.value.map((r) => r.precipitacion)
)

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
        Últimos {{ dias }} días · {{ store.estacionNombre }}
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

    <SectionCard title="Temperatura máxima diaria" subtitle="Últimas 2 semanas">
      <template #icon><History /></template>
      <p v-if="loading" class="skeleton">Cargando histórico…</p>
      <p v-else-if="error" class="error-text">{{ error }}</p>
      <SimpleBarChart
        v-else-if="labels.length"
        :labels="labels"
        :values="tempsMax"
        unit="°C"
      />
      <p v-else class="muted">Sin datos históricos.</p>
    </SectionCard>

    <SectionCard title="Precipitación" subtitle="mm por día">
      <SimpleBarChart
        v-if="labels.length && !loading"
        :labels="labels"
        :values="lluvia"
        unit=" mm"
        color="var(--color-sky)"
      />
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
</style>
