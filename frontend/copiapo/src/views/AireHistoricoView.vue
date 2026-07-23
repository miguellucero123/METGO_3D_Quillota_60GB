<template>
  <div class="page">
    <header class="page-head">
      <h1>Histórico reciente</h1>
      <p>Últimos días CAMS · {{ estacionActiva }}</p>
    </header>

    <div class="toolbar">
      <label>
        Estación
        <select v-model="slug">
          <option v-for="s in site.stations" :key="s.slug" :value="s.slug">
            {{ s.nombre }}
          </option>
        </select>
      </label>
      <label>
        Días
        <select v-model.number="dias">
          <option :value="7">7</option>
          <option :value="14">14</option>
          <option :value="30">30</option>
        </select>
      </label>
    </div>

    <div v-if="loading" class="state">Cargando histórico…</div>
    <div v-else-if="error" class="state error">{{ error }}</div>
    <template v-else-if="filas.length">
      <AireSeriesChart
        :labels="labels"
        y-name="µg/m³"
        :series="[
          { name: 'PM2.5', data: pm25, color: '#fbbf24' },
          { name: 'PM10', data: pm10, color: '#fb923c' },
        ]"
      />
      <AireSeriesChart
        class="mt"
        :labels="labels"
        y-name="ICAP"
        :series="[{ name: 'ICAP', data: icaps, color: '#f59e0b' }]"
      />
    </template>
    <div v-else class="state">Sin histórico disponible</div>
  </div>
</template>

<script setup>
import { computed, inject, ref, watch } from 'vue'
import AireSeriesChart from '@/components/aire/AireSeriesChart.vue'
import { wakeApi, fetchAireHistorico } from '@/services/aireApi'

const site = inject('site')
const slug = ref(site.stations[0]?.slug || 'copiapo_centro')
const dias = ref(7)
const loading = ref(false)
const error = ref(null)
const filas = ref([])

const estacionActiva = computed(
  () => site.stations.find((s) => s.slug === slug.value)?.nombre || slug.value
)
const labels = computed(() => filas.value.map((f) => f.fecha?.slice(5) || f.fecha))
const pm25 = computed(() => filas.value.map((f) => f.pm2_5))
const pm10 = computed(() => filas.value.map((f) => f.pm10))
const icaps = computed(() => filas.value.map((f) => f.icap))

async function cargar() {
  loading.value = true
  error.value = null
  try {
    await wakeApi()
    const data = await fetchAireHistorico(slug.value, dias.value)
    filas.value = Array.isArray(data) ? data : []
  } catch (err) {
    error.value = err?.message || 'Error al cargar histórico'
    filas.value = []
  } finally {
    loading.value = false
  }
}

watch([slug, dias], cargar, { immediate: true })
</script>

<style scoped>
.page { max-width: 1100px; }
.page-head { margin-bottom: 1rem; }
.page-head h1 { margin: 0 0 0.25rem; }
.page-head p { margin: 0; color: var(--color-text-secondary); }
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}
.toolbar select {
  display: block;
  margin-top: 0.35rem;
  padding: 0.4rem 0.6rem;
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 6px;
}
.mt { margin-top: 1rem; }
.state { padding: 2rem; text-align: center; color: var(--color-text-secondary); }
.state.error { color: var(--color-danger); }
</style>
