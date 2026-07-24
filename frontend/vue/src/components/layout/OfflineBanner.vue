<script setup>
import { useOnline } from '@/composables/useOnline'

const { online } = useOnline()
</script>

<template>
  <div
    v-if="!online"
    class="offline-banner"
    role="status"
    aria-live="polite"
  >
    Sin conexión — mostrando datos en caché cuando estén disponibles.
  </div>
</template>

<style scoped>
.offline-banner {
  background: var(--color-warning-bg);
  color: var(--color-warning);
  border-bottom: 1px solid var(--color-border);
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  text-align: center;
  font-weight: 500;
}
</style>
