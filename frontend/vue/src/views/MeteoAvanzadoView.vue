<script setup>
import { ref } from 'vue'
import { useMetgoStore } from '@/stores/metgo'
import PronosticoHeladaAvanzado from '@/components/charts/PronosticoHeladaAvanzado.vue'
import AnalizadorNubosidad from '@/components/charts/AnalizadorNubosidad.vue'
import PredictorNiebla from '@/components/charts/PredictorNiebla.vue'
import MapasMeteoGlobales from '@/components/maps/MapasMeteoGlobales.vue'
import VariablesCompletasPanel from '@/components/meteo/VariablesCompletasPanel.vue'
import ComparacionModelosChart from '@/components/charts/ComparacionModelosChart.vue'

const store = useMetgoStore()
const tab = ref('helada')
</script>

<template>
  <div class="page meteo-av">
    <header class="page-header">
      <h2 class="page-title">Meteorología avanzada</h2>
      <p class="page-subtitle">
        Heladas radiativas, nubosidad, nieblas y mapas · {{ store.estacionNombre }}
      </p>
      <label class="estacion-sel">
        Estación:
        <select v-model="store.estacionActiva">
          <option v-for="e in store.estaciones" :key="e.id" :value="e.id">{{ e.nombre }}</option>
        </select>
      </label>
    </header>

    <nav class="tabs">
      <button type="button" :class="{ active: tab === 'helada' }" @click="tab = 'helada'">Heladas</button>
      <button type="button" :class="{ active: tab === 'nubosidad' }" @click="tab = 'nubosidad'">Nubosidad</button>
      <button type="button" :class="{ active: tab === 'niebla' }" @click="tab = 'niebla'">Nieblas</button>
      <button type="button" :class="{ active: tab === 'variables' }" @click="tab = 'variables'">Variables 15+</button>
      <button type="button" :class="{ active: tab === 'mapas' }" @click="tab = 'mapas'">Mapas</button>
      <button type="button" :class="{ active: tab === 'modelos' }" @click="tab = 'modelos'">Modelos</button>
    </nav>

    <section v-show="tab === 'helada'"><PronosticoHeladaAvanzado /></section>
    <section v-show="tab === 'nubosidad'"><AnalizadorNubosidad /></section>
    <section v-show="tab === 'niebla'"><PredictorNiebla /></section>
    <section v-show="tab === 'variables'"><VariablesCompletasPanel /></section>
    <section v-show="tab === 'mapas'"><MapasMeteoGlobales /></section>
    <section v-show="tab === 'modelos'"><ComparacionModelosChart /></section>
  </div>
</template>

<style scoped>
.meteo-av { padding: 1rem 1.25rem; }
.page-subtitle { color: #6b7280; margin: 0.25rem 0 0.75rem; }
.estacion-sel { font-size: 0.85rem; }
.estacion-sel select { margin-left: 0.35rem; padding: 0.25rem 0.5rem; border-radius: 6px; }
.tabs { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 1rem; border-bottom: 1px solid #e5e7eb; padding-bottom: 0.5rem; }
.tabs button {
  padding: 0.45rem 0.85rem;
  border: none;
  background: transparent;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-size: 0.85rem;
  color: #6b7280;
}
.tabs button.active { color: #0284c7; border-bottom-color: #0284c7; }
</style>
