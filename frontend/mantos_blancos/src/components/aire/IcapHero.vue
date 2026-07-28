<template>
  <div class="icap-hero" :data-nivel="nivel || 'sin'">
    <div class="icap-valor">
      <span class="icap-num">{{ icapDisplay }}</span>
      <span class="icap-label">ICAP</span>
    </div>
    <div class="icap-meta">
      <p class="icap-cat">{{ etiqueta }}</p>
      <p v-if="rector" class="icap-rector">Rector: {{ rectorLabel }}</p>
      <ul v-if="recomendaciones?.length" class="icap-recs">
        <li v-for="(r, i) in recomendaciones" :key="i">{{ r }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  icap: { type: [Number, null], default: null },
  nivel: { type: String, default: null },
  etiqueta: { type: String, default: 'Sin datos' },
  contaminanteRector: { type: String, default: null },
  recomendaciones: { type: Array, default: () => [] },
})

const icapDisplay = computed(() =>
  props.icap == null || Number.isNaN(props.icap) ? '—' : Number(props.icap).toFixed(0)
)
const rectorLabel = computed(() => {
  const m = { pm2_5: 'PM2.5', pm10: 'PM10' }
  return m[props.contaminanteRector] || props.contaminanteRector
})
const rector = computed(() => props.contaminanteRector)
</script>

<style scoped>
.icap-hero {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: center;
  padding: 1.5rem;
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-left: 4px solid var(--color-primary);
}
.icap-hero[data-nivel='bueno'] { border-left-color: #10b981; }
.icap-hero[data-nivel='regular'] { border-left-color: #fb923c; }
.icap-hero[data-nivel='alerta'] { border-left-color: #f97316; }
.icap-hero[data-nivel='preemergencia'] { border-left-color: #ef4444; }
.icap-hero[data-nivel='emergencia'] { border-left-color: #7f1d1d; }

.icap-valor {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 100px;
}
.icap-num {
  font-size: 3rem;
  font-weight: 700;
  line-height: 1;
  color: var(--color-primary);
}
.icap-label {
  font-size: 0.8rem;
  color: var(--color-muted);
  letter-spacing: 0.08em;
}
.icap-cat {
  margin: 0 0 0.35rem;
  font-size: 1.35rem;
  font-weight: 600;
}
.icap-rector {
  margin: 0 0 0.75rem;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}
.icap-recs {
  margin: 0;
  padding-left: 1.1rem;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}
.icap-recs li { margin-bottom: 0.25rem; }
</style>
