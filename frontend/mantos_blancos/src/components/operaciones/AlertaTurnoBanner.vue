<template>
  <div
    v-if="alerta?.hay_bloqueo"
    class="alerta"
    role="alert"
  >
    <div class="alerta-head">
      <strong>Bloqueo operacional — turno {{ etiquetaTurno }}</strong>
    </div>
    <p class="alerta-detalle">
      {{ alerta.estaciones.filter((e) => e.nivel_global === 'rojo').length || alerta.estaciones.length }}
      punto(s) con actividad en rojo entre
      {{ formatearHora(alerta.desde) }} y {{ formatearHora(alerta.hasta) }}.
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  alerta: { type: Object, default: null },
  turno: { type: String, default: 'dia' },
})

const etiquetaTurno = computed(() => (props.turno === 'noche' ? 'noche (19–07)' : 'día (07–19)'))

function formatearHora(iso) {
  if (!iso) return '—'
  return String(iso).slice(11, 16)
}
</script>

<style scoped>
.alerta {
  border-radius: 10px;
  padding: 1rem 1.15rem;
  margin-bottom: 1.25rem;
  border: 1px solid var(--color-danger);
  background: var(--color-danger-bg);
}
.alerta-head { font-size: 1.05rem; margin-bottom: 0.35rem; }
.alerta-detalle { margin: 0; font-size: 0.9rem; color: var(--color-text-secondary); }
</style>
