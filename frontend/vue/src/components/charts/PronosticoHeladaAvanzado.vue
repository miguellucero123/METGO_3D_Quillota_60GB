<script setup>
import { ref, computed, watch } from 'vue'
import { useMetgoStore } from '@/stores/metgo'
import { fetchPronosticoHeladaAvanzado } from '@/api/metgoApi'

const store = useMetgoStore()
const cargando = ref(false)
const datos = ref([])
const resumen = ref(null)
const expandidoIdx = ref(-1)
const cultivo = ref('palto')

async function cargar() {
  cargando.value = true
  try {
    const res = await fetchPronosticoHeladaAvanzado(store.estacionActiva, 7, cultivo.value)
    datos.value = res.pronosticos_helada ?? []
    resumen.value = res.resumen ?? null
  } catch {
    datos.value = []
    resumen.value = null
  } finally {
    cargando.value = false
  }
}

watch([() => store.estacionActiva, cultivo], cargar, { immediate: true })

const maxPop = 100
const minTemp = computed(() => Math.min(...datos.value.map((d) => d.temperatura_minima_esperada), 0))

function fmt(fechaStr) {
  return new Date(fechaStr).toLocaleDateString('es-CL', { weekday: 'short', day: 'numeric', month: 'short' })
}

function tempClass(t) {
  if (t < -5) return 'ext'
  if (t < 0) return 'crit'
  if (t < 5) return 'riesgo'
  return 'ok'
}

function popColor(p) {
  if (p > 70) return '#ef4444'
  if (p > 40) return '#f97316'
  if (p > 20) return '#f59e0b'
  return '#22c55e'
}

const barras = computed(() => {
  const n = datos.value.length || 1
  const w = 100 / n
  return datos.value.map((d, i) => ({
    x: i * w + w * 0.12,
    w: w * 0.76,
    hPop: (d.probabilidad_helada / maxPop) * 55,
    yTemp: 85 - ((d.temperatura_minima_esperada - minTemp.value) / Math.max(1, 15 - minTemp.value)) * 55,
    ...d,
  }))
})
</script>

<template>
  <div class="helada-av">
    <header class="helada-av__head">
      <h3>Pronóstico de helada radiativa</h3>
      <select v-model="cultivo" class="cultivo-sel">
        <option value="palto">Palto</option>
        <option value="vid">Vid</option>
        <option value="citricos">Cítricos</option>
        <option value="tomate">Tomate</option>
        <option value="lechuga">Lechuga</option>
      </select>
    </header>

    <div v-if="cargando" class="loading">Cargando…</div>
    <template v-else-if="datos.length">
      <div class="resumen" v-if="resumen">
        <div class="card sev"><strong>{{ resumen.dias_riesgo_severo }}</strong><span>Severo</span></div>
        <div class="card mod"><strong>{{ resumen.dias_riesgo_moderado }}</strong><span>Moderado</span></div>
        <div class="card min"><strong>{{ resumen.temperatura_minima_7d }}°C</strong><span>T° mín 7d</span></div>
      </div>

      <svg viewBox="0 0 100 95" class="chart-svg" role="img" aria-label="Helada 7 días">
        <line x1="0" y1="85" x2="100" y2="85" stroke="var(--color-border, #334155)" />
        <rect
          v-for="(b, i) in barras"
          :key="i"
          :x="b.x"
          :y="85 - b.hPop"
          :width="b.w"
          :height="b.hPop"
          :fill="popColor(b.probabilidad_helada)"
          opacity="0.85"
          rx="0.5"
        />
        <polyline
          :points="barras.map((b, i) => `${b.x + b.w / 2},${b.yTemp}`).join(' ')"
          fill="none"
          stroke="#3b82f6"
          stroke-width="0.8"
        />
        <text v-for="(b, i) in barras" :key="'l' + i" :x="b.x + b.w / 2" y="93" text-anchor="middle" font-size="2.2" fill="var(--color-text-muted, #94a3b8)">
          {{ fmt(b.fecha_pronostico).split(' ')[0] }}
        </text>
      </svg>

      <table class="tabla">
        <thead>
          <tr>
            <th>Fecha</th><th>T° mín</th><th>PoP</th><th>Nubes</th><th>Viento</th><th>Riesgo</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(d, i) in datos" :key="i" :class="{ alto: d.riesgo_severo }">
            <td>{{ fmt(d.fecha_pronostico) }}</td>
            <td><span class="badge" :class="tempClass(d.temperatura_minima_esperada)">{{ d.temperatura_minima_esperada }}°C</span></td>
            <td>{{ d.probabilidad_helada }}%</td>
            <td>{{ d.cobertura_nubosa }}%</td>
            <td>{{ d.velocidad_viento }} m/s</td>
            <td>{{ d.riesgo_severo ? '🔴 SEVERO' : d.riesgo_moderado ? '🟠 MOD' : '🟢 BAJO' }}</td>
          </tr>
        </tbody>
      </table>

      <div class="factores">
        <button v-for="(d, i) in datos" :key="'f' + i" type="button" class="exp-btn" @click="expandidoIdx = expandidoIdx === i ? -1 : i">
          {{ fmt(d.fecha_pronostico) }} <span>{{ expandidoIdx === i ? '▼' : '▶' }}</span>
        </button>
        <div v-if="expandidoIdx >= 0" class="exp-body">
          <p v-for="f in datos[expandidoIdx].factores_contribuyentes" :key="f">→ {{ f }}</p>
          <ul>
            <li v-for="(r, j) in datos[expandidoIdx].recomendaciones" :key="j">{{ r }}</li>
          </ul>
        </div>
      </div>
    </template>
    <p v-else class="empty">Sin datos de helada avanzada</p>
  </div>
