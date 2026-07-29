<template>
  <div class="page">
    <header class="page-head">
      <h1>Ambiente de faena</h1>
      <p>Meteo · aire CAMS · nieve · viento · informe imprimible (M2)</p>
    </header>

    <div class="controls">
      <label>
        Faena / minera
        <select v-model="faenaId">
          <option v-for="f in faenas" :key="f.id" :value="f.id">
            {{ f.nombre }}{{ f.region ? ` · ${f.region}` : '' }}{{ f.altitud_m ? ` (${f.altitud_m} m)` : '' }}
          </option>
        </select>
      </label>
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
        <div v-if="pkg.altitud_m != null">
          <span class="lbl">Altitud</span>
          <strong>{{ pkg.altitud_m }} m</strong>
        </div>
      </section>

      <section v-if="pkg.operaciones" class="ops">
        <h2>Umbrales operativos (izaje · caminos · botaderos)</h2>
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
        <p class="muted flags-line">
          Flags:
          <span v-if="pkg.flags?.flag_nieve_activa">nieve activa</span>
          <span v-if="pkg.flags?.flag_izaje_restringido">· izaje</span>
          <span v-if="pkg.flags?.flag_caminos_restringido">· caminos</span>
          <span v-if="pkg.flags?.flag_botaderos_restringido">· botaderos</span>
          <span v-if="!hayFlags">ninguno</span>
        </p>
      </section>

      <section class="grid-2">
        <div>
          <h2>Meteorología actual</h2>
          <table class="data">
            <tbody>
              <tr><th>Temperatura</th><td>{{ n(pkg.actual?.temperatura_c, 1) }} °C</td></tr>
              <tr><th>Humedad</th><td>{{ n(pkg.actual?.humedad_relativa_pct, 0) }} %</td></tr>
              <tr><th>Precipitación</th><td>{{ n(pkg.actual?.precipitacion_mm) }} mm</td></tr>
              <tr><th>Snowfall</th><td>{{ n(pkg.actual?.snowfall_mm) }} mm</td></tr>
              <tr><th>Presión MSL</th><td>{{ n(pkg.actual?.presion_msl_hpa, 1) }} hPa</td></tr>
              <tr><th>Visibilidad</th><td>{{ n(pkg.actual?.visibilidad_m, 0) }} m</td></tr>
              <tr><th>Viento 100 m</th><td>{{ n(pkg.actual?.viento_100m_ms) }} m/s · {{ n(pkg.actual?.viento_100m_dir_deg, 0) }}°</td></tr>
            </tbody>
          </table>
        </div>
        <div>
          <h2>Calidad del aire (CAMS)</h2>
          <table class="data">
            <tbody>
              <tr><th>PM2.5</th><td>{{ n(pkg.actual?.pm2_5, 1) }} µg/m³</td></tr>
              <tr><th>PM10</th><td>{{ n(pkg.actual?.pm10, 1) }} µg/m³</td></tr>
              <tr><th>SO₂</th><td>{{ n(pkg.actual?.so2, 1) }} µg/m³</td></tr>
              <tr><th>NO₂ / NOx proxy</th><td>{{ n(pkg.actual?.no2, 1) }} µg/m³</td></tr>
              <tr><th>O₃</th><td>{{ n(pkg.actual?.o3, 1) }} µg/m³</td></tr>
              <tr><th>Dust</th><td>{{ n(pkg.actual?.dust, 1) }} µg/m³</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-if="(pkg.estaciones_area || []).length">
        <h2>Estaciones por área (modelo)</h2>
        <ul class="estaciones">
          <li v-for="e in pkg.estaciones_area" :key="e.id">
            <strong>{{ e.nombre }}</strong>
            <span class="muted">{{ e.rol }} · {{ e.lat }}, {{ e.lon }}</span>
            <span class="fuente-badge">{{ e.fuente || 'modelo' }}</span>
          </li>
        </ul>
      </section>

      <section class="mvo">
        <h2>Modelo vs observado (M5–M7)</h2>
        <p v-if="statusLoading" class="muted">Estado observado…</p>
        <p v-else-if="obsStatus" class="status-line">
          Readiness:
          <strong :class="obsStatus.listo_produccion ? 'nv-verde' : 'nv-amarillo'">
            {{ obsStatus.estado_mvo || '—' }}
          </strong>
          <span class="muted">
            · pares aire {{ obsStatus.aire?.n_pares ?? 0 }}
            · IoT {{ obsStatus.iot?.n_lecturas ?? 0 }}
            · {{ obsStatus.listo_produccion ? 'listo' : 'pendiente datos' }}
          </span>
        </p>
        <p v-if="mvoLoading" class="muted">Comparando series…</p>
        <p v-else-if="mvoError" class="muted">{{ mvoError }}</p>
        <template v-else-if="mvo">
          <p>
            Estado: <strong :class="'nv-' + (mvo.estado === 'ok' ? 'verde' : mvo.estado === 'parcial' ? 'amarillo' : 'rojo')">{{ mvo.estado }}</strong>
            · estación {{ mvo.estacion_id }}
            · tipo_dato modelo / observado
          </p>
          <div class="ops-grid">
            <div class="ops-card">
              <span class="lbl">Aire</span>
              <strong>{{ mvo.aire?.estado || '—' }}</strong>
              <p class="muted">
                pares {{ mvo.aire?.n_pares ?? 0 }} ·
                PM2.5 sesgo {{ mvo.aire?.pm25?.sesgo_medio ?? '—' }} ·
                PM10 {{ mvo.aire?.pm10?.sesgo_medio ?? '—' }}
              </p>
            </div>
            <div class="ops-card">
              <span class="lbl">Meteo</span>
              <strong>{{ mvo.meteo?.estado || '—' }}</strong>
              <p class="muted">
                pares {{ mvo.meteo?.n_pares ?? 0 }} ·
                T sesgo {{ mvo.meteo?.temperatura?.sesgo_medio ?? '—' }} °C
              </p>
            </div>
            <div class="ops-card">
              <span class="lbl">IoT</span>
              <strong>{{ mvo.iot?.estado || '—' }}</strong>
              <p class="muted">{{ mvo.iot?.n_lecturas ?? 0 }} lecturas</p>
            </div>
          </div>
          <p v-if="mvo.estado === 'sin_observado'" class="muted">
            Sin series observadas. En API local:
            <code>POST /api/cron/faena/demo-observado?faena={{ faenaId }}</code>
          </p>
        </template>
      </section>

      <p class="muted">
        Generado {{ pkg.generado_en }} · fuente {{ pkg.fuente?.meteo }}
        <template v-if="pkg.fuente?.aire"> + {{ pkg.fuente.aire }}</template>
        · tipo {{ pkg.fuente?.tipo_dato || 'modelo' }}
      </p>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import site from '@/site.config.js'
