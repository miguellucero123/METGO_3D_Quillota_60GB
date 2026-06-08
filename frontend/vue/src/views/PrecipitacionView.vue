<script setup>
import { ref } from 'vue'
import { useMetgoStore } from '@/stores/metgo'
import PronosticoPrecipitacionAvanzado from '@/components/charts/PronosticoPrecipitacionAvanzado.vue'
import HistoricoPrecipitacionDetallado from '@/components/charts/HistoricoPrecipitacionDetallado.vue'
import VallePrecipMap from '@/components/maps/VallePrecipMap.vue'
import PronosticoHeladasPanel from '@/components/meteo/PronosticoHeladasPanel.vue'
import { fetchAlertasPrecipitacion } from '@/api/metgoApi'
import { onMounted, watch } from 'vue'

const store = useMetgoStore()
const tab = ref('pronostico')
const alertas = ref([])

async function cargarAlertas() {
  try {
    const res = await fetchAlertasPrecipitacion(store.estacionActiva)
    alertas.value = res.alertas_activas ?? []
  } catch {
    alertas.value = []
  }
}

onMounted(cargarAlertas)
watch(() => store.estacionActiva, cargarAlertas)
</script>

<template>
  <div class="page precip-page">
    <header class="page-header">
      <h2 class="page-title">Precipitación y heladas</h2>
      <p class="page-subtitle">
        Pronóstico calibrado, alertas agrícolas y mapa del valle · {{ store.estacionNombre }}
      </p>
      <label class="estacion-sel">
        Estación:
        <select v-model="store.estacionActiva">
          <option v-for="e in store.estaciones" :key="e.id" :value="e.id">{{ e.nombre }}</option>
        </select>
      </label>
    </header>

    <nav class="tabs">
      <button type="button" :class="{ active: tab === 'pronostico' }" @click="tab = 'pronostico'">Pronóstico</button>
      <button type="button" :class="{ active: tab === 'historico' }" @click="tab = 'historico'">Histórico</button>
      <button type="button" :class="{ active: tab === 'alertas' }" @click="tab = 'alertas'">Alertas</button>
      <button type="button" :class="{ active: tab === 'mapas' }" @click="tab = 'mapas'">Mapas</button>
      <button type="button" :class="{ active: tab === 'heladas' }" @click="tab = 'heladas'">Heladas</button>
    </nav>

    <section v-show="tab === 'pronostico'">
      <PronosticoPrecipitacionAvanzado />
    </section>
    <section v-show="tab === 'historico'">
      <HistoricoPrecipitacionDetallado />
    </section>
    <section v-show="tab === 'alertas'" class="alertas-sec">
      <div v-if="!alertas.length" class="sin-alertas">Sin alertas de precipitación activas</div>
      <article v-for="a in alertas" :key="a.id" class="alerta-card" :class="'sev-' + a.nivel_severidad">
        <h4>{{ a.cultivo }} — {{ a.tipo_alerta }}</h4>
        <p>{{ a.descripcion }}</p>
        <p class="mm">24h: {{ a.lluvia_24h_pronosticada }} mm · 48h: {{ a.lluvia_48h_pronosticada }} mm</p>
        <ul v-if="a.recomendaciones?.length">
          <li v-for="(r, i) in a.recomendaciones" :key="i">{{ r }}</li>
        </ul>
      </article>
    </section>
    <section v-show="tab === 'mapas'">
      <VallePrecipMap />
    </section>
    <section v-show="tab === 'heladas'">
      <PronosticoHeladasPanel />
    </section>
  </div>
</template>

<style scoped>
.precip-page { padding: 1rem 1.25rem; }
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
.alertas-sec { display: grid; gap: 0.65rem; }
.alerta-card {
  border: 1px solid #e5e7eb;
  border-left: 4px solid #f97316;
  border-radius: 8px;
  padding: 0.75rem;
  background: #fff;
}
.alerta-card.sev-rojo { border-left-color: #ef4444; background: #fef2f2; }
.alerta-card h4 { margin: 0 0 0.35rem; font-size: 0.9rem; }
.alerta-card .mm { font-size: 0.8rem; color: #4b5563; }
.sin-alertas { padding: 1.5rem; text-align: center; color: #10b981; font-weight: 600; }
</style>
