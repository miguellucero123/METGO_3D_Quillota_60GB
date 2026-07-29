<template>
  <div class="page">
    <header class="page-head">
      <h1>Ambiente de faena</h1>
      <p>Meteo · aire CAMS · nieve · viento · informe imprimible (M2)</p>
    </header>

    <div class="controls">
      <button type="button" class="btn" :disabled="loading" @click="cargar">Actualizar</button>
      <a class="btn btn-ghost" :href="urlCsv" target="_blank" rel="noopener">Descargar CSV</a>
      <a class="btn btn-ghost" :href="urlPdf" target="_blank" rel="noopener">Descargar PDF</a>
      <a class="btn btn-ghost" :href="urlMvoCsv" target="_blank" rel="noopener">MVO CSV</a>
    </div>

    <div v-if="loading" class="state">Cargando paquete ambiental…</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button type="button" class="btn" @click="cargar">Reintentar</button>
    </div>

    <template v-else-if="pkg">
      <section class="hero">
        <div>
          <span class="lbl">Faena</span>
          <strong>{{ pkg.nombre }}</strong>
        </div>
        <div>
          <span class="lbl">Nivel ops</span>
          <strong :class="'nv-' + (pkg.flags?.nivel_global || 'verde')">{{ pkg.flags?.nivel_global || '—' }}</strong>
        </div>
        <div>
          <span class="lbl">ICAP</span>
          <strong>{{ n(pkg.actual?.icap, 0) }} · {{ pkg.actual?.nivel_icap || '—' }}</strong>
        </div>
        <div>
          <span class="lbl">Viento 10 m</span>
          <strong>{{ n(pkg.actual?.viento_10m_ms) }} m/s · {{ n(pkg.actual?.viento_10m_dir_deg, 0) }}°</strong>
        </div>
        <div>
          <span class="lbl">Ráfaga</span>
          <strong>{{ n(pkg.actual?.rafaga_10m_ms) }} m/s</strong>
        </div>
        <div>
          <span class="lbl">Nieve 24 h</span>
          <strong>{{ n(pkg.nieve?.acumulacion_24h_cm, 1) }} cm</strong>
        </div>
        <div>
          <span class="lbl">PM2.5 / PM10</span>
          <strong>{{ n(pkg.actual?.pm2_5, 1) }} / {{ n(pkg.actual?.pm10, 1) }}</strong>
        </div>
      </section>

      <section v-if="pkg.operaciones" class="ops">
        <h2>Umbrales operativos</h2>
        <div class="ops-grid">
          <div
            v-for="(act, id) in pkg.operaciones.actividades"
            :key="id"
            class="ops-card"
            :class="'nv-' + act.nivel"
          >
            <span class="lbl">{{ id }}</span>
            <strong>{{ act.nivel }}</strong>
            <p class="muted">{{ (act.razones || []).join(' · ') || 'Sin restricciones' }}</p>
          </div>
        </div>
      </section>

      <section class="grid-2">
        <div>
          <h2>Meteorología</h2>
          <table class="data">
            <tbody>
              <tr><th>Temperatura</th><td>{{ n(pkg.actual?.temperatura_c, 1) }} °C</td></tr>
              <tr><th>Humedad</th><td>{{ n(pkg.actual?.humedad_relativa_pct, 0) }} %</td></tr>
              <tr><th>Precipitación</th><td>{{ n(pkg.actual?.precipitacion_mm) }} mm</td></tr>
              <tr><th>Visibilidad</th><td>{{ n(pkg.actual?.visibilidad_m, 0) }} m</td></tr>
              <tr><th>SO₂</th><td>{{ n(pkg.actual?.so2, 1) }} µg/m³</td></tr>
              <tr><th>NO₂</th><td>{{ n(pkg.actual?.no2, 1) }} µg/m³</td></tr>
            </tbody>
          </table>
        </div>
        <div>
          <h2>Estaciones por área</h2>
          <ul class="estaciones">
            <li v-for="e in pkg.estaciones_area || []" :key="e.id">
              <strong>{{ e.nombre }}</strong>
              <span class="muted">{{ e.rol }} · {{ e.lat }}, {{ e.lon }} · {{ e.fuente || 'modelo' }}</span>
            </li>
          </ul>
        </div>
      </section>

      <section class="mvo">
        <h2>Modelo vs observado (M5–M7)</h2>
        <p v-if="obsStatus">
          Readiness: <strong>{{ obsStatus.estado_mvo }}</strong>
          · pares {{ obsStatus.aire?.n_pares ?? 0 }}
          · {{ obsStatus.listo_produccion ? 'listo' : 'pendiente' }}
        </p>
        <p v-if="mvoLoading" class="muted">Comparando series…</p>
        <p v-else-if="mvoError" class="muted">{{ mvoError }}</p>
        <template v-else-if="mvo">
          <p>
            Estado: <strong>{{ mvo.estado }}</strong>
            · {{ mvo.estacion_id }}
            · aire {{ mvo.aire?.n_pares ?? 0 }} pares
            · meteo {{ mvo.meteo?.n_pares ?? 0 }} pares
            · IoT {{ mvo.iot?.n_lecturas ?? 0 }}
          </p>
          <p v-if="mvo.estado === 'sin_observado'" class="muted">
            Sin series observadas. API:
            <code>POST /api/cron/faena/demo-observado?faena=mantos_blancos</code>
          </p>
        </template>
      </section>

      <p class="muted">Generado {{ pkg.generado_en }} · {{ pkg.fuente?.tipo_dato || 'modelo' }}</p>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { FAENA, fetchPaqueteAmbiental, fetchModeloVsObservado, fetchObservadoStatus, urlInformeFaena, urlModeloVsObservadoCsv } from '@/services/aireApi'

