<template>
  <aside id="metgo-sidebar" class="metgo-sidebar" aria-label="Navegación principal">
    <nav>
      <p class="nav-section">Operaciones</p>
      <router-link
        v-for="item in operaciones"
        :key="item.to"
        :to="item.to"
        class="nav-item"
        active-class="nav-item--active"
      >
        <component :is="item.icon" :size="18" />
        <span>{{ item.label }}</span>
      </router-link>

      <p class="nav-section">Observatorio</p>
      <router-link
        v-for="item in observatorio"
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
import {
  Gauge,
  Clock3,
  SlidersHorizontal,
  Map,
  Waves,
  HardHat,
  Activity,
  Satellite,
  Thermometer,
  Wind,
  Layers,
  CloudSun,
} from 'lucide-vue-next'

const site = inject('site')

const operaciones = [
  { to: '/', label: 'Panel turno', icon: Gauge },
  { to: '/ventanas', label: 'Ventanas', icon: Clock3 },
  { to: '/umbrales', label: 'Umbrales', icon: SlidersHorizontal },
  { to: '/ambiente', label: 'Ambiente faena', icon: CloudSun },
]

const observatorio = [
  { to: '/mapa', label: 'Mapa', icon: Map },
  { to: '/dispersion', label: 'Dispersión', icon: Waves },
  { to: '/ventilacion', label: 'Ventilación N/R/M', icon: HardHat },
  { to: '/sounding', label: 'Sounding', icon: Activity },
  { to: '/satelite', label: 'Satélite', icon: Satellite },
  { to: '/olas-calor', label: 'Olas de calor', icon: Thermometer },
  { to: '/aire', label: 'Aire ICAP', icon: Wind },
  { to: '/airshed', label: 'Airshed', icon: Layers },
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
.nav-section {
  margin: 0.65rem 0 0.35rem;
  padding: 0 0.5rem;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-muted);
}
.nav-section:first-child {
  margin-top: 0;
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
