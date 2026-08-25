<script setup>
import { Moon, Sun } from 'lucide-vue-next'
import { useColorMode } from '@/composables/useColorMode'

const { theme, toggleTheme } = useColorMode()
</script>

<template>
  <button
    type="button"
    class="theme-toggle"
    :title="theme === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'"
    :aria-label="theme === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'"
    @click="toggleTheme"
  >
    <Sun v-if="theme === 'dark'" :size="18" aria-hidden="true" />
    <Moon v-else :size="18" aria-hidden="true" />
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
.theme-toggle:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}
</style>
