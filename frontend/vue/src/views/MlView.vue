<script setup>
import { ref, computed, onMounted } from 'vue'
import { Cpu, Sparkles, RefreshCw, CheckCircle, XCircle } from 'lucide-vue-next'
import { useMetgoStore } from '@/stores/metgo'
import SectionCard from '@/components/ui/SectionCard.vue'
import { useApiCall } from '@/composables/useApiCall'
import {
  fetchMlModelos,
  fetchMlPrediccion,
  fetchMlResumen,
  syncMlRegistry,
  fetchMlTrainStatus,
  encolarMlTrain,
  ejecutarMlTrainSiguiente,
  entrenarMlQuillota,
  fetchWorkersStatus,
} from '@/api/metgoApi'

const store = useMetgoStore()
const variable = ref('temperatura_max')
const prediccion = ref(null)
const resumen = ref(null)
const predError = ref('')
const filtro = ref('todos') // todos | servibles | no_servibles
const syncMsg = ref('')
const syncing = ref(false)
const trainStatus = ref(null)
const trainMsg = ref('')
const workers = ref(null)
const entrenando = ref(false)

const { data: modelos, loading, error, run } = useApiCall(() => fetchMlModelos(false))

const modelosFiltrados = computed(() => {
  const list = modelos.value || []
  if (filtro.value === 'servibles') return list.filter((m) => m.servible)
  if (filtro.value === 'no_servibles') return list.filter((m) => !m.servible)
  return list
})

const modelosServibles = computed(() => (modelos.value || []).filter((m) => m.servible))

async function cargarCola() {
  try {
    trainStatus.value = await fetchMlTrainStatus()
  } catch {
    trainStatus.value = null
  }
}

async function cargarWorkers() {
  try {
    workers.value = await fetchWorkersStatus()
  } catch {
    workers.value = null
  }
}

async function encolarSync(modo = 'sync') {
  trainMsg.value = ''
  try {
    await encolarMlTrain([], store.estacionActiva, 'desde Vue', modo)
    trainMsg.value = modo === 'train' ? 'Entrenamiento encolado' : 'Sync encolado'
    await cargarCola()
  } catch (e) {
    trainMsg.value = e.message
  }
}

async function entrenarAhora() {
  entrenando.value = true
  trainMsg.value = ''
  try {
    const r = await entrenarMlQuillota(store.estacionActiva)
    trainMsg.value = `Entrenados: ${r.entrenados} (${r.origen_datos}) · servibles ${r.registry_servibles}`
    await cargarTodo()
  } catch (e) {
    trainMsg.value = e.message
  } finally {
    entrenando.value = false
  }
}

async function ejecutarCola() {
  trainMsg.value = ''
  try {
    const r = await ejecutarMlTrainSiguiente()
    trainMsg.value = r.ok ? 'Cola procesada (sync registro)' : r.error || 'Sin pendientes'
    await cargarCola()
    await cargarTodo()
  } catch (e) {
    trainMsg.value = e.message
  }
}

async function cargarTodo() {
  await run()
  try {
    resumen.value = await fetchMlResumen()
  } catch {
    resumen.value = null
  }
  await cargarCola()
  await cargarWorkers()
  if (modelosServibles.value.length && !modelosServibles.value.find((m) => m.variable === variable.value)) {
    variable.value = modelosServibles.value[0].variable
  }
}

async function sincronizarRegistro() {
  syncing.value = true
  syncMsg.value = ''
  try {
    const reg = await syncMlRegistry()
    syncMsg.value = `Registro actualizado: ${reg.servibles}/${reg.total} servibles`
    await cargarTodo()
  } catch (e) {
    syncMsg.value = e.message
  } finally {
    syncing.value = false
  }
}

async function predecir() {
  predError.value = ''
  prediccion.value = null
  try {
    prediccion.value = await fetchMlPrediccion(variable.value, store.estacionActiva)
  } catch (e) {
    predError.value = e.message
  }
}

