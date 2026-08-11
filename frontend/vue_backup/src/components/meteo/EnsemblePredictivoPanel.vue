<script setup>
import { ref, computed, onMounted } from 'vue'
import MeteogramaAvanzado from '@/components/charts/MeteogramaAvanzado.vue'
import { fetchEnsemble } from '@/api/metgoApi'

const ensembleData = ref([])
const loading = ref(true)
const error = ref(null)

const esDegradado = computed(() =>
  ensembleData.value.some((d) => d?.fuente === 'pronostico_degradado')
)

const loadEnsemble = async () => {
  loading.value = true
  error.value = null
  try {
    const data = await fetchEnsemble()
    if (!Array.isArray(data) || data.length === 0) {
      throw new Error('Sin datos de ensemble disponibles')
    }
    ensembleData.value = data
  } catch (err) {
    error.value =
      err?.message ||
      'El servicio de ensemble no está disponible temporalmente.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadEnsemble()
})
</script>

<template>
  <div class="ensemble-panel">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Calculando consenso de modelos globales...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button type="button" @click="loadEnsemble" class="btn-retry">Reintentar</button>
    </div>

    <div v-else class="ensemble-content">
      <p v-if="esDegradado" class="aviso-degradado">
        OpenMeteo multi-modelo no respondió desde el servidor; mostrando pronóstico
        de respaldo (dato real en caché/BD).
      </p>
      <MeteogramaAvanzado :ensembleData="ensembleData" />
    </div>
  </div>
</template>

<style scoped>
.ensemble-panel {
  width: 100%;
  min-height: 400px;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
}

.aviso-degradado {
  margin: 0 0 0.75rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
  color: var(--color-text-muted, #8a9a8e);
  border-left: 3px solid var(--color-primary);
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: var(--color-primary);
  text-align: center;
  padding: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(0, 255, 170, 0.1);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn-retry {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: var(--color-primary-muted);
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
  border-radius: 4px;
  cursor: pointer;
}
.btn-retry:hover {
  background: var(--color-primary);
  color: #fff;
}
</style>