import {
  fetchFaenas,
  fetchPaqueteAmbiental,
  fetchModeloVsObservado,
  fetchObservadoStatus,
  urlInformeFaena,
  urlModeloVsObservadoCsv,
} from '@/services/spatiApi'

const faenas = ref([])
const faenaId = ref(site.spatiDefaultSitio || 'escondida')
const pkg = ref(null)
const mvo = ref(null)
const obsStatus = ref(null)
const mvoLoading = ref(false)
const statusLoading = ref(false)
const mvoError = ref(null)
const loading = ref(true)
const error = ref(null)

const urlCsv = computed(() => urlInformeFaena(faenaId.value, 'csv'))
const urlPdf = computed(() => urlInformeFaena(faenaId.value, 'pdf'))
const urlMvoCsv = computed(() => urlModeloVsObservadoCsv(faenaId.value, 14))
const hayFlags = computed(() => {
  const f = pkg.value?.flags
  if (!f) return false
  return Boolean(
    f.flag_nieve_activa ||
      f.flag_izaje_restringido ||
      f.flag_caminos_restringido ||
      f.flag_botaderos_restringido
  )
})

function n(v, dec = 2) {
  if (v == null || Number.isNaN(Number(v))) return '—'
  return Number(v).toFixed(dec)
}

async function cargarLista() {
  try {
    const list = await fetchFaenas({ incluirIzaje: true })
    faenas.value = list.filter(
      (f) => (f.capacidades || []).includes('paquete_ambiental') || f.origen === 'spati'
    )
    if (!faenas.value.length) faenas.value = list
    if (!faenas.value.some((f) => f.id === faenaId.value) && faenas.value[0]) {
      faenaId.value = faenas.value[0].id
    }
  } catch {
    faenas.value = (site.stations || []).map((s) => ({
      id: s.slug,
      nombre: s.nombre,
      region: s.region,
      altitud_m: s.altitud_msnm,
    }))
  }
}

async function cargarMvo() {
  mvoLoading.value = true
  statusLoading.value = true
  mvoError.value = null
  try {
    const [rep, st] = await Promise.all([
      fetchModeloVsObservado(faenaId.value, { dias: 14 }),
      fetchObservadoStatus(faenaId.value, { dias: 14 }),
    ])
    mvo.value = rep
    obsStatus.value = st
  } catch (e) {
    mvoError.value = e?.message || 'Sin comparación observada'
    mvo.value = null
    obsStatus.value = null
  } finally {
    mvoLoading.value = false
    statusLoading.value = false
  }
}

async function cargar() {
  loading.value = true
  error.value = null
  try {
    pkg.value = await fetchPaqueteAmbiental(faenaId.value, { horas: 72 })
    await cargarMvo()
  } catch (e) {
    error.value = e?.message || 'No se pudo cargar el paquete ambiental'
    pkg.value = null
    mvo.value = null
  } finally {
    loading.value = false
  }
}

watch(faenaId, cargar)
onMounted(async () => {
  await cargarLista()
  await cargar()
})
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
  align-items: end;
  margin: 1.25rem 0;
}
.controls label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}
.controls select {
  min-width: 16rem;
  padding: 0.45rem 0.6rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
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
  cursor: not-allowed;
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
.flags-line span {
  margin-right: 0.25rem;
}
.status-line {
  margin: 0 0 0.75rem;
}
.status-line code {
  font-size: 0.8rem;
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
  font-size: 0.9rem;
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
  align-items: center;
  padding: 0.45rem 0.6rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}
.fuente-badge {
  margin-left: auto;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-muted);
  border: 1px solid var(--color-border);
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
}
.muted {
  color: var(--color-muted);
  font-size: 0.9rem;
}
</style>
