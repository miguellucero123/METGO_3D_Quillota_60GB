<script setup>
import { computed, inject, provide, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAccess } from '@/stores/access'
import { getToken } from '@/services/authApi'

const site = inject('site')
const route = useRoute()
const access = useAccess()
const puerto = computed(() => String(route.params.puerto || '').toLowerCase())
const faenaMeta = computed(
  () => (site.stations || []).find((s) => s.slug === puerto.value) || { slug: puerto.value, nombre: puerto.value },
)
provide('faena', puerto) // keep injection key identical for underlying components
provide('faenaMeta', faenaMeta)

watch(
  puerto,
  (p) => {
    if (p && getToken() && !route.meta?.public) access.refresh(p)
  },
  { immediate: true },
)

const show = (tab) => access.canTab(puerto.value, tab)
const isPreview = computed(() => {
  const snap = access.snapshot(puerto.value)
  return Boolean(snap?.preview || snap?.plan_code === 'preview')
})
</script>

<template>
  <div class="puerto-shell">
    <nav v-if="!$route.meta.public" class="puerto-nav" aria-label="Puerto">
      <router-link
        v-if="show('panel')"
        :to="{ name: 'puerto-dashboard', params: { puerto } }"
        :class="{ 'router-link-active': $route.name === 'puerto-dashboard' }"
      >Panel Marítimo</router-link>
      <!-- Funcionalidades en desarrollo (Rutas aún no definidas) -->
      <!--
      <router-link
        v-if="show('panel') && !isPreview"
        :to="{ name: 'puerto-informes', params: { puerto } }"
        :class="{ 'router-link-active': $route.name === 'puerto-informes' }"
      >Informes</router-link>
      <router-link v-if="show('umbrales')" :to="{ name: 'puerto-umbrales', params: { puerto } }">Umbrales</router-link>
      -->
    </nav>
    <router-view />
  </div>
</template>

<style scoped>
.puerto-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 0.65rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(8px);
  font-size: 0.85rem;
}
.puerto-nav a {
  color: var(--color-muted);
  text-decoration: none;
  font-weight: 600;
}
.puerto-nav a.router-link-active {
  color: var(--color-primary);
}
</style>
