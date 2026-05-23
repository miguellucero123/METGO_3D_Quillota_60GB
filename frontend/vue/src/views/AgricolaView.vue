<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Sprout, Droplets, ThermometerSnowflake, Tractor } from 'lucide-vue-next'
import { useMetgoStore } from '@/stores/metgo'
import MetricCard from '@/components/ui/MetricCard.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import { fetchRecomendacionesAgricolas } from '@/api/metgoApi'
import {
  CULTIVOS_QUILLOTA,
  riesgoHelada,
  necesidadRiego,
  condicionViento,
} from '@/utils/agroInsights'

const store = useMetgoStore()
const recomendaciones = ref([])
const cargando = ref(false)

const d = computed(() => store.datosMeteo)
const helada = computed(() => riesgoHelada(d.value?.temperatura_min))
const riego = computed(() => necesidadRiego(d.value?.humedad, d.value?.precipitacion))
const viento = computed(() => condicionViento(d.value?.viento))

async function cargar() {
  cargando.value = true
  try {
    recomendaciones.value = await fetchRecomendacionesAgricolas(store.estacionActiva)
  } catch {
    recomendaciones.value = []
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
watch(() => store.estacionActiva, cargar)
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Gestión agrícola</h2>
      <p class="page-subtitle">
        Recomendaciones operativas · {{ store.estacionNombre }} · Valle del Aconcagua
      </p>
    </header>

    <div v-if="d" class="card-grid">
      <MetricCard
        label="Riesgo heladas"
        :value="helada.label"
        :variant="helada.nivel === 'high' ? 'alert' : helada.nivel === 'medium' ? 'warning' : 'default'"
      >
        <template #icon><ThermometerSnowflake /></template>
      </MetricCard>
      <MetricCard
        label="Manejo de riego"
        :value="riego.label"
        :variant="riego.nivel === 'high' ? 'warning' : 'default'"
      >
        <template #icon><Droplets /></template>
      </MetricCard>
      <MetricCard label="Aplicaciones / viento" :value="viento.label">
        <template #icon><Tractor /></template>
      </MetricCard>
    </div>

    <div class="layout-split">
      <SectionCard title="Recomendaciones por cultivo" subtitle="Basadas en pronóstico OpenMeteo">
        <template #icon><Sprout /></template>
        <p v-if="cargando" class="skeleton">Analizando condiciones…</p>
        <div v-else-if="recomendaciones.length" class="reco-cards">
          <article v-for="(r, i) in recomendaciones" :key="i" class="reco-card">
            <h4>{{ r.cultivo }}</h4>
            <p class="reco-card__accion">{{ r.accion }}</p>
            <p class="reco-card__motivo">{{ r.motivo }}</p>
          </article>
        </div>
        <p v-else class="muted">Sin recomendaciones (verifique la API).</p>
      </SectionCard>

      <SectionCard title="Cultivos principales — Quillota" subtitle="Referencia regional MIP">
        <template #icon><Sprout /></template>
        <table class="data-table">
          <thead>
            <tr>
              <th>Cultivo</th>
              <th>Importancia</th>
              <th>Estado fenológico ref.</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in CULTIVOS_QUILLOTA" :key="c.nombre">
              <td><strong>{{ c.nombre }}</strong></td>
              <td>{{ c.area }}</td>
              <td>{{ c.estacion }}</td>
            </tr>
          </tbody>
        </table>
        <p class="muted footnote">
          Condiciones actuales: {{ d?.temperatura }}°C media · {{ d?.humedad }}% HR ·
          {{ d?.precipitacion }} mm precip.
        </p>
      </SectionCard>
    </div>
  </div>
</template>

<style scoped>
.page {
  max-width: 1280px;
}

.reco-cards {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.reco-card {
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-primary-subtle);
  border-left: 3px solid var(--color-primary);
}

.reco-card h4 {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-primary);
}

.reco-card__accion {
  font-size: 0.875rem;
  margin-top: 0.35rem;
  color: var(--color-text);
}

.reco-card__motivo {
  font-size: 0.78rem;
  color: var(--color-muted);
  margin-top: 0.25rem;
}

.footnote {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
}
</style>
