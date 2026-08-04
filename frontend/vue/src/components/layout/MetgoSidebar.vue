<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  LayoutDashboard,
  CloudSun,
  CloudRain,
  CloudFog,
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
  ChevronDown,
  Database,
  Wrench,
  Layers,
  Home,
} from 'lucide-vue-next'

const STORAGE_KEY = 'metgo_sidebar_groups_v2'

const auth = useAuthStore()
const route = useRoute()

const gruposDef = [
  {
    id: 'principal',
    label: 'Principal',
    icon: Home,
    match: (path) =>
      path === '/' ||
      path.startsWith('/estado') ||
      path.startsWith('/metricas') ||
      path.startsWith('/favoritos'),
    items: [
      { to: '/app', label: 'Panel general', icon: LayoutDashboard, exact: true },
      { to: '/estado', label: 'Estado sistema', icon: Activity },
      { to: '/metricas', label: 'Métricas globales', icon: Gauge },
      { to: '/favoritos', label: 'Favoritos', icon: Star, requiresAuth: true },
    ],
  },
  {
    id: 'meteo',
    label: 'Meteorología',
    icon: CloudSun,
    match: (path) =>
      path === '/meteo' ||
      path.startsWith('/meteo/precipitacion') ||
      path.startsWith('/meteo/avanzado') ||
      path.startsWith('/meteo/historico'),
    items: [
      { to: '/meteo', label: 'Meteorología', icon: CloudSun, exact: true },
      { to: '/meteo/precipitacion', label: 'Precipitación', icon: CloudRain },
      { to: '/meteo/avanzado', label: 'Meteo avanzada', icon: CloudFog },
      { to: '/meteo/historico', label: 'Histórico meteo', icon: History },
    ],
  },
  {
    id: 'datos',
    label: 'Datos y modelos',
    icon: Database,
    match: (path) =>
      path.startsWith('/iot') ||
      path.startsWith('/ml') ||
      path.startsWith('/meteo/comparativo'),
    items: [
      { to: '/iot', label: 'Sensores IoT', icon: Radio },
      { to: '/ml', label: 'Modelos ML', icon: Cpu },
      { to: '/meteo/comparativo', label: 'Visualizaciones', icon: GitCompare },
    ],
  },
  {
    id: 'ops',
    label: 'Operaciones',
    icon: Sprout,
    match: (path) =>
      path.startsWith('/agricola') ||
      path.startsWith('/monitoreo') ||
      path.startsWith('/alertas'),
    items: [
      { to: '/agricola', label: 'Gestión agrícola', icon: Sprout },
      { to: '/monitoreo', label: 'Alertas', icon: BellRing },
      { to: '/alertas/config', label: 'Config. alertas', icon: SlidersHorizontal },
    ],
  },
  {
    id: 'sistema',
    label: 'Sistema',
    icon: Layers,
    match: (path) =>
      path.startsWith('/integracion') ||
      path.startsWith('/puertos') ||
      path.startsWith('/servicios') ||
      path.startsWith('/modulos'),
    items: [
      { to: '/integracion', label: 'Conexiones', icon: Link2 },
      { to: '/puertos', label: 'Visor de puertos', icon: Monitor },
      { to: '/servicios', label: 'Centro de servicios', icon: Server },
      { to: '/modulos', label: 'Catálogo', icon: Grid3x3 },
    ],
  },
  {
    id: 'cuenta',
    label: 'Cuenta',
    icon: Wrench,
    match: (path) =>
      path.startsWith('/preferencias') || path.startsWith('/configuracion'),
    items: [
      { to: '/preferencias', label: 'Preferencias', icon: UserCog, requiresAuth: true },
      { to: '/configuracion', label: 'Configuración', icon: Settings },
    ],
  },
]

const grupos = computed(() =>
  gruposDef
    .map((g) => ({
      ...g,
      items: g.items.filter((link) => !link.requiresAuth || auth.isAuthenticated),
    }))
    .filter((g) => g.items.length > 0)
)

function loadOpenState() {
  const defaults = {
    principal: true,
    meteo: false,
    datos: false,
    ops: false,
    sistema: false,
    cuenta: false,
  }
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      if (parsed && typeof parsed === 'object') {
        return { ...defaults, ...parsed }
      }
    }
  } catch {
    /* ignore */
  }
  return defaults
}

const openGroups = ref(loadOpenState())

function persistOpen() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(openGroups.value))
  } catch {
    /* ignore */
  }
}

