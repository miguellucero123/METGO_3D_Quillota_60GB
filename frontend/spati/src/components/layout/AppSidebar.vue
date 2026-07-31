<template>
  <aside id="metgo-sidebar" class="metgo-sidebar" aria-label="Navegación SPATI">
    <nav>
      <router-link
        v-for="item in items"
        :key="item.name || item.to"
        :to="item.to"
        class="nav-item"
        :class="{ 'nav-item--active': isActive(item) }"
      >
        <component :is="item.icon" :size="18" />
        <span>{{ item.label }}</span>
      </router-link>
    </nav>
    <p class="sidebar-foot">{{ site.region }}</p>
  </aside>
</template>

<script setup>
import { computed, inject, watch, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Wind, Plane, SlidersHorizontal, CloudSun, CreditCard, LayoutGrid, Gauge, MapPinned, FileText } from 'lucide-vue-next'
import { useAccess } from '@/stores/access'
import { fetchMe, getToken } from '@/services/authApi'

const site = inject('site')
const route = useRoute()
const access = useAccess()
const faena = computed(() => String(route.params.faena || site.spatiDefaultSitio || 'escondida'))
const showHubLink = ref(false)

watch(
  faena,
  (f) => {
    if (f && getToken()) access.refresh(f)
  },
  { immediate: true },
)

onMounted(async () => {
  if (!getToken()) return
  try {
    const me = await fetchMe()
    showHubLink.value = Boolean(me.catalogo_completo || me.multi_faena || (me.faenas || []).length > 1)
  } catch {
    showHubLink.value = false
  }
})

function isActive(item) {
  if (item.name) return route.name === item.name
  const path = String(item.to || '')
  return route.path === path || route.path === path.replace(/\/$/, '')
}

const items = computed(() => {
  const f = faena.value
  const all = [
    {
      name: 'faena-ahora',
      to: { name: 'faena-ahora', params: { faena: f } },
      label: 'Ahora',
      icon: MapPinned,
      tab: 'ahora',
    },
    {
      name: 'faena-panel',
      to: { name: 'faena-panel', params: { faena: f } },
      label: 'Panel técnico',
      icon: Wind,
      tab: 'panel',
    },
    {
      name: 'faena-informes',
      to: { name: 'faena-informes', params: { faena: f } },
      label: 'Informes',
      icon: FileText,
      tab: 'panel',
    },
    {
      name: 'faena-ambiente',
      to: { name: 'faena-ambiente', params: { faena: f } },
      label: 'Ambiente faena',
      icon: CloudSun,
      tab: 'ambiente',
    },
    {
      name: 'faena-dron',
      to: { name: 'faena-dron', params: { faena: f } },
      label: 'Calibración dron',
      icon: Plane,
      tab: 'dron',
    },
    {
      name: 'faena-umbrales',
      to: { name: 'faena-umbrales', params: { faena: f } },
      label: 'Umbrales',
      icon: SlidersHorizontal,
      tab: 'umbrales',
    },
    {
      name: 'faena-cuenta',
      to: { name: 'faena-cuenta', params: { faena: f } },
      label: 'Cuenta',
      icon: CreditCard,
    },
  ]
  if (showHubLink.value) {
    all.push({ to: '/ops', label: 'Ops multi-faena', icon: Gauge, name: 'ops-board' })
    all.push({ to: '/app', label: 'Mis faenas', icon: LayoutGrid, name: 'faenas-hub' })
  }
  return all.filter((item) => !item.tab || access.canTab(f, item.tab))
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
