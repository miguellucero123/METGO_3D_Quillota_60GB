<script setup>
import { inject } from 'vue'
import { HardHat } from 'lucide-vue-next'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'

const site = inject('site')
const faenas = site.stations || []
</script>

<template>
  <div class="hub">
    <header>
      <ThemeToggle />
      <div class="brand">
        <HardHat :size="28" aria-hidden="true" />
        <div>
          <h1>{{ site.productName }} SPATI</h1>
          <p>Elija su faena — cada minera tiene enlace, reglas y suscripción propios.</p>
        </div>
      </div>
    </header>
    <ul class="list">
      <li v-for="f in faenas" :key="f.slug">
        <router-link :to="`/f/${f.slug}/`">
          <strong>{{ f.nombre }}</strong>
          <span>{{ f.region }} · {{ f.altitud_msnm }} m</span>
          <em>/f/{{ f.slug }}/</em>
        </router-link>
        <div class="actions">
          <router-link :to="`/f/${f.slug}/login`">Ingresar</router-link>
          <router-link :to="`/f/${f.slug}/registro`">Registrarse</router-link>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.hub {
  min-height: 100vh;
  padding: 1.5rem;
  background: var(--color-bg);
  color: var(--color-text);
}
header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}
.brand {
  display: flex;
  gap: 0.85rem;
  align-items: center;
}
.brand h1 { margin: 0; font-size: 1.35rem; }
.brand p { margin: 0.25rem 0 0; color: var(--color-muted); font-size: 0.9rem; }
.list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.65rem;
  max-width: 820px;
}
.list li {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 0.85rem 1rem;
  background: rgba(17, 24, 39, 0.55);
}
.list a { color: inherit; text-decoration: none; }
.list strong { display: block; }
.list span, .list em {
  display: block;
  font-size: 0.8rem;
  color: var(--color-muted);
  font-style: normal;
}
.actions {
  display: flex;
  gap: 0.75rem;
  font-size: 0.85rem;
  font-weight: 600;
}
.actions a { color: var(--color-primary); }
@media (max-width: 640px) {
  .list li { flex-direction: column; align-items: flex-start; }
}
</style>