function toggleGroup(id) {
  const actualmente = Boolean(openGroups.value[id])
  openGroups.value = {
    ...openGroups.value,
    [id]: !actualmente,
  }
  persistOpen()
}

function isGroupOpen(id) {
  return Boolean(openGroups.value[id])
}

/** Solo al cambiar de ruta: abrir el grupo de la página actual. */
function ensureActiveGroupOpen() {
  const path = route.path
  let activeId = null
  for (const g of gruposDef) {
    if (g.match(path)) {
      activeId = g.id
      break
    }
  }
  if (!activeId) return
  const next = { ...openGroups.value }
  for (const g of gruposDef) {
    next[g.id] = g.id === activeId
  }
  openGroups.value = next
  persistOpen()
}

watch(
  () => route.path,
  (path, prev) => {
    if (path !== prev) ensureActiveGroupOpen()
  },
  { immediate: true }
)

function linkIsActive(link) {
  const path = route.path
  if (link.exact) return path === link.to
  if (link.to === '/') return path === '/'
  return path === link.to || path.startsWith(`${link.to}/`)
}
</script>

<template>
  <aside id="metgo-sidebar" class="sidebar" aria-label="Navegación principal">
    <div class="sidebar__brand">
      <span class="sidebar__mark">M</span>
      <span class="sidebar__name">METGO</span>
    </div>

    <nav class="sidebar__nav">
      <div
        v-for="grupo in grupos"
        :key="grupo.id"
        class="nav-group"
        :class="{
          'nav-group--open': isGroupOpen(grupo.id),
          'nav-group--active': grupo.match(route.path),
          'nav-group--cuenta': grupo.id === 'cuenta',
        }"
      >
        <button
          type="button"
          class="nav-group__header"
          :aria-expanded="isGroupOpen(grupo.id)"
          :aria-controls="`nav-group-${grupo.id}`"
          @click.stop.prevent="toggleGroup(grupo.id)"
        >
          <component :is="grupo.icon" class="nav-group__icon" aria-hidden="true" />
          <span class="nav-group__label">{{ grupo.label }}</span>
          <ChevronDown class="nav-group__chevron" aria-hidden="true" />
        </button>
        <div
          v-show="isGroupOpen(grupo.id)"
          :id="`nav-group-${grupo.id}`"
          class="nav-group__body"
        >
          <RouterLink
            v-for="link in grupo.items"
            :key="link.to"
            :to="link.to"
            class="nav-link nav-link--nested"
            :class="{ active: linkIsActive(link) }"
          >
            <component :is="link.icon" class="nav-link__icon" aria-hidden="true" />
            <span>{{ link.label }}</span>
          </RouterLink>
        </div>
      </div>
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
  min-height: 0;
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
  padding: 0.65rem 0.55rem;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.nav-group {
  border-radius: var(--radius-md);
}

.nav-group--cuenta {
  margin-top: auto;
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-border);
}

.nav-group--active .nav-group__header {
  color: var(--color-primary);
}

.nav-group__header {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.55rem 0.7rem;
  margin: 0;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: background 0.12s, color 0.12s;
}

.nav-group__header:hover {
  background: var(--color-primary-muted);
  color: var(--color-primary);
}

.nav-group__icon {
  width: 1rem;
  height: 1rem;
  stroke-width: 1.85;
  opacity: 0.9;
  flex-shrink: 0;
}

.nav-group__label {
  flex: 1;
  text-align: left;
}

.nav-group__chevron {
  width: 0.95rem;
  height: 0.95rem;
  opacity: 0.65;
  transition: transform 0.18s ease;
  flex-shrink: 0;
}

.nav-group--open .nav-group__chevron {
  transform: rotate(180deg);
}

.nav-group__body {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  padding: 0.1rem 0 0.35rem 0.15rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.55rem 0.85rem;
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: var(--radius-md);
  transition: background 0.12s, color 0.12s;
}

.nav-link--nested {
  padding-left: 1.15rem;
  font-size: 0.84rem;
}

.nav-link__icon {
  width: 1.125rem;
  height: 1.125rem;
  stroke-width: 1.75;
  opacity: 0.85;
  flex-shrink: 0;
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

@media (max-width: 900px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    z-index: 40;
    width: min(280px, 88vw);
    transform: translateX(-105%);
    transition: transform 0.22s ease;
    box-shadow: var(--shadow-lg);
  }
  :global(.app-shell--nav-open) .sidebar {
    transform: translateX(0);
  }
}
</style>
