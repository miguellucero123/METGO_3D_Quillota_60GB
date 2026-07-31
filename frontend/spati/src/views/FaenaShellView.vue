<script setup>
import { computed, inject, provide, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAccess } from '@/stores/access'
import { getToken } from '@/services/authApi'

const site = inject('site')
const route = useRoute()
const access = useAccess()
const faena = computed(() => String(route.params.faena || '').toLowerCase())
const faenaMeta = computed(
  () => (site.stations || []).find((s) => s.slug === faena.value) || { slug: faena.value, nombre: faena.value },
)
provide('faena', faena)
provide('faenaMeta', faenaMeta)

watch(
  faena,
  (f) => {
    if (f && getToken() && !route.meta?.public) access.refresh(f)
  },
  { immediate: true },
)

const show = (tab) => access.canTab(faena.value, tab)
const isPreview = computed(() => {
  const snap = access.snapshot(faena.value)
  return Boolean(snap?.preview || snap?.plan_code === 'preview')
})
</script>

<template>
  <div class="faena-shell">
    <nav v-if="!$route.meta.public" class="faena-nav" aria-label="Faena">
      <router-link
        v-if="show('ahora') || show('panel')"
        :to="{ name: 'faena-ahora', params: { faena } }"
        :class="{ 'router-link-active': $route.name === 'faena-ahora' }"
      >Ahora</router-link>
      <router-link
        v-if="show('panel')"
        :to="{ name: 'faena-panel', params: { faena } }"
        :class="{ 'router-link-active': $route.name === 'faena-panel' }"
      >Panel técnico</router-link>
      <router-link
        v-if="show('panel') && !isPreview"
        :to="{ name: 'faena-informes', params: { faena } }"
        :class="{ 'router-link-active': $route.name === 'faena-informes' }"
      >Informes</router-link>
      <router-link v-if="show('ambiente')" :to="{ name: 'faena-ambiente', params: { faena } }">Ambiente</router-link>
      <router-link v-if="show('dron')" :to="{ name: 'faena-dron', params: { faena } }">Dron</router-link>
      <router-link v-if="show('umbrales')" :to="{ name: 'faena-umbrales', params: { faena } }">Umbrales</router-link>
    </nav>
    <router-view />
  </div>
</template>

<style scoped>
.faena-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 0.65rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(8px);
  font-size: 0.85rem;
}
.faena-nav a {
  color: var(--color-muted);
  text-decoration: none;
  font-weight: 600;
}
.faena-nav a.router-link-active {
  color: var(--color-primary);
}
</style>
