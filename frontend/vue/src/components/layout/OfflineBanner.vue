<script setup>
import { useOnline } from '@/composables/useOnline'
import { useI18n } from 'vue-i18n'

const { online } = useOnline()
const { t } = useI18n()
</script>

<template>
  <div
    v-if="!online"
    class="offline-banner"
    role="status"
    aria-live="polite"
  >
    {{ t('app.offline') }}
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
