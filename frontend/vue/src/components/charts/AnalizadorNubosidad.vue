<script setup>
import { ref, computed, watch } from 'vue'
import { useMetgoStore } from '@/stores/metgo'
import { fetchAnalisisNubosidad } from '@/api/metgoApi'

const store = useMetgoStore()
const cargando = ref(false)
const datos = ref([])

async function cargar() {
  cargando.value = true
  try {
    const res = await fetchAnalisisNubosidad(store.estacionActiva, 7)
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

function cobColor(c) {
  if (c < 10) return '#fbbf24'
  if (c < 50) return '#60a5fa'
  if (c < 80) return 'var(--color-text-muted, #94a3b8)'
  return 'var(--color-background, #0f172a)'
}

const maxRad = computed(() => Math.max(100, ...datos.value.map((d) => d.radiacion || 0)))
</script>

<template>
  <div class="nub-panel">
    <h3>☁️ Nubosidad y radiación solar</h3>
    <div v-if="cargando" class="loading">Cargando…</div>
    <template v-else-if="datos.length">
      <div class="charts-row">
        <svg viewBox="0 0 100 50" class="mini-chart">
          <rect
            v-for="(d, i) in datos"
            :key="'n' + i"
            :x="i * (100 / datos.length) + 1"
            :y="50 - (d.cobertura / 100) * 45"
            :width="100 / datos.length - 2"
            :height="(d.cobertura / 100) * 45"
            :fill="cobColor(d.cobertura)"
            rx="0.5"
          />
        </svg>
        <svg viewBox="0 0 100 50" class="mini-chart">
          <polyline
            :points="datos.map((d, i) => `${i * (100 / datos.length) + 50 / datos.length},${50 - (d.radiacion / maxRad) * 45}`).join(' ')"
            fill="none"
            stroke="#fbbf24"
            stroke-width="1.2"
          />
        </svg>
      </div>
      <table class="tabla">
        <thead>
          <tr><th>Fecha</th><th>Cobertura</th><th>Tipo</th><th>Radiación</th><th>ΔT día</th><th>ΔT noche</th></tr>
        </thead>
        <tbody>
          <tr v-for="(d, i) in datos" :key="i">
            <td>{{ fmt(d.fecha) }}</td>
            <td>{{ d.cobertura }}%</td>
            <td>{{ d.tipo_nube }}</td>
            <td>{{ d.radiacion }} W/m²</td>
            <td :class="d.impacto_temp_dia < 0 ? 'neg' : ''">{{ d.impacto_temp_dia }}°C</td>
            <td :class="d.impacto_temp_noche > 0 ? 'pos' : ''">+{{ d.impacto_temp_noche }}°C</td>
          </tr>
        </tbody>
      </table>
      <div class="info-grid">
        <div class="info"><strong>Día</strong> Nubes reducen radiación → días más frescos.</div>
        <div class="info"><strong>Noche</strong> Nubes atrapan calor → menos riesgo de helada radiativa.</div>
      </div>
    </template>
    <p v-else class="empty">Sin datos de nubosidad</p>
  </div>
</template>

<style scoped>
.nub-panel { background: var(--color-surface, #1e293b); border-radius: 8px; padding: 1rem; }
.nub-panel h3 { margin: 0 0 0.75rem; font-size: 1rem; }
.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 0.75rem; }
.mini-chart { width: 100%; height: 120px; background: var(--color-background, rgba(15, 23, 42, 0.4)); border-radius: 6px; border: 1px solid var(--color-border, #334155); }
.tabla { width: 100%; font-size: 0.78rem; border-collapse: collapse; }
.tabla th, .tabla td { padding: 0.4rem; border-bottom: 1px solid var(--color-border, #334155); }
.neg { color: #ef4444; }
.pos { color: #10b981; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 0.75rem; }
.info { font-size: 0.75rem; background: rgba(2, 132, 199, 0.1); padding: 0.5rem; border-radius: 6px; border-left: 3px solid #0284c7; }
.loading, .empty { text-align: center; padding: 1.5rem; color: var(--color-text-muted, #94a3b8); }
</style>
