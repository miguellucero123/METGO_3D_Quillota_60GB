<script setup>
import { ref, computed, watch } from 'vue'
import { useMetgoStore } from '@/stores/metgo'
import { fetchPrecipitacionHistorico } from '@/api/metgoApi'
import { precipColor } from '@/utils/colorScale'
import { exportarDatosCSV } from '@/utils/exportData'

const store = useMetgoStore()
const diasRango = ref(30)
const cargando = ref(false)
const datos = ref([])
const estadisticas = ref(null)

async function cargar() {
  cargando.value = true
  const hasta = new Date()
  const desde = new Date()
  desde.setDate(desde.getDate() - diasRango.value)
  try {
    const res = await fetchPrecipitacionHistorico(
      store.estacionActiva,
      desde.toISOString().slice(0, 10),
      hasta.toISOString().slice(0, 10)
    )
    datos.value = res.datos ?? []
    estadisticas.value = res.estadisticas ?? null
  } catch {
    datos.value = []
    estadisticas.value = null
  } finally {
    cargando.value = false
  }
}

watch(() => store.estacionActiva, cargar, { immediate: true })
watch(diasRango, cargar)

const maxP = computed(() => Math.max(1, ...datos.value.map((d) => d.precipitacion)))

function fmt(f) {
  return new Date(f).toLocaleDateString('es-CL', { month: 'short', day: 'numeric' })
}
</script>

<template>
  <div class="hist-precip">
    <div class="hist-precip__ctrl">
      <div class="rango">
        <button v-for="d in [7, 30, 90]" :key="d" type="button" :class="{ active: diasRango === d }" @click="diasRango = d">
          {{ d }}d
        </button>
      </div>
      <button type="button" @click="exportarDatosCSV(datos, `hist_precip_${store.estacionActiva}`)">CSV</button>
    </div>

    <div v-if="cargando" class="loading">Cargando histórico…</div>
    <svg v-else viewBox="0 0 100 60" class="chart">
      <rect
        v-for="(d, i) in datos"
        :key="d.fecha"
        :x="(i / Math.max(datos.length, 1)) * 96 + 2"
        :y="55 - (d.precipitacion / maxP) * 48"
        :width="96 / Math.max(datos.length, 1) - 0.5"
        :height="(d.precipitacion / maxP) * 48"
        :fill="precipColor(d.precipitacion)"
        rx="0.3"
      >
        <title>{{ fmt(d.fecha) }}: {{ d.precipitacion }} mm</title>
      </rect>
    </svg>

    <div v-if="estadisticas" class="stats">
      <div><span>Total</span><strong>{{ estadisticas.precipitacion_total }} mm</strong></div>
      <div><span>Días lluvia</span><strong>{{ estadisticas.dias_con_lluvia }}</strong></div>
      <div><span>Máximo</span><strong>{{ estadisticas.precipitacion_max_dia }} mm</strong></div>
    </div>
  </div>
</template>

<style scoped>
.hist-precip { padding: 0.5rem 0; }
.hist-precip__ctrl { display: flex; justify-content: space-between; margin-bottom: 0.75rem; }
.rango { display: flex; gap: 0.35rem; }
.rango button, .hist-precip__ctrl > button {
  padding: 0.35rem 0.6rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fff;
  font-size: 0.78rem;
  cursor: pointer;
}
.rango button.active { background: #0284c7; color: #fff; }
.chart { width: 100%; height: 160px; }
.stats { display: flex; gap: 1rem; margin-top: 0.75rem; font-size: 0.8rem; }
.stats strong { display: block; }
.loading { padding: 1.5rem; text-align: center; color: #6b7280; }
</style>
