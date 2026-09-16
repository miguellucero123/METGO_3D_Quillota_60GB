<template>
  <div class="mjo-widget card">
    <header class="widget-head">
      <h3>Pronóstico Extendido (20-90 días)</h3>
      <span class="badge mjo-badge">MJO_Chile</span>
    </header>

    <div v-if="loading" class="loading">Cargando pronóstico extendido...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="data && data.disponible === false" class="no-disponible">
      <p>Índice MJO real no disponible en este momento (fuente NOAA/PSL sin respuesta y sin caché previa). No se muestra un valor estimado.</p>
    </div>
    <div v-else-if="data" class="mjo-content">
      <div class="mjo-phase-display">
        <div class="phase-circle">
          <span class="phase-label">Fase {{ data.fase_mjo }}</span>
        </div>
        <div class="phase-details">
          <p><strong>Amplitud:</strong> {{ data.amplitud_mjo }}</p>
          <p><strong>Bloqueo Anticiclónico:</strong> {{ (data.probabilidad_bloqueo_anticiclonico * 100).toFixed(0) }}%</p>
        </div>
      </div>

      <div class="impacts">
        <div class="impact-item">
          <span class="icon">💨</span>
          <div>
            <h4>Impacto Viento</h4>
            <p>{{ data.impacto_viento }}</p>
          </div>
        </div>
        <div class="impact-item">
          <span class="icon">🌊</span>
          <div>
            <h4>Impacto Oleaje</h4>
            <p>{{ data.impacto_oleaje }}</p>
          </div>
        </div>
      </div>

      <div class="recommendation">
        <h4>Recomendación Estratégica</h4>
        <p>{{ data.recomendacion_estrategica }}</p>
      </div>

      <p class="fuente-footer">
        Fuente: índice real ROMI (NOAA/PSL{{ data.fecha_indice ? ', dato del ' + data.fecha_indice : '' }}){{ data.desde_cache ? ' — desde caché local' : '' }}.
        {{ data.nota_metodologica }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { fetchSpatiExtendidoMjo } from '@/services/spatiApi'

const props = defineProps({
  sitioId: {
    type: String,
    required: true
  }
})

const data = ref(null)
const loading = ref(true)
const error = ref('')

async function fetchMjoData() {
  loading.value = true
  error.value = ''
  try {
    data.value = await fetchSpatiExtendidoMjo(props.sitioId)
  } catch (e) {
    error.value = 'No se pudo cargar el pronóstico extendido.'
  } finally {
    loading.value = false
  }
}

watch(() => props.sitioId, fetchMjoData)
onMounted(fetchMjoData)
</script>

<style scoped>
.mjo-widget {
  background: var(--color-surface, #111827);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
}
.widget-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.widget-head h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--color-text);
}
.mjo-badge {
  background: #8b5cf6;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: bold;
}
.mjo-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.mjo-phase-display {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}
.phase-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: conic-gradient(from 0deg, #3b82f6, #8b5cf6, #ec4899, #3b82f6);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.phase-label {
  background: #111827;
  color: white;
  padding: 0.5rem;
  border-radius: 50%;
  font-weight: bold;
  font-size: 0.9rem;
}
.phase-details p {
  margin: 0.25rem 0;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}
.impacts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.impact-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  padding: 0.75rem;
  border-radius: 8px;
}
.impact-item .icon {
  font-size: 1.5rem;
}
.impact-item h4 {
  margin: 0 0 0.25rem;
  font-size: 0.9rem;
  color: var(--color-text);
}
.impact-item p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--color-muted);
}
.recommendation {
  background: rgba(139, 92, 246, 0.1);
  border-left: 4px solid #8b5cf6;
  padding: 1rem;
  border-radius: 0 8px 8px 0;
}
.recommendation h4 {
  margin: 0 0 0.5rem;
  color: #a78bfa;
  font-size: 0.95rem;
}
.recommendation p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-text);
}
.loading, .error, .no-disponible {
  text-align: center;
  padding: 2rem;
  color: var(--color-muted);
}
.error {
  color: #f87171;
}
.fuente-footer {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-muted, #9ca3af);
  line-height: 1.4;
}
</style>
