<script setup>
import { Moon, Sun } from 'lucide-vue-next'
import { usePreferencesStore } from '@/stores/preferences'

const prefs = usePreferencesStore()

function toggle() {
  prefs.setTheme(prefs.theme === 'dark' ? 'light' : 'dark')
}
</script>

<template>
  <button
    type="button"
    class="theme-toggle"
    :title="prefs.theme === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'"
    :aria-label="prefs.theme === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'"
    @click="toggle"
  >
    <Sun v-if="prefs.theme === 'dark'" aria-hidden="true" />
    <Moon v-else aria-hidden="true" />
  </button>
</template>

<style scoped>
.theme-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: var(--radius-sm, 8px);
  border: 1px solid var(--color-border);
  background: var(--color-surface-elevated);
  color: var(--color-text);
  cursor: pointer;
}
.theme-toggle :deep(svg) {
  width: 1.1rem;
  height: 1.1rem;
}
.theme-toggle:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}
</style>
