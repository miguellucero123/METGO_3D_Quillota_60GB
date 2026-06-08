<script setup>
import { ref, watch } from 'vue'
import { useMetgoStore } from '@/stores/metgo'
import { fetchVariablesMeteoCompletas } from '@/api/metgoApi'
import { exportarDatosCSV } from '@/utils/exportData'

const store = useMetgoStore()
const cargando = ref(false)
const datos = ref([])

async function cargar() {
  cargando.value = true
  try {
    const res = await fetchVariablesMeteoCompletas(store.estacionActiva, 7)
    datos.value = res.datos ?? []
  } catch {
    datos.value = []
  } finally {
    cargando.value = false
  }
}

watch(() => store.estacionActiva, cargar, { immediate: true })

function fmt(f) {
  return new Date(f).toLocaleDateString('es-CL', { weekday: 'short', day: 'numeric', month: 'short' })
}

function exportCsv() {
  const rows = datos.value.map((d) => ({
    fecha: d.fecha,
    temp_max: d.temperatura?.maxima_celsius,
    temp_min: d.temperatura?.minima_celsius,
    punto_rocio: d.temperatura?.punto_rocio_celsius,
    humedad: d.humedad?.relativa_porcentaje,
    nubosidad: d.nubosidad?.cobertura_porcentaje,
    radiacion_wm2: d.radiacion_solar?.global_superficie_wm2,
    visibilidad_km: d.visibilidad?.horizontal_km,
    riesgo_helada: d.indices_agricolas?.riesgo_helada_radiativa,
    riesgo_niebla: d.indices_agricolas?.riesgo_niebla,
  }))
  exportarDatosCSV(rows, `variables_${store.estacionActiva}`)
}
</script>

<template>
  <div class="vars-panel">
    <header class="vars-panel__head">
      <h3>Variables meteorológicas completas (15+)</h3>
      <button type="button" class="btn-export" :disabled="!datos.length" @click="exportCsv">Exportar CSV</button>
    </header>
    <div v-if="cargando" class="loading">Cargando…</div>
    <div v-else-if="datos.length" class="table-wrap">
      <table class="tabla">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>T° máx/mín</th>
            <th>HR</th>
            <th>Nubes</th>
            <th>Radiación</th>
            <th>Visibilidad</th>
            <th>Helada</th>
            <th>Niebla</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(d, i) in datos" :key="i">
            <td>{{ fmt(d.fecha) }}</td>
            <td>{{ d.temperatura?.maxima_celsius }} / {{ d.temperatura?.minima_celsius }}°C</td>
            <td>{{ d.humedad?.relativa_porcentaje }}%</td>
            <td>{{ d.nubosidad?.cobertura_porcentaje }}%</td>
            <td>{{ d.radiacion_solar?.global_superficie_wm2 }} W/m²</td>
            <td>{{ d.visibilidad?.horizontal_km }} km</td>
            <td>{{ d.indices_agricolas?.riesgo_helada_radiativa }}</td>
            <td>{{ d.indices_agricolas?.riesgo_niebla }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="empty">Sin datos de variables completas</p>
  </div>
</template>

<style scoped>
.vars-panel { background: #fff; border-radius: 8px; padding: 1rem; }
.vars-panel__head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
.vars-panel__head h3 { margin: 0; font-size: 1rem; }
.btn-export { font-size: 0.75rem; padding: 0.35rem 0.65rem; border-radius: 6px; border: 1px solid #e5e7eb; cursor: pointer; }
.tabla { width: 100%; border-collapse: collapse; font-size: 0.78rem; }
.tabla th, .tabla td { padding: 0.45rem; border-bottom: 1px solid #e5e7eb; text-align: left; }
.table-wrap { overflow-x: auto; }
.loading, .empty { text-align: center; padding: 1.5rem; color: #6b7280; }
</style>
