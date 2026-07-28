<script setup>
import { computed } from 'vue'

const props = defineProps({
  tipo: { type: String, default: '' },
})

const normalizado = computed(() => {
  const t = String(props.tipo || '').toLowerCase()
  if (t.includes('observ')) return 'observado'
  if (t.includes('pronost') || t.includes('forecast')) return 'pronostico'
  if (t.includes('model') || t.includes('cams') || t.includes('reanal')) return 'modelo'
  return t || ''
})

const label = computed(() => {
  if (normalizado.value === 'observado') return 'Observado'
  if (normalizado.value === 'pronostico') return 'Pronóstico'
  if (normalizado.value === 'modelo') return 'Modelo'
  return props.tipo || '—'
})

const badgeClass = computed(() => {
  if (normalizado.value === 'observado') return 'badge badge--observado'
  if (normalizado.value === 'pronostico') return 'badge badge--pronostico'
  if (normalizado.value === 'modelo') return 'badge badge--modelo'
  return 'badge badge--neutral'
})
</script>

<template>
  <span v-if="normalizado" :class="badgeClass" :title="`tipo_dato: ${tipo}`">
    {{ label }}
  </span>
</template>
