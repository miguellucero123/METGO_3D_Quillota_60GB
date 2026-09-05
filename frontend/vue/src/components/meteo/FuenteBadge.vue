<script setup>
import { computed } from 'vue'

const props = defineProps({
  fuente: { type: String, default: '' },
})

const normalizado = computed(() => {
  const f = String(props.fuente || '').toLowerCase()
  if (f.includes('dmc') || f.includes('meteochile')) return 'dmc'
  if (f.includes('agromet') || f.includes('inia')) return 'agromet'
  if (f.includes('openmeteo') || f.includes('open-meteo') || f.includes('om_')) return 'openmeteo'
  if (f.includes('lastgood') || f.includes('cache') || f.includes('supabase')) return 'cache'
  if (f.includes('sinca')) return 'sinca'
  return f || ''
})

const label = computed(() => {
  const map = {
    dmc: 'DMC (observado)',
    agromet: 'Agromet (observado)',
    openmeteo: 'Open-Meteo',
    cache: 'Caché / store',
    sinca: 'SINCA',
  }
  return map[normalizado.value] || props.fuente || '—'
})

const badgeClass = computed(() => {
  if (normalizado.value === 'dmc' || normalizado.value === 'agromet') return 'badge badge--observado'
  if (normalizado.value === 'openmeteo') return 'badge badge--pronostico'
  return 'badge badge--neutral'
})
</script>

<template>
  <span v-if="fuente" :class="badgeClass" :title="`fuente: ${fuente}`">
    {{ label }}
  </span>
</template>
