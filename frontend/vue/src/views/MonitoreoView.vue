<script setup>
import { ref, watch, onMounted } from 'vue'
import { BellRing, AlertTriangle, Info } from 'lucide-vue-next'
import { useMetgoStore } from '@/stores/metgo'
import SectionCard from '@/components/ui/SectionCard.vue'
import { fetchAlertas, fetchAlertasHistorial } from '@/api/metgoApi'

const store = useMetgoStore()
const alertas = ref([])
const historial = ref([])
const cargando = ref(true)

function iconFor(nivel) {
  if (nivel === 'warning') return AlertTriangle
  return Info
}

async function cargar() {
  cargando.value = true
  try {
    alertas.value = await fetchAlertas(store.estacionActiva)
    historial.value = await fetchAlertasHistorial(store.estacionActiva)
  } catch {
    alertas.value = []
    historial.value = []
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
      <h2 class="page-title">Alertas y monitoreo</h2>
      <p class="page-subtitle">
        Umbrales automáticos y personalizados · {{ store.estacionNombre }}
        · <router-link to="/alertas/config">Configurar reglas</router-link>
      </p>
    </header>

    <SectionCard
      title="Estado de alertas"
      :subtitle="`${alertas.length} notificación(es) activa(s)`"
    >
      <template #icon><BellRing /></template>
      <p v-if="cargando" class="skeleton">Cargando alertas…</p>
      <ul v-else-if="alertas.length" class="alert-grid">
        <li v-for="a in alertas" :key="a.id" :class="['alert-card', a.nivel]">
          <component :is="iconFor(a.nivel)" class="alert-card__icon" aria-hidden="true" />
          <div>
            <p class="alert-card__text">{{ a.mensaje }}</p>
            <span v-if="a.estacion_id" class="alert-card__meta">Estación: {{ a.estacion_id }}</span>
          </div>
        </li>
      </ul>
      <p v-else class="muted">No hay alertas registradas.</p>
    </SectionCard>

    <SectionCard
      title="Historial de alertas"
      :subtitle="`${historial.length} evento(s) · módulo 07`"
    >
      <ul v-if="historial.length" class="hist-list">
        <li v-for="(h, i) in historial" :key="i">
          <span class="hist-time">{{ h.timestamp || h.fecha }}</span>
          {{ h.mensaje || h.detalle || JSON.stringify(h) }}
        </li>
      </ul>
      <p v-else class="muted">Sin historial persistido.</p>
    </SectionCard>
  </div>
</template>

<style scoped>
.page {
  max-width: 900px;
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
