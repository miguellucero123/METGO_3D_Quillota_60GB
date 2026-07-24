<template>
  <aside class="metgo-sidebar">
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
import { inject } from 'vue'
import { Gauge, Clock3, SlidersHorizontal } from 'lucide-vue-next'

const site = inject('site')
const items = [
  { to: '/', label: 'Panel turno', icon: Gauge },
  { to: '/ventanas', label: 'Ventanas 48 h', icon: Clock3 },
  { to: '/umbrales', label: 'Umbrales', icon: SlidersHorizontal },
]
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
@media (max-width: 768px) {
  .metgo-sidebar {
    width: 100%;
    min-height: auto;
    flex-direction: row;
    flex-wrap: wrap;
    border-right: none;
    border-bottom: 1px solid var(--color-border);
  }
  .sidebar-foot { display: none; }
}
</style>