</template>

<style scoped>
.helada-av { background: var(--color-surface, #1e293b); border-radius: 8px; padding: 1rem; }
.helada-av__head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
.helada-av__head h3 { margin: 0; font-size: 1rem; }
.cultivo-sel { font-size: 0.8rem; padding: 0.25rem 0.5rem; border-radius: 6px; }
.resumen { display: flex; gap: 0.75rem; margin-bottom: 0.75rem; }
.card { flex: 1; text-align: center; padding: 0.5rem; border-radius: 8px; font-size: 0.75rem; }
.card strong { display: block; font-size: 1.1rem; }
.card.sev { background: rgba(239, 68, 68, 0.1); border-left: 3px solid #ef4444; }
.card.mod { background: rgba(249, 115, 22, 0.1); border-left: 3px solid #f97316; }
.card.min { background: rgba(34, 197, 94, 0.1); border-left: 3px solid #22c55e; }
.chart-svg { width: 100%; height: 220px; margin-bottom: 0.75rem; }
.tabla { width: 100%; border-collapse: collapse; font-size: 0.78rem; }
.tabla th, .tabla td { padding: 0.45rem; border-bottom: 1px solid var(--color-border, #334155); text-align: left; }
.tabla tr.alto { background: rgba(239, 68, 68, 0.15); }
.badge { padding: 0.15rem 0.4rem; border-radius: 4px; color: var(--color-background, #0f172a); font-weight: 600; font-size: 0.72rem; }
.badge.ok { background: #22c55e; }
.badge.riesgo { background: #f59e0b; }
.badge.crit { background: #ef4444; }
.badge.ext { background: #7c3aed; }
.factores { margin-top: 0.75rem; }
.exp-btn { width: 100%; text-align: left; padding: 0.5rem; border: 1px solid var(--color-border, #334155); background: rgba(255, 255, 255, 0.05); border-radius: 6px; margin-bottom: 0.35rem; cursor: pointer; font-size: 0.8rem; }
.exp-body { padding: 0.5rem; background: rgba(255, 255, 255, 0.02); border: 1px solid var(--color-border, #334155); border-radius: 6px; font-size: 0.78rem; }
.loading, .empty { padding: 1.5rem; text-align: center; color: var(--color-text-muted, #94a3b8); }
</style>
