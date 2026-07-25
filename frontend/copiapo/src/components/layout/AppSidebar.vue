<template>
  <aside id="metgo-sidebar" class="metgo-sidebar" aria-label="Navegación principal">
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
import { Wind, CalendarRange, History, Waves, Map, Layers, HardHat, Activity, Satellite, Thermometer, ChartLine } from 'lucide-vue-next'

const site = inject('site')
const items = [
  { to: '/', label: 'Panel ICAP', icon: Wind },
  { to: '/mapa', label: 'Mapa', icon: Map },
  { to: '/dispersion', label: 'Dispersión', icon: Waves },
  { to: '/operaciones', label: 'Paipote N/R/M', icon: HardHat },
  { to: '/conjunto', label: 'Variables', icon: ChartLine },
  { to: '/airshed', label: 'Modelo airshed', icon: Layers },
  { to: '/sounding', label: 'Sounding', icon: Activity },
  { to: '/satelite', label: 'Satélite', icon: Satellite },
  { to: '/olas-calor', label: 'Olas de calor', icon: Thermometer },
  { to: '/pronostico', label: 'Pronóstico', icon: CalendarRange },
  { to: '/historico', label: 'Histórico', icon: History },
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
