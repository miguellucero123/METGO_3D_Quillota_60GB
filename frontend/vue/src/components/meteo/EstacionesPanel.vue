<script setup>
import { useMetgoStore } from '@/stores/metgo'

const store = useMetgoStore()
</script>

<template>
  <div class="card">
    <h3>Estaciones soportadas</h3>
    <ul class="estaciones">
      <li v-for="e in store.estaciones" :key="e.id">
        <span :class="{ activa: e.id === store.estacionActiva }">{{ e.nombre }}</span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.estaciones {
  list-style: none;
  margin-top: 0.75rem;
}
.estaciones li {
  padding: 0.35rem 0;
}
.activa {
  font-weight: 700;
  color: var(--metgo-primary);
}
</style>
