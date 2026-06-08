<script setup>
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  LayoutDashboard,
  CloudSun,
  CloudRain,
  Sprout,
  BellRing,
  Server,
  Grid3x3,
  Settings,
  Monitor,
  Activity,
  History,
  GitCompare,
  Gauge,
  SlidersHorizontal,
  Radio,
  Cpu,
  Link2,
  Star,
  UserCog,
} from 'lucide-vue-next'

const links = [
  { to: '/', label: 'Panel general', icon: LayoutDashboard },
  { to: '/estado', label: 'Estado sistema', icon: Activity },
  { to: '/integracion', label: 'Conexiones', icon: Link2 },
  { to: '/favoritos', label: 'Favoritos', icon: Star, requiresAuth: true },
  { to: '/preferencias', label: 'Preferencias', icon: UserCog, requiresAuth: true },
  { to: '/metricas', label: 'Métricas globales', icon: Gauge },
  { to: '/iot', label: 'Sensores IoT', icon: Radio },
  { to: '/ml', label: 'Modelos ML', icon: Cpu },
  { to: '/meteo', label: 'Meteorología', icon: CloudSun },
  { to: '/meteo/precipitacion', label: 'Precipitación', icon: CloudRain },
  { to: '/meteo/historico', label: 'Histórico meteo', icon: History },
  { to: '/meteo/comparativo', label: 'Visualizaciones', icon: GitCompare },
  { to: '/agricola', label: 'Gestión agrícola', icon: Sprout },
  { to: '/monitoreo', label: 'Alertas', icon: BellRing },
  { to: '/alertas/config', label: 'Config. alertas', icon: SlidersHorizontal },
  { to: '/puertos', label: 'Visor de puertos', icon: Monitor },
  { to: '/servicios', label: 'Centro de servicios', icon: Server },
  { to: '/modulos', label: 'Catálogo', icon: Grid3x3 },
  { to: '/configuracion', label: 'Configuración', icon: Settings },
]

const auth = useAuthStore()

const linksVisibles = links.filter((link) => !link.requiresAuth || auth.isAuthenticated)
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar__brand">
      <span class="sidebar__mark">M</span>
      <span class="sidebar__name">METGO</span>
    </div>
    <nav class="sidebar__nav">
      <RouterLink
        v-for="link in linksVisibles"
        :key="link.to"
        :to="link.to"
        class="nav-link"
        active-class="active"
      >
        <component :is="link.icon" class="nav-link__icon" aria-hidden="true" />
        <span>{{ link.label }}</span>
      </RouterLink>
    </nav>
    <footer class="sidebar__footer">
      <span>Valle de Aconcagua</span>
      <span class="sidebar__ver">v1.0 · Quillota</span>
    </footer>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 240px;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 1.25rem 1.25rem 1rem;
  border-bottom: 1px solid var(--color-border);
}

.sidebar__mark {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: #fff;
  font-size: 0.85rem;
  font-weight: 700;
  border-radius: var(--radius-md);
}

.sidebar__name {
  font-weight: 600;
  font-size: 0.95rem;
  letter-spacing: 0.06em;
  color: var(--color-text);
}

.sidebar__nav {
  padding: 0.75rem 0.65rem;
  flex: 1;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.65rem 0.85rem;
  margin-bottom: 0.2rem;
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: var(--radius-md);
  transition: background 0.12s, color 0.12s;
}

.nav-link__icon {
  width: 1.125rem;
  height: 1.125rem;
  stroke-width: 1.75;
  opacity: 0.85;
}

.nav-link:hover {
  background: var(--color-primary-muted);
  color: var(--color-primary);
}

.nav-link.active {
  background: var(--color-primary-muted);
  color: var(--color-primary);
  font-weight: 600;
}

.nav-link.active .nav-link__icon {
  opacity: 1;
}

.sidebar__footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--color-border);
  font-size: 0.7rem;
  color: var(--color-muted);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.sidebar__ver {
  opacity: 0.75;
}
</style>