const pkg = ref(null)
const mvo = ref(null)
const obsStatus = ref(null)
const mvoLoading = ref(false)
const mvoError = ref(null)
const loading = ref(true)
const error = ref(null)
const urlCsv = computed(() => urlInformeFaena('csv', FAENA))
const urlPdf = computed(() => urlInformeFaena('pdf', FAENA))
const urlMvoCsv = computed(() => urlModeloVsObservadoCsv(FAENA, 14))

function n(v, dec = 2) {
  if (v == null || Number.isNaN(Number(v))) return '—'
  return Number(v).toFixed(dec)
}

async function cargar() {
  loading.value = true
  error.value = null
  mvoLoading.value = true
  mvoError.value = null
  try {
    pkg.value = await fetchPaqueteAmbiental({ faenaId: FAENA, horas: 72 })
    try {
      const [rep, st] = await Promise.all([
        fetchModeloVsObservado({ faenaId: FAENA, dias: 14 }),
        fetchObservadoStatus({ faenaId: FAENA, dias: 14 }),
      ])
      mvo.value = rep
      obsStatus.value = st
    } catch (e) {
      mvoError.value = e?.message || 'Sin comparación'
      mvo.value = null
      obsStatus.value = null
    }
  } catch (e) {
    error.value = e?.message || 'No se pudo cargar el paquete ambiental'
    pkg.value = null
  } finally {
    loading.value = false
    mvoLoading.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1.25rem 1.25rem 2.5rem;
}
.page-head h1 {
  margin: 0 0 0.35rem;
}
.page-head p {
  margin: 0;
  color: var(--color-text-secondary);
}
.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin: 1.25rem 0;
}
.btn {
  padding: 0.5rem 0.9rem;
  border-radius: var(--radius-md);
  border: none;
  background: var(--color-primary);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}
.btn:disabled {
  opacity: 0.6;
}
.btn-ghost {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text);
}
.state {
  padding: 1.5rem;
  color: var(--color-text-secondary);
}
.state.error {
  color: #f87171;
}
.hero {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  padding: 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}
.lbl {
  display: block;
  font-size: 0.75rem;
  color: var(--color-muted);
  margin-bottom: 0.2rem;
}
.ops {
  margin-bottom: 1.25rem;
}
.ops-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}
@media (max-width: 800px) {
  .ops-grid {
    grid-template-columns: 1fr;
  }
}
.ops-card {
  padding: 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
}
.ops-card.nv-verde {
  border-color: #4ade80;
}
.ops-card.nv-amarillo {
  border-color: #facc15;
}
.ops-card.nv-rojo {
  border-color: #f87171;
}
.nv-verde {
  color: #4ade80;
}
.nv-amarillo {
  color: #facc15;
}
.nv-rojo {
  color: #f87171;
}
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}
@media (max-width: 800px) {
  .grid-2 {
    grid-template-columns: 1fr;
  }
}
h2 {
  font-size: 1.05rem;
  margin: 0 0 0.6rem;
}
.data {
  width: 100%;
  border-collapse: collapse;
  background: var(--color-surface);
}
.data th,
.data td {
  border: 1px solid var(--color-border);
  padding: 0.4rem 0.55rem;
  text-align: left;
}
.data th {
  width: 42%;
  color: var(--color-text-secondary);
  font-weight: 500;
}
.estaciones {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.4rem;
}
.estaciones li {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.45rem 0.6rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}
.muted {
  color: var(--color-muted);
  font-size: 0.9rem;
}
</style>
