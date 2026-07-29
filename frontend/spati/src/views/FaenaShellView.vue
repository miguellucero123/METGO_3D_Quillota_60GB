<script setup>
import { computed, inject, provide } from 'vue'
import { useRoute } from 'vue-router'

const site = inject('site')
const route = useRoute()
const faena = computed(() => String(route.params.faena || '').toLowerCase())
const faenaMeta = computed(
  () => (site.stations || []).find((s) => s.slug === faena.value) || { slug: faena.value, nombre: faena.value },
)
provide('faena', faena)
provide('faenaMeta', faenaMeta)
</script>

<template>
  <div class="faena-shell">
    <nav v-if="!$route.meta.public" class="faena-nav" aria-label="Faena">
      <router-link :to="`/f/${faena}/`">{{ faenaMeta.nombre || faena }}</router-link>
      <router-link :to="`/f/${faena}/ambiente`">Ambiente</router-link>
      <router-link :to="`/f/${faena}/dron`">Dron</router-link>
      <router-link :to="`/f/${faena}/umbrales`">Umbrales</router-link>
      <router-link :to="`/f/${faena}/cuenta`">Cuenta</router-link>
      <router-link to="/">Todas</router-link>
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
  background: rgba(17, 24, 39, 0.7);
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
