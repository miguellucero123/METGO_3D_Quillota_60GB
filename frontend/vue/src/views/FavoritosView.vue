<script setup>
import { computed } from 'vue'
import { Star, MapPin } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useMetgoStore } from '@/stores/metgo'
import { useFavoritesStore } from '@/stores/favorites'
import SectionCard from '@/components/ui/SectionCard.vue'
import { formatTemperatura } from '@/utils/formatTemperatura'
import { usePreferencesStore } from '@/stores/preferences'

const router = useRouter()
const metgo = useMetgoStore()
const favorites = useFavoritesStore()
const prefs = usePreferencesStore()

const estacionesFav = computed(() =>
  metgo.estaciones.filter((e) => favorites.isFavorite(e.id))
)

function irEstacion(id) {
  metgo.estacionActiva = id
  metgo.cargarDatosMeteo()
  router.push('/meteo')
}
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Estaciones favoritas</h2>
      <p class="page-subtitle">Acceso rápido a parcelas del valle · Portafolio 7</p>
    </header>

    <SectionCard title="Mis estaciones" subtitle="Marque favoritas en Meteorología con la estrella">
      <template #icon><Star /></template>
      <p v-if="!estacionesFav.length" class="muted">
        Aún no tiene favoritas. Vaya a <router-link to="/meteo">Meteorología</router-link> y pulse ★.
      </p>
      <ul v-else class="fav-list">
        <li v-for="e in estacionesFav" :key="e.id" class="fav-item">
          <button type="button" class="fav-btn" @click="irEstacion(e.id)">
            <MapPin class="fav-icon" aria-hidden="true" />
            <span class="fav-name">{{ e.nombre }}</span>
            <span v-if="metgo.datosMeteo && metgo.estacionActiva === e.id" class="fav-meta">
              {{ formatTemperatura(metgo.datosMeteo.temperatura_max, prefs.tempUnit) }} máx
            </span>
          </button>
          <button
            type="button"
            class="fav-remove"
            title="Quitar de favoritos"
            @click="favorites.toggle(e.id)"
          >
            ★
          </button>
        </li>
      </ul>
    </SectionCard>
  </div>
</template>

<style scoped>
.fav-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.fav-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
}
.fav-btn {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 0.85rem;
  border: none;
  background: var(--color-surface);
  text-align: left;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.9rem;
}
.fav-btn:hover {
  background: var(--color-primary-muted);
}
.fav-icon {
  width: 1rem;
  height: 1rem;
  color: var(--color-primary);
}
.fav-name {
  font-weight: 600;
}
.fav-meta {
  margin-left: auto;
  font-size: 0.8rem;
  color: var(--color-muted);
}
.fav-remove {
  padding: 0.65rem 0.85rem;
  border: none;
  border-left: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-warning);
  cursor: pointer;
  font-size: 1.1rem;
}
</style>
