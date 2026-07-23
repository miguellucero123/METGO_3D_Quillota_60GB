<template>
  <div class="page">
    <header class="page-head">
      <h1>Pronóstico de aire</h1>
      <p>Promedios diarios e ICAP · {{ estacionActiva }}</p>
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
    </div>

    <div v-if="loading" class="state">Cargando pronóstico…</div>
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
        :series="[{ name: 'ICAP', data: icaps, type: 'bar', color: '#f59e0b' }]"
      />
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Fecha</th>
              <th>PM2.5</th>
              <th>PM10</th>
              <th>ICAP</th>
              <th>Categoría</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="f in filas" :key="f.fecha">
              <td>{{ f.fecha }}</td>
              <td>{{ f.pm2_5 ?? '—' }}</td>
              <td>{{ f.pm10 ?? '—' }}</td>
              <td>{{ f.icap ?? '—' }}</td>
              <td>{{ f.etiqueta ?? '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
    <div v-else class="state">Sin datos de pronóstico</div>
  </div>
</template>

<script setup>
import { computed, inject, ref, watch } from 'vue'
import AireSeriesChart from '@/components/aire/AireSeriesChart.vue'
import { wakeApi, fetchAirePronostico } from '@/services/aireApi'

const site = inject('site')
const slug = ref(site.stations[0]?.slug || 'copiapo_centro')
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
    const data = await fetchAirePronostico(slug.value, 5)
    filas.value = Array.isArray(data) ? data : []
  } catch (err) {
    error.value = err?.message || 'Error al cargar pronóstico'
    filas.value = []
  } finally {
    loading.value = false
  }
}

watch(slug, cargar, { immediate: true })
</script>

<style scoped>
.page { max-width: 1100px; }
.page-head { margin-bottom: 1rem; }
.page-head h1 { margin: 0 0 0.25rem; }
.page-head p { margin: 0; color: var(--color-text-secondary); }
.toolbar { margin-bottom: 1rem; }
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
.table-wrap { margin-top: 1.25rem; overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
th, td { padding: 0.5rem 0.65rem; border-bottom: 1px solid var(--color-border); text-align: left; }
th { color: var(--color-muted); font-weight: 500; }
</style>
