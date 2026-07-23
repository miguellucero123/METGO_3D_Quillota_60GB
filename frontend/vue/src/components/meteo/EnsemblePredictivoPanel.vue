<script setup>
import { ref, onMounted } from 'vue'
import MeteogramaAvanzado from '@/components/charts/MeteogramaAvanzado.vue'
import { fetchEnsemble } from '@/api/metgoApi'

const ensembleData = ref([])
const loading = ref(true)
const error = ref(null)

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
      'El servicio de ensemble (OpenMeteo) no está disponible temporalmente.'
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
