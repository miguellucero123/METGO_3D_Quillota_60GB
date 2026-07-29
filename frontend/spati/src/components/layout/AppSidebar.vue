<template>
  <aside id="metgo-sidebar" class="metgo-sidebar" aria-label="Navegación SPATI">
    <nav>
      <router-link
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="nav-item"
        active-class="nav-item--active"
      >
        <component :is="item.icon" :size="18" />
        <span>{{ item.label }}</span>
      </router-link>
    </nav>
    <p class="sidebar-foot">{{ site.region }}</p>
  </aside>
</template>

<script setup>
import { computed, inject } from 'vue'
import { useRoute } from 'vue-router'
import { Wind, Plane, SlidersHorizontal, CloudSun, CreditCard, LayoutGrid } from 'lucide-vue-next'

const site = inject('site')
const route = useRoute()
const faena = computed(() => String(route.params.faena || site.spatiDefaultSitio || 'escondida'))

const items = computed(() => {
  const f = faena.value
  return [
    { to: `/f/${f}/`, label: 'Pronóstico 72 h', icon: Wind },
    { to: `/f/${f}/ambiente`, label: 'Ambiente faena', icon: CloudSun },
    { to: `/f/${f}/dron`, label: 'Calibración dron', icon: Plane },
    { to: `/f/${f}/umbrales`, label: 'Umbrales', icon: SlidersHorizontal },
    { to: `/f/${f}/cuenta`, label: 'Cuenta', icon: CreditCard },
    { to: '/', label: 'Todas las faenas', icon: LayoutGrid },
  ]
})
</script>

<style scoped>
.metgo-sidebar {
  width: 220px;
  flex-shrink: 0;
  padding: 1rem 0.75rem;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-height: calc(100vh - 64px);
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-weight: 500;
  margin-bottom: 0.35rem;
}
.nav-item:hover {
  background: var(--color-primary-subtle);
  color: var(--color-text);
}
.nav-item--active {
  background: var(--color-primary-muted);
  color: var(--color-primary);
}
.sidebar-foot {
  margin-top: auto;
  font-size: 0.75rem;
  color: var(--color-muted);
  padding: 0 0.5rem;
}
@media (max-width: 900px) {
  .metgo-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    z-index: 40;
    width: min(280px, 88vw);
    min-height: 100vh;
    transform: translateX(-105%);
    transition: transform 0.22s ease;
    box-shadow: var(--shadow-lg);
  }
  :global(.app-shell--nav-open) .metgo-sidebar {
    transform: translateX(0);
  }
}
</style>
