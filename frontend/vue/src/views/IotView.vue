<script setup>
import { ref, onMounted } from 'vue'
import { Radio, RefreshCw } from 'lucide-vue-next'
import { useMetgoStore } from '@/stores/metgo'
import SectionCard from '@/components/ui/SectionCard.vue'
import { useApiCall } from '@/composables/useApiCall'
import {
  fetchIotLecturas,
  fetchIotSensores,
  simularIot,
  fetchIotDrones,
  fetchIotSatelital,
  fetchMqttStatus,
  ingestarMqtt,
} from '@/api/metgoApi'

const store = useMetgoStore()
const sensores = ref([])
const drones = ref(null)
const satelital = ref(null)
const mqttStatus = ref(null)
const mqttMsg = ref('')
const mqttValor = ref(20)

const { data: lecturas, loading, error, run } = useApiCall(() =>
  fetchIotLecturas(store.estacionActiva)
)

async function cargarSensores() {
  try {
    sensores.value = await fetchIotSensores()
  } catch {
    sensores.value = []
  }
}

async function refrescar() {
  await run()
}

async function simular() {
  await simularIot()
  await refrescar()
}

async function cargarExtras() {
  try {
    drones.value = await fetchIotDrones()
    satelital.value = await fetchIotSatelital()
  } catch {
    drones.value = null
    satelital.value = null
  }
}

async function cargarMqtt() {
  try {
    mqttStatus.value = await fetchMqttStatus()
  } catch {
    mqttStatus.value = null
  }
}

async function enviarMqtt() {
  mqttMsg.value = ''
  const topic = `metgo/${store.estacionActiva}/temperatura`
  try {
    await ingestarMqtt(topic, { valor: mqttValor.value })
    mqttMsg.value = 'Lectura MQTT registrada'
    await refrescar()
  } catch (e) {
    mqttMsg.value = e.message
  }
}

onMounted(async () => {
  await cargarSensores()
  await refrescar()
  await cargarExtras()
  await cargarMqtt()
})
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Sensores IoT</h2>
      <p class="page-subtitle">
        Lecturas propias (simuladas / API) · {{ store.estacionNombre }}
        <span class="badge badge--neutral">Fase 3 / 7</span>
      </p>
      <button type="button" class="btn btn-sm" :disabled="loading" @click="simular">
        <RefreshCw /> Nueva ronda simulada
      </button>
    </header>

    <SectionCard
      v-if="mqttStatus"
      title="Adaptador MQTT"
      :subtitle="mqttStatus.estado || '—'"
    >
      <p class="muted">{{ mqttStatus.modo_mvp }}</p>
      <p v-if="mqttStatus.inbox" class="muted">Inbox: {{ mqttStatus.inbox }}</p>
      <div class="mqtt-form">
        <label>
          Valor prueba (°C)
          <input v-model.number="mqttValor" type="number" step="0.1" class="input-sm" />
        </label>
        <button type="button" class="btn btn-sm btn-primary" @click="enviarMqtt">
          Ingestar vía REST
        </button>
      </div>
      <p v-if="mqttMsg" class="sync-msg">{{ mqttMsg }}</p>
    </SectionCard>

    <SectionCard title="Sensores registrados" :subtitle="`${sensores.length} dispositivo(s)`">
      <template #icon><Radio /></template>
      <ul class="sensor-list">
        <li v-for="s in sensores" :key="s.id">
          <strong>{{ s.id }}</strong> · {{ s.tipo }} · {{ s.ubicacion }}
        </li>
      </ul>
    </SectionCard>

    <SectionCard title="Últimas lecturas">
      <p v-if="loading" class="skeleton">Cargando…</p>
      <p v-else-if="error" class="error-text">{{ error }}</p>
      <table v-else-if="lecturas?.length" class="data-table">
        <thead>
          <tr>
            <th>Hora</th>
            <th>Sensor</th>
            <th>Valor</th>
            <th>Fuente</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="l in lecturas" :key="l.id">
            <td>{{ l.timestamp?.slice(0, 19) }}</td>
            <td>{{ l.sensor_id }}</td>
            <td>{{ l.valor }} {{ l.unidad }}</td>
            <td>{{ l.fuente }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="muted">Sin lecturas para esta estación.</p>
    </SectionCard>

    <SectionCard v-if="drones" title="Drones (módulo 03)" :subtitle="drones.resumen || 'Operaciones'">
      <p>Vuelos registrados: {{ drones.vuelos ?? 0 }}</p>
    </SectionCard>

    <SectionCard v-if="satelital" title="Datos satelitales">
      <p class="muted">{{ satelital.proveedor }} · capas: {{ (satelital.capas || []).join(', ') }}</p>
    </SectionCard>
  </div>
</template>

<style scoped>
.mqtt-form {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: flex-end;
  margin-top: 0.5rem;
}
.input-sm {
  width: 5rem;
  margin-left: 0.35rem;
}
.sync-msg {
  font-size: 0.85rem;
  color: var(--color-success, #2d6a4f);
}
.sensor-list {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 0.85rem;
}
.sensor-list li {
  padding: 0.35rem 0;
  border-bottom: 1px solid var(--color-border);
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
