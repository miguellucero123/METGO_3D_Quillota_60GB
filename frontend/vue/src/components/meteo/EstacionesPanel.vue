<script setup>
import { useRouter } from 'vue-router'
import { Star } from 'lucide-vue-next'
import { useMetgoStore } from '@/stores/metgo'
import { useFavoritesStore } from '@/stores/favorites'

const store = useMetgoStore()
const favorites = useFavoritesStore()
const router = useRouter()

function seleccionar(id) {
  store.estacionActiva = id
  store.cargarDatosMeteo()
  router.push('/meteo')
}
</script>

<template>
  <div class="card">
    <h3>Estaciones del valle</h3>
    <ul class="estaciones">
      <li v-for="e in store.estaciones" :key="e.id">
        <button type="button" class="est-btn" @click="seleccionar(e.id)">
          <span :class="{ activa: e.id === store.estacionActiva }">{{ e.nombre }}</span>
        </button>
        <button
          type="button"
          class="fav-btn"
          :class="{ 'fav-btn--on': favorites.isFavorite(e.id) }"
          :title="favorites.isFavorite(e.id) ? 'Quitar favorita' : 'Marcar favorita'"
          @click.stop="favorites.toggle(e.id)"
        >
          <Star aria-hidden="true" />
        </button>
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
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0;
}
.est-btn {
  flex: 1;
  border: none;
  background: none;
  text-align: left;
  padding: 0.25rem 0;
  font-family: inherit;
  font-size: 0.9rem;
  cursor: pointer;
  color: var(--color-text-secondary);
}
.est-btn:hover .activa,
.est-btn:hover span {
  color: var(--color-primary);
}
.activa {
  font-weight: 700;
  color: var(--color-primary);
}
.fav-btn {
  border: none;
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  padding: 0.15rem;
}
.fav-btn svg {
  width: 0.9rem;
  height: 0.9rem;
}
.fav-btn--on {
  color: var(--color-warning);
  fill: var(--color-warning);
}
</style>