onMounted(() => cargarTodo())
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Modelos ML</h2>
      <p class="page-subtitle">
        Registro MLOps · {{ store.estacionNombre }}
        <span class="badge badge--neutral">Fase 3.2 / 8</span>
      </p>
      <div class="header-actions">
        <button type="button" class="btn btn-sm" :disabled="loading || syncing" @click="cargarTodo">
          <RefreshCw /> Recargar
        </button>
        <button type="button" class="btn btn-sm btn-primary" :disabled="syncing" @click="sincronizarRegistro">
          <RefreshCw :class="{ spin: syncing }" /> Sincronizar registro
        </button>
      </div>
      <p v-if="syncMsg" class="sync-msg">{{ syncMsg }}</p>
    </header>

    <SectionCard
      v-if="trainStatus"
      title="Cola entrenamiento (MVP)"
      :subtitle="`${trainStatus.pendientes} pendiente(s)`"
    >
      <p class="muted">
        Cada trabajo ejecuta sincronización del registro MLOps (no entrena modelos pesados en la petición).
      </p>
      <div class="header-actions">
        <button type="button" class="btn btn-sm" @click="encolarSync('sync')">Encolar sync</button>
        <button type="button" class="btn btn-sm" @click="encolarSync('train')">Encolar train</button>
        <button type="button" class="btn btn-sm btn-primary" :disabled="entrenando" @click="entrenarAhora">
          Entrenar ahora (admin)
        </button>
        <button type="button" class="btn btn-sm" @click="ejecutarCola">Ejecutar cola</button>
      </div>
      <p v-if="workers" class="muted">
        Workers: MQTT {{ workers.mqtt_listener?.estado || '—' }} · ML {{ workers.ml_training?.estado || '—' }}
      </p>
      <p v-if="trainMsg" class="sync-msg">{{ trainMsg }}</p>
    </SectionCard>

    <SectionCard
      v-if="resumen"
      title="Registro MLOps"
      :subtitle="`${resumen.servibles ?? resumen.disponibles}/${resumen.total_modelos} servibles · actualizado ${resumen.actualizado || '—'}`"
    >
      <template #icon><Cpu /></template>
      <p class="muted">
        Solo los modelos <strong>servibles</strong> pasaron sanity-check (carga + dimensiones + predicción de prueba).
      </p>
    </SectionCard>

    <SectionCard title="Catálogo de modelos">
      <div class="filtros">
        <label>
          Mostrar
          <select v-model="filtro">
            <option value="todos">Todos</option>
            <option value="servibles">Solo servibles</option>
            <option value="no_servibles">No servibles</option>
          </select>
        </label>
        <span class="muted">{{ modelosFiltrados.length }} modelo(s)</span>
      </div>
      <p v-if="loading" class="skeleton">Cargando…</p>
      <p v-else-if="error" class="error-text">{{ error }}</p>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Variable</th>
              <th>Paquete</th>
              <th>R²</th>
              <th>Archivo</th>
              <th>Features</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in modelosFiltrados" :key="m.id || `${m.paquete}-${m.archivo}`">
              <td>{{ m.variable }}</td>
              <td><code>{{ m.paquete }}</code></td>
              <td>{{ m.r2 != null ? m.r2.toFixed(3) : '—' }}</td>
              <td class="archivo">{{ m.archivo }}</td>
              <td>{{ m.n_features ?? (m.features?.length || '—') }}</td>
              <td>
                <span v-if="m.servible" class="estado ok">
                  <CheckCircle size="14" /> Servible
                </span>
                <span v-else class="estado no" :title="m.motivo_no_servible">
                  <XCircle size="14" /> No servible
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <details v-if="modelosFiltrados.some((m) => !m.servible)" class="motivos">
        <summary>Motivos modelos no servibles</summary>
        <ul>
          <li v-for="m in modelosFiltrados.filter((x) => !x.servible)" :key="'m-' + m.archivo">
            <strong>{{ m.archivo }}</strong> — {{ m.motivo_no_servible || 'sin detalle' }}
          </li>
        </ul>
      </details>
    </SectionCard>

    <SectionCard title="Predicción (solo modelos servibles)">
      <template #icon><Sparkles /></template>
      <div class="pred-form">
        <label>
          Variable
          <select v-model="variable">
            <option v-for="m in modelosServibles" :key="m.variable" :value="m.variable">
              {{ m.variable }} ({{ m.paquete }})
            </option>
          </select>
        </label>
        <button
          type="button"
          class="btn btn-primary"
          :disabled="!modelosServibles.length"
          @click="predecir"
        >
          Predecir
        </button>
      </div>
      <p v-if="!modelosServibles.length" class="muted">
        No hay modelos servibles. Pulse «Sincronizar registro» o revise dependencias sklearn/joblib.
      </p>
      <p v-if="predError" class="error-text">{{ predError }}</p>
      <p v-else-if="prediccion" class="pred-result">
        Predicción <strong>{{ prediccion.prediccion }}</strong>
        · modelo <code>{{ prediccion.modelo }}</code>
        <span v-if="prediccion.r2_entrenamiento != null">
          · R² train {{ prediccion.r2_entrenamiento.toFixed(3) }}
        </span>
        <span v-if="prediccion.modo_prediccion"> · {{ prediccion.modo_prediccion }}</span>
        <span v-if="prediccion.usa_scaler"> · con scaler</span>
      </p>
    </SectionCard>
  </div>
</template>

<style scoped>
.header-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 0.5rem;
}
.sync-msg {
  font-size: 0.8rem;
  color: var(--color-muted);
  margin-top: 0.35rem;
}
.filtros {
  display: flex;
  align-items: flex-end;
  gap: 1rem;
  margin-bottom: 0.75rem;
}
.filtros label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8rem;
}
.table-wrap {
  overflow-x: auto;
}
.data-table {
  width: 100%;
  font-size: 0.75rem;
  border-collapse: collapse;
}
.data-table th,
.data-table td {
  padding: 0.45rem 0.5rem;
  border-bottom: 1px solid var(--color-border);
  text-align: left;
}
.archivo {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.estado {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.72rem;
  font-weight: 600;
}
.estado.ok {
  color: var(--color-success);
}
.estado.no {
  color: var(--color-danger, #b91c1c);
}
.motivos {
  margin-top: 0.75rem;
  font-size: 0.75rem;
}
.motivos ul {
  margin: 0.5rem 0 0;
  padding-left: 1.2rem;
}
.pred-form {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
  flex-wrap: wrap;
}
.pred-form label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8rem;
}
.pred-result {
  margin-top: 0.75rem;
}
.error-text {
  color: var(--color-danger, #b91c1c);
}
.muted {
  color: var(--color-muted);
  font-size: 0.8rem;
}
.spin {
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
