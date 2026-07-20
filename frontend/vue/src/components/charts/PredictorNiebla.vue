<script setup>
import { ref, watch } from 'vue'
import { useMetgoStore } from '@/stores/metgo'
import { fetchPronosticoNiebla } from '@/api/metgoApi'

const store = useMetgoStore()
const cargando = ref(false)
const datos = ref([])
const resumen = ref(null)

async function cargar() {
  cargando.value = true
  try {
    const res = await fetchPronosticoNiebla(store.estacionActiva, 7)
    datos.value = res.pronosticos_niebla ?? []
    resumen.value = res.resumen ?? null
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

function popColor(p) {
  if (p > 70) return '#ef4444'
  if (p > 40) return '#f97316'
  if (p > 20) return '#f59e0b'
  return '#22c55e'
}

function tipoLabel(t) {
  return { radiativa: 'Radiativa', advectiva: 'Advectiva', rocio_cerro: 'Rocío' }[t] || t
}
</script>

<template>
  <div class="niebla-panel">
    <h3>🌫️ Nieblas y visibilidad</h3>
    <div v-if="cargando" class="loading">Cargando…</div>
    <template v-else-if="datos.length">
      <p v-if="resumen" class="resumen">
        Días con niebla: <strong>{{ resumen.dias_con_niebla }}</strong> ·
        Visibilidad mín: <strong>{{ resumen.visibilidad_minima }} km</strong>
      </p>
      <svg viewBox="0 0 100 55" class="chart-svg">
        <rect
          v-for="(d, i) in datos"
          :key="i"
          :x="i * (100 / datos.length) + 1"
          :y="55 - (d.probabilidad_niebla / 100) * 48"
          :width="100 / datos.length - 2"
          :height="(d.probabilidad_niebla / 100) * 48"
          :fill="popColor(d.probabilidad_niebla)"
          rx="0.5"
        />
      </svg>
      <table class="tabla">
        <thead>
          <tr><th>Fecha</th><th>PoP</th><th>Tipo</th><th>Severidad</th><th>Visibilidad</th><th>Alerta</th></tr>
        </thead>
        <tbody>
          <tr v-for="(d, i) in datos" :key="i" :class="{ crit: d.severidad === 'muy_densa' }">
            <td>{{ fmt(d.fecha_pronostico) }}</td>
            <td>{{ d.probabilidad_niebla }}%</td>
            <td>{{ tipoLabel(d.tipo_niebla) }}</td>
            <td>{{ d.severidad.replace('_', ' ') }}</td>
            <td>{{ d.visibilidad_esperada }} km</td>
            <td>{{ d.severidad === 'muy_densa' ? '🔴' : d.severidad === 'densa' ? '🟠' : '🟢' }}</td>
          </tr>
        </tbody>
      </table>
      <div class="seguridad">
        <strong>Seguridad vial:</strong> &lt; 1 km precaución · &lt; 500 m alerta · &lt; 100 m crítica
      </div>
    </template>
    <p v-else class="empty">Sin pronóstico de niebla</p>
  </div>
</template>

<style scoped>
.niebla-panel { background: var(--color-surface, #1e293b); border-radius: 8px; padding: 1rem; }
.niebla-panel h3 { margin: 0 0 0.75rem; font-size: 1rem; }
.resumen { font-size: 0.8rem; color: #4b5563; margin-bottom: 0.5rem; }
.chart-svg { width: 100%; height: 140px; margin-bottom: 0.75rem; }
.tabla { width: 100%; font-size: 0.78rem; border-collapse: collapse; }
.tabla th, .tabla td { padding: 0.4rem; border-bottom: 1px solid var(--color-border, #334155); }
.tabla tr.crit { background: #fef2f2; }
.seguridad { margin-top: 0.75rem; font-size: 0.75rem; background: #fef2f2; padding: 0.5rem; border-radius: 6px; border-left: 3px solid #ef4444; }
.loading, .empty { text-align: center; padding: 1.5rem; color: #6b7280; }
</style>
