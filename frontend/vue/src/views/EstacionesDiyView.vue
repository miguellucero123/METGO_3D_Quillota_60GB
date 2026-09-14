<script setup>
import { computed, onMounted, ref } from 'vue'
import { MapPin, RefreshCw, Radio } from 'lucide-vue-next'
import SectionCard from '@/components/ui/SectionCard.vue'
import { useApiCall } from '@/composables/useApiCall'
import {
  fetchEstacionesDiy,
  fetchIotLecturas,
  simularEstacionesDiy,
} from '@/api/metgoApi'

const seleccion = ref(null)
const simMsg = ref('')
const simLoading = ref(false)

const {
  data: catalogo,
  loading: loadingCat,
  error: errorCat,
  run: cargarCatalogo,
} = useApiCall(fetchEstacionesDiy)

const {
  data: lecturas,
  loading: loadingLecturas,
  error: errorLecturas,
  run: cargarLecturas,
} = useApiCall(() => fetchIotLecturas(seleccion.value || undefined))

const estaciones = computed(() => catalogo.value?.estaciones || [])

const lecturasDiy = computed(() => {
  const rows = lecturas.value || []
  return rows.filter(
    (l) =>
      l.fuente === 'lora_diy' ||
      String(l.sensor_id || '').startsWith('lora-') ||
      (seleccion.value && l.estacion_id === seleccion.value)
  )
})

const ultimaPorTipo = computed(() => {
  const map = {}
  for (const l of lecturasDiy.value) {
    const t = l.tipo
    if (!map[t] || (l.timestamp || '') > (map[t].timestamp || '')) {
      map[t] = l
    }
  }
  return map
})

async function seleccionar(id) {
  seleccion.value = id
  await cargarLecturas()
}

async function simular() {
  simMsg.value = ''
  simLoading.value = true
  try {
    const est = estaciones.value.find((e) => e.id === seleccion.value)
    const res = await simularEstacionesDiy(est?.station_id || seleccion.value)
    simMsg.value = `Generadas ${res.lecturas_nuevas} lecturas (fuente=lora_diy)`
    await cargarCatalogo()
    await cargarLecturas()
  } catch (e) {
    simMsg.value = e.message || 'Error al simular'
  } finally {
    simLoading.value = false
  }
}

onMounted(async () => {
  await cargarCatalogo()
  if (estaciones.value.length) {
    seleccion.value = estaciones.value[0].id
  }
  await cargarLecturas()
})
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Estaciones LoRa DIY</h2>
      <p class="page-subtitle">
        Red Aconcagua · ESP32 + LoRa → MQTT → METGO
        <span class="badge badge--neutral">Fase 3.x</span>
      </p>
      <div class="header-actions">
        <button
          type="button"
          class="btn btn-sm btn-primary"
          :disabled="simLoading"
          @click="simular"
        >
          <RefreshCw /> Simular ronda DIY
        </button>
        <button type="button" class="btn btn-sm" :disabled="loadingCat" @click="cargarCatalogo">
          Actualizar catálogo
        </button>
      </div>
      <p v-if="simMsg" class="sync-msg">{{ simMsg }}</p>
    </header>

    <p v-if="loadingCat" class="muted">Cargando red…</p>
    <p v-else-if="errorCat" class="error-text">{{ errorCat }}</p>

    <div v-else class="grid-nodos">
      <button
        v-for="e in estaciones"
        :key="e.id"
        type="button"
        class="nodo"
        :class="{ 'nodo--activo': seleccion === e.id }"
        @click="seleccionar(e.id)"
      >
        <div class="nodo-top">
          <Radio :size="18" />
          <strong>{{ e.station_id }}</strong>
          <span class="estado" :data-estado="e.estado">{{ e.estado }}</span>
        </div>
        <p class="nodo-nombre">{{ e.nombre }}</p>
        <p class="nodo-meta">
          <MapPin :size="14" /> {{ e.lat }}, {{ e.lon }} · SF{{ e.lora_sf }} · {{ e.profile }}
        </p>
        <p class="nodo-meta">Lecturas recientes: {{ e.lecturas_recientes ?? 0 }}</p>
      </button>
    </div>

    <SectionCard
      title="Últimas variables"
      :subtitle="seleccion ? `Nodo ${seleccion}` : 'Seleccione un nodo'"
    >
      <template #icon><Radio /></template>
      <div v-if="Object.keys(ultimaPorTipo).length" class="kpis">
        <div v-for="(l, tipo) in ultimaPorTipo" :key="tipo" class="kpi">
          <span class="kpi-label">{{ tipo }}</span>
          <span class="kpi-valor">{{ l.valor }} {{ l.unidad }}</span>
        </div>
      </div>
      <p v-else class="muted">
        Sin lecturas DIY aún. Pulse «Simular ronda DIY» o espere ingesta desde el gateway.
      </p>
    </SectionCard>

    <SectionCard title="Historial (fuente lora_diy)">
      <p v-if="loadingLecturas" class="skeleton">Cargando…</p>
      <p v-else-if="errorLecturas" class="error-text">{{ errorLecturas }}</p>
      <table v-else-if="lecturasDiy.length" class="data-table">
        <thead>
          <tr>
            <th>Hora</th>
            <th>Sensor</th>
            <th>Tipo</th>
            <th>Valor</th>
            <th>Fuente</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="l in lecturasDiy" :key="l.id">
            <td>{{ l.timestamp?.slice(0, 19) }}</td>
            <td>{{ l.sensor_id }}</td>
            <td>{{ l.tipo }}</td>
            <td>{{ l.valor }} {{ l.unidad }}</td>
            <td>{{ l.fuente }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="muted">Sin filas para este nodo.</p>
    </SectionCard>
  </div>
</template>

<style scoped>
.header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
.sync-msg {
  font-size: 0.85rem;
  color: var(--color-success, #2d6a4f);
  margin-top: 0.35rem;
}
.grid-nodos {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.nodo {
  text-align: left;
  background: var(--color-surface, #0f1a24);
  border: 1px solid var(--color-border, #1b2d42);
  border-radius: 8px;
  padding: 0.85rem 1rem;
  color: inherit;
  cursor: pointer;
}
.nodo--activo {
  border-color: var(--color-accent, #3d9b72);
  box-shadow: 0 0 0 1px var(--color-accent, #3d9b72);
}
.nodo-top {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 0.35rem;
}
.nodo-nombre {
  margin: 0 0 0.35rem;
  font-size: 0.9rem;
}
.nodo-meta {
  margin: 0.15rem 0 0;
  font-size: 0.75rem;
  color: var(--color-muted, #6b83a0);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.estado {
  margin-left: auto;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  background: #1a2a3a;
}
.estado[data-estado='prototipo'] {
  color: #7ecfaa;
}
.estado[data-estado='planificado'] {
  color: #7eaaee;
}
.kpis {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.kpi {
  min-width: 7rem;
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
}
.kpi-label {
  display: block;
  font-size: 0.7rem;
  color: var(--color-muted, #6b83a0);
  text-transform: uppercase;
}
.kpi-valor {
  font-size: 1.15rem;
  font-weight: 600;
}
.data-table {
  width: 100%;
  font-size: 0.8rem;
  border-collapse: collapse;
}
.data-table th,
.data-table td {
  padding: 0.45rem 0.5rem;
  border-bottom: 1px solid var(--color-border);
  text-align: left;
}
.error-text {
  color: var(--color-danger, #b91c1c);
}
</style>
