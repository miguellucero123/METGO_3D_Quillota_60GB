<template>
  <div class="page">
    <header class="page-head">
      <h1>Variables en conjunto</h1>
      <p>Combo multi-serie extensible · catálogo activable · airshed Paipote</p>
    </header>

    <div class="controls">
      <label>
        Estación
        <select v-model="slug">
          <option v-for="est in site.stations" :key="est.slug" :value="est.slug">
            {{ est.nombre }}
          </option>
        </select>
      </label>
      <button type="button" class="btn" @click="cargar" :disabled="loading">Actualizar</button>
    </div>

    <div class="toggles" v-if="catalogo.length">
      <label v-for="slot in catalogo" :key="slot.id" class="tog">
        <input type="checkbox" :value="slot.id" v-model="activas" />
        <span :style="{ borderColor: slot.color }">{{ slot.nombre }}</span>
      </label>
    </div>

    <div v-if="loading" class="state">Cargando series…</div>
    <div v-else-if="error" class="state error">{{ error }}</div>
    <template v-else-if="payload">
      <VariablesConjuntoChart
        :labels="payload.labels || []"
        :series-map="payload.series || {}"
        :slots="slotsActivos"
      />
      <p class="meta">
        {{ payload.estacion_nombre }} · {{ (payload.labels || []).length }} horas · catálogo v{{
          payload.catalogo_version
        }}
      </p>
    </template>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, ref, watch } from 'vue'
import VariablesConjuntoChart from '@/components/aire/VariablesConjuntoChart.vue'
import { fetchConjuntoCatalogo, fetchConjuntoSeries } from '@/services/aireApi'

const site = inject('site')
const slug = ref('paipote')
const catalogo = ref([])
const activas = ref([])
const loading = ref(false)
const error = ref(null)
const payload = ref(null)

const slotsActivos = computed(() =>
  (catalogo.value || []).filter((s) => activas.value.includes(s.id))
)

async function cargarCatalogo() {
  const cat = await fetchConjuntoCatalogo()
  catalogo.value = cat.slots || []
  activas.value = catalogo.value.filter((s) => s.default).map((s) => s.id)
}

async function cargar() {
  if (!activas.value.length) {
    error.value = 'Activa al menos una serie'
    return
  }
  loading.value = true
  error.value = null
  try {
    payload.value = await fetchConjuntoSeries(slug.value, {
      horas: 72,
      series: activas.value,
    })
  } catch (e) {
    error.value = e?.message || 'Error al cargar conjunto'
    payload.value = null
  } finally {
    loading.value = false
  }
}

watch(activas, () => {
  if (activas.value.length) cargar()
})
watch(slug, cargar)

onMounted(async () => {
  try {
    await cargarCatalogo()
    await cargar()
  } catch (e) {
    error.value = e?.message || 'Error catálogo'
  }
})
</script>

<style scoped>
.page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 1.25rem;
}
.page-head h1 {
  margin: 0 0 0.35rem;
}
.page-head p {
  margin: 0;
  color: var(--color-text-secondary);
}
.controls {
  display: flex;
  gap: 1rem;
  align-items: end;
  margin: 1rem 0;
}
.controls label {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.85rem;
}
.controls select {
  padding: 0.4rem 0.55rem;
  border-radius: 8px;
  border: 1px solid var(--color-border);
}
.btn {
  border: none;
  border-radius: 8px;
  padding: 0.45rem 0.9rem;
  background: var(--color-primary);
  font-weight: 600;
  cursor: pointer;
}
.toggles {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-bottom: 1rem;
}
.tog {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.78rem;
  cursor: pointer;
}
.tog span {
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  border: 2px solid #cbd5e1;
  background: var(--color-surface);
}
.tog input:checked + span {
  background: color-mix(in srgb, var(--color-primary) 18%, transparent);
}
.meta {
  font-size: 0.75rem;
  color: var(--color-muted);
  margin-top: 0.5rem;
}
.state {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-secondary);
}
.state.error {
  color: #b91c1c;
}
</style>
