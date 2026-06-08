<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { BellRing, AlertTriangle, Info, Activity, Radio } from 'lucide-vue-next'
import { useMetgoStore } from '@/stores/metgo'
import MetricCard from '@/components/ui/MetricCard.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import HorizontalBarChart from '@/components/charts/HorizontalBarChart.vue'
import {
  fetchAlertas,
  fetchAlertasHistorial,
  fetchComparativo,
  fetchIotSensores,
} from '@/api/metgoApi'
import { hoyChile } from '@/utils/meteoDates'

const store = useMetgoStore()
const alertas = ref([])
const historial = ref([])
const comparativo = ref([])
const sensores = ref([])
const ambito = ref('estacion')
const cargando = ref(true)

function iconFor(nivel) {
  if (nivel === 'warning') return AlertTriangle
  return Info
}

const alertasFiltradas = computed(() => {
  const list = alertas.value || []
  if (ambito.value === 'valle') return list
  return list.filter(
    (a) => !a.estacion_id || a.estacion_id === store.estacionActiva
  )
})

const conteo = computed(() => {
  const w = alertasFiltradas.value.filter((a) => a.nivel === 'warning').length
  const i = alertasFiltradas.value.filter((a) => a.nivel !== 'warning').length
  return { warning: w, info: i, total: alertasFiltradas.value.length }
})

const labelsEst = computed(() => comparativo.value.map((r) => r.estacion))
const tempsMax = computed(() => comparativo.value.map((r) => r.temperatura_max))

async function cargar() {
  cargando.value = true
  try {
    const [a, h, c, s] = await Promise.all([
      fetchAlertas(ambito.value === 'valle' ? null : store.estacionActiva),
      fetchAlertasHistorial(store.estacionActiva),
      fetchComparativo(),
      fetchIotSensores().catch(() => []),
    ])
    alertas.value = a
    historial.value = h
    comparativo.value = c
    sensores.value = Array.isArray(s) ? s : s?.sensores || []
  } catch {
    alertas.value = []
    historial.value = []
    comparativo.value = []
    sensores.value = []
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
watch(() => store.estacionActiva, cargar)
watch(ambito, cargar)
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Alertas y monitoreo</h2>
      <p class="page-subtitle">
        Umbrales automáticos · {{ store.estacionNombre }} · {{ hoyChile() }}
        ·
        <router-link to="/alertas/config">Configurar reglas</router-link>
        ·
        <router-link to="/iot">Sensores IoT</router-link>
      </p>
      <div class="page-meta">
        <label class="inline-select">
          Alertas:
          <select v-model="ambito">
            <option value="estacion">Estación activa</option>
            <option value="valle">Todo el valle</option>
          </select>
        </label>
      </div>
    </header>

    <div class="card-grid">
      <MetricCard label="Alertas activas" :value="conteo.total">
        <template #icon><BellRing /></template>
      </MetricCard>
      <MetricCard
        label="Nivel warning"
        :value="conteo.warning"
        variant="warning"
      >
        <template #icon><AlertTriangle /></template>
      </MetricCard>
      <MetricCard label="Informativas" :value="conteo.info">
        <template #icon><Info /></template>
      </MetricCard>
      <MetricCard label="Sensores IoT" :value="sensores.length || '—'">
        <template #icon><Radio /></template>
      </MetricCard>
    </div>

    <SectionCard
      v-if="comparativo.length"
      title="Condiciones por estación (hoy)"
      subtitle="Referencia para monitoreo multi-zona"
    >
      <template #icon><Activity /></template>
      <HorizontalBarChart :labels="labelsEst" :values="tempsMax" unit="°C" kind="temp" />
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Estación</th>
              <th>T° máx</th>
              <th>T° mín</th>
              <th>Lluvia</th>
              <th>Viento</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in comparativo" :key="r.estacion_id">
              <td>{{ r.estacion }}</td>
              <td>{{ r.temperatura_max }}°C</td>
              <td>{{ r.temperatura_min }}°C</td>
              <td>{{ r.precipitacion }} mm</td>
              <td>{{ r.viento }} km/h</td>
            </tr>
          </tbody>
        </table>
      </div>
    </SectionCard>

    <SectionCard
      title="Estado de alertas"
      :subtitle="`${alertasFiltradas.length} notificación(es)`"
    >
      <template #icon><BellRing /></template>
      <p v-if="cargando" class="skeleton">Cargando alertas…</p>
      <ul v-else-if="alertasFiltradas.length" class="alert-grid">
        <li
          v-for="a in alertasFiltradas"
          :key="a.id"
          :class="['alert-card', a.nivel === 'warning' ? 'warning' : 'info']"
        >
          <component :is="iconFor(a.nivel)" class="alert-card__icon" aria-hidden="true" />
          <div>
            <p class="alert-card__text">{{ a.mensaje }}</p>
            <span v-if="a.estacion_id" class="alert-card__meta">{{ a.estacion_id }}</span>
          </div>
        </li>
      </ul>
      <p v-else class="muted">No hay alertas para el filtro seleccionado.</p>
    </SectionCard>

    <SectionCard
      title="Historial de alertas"
      :subtitle="`${historial.length} evento(s) · ${store.estacionNombre}`"
    >
      <ul v-if="historial.length" class="hist-list">
        <li v-for="(h, i) in historial" :key="i">
          <span class="hist-time">{{ h.timestamp || h.fecha }}</span>
          {{ h.mensaje || h.detalle || '—' }}
        </li>
      </ul>
      <p v-else class="muted">Sin historial persistido para esta estación.</p>
    </SectionCard>
  </div>
</template>

<style scoped>
.page {
  max-width: 1100px;
}

.page-meta {
  margin-top: 0.5rem;
}

.inline-select {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--color-muted);
}

.inline-select select {
  padding: 0.3rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-family: inherit;
}

.table-wrap {
  margin-top: 1rem;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}

.data-table th,
.data-table td {
  padding: 0.45rem 0.6rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.alert-grid {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.alert-card {
  display: flex;
  gap: 0.85rem;
  padding: 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
}

.alert-card.warning {
  background: var(--color-warning-bg);
  border-color: transparent;
}

.alert-card.info {
  background: var(--color-info-bg);
  border-color: transparent;
}

.alert-card__icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
  color: var(--color-primary);
}

.alert-card.warning .alert-card__icon {
  color: var(--color-warning);
}

.alert-card__text {
  font-size: 0.9rem;
  color: var(--color-text);
}

.alert-card__meta {
  font-size: 0.72rem;
  color: var(--color-muted);
  margin-top: 0.25rem;
  display: block;
}

.hist-list {
  list-style: none;
  padding: 0;
  font-size: 0.8rem;
}

.hist-list li {
  padding: 0.4rem 0;
  border-bottom: 1px solid var(--color-border);
}

.hist-time {
  display: block;
  font-size: 0.7rem;
  color: var(--color-muted);
}
</style>
