<template>
  <div v-if="alerta.hay_alerta" class="alerta" :class="`nivel-${alerta.nivel_max || 'alerta'}`" role="alert">
    <div class="alerta-head">
      <span class="icono" aria-hidden="true">⚠️</span>
      <strong>Alerta de calidad del aire — {{ etiquetaNivel }}</strong>
    </div>
    <p class="alerta-detalle">
      {{ alerta.estaciones.length }}
      {{ alerta.estaciones.length === 1 ? 'estación supera' : 'estaciones superan' }}
      el umbral ICAP ({{ alerta.umbral }}):
      <span class="estaciones">{{ nombresEstaciones }}</span>
    </p>
    <ul v-if="recomendaciones.length" class="reco">
      <li v-for="(r, i) in recomendaciones" :key="i">{{ r }}</li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  alerta: {
    type: Object,
    default: () => ({ hay_alerta: false, estaciones: [], umbral: 200, nivel_max: null }),
  },
})

const ETIQUETAS = {
  alerta: 'Alerta',
  preemergencia: 'Preemergencia',
  emergencia: 'Emergencia',
}

const etiquetaNivel = computed(() => ETIQUETAS[props.alerta.nivel_max] || 'Alerta')

const nombresEstaciones = computed(() =>
  (props.alerta.estaciones || [])
    .map((e) => `${e.nombre} (ICAP ${Math.round(e.icap)})`)
    .join(' · ')
)

const recomendaciones = computed(() => {
  const peor = [...(props.alerta.estaciones || [])].sort((a, b) => b.icap - a.icap)[0]
  return peor?.recomendaciones || []
})
</script>

<style scoped>
.alerta {
  border-radius: 10px;
  padding: 1rem 1.15rem;
  margin-bottom: 1.25rem;
  border: 1px solid var(--color-warning, #f59e0b);
  background: rgba(245, 158, 11, 0.12);
}
.alerta.nivel-preemergencia {
  border-color: #f97316;
  background: rgba(249, 115, 22, 0.14);
}
.alerta.nivel-emergencia {
  border-color: var(--color-danger, #ef4444);
  background: rgba(239, 68, 68, 0.16);
}
.alerta-head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.05rem;
}
.alerta-detalle {
  margin: 0.5rem 0 0;
  font-size: 0.9rem;
}
.estaciones { color: var(--color-text-secondary); }
.reco {
  margin: 0.6rem 0 0;
  padding-left: 1.2rem;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}
.reco li { margin-bottom: 0.2rem; }
</style>
