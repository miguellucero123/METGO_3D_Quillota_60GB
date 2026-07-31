<template>
  <div class="ahora">
    <header class="ahora-head">
      <div>
        <h1>{{ faenaMeta?.nombre || sitioId }} · Ahora</h1>
        <p class="sub">
          Ubicación de faena · viento 72 h
          <span v-if="horaSeleccionada"> · {{ fmtHora(horaSeleccionada.valid_time) }}</span>
        </p>
      </div>
      <div class="head-actions">
        <button type="button" class="btn" :disabled="loading" @click="cargar">Actualizar</button>
        <router-link class="btn btn-ghost" :to="{ name: 'faena-panel', params: { faena: sitioId } }">
          Panel técnico
        </router-link>
        <router-link class="btn btn-ghost" :to="{ name: 'faena-informes', params: { faena: sitioId } }">
          Informes
        </router-link>
      </div>
    </header>

    <div v-if="loading" class="state">Cargando pronóstico…</div>
    <div v-else-if="error" class="state error">
      <p>{{ error }}</p>
      <button type="button" class="btn" @click="cargar">Reintentar</button>
    </div>

    <template v-else-if="data">
      <p v-if="data.nwp_aviso" class="aviso" role="status">{{ data.nwp_aviso }}</p>

      <!-- Estado operativo actual -->
      <section class="badge-row" :class="'nivel-' + nivelActual">
        <div class="badge-main">
          <span class="dot" />
          <strong>{{ nivelNombre }}</strong>
          <span class="vel">{{ velActual }} km/h</span>
        </div>
        <div class="badge-meta">
          <span>Ráfaga {{ rafagaActual }} km/h</span>
          <span>Pico 72 h {{ pico72 }} km/h</span>
          <span v-if="dirLabel">Dir {{ dirLabel }}</span>
        </div>
        <p class="reco">{{ recomendacion }}</p>
      </section>

      <!-- Mapa estilo Windy (simple) -->
      <section class="map-wrap">
        <div ref="mapEl" class="map" role="img" :aria-label="`Mapa viento ${faenaMeta?.nombre || sitioId}`" />
        <div class="map-overlay">
          <div class="wind-pill" :style="{ background: colorNivel(nivelActual) }">
            <span class="arrow" :style="{ transform: `rotate(${dirDeg}deg)` }">↑</span>
            <span>{{ velActual }} km/h</span>
          </div>
          <p class="map-hint">Desplace la línea de tiempo para ver el viento por hora</p>
        </div>
      </section>

      <!-- Timeline de horas -->
      <section class="timeline" v-if="horas.length">
        <div class="timeline-label">
          <span>{{ fmtDiaCorto(horas[0]?.valid_time) }}</span>
          <strong>{{ fmtHoraCorta(horaSeleccionada?.valid_time) }}</strong>
          <span>{{ fmtDiaCorto(horas[horas.length - 1]?.valid_time) }}</span>
        </div>
        <input
          class="slider"
          type="range"
          min="0"
          :max="Math.max(0, horas.length - 1)"
          step="1"
          v-model.number="horaIdx"
          :aria-valuetext="fmtHora(horaSeleccionada?.valid_time)"
        />
        <div class="ticks" aria-hidden="true">
          <button
            v-for="(h, i) in horasMarcadas"
            :key="h.i"
            type="button"
            class="tick"
            :class="{ active: horaIdx === h.i, crit: h.nivel >= 2 }"
            :style="{ left: h.pct + '%' }"
            @click="horaIdx = h.i"
          >
            {{ h.label }}
          </button>
        </div>
      </section>

      <!-- Gráfico horas críticas (barras coloreadas) -->
      <section class="chart-sec">
        <h2>Horas críticas · 72 h</h2>
        <p class="legend">
          <span class="lg verde">Verde &lt;26</span>
          <span class="lg amarillo">Amarillo 26–29</span>
          <span class="lg naranja">Naranja 30–34</span>
          <span class="lg rojo">Rojo ≥35</span>
        </p>
        <div class="bars" role="img" aria-label="Velocidad de viento por hora">
          <div
            v-for="(h, i) in horas"
            :key="h.valid_time"
            class="bar-col"
            :class="{ selected: i === horaIdx }"
            :title="`${fmtHora(h.valid_time)} · ${h.v} km/h · ${h.nivel_nombre}`"
            @click="horaIdx = i"
          >
            <div
              class="bar"
              :style="{
                height: barHeight(h.v) + '%',
                background: colorNivel(h.nivel),
              }"
            />
          </div>
        </div>
        <div class="bar-axis">
          <span>0 h</span>
          <span>24 h</span>
          <span>48 h</span>
          <span>72 h</span>
        </div>
        <div class="thres-lines" aria-hidden="true">
          <span>26</span><span>31</span><span>36</span>
        </div>
      </section>

      <!-- Tabla tipo Windy: viento / ráfaga por hora -->
      <section class="strip-sec">
        <h2>Viento por hora</h2>
        <div class="strip-scroll">
          <table class="strip">
            <thead>
              <tr>
                <th class="sticky">Día</th>
                <th v-for="(g, gi) in gruposDia" :key="'d' + gi" :colspan="g.count">
                  {{ g.label }}
                </th>
              </tr>
              <tr>
                <th class="sticky">Hora</th>
                <th
                  v-for="(h, i) in horas"
                  :key="'hh' + h.valid_time"
                  :class="{ sel: i === horaIdx }"
                  @click="horaIdx = i"
                >
                  {{ pad(new Date(h.valid_time).getHours()) }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th class="sticky">Viento</th>
                <td
                  v-for="(h, i) in horas"
                  :key="'v' + h.valid_time"
                  :class="['cell', 'n' + h.nivel, { sel: i === horaIdx }]"
                  @click="horaIdx = i"
                >
                  {{ h.v }}
                </td>
              </tr>
              <tr>
                <th class="sticky">Ráfaga</th>
                <td
                  v-for="(h, i) in horas"
                  :key="'r' + h.valid_time"
                  :class="['cell', 'n' + h.nivel, { sel: i === horaIdx }]"
                  @click="horaIdx = i"
                >
                  {{ h.rafaga }}
                </td>
              </tr>
              <tr>
                <th class="sticky">Dir</th>
                <td
                  v-for="(h, i) in horas"
                  :key="'dir' + h.valid_time"
                  class="cell dir"
                  :class="{ sel: i === horaIdx }"
                  @click="horaIdx = i"
                >
                  <span class="dir-arr" :style="{ transform: `rotate(${h.dir}deg)` }">↑</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="strip-note">Valores en km/h · celdas coloreadas según umbral de izaje</p>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, inject, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { fetchSpatiPronostico } from '@/services/spatiApi'
import { wakeApi } from '@/services/authApi'

const site = inject('site')
const route = useRoute()
const injectedFaena = inject('faena', null)
const injectedMeta = inject('faenaMeta', null)

const sitioId = computed(
  () =>
    (injectedFaena && injectedFaena.value) ||
    String(route.params.faena || site.spatiDefaultSitio || 'escondida').toLowerCase(),
)
const faenaMeta = computed(
  () =>
    (injectedMeta && injectedMeta.value) ||
    (site.stations || []).find((s) => s.slug === sitioId.value) || {
      slug: sitioId.value,
      nombre: sitioId.value,
      lat: site.center?.lat,
      lon: site.center?.lon,
    },
)

const loading = ref(true)
const error = ref(null)
const data = ref(null)
const horaIdx = ref(0)
const mapEl = ref(null)
let map = null
let marker = null

const U = site.umbralesSpati || {
  verde_max_kmh: 26,
  amarillo: [26, 29],
  naranja: [30, 34],
  rojo_min_kmh: 35,
}

function nivelDeVel(v) {
  const x = Number(v) || 0
  if (x < U.verde_max_kmh) return 0
  if (x <= (U.amarillo?.[1] ?? 29)) return 1
  if (x <= (U.naranja?.[1] ?? 34)) return 2
  return 3
}

function colorNivel(n) {
  return ['#10b981', '#f59e0b', '#f97316', '#ef4444'][Math.min(3, Math.max(0, n))] || '#10b981'
}

function pad(n) {
  return String(n).padStart(2, '0')
}

function fmtHora(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('es-CL', { weekday: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch {
    return iso
  }
}

function fmtHoraCorta(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return '—'
  }
}

function fmtDiaCorto(iso) {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleDateString('es-CL', { weekday: 'short', day: 'numeric' })
  } catch {
    return ''
  }
}

/** Agrega serie 15 min → 1 h (máx ráfaga / v en la hora). */
const horas = computed(() => {
  const serie = data.value?.serie || []
  if (!serie.length) return []
  const buckets = new Map()
  for (const row of serie) {
    const t = new Date(row.valid_time)
    if (Number.isNaN(t.getTime())) continue
    t.setMinutes(0, 0, 0)
    const key = t.toISOString()
    const v = Number(row.v_final_kmh ?? row.v_mos_kmh ?? row.v_fisica_grua ?? 0)
    const raf = Number(row.rafaga_modelo ?? row.variables_zona_izaje?.rafaga_10m_kmh ?? v)
    const dir = Number(row.dir_viento_deg ?? row.dir_100m_deg ?? 0)
    const nivelApi = row.nivel_alerta
    const prev = buckets.get(key)
    if (!prev) {
      buckets.set(key, {
        valid_time: key,
        v: Math.round(v),
        rafaga: Math.round(raf),
        dir,
        nivel: typeof nivelApi === 'number' ? nivelApi : nivelDeVel(Math.max(v, raf)),
        nivel_nombre: row.nivel_nombre || '',
      })
    } else {
      prev.v = Math.max(prev.v, Math.round(v))
      prev.rafaga = Math.max(prev.rafaga, Math.round(raf))
      prev.dir = dir
      const n = typeof nivelApi === 'number' ? nivelApi : nivelDeVel(Math.max(prev.v, prev.rafaga))
      prev.nivel = Math.max(prev.nivel, n)
    }
  }
  const list = [...buckets.values()].slice(0, 72)
  for (const h of list) {
    if (!h.nivel_nombre) {
      h.nivel_nombre = ['VERDE', 'AMARILLO', 'NARANJA', 'ROJO'][h.nivel] || '—'
    }
  }
  return list
})

const horaSeleccionada = computed(() => horas.value[horaIdx.value] || horas.value[0] || null)

const horasMarcadas = computed(() => {
  const list = horas.value
  if (!list.length) return []
  const out = []
  const step = Math.max(1, Math.floor(list.length / 8))
  for (let i = 0; i < list.length; i += step) {
    out.push({
      i,
      pct: (i / Math.max(1, list.length - 1)) * 100,
      label: pad(new Date(list[i].valid_time).getHours()),
      nivel: list[i].nivel,
    })
  }
  return out
})

const gruposDia = computed(() => {
  const groups = []
  let cur = null
  for (const h of horas.value) {
    const d = new Date(h.valid_time)
    const label = d.toLocaleDateString('es-CL', { weekday: 'short', day: 'numeric' })
    if (!cur || cur.label !== label) {
      cur = { label, count: 1 }
      groups.push(cur)
    } else {
      cur.count += 1
    }
  }
  return groups
})

const nivelActual = computed(() => horaSeleccionada.value?.nivel ?? data.value?.nivel_maximo ?? 0)
const nivelNombre = computed(
  () =>
    horaSeleccionada.value?.nivel_nombre ||
    data.value?.nivel_maximo_nombre ||
    ['VERDE', 'AMARILLO', 'NARANJA', 'ROJO'][nivelActual.value] ||
    '—',
)
const velActual = computed(() => horaSeleccionada.value?.v ?? Math.round(data.value?.variables_zona_izaje?.v_pluma_kmh || 0))
const rafagaActual = computed(
  () => horaSeleccionada.value?.rafaga ?? Math.round(data.value?.variables_zona_izaje?.rafaga_10m_kmh || velActual.value),
)
const pico72 = computed(() => {
  if (!horas.value.length) return '—'
  return Math.max(...horas.value.map((h) => h.rafaga || h.v))
})
const dirDeg = computed(() => Number(horaSeleccionada.value?.dir || 0))
const dirLabel = computed(() => {
  const d = dirDeg.value
  const dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSO', 'SO', 'OSO', 'O', 'ONO', 'NO', 'NNO']
  return dirs[Math.round(((d % 360) / 22.5)) % 16]
})

const recomendacion = computed(() => {
  const n = nivelActual.value
  if (n >= 3) return 'Suspender izaje — ráfaga en rango crítico.'
  if (n === 2) return 'Suspensión recomendada — programar ventana más segura.'
  if (n === 1) return 'Precaución — operar con protocolo reforzado.'
  return 'Condición favorable para izaje en esta hora.'
})

function barHeight(v) {
  const max = Math.max(45, ...horas.value.map((h) => h.v || 0))
  return Math.max(4, Math.round(((Number(v) || 0) / max) * 100))
}

function destroyMap() {
  if (map) {
    map.remove()
    map = null
    marker = null
  }
}

function initMap() {
  if (!mapEl.value) return
  destroyMap()
  const lat = Number(faenaMeta.value?.lat ?? site.center?.lat ?? -21)
  const lon = Number(faenaMeta.value?.lon ?? site.center?.lon ?? -68.8)
  map = L.map(mapEl.value, {
    zoomControl: true,
    attributionControl: true,
  }).setView([lat, lon], 12)
  // OSM estándar (más confiable que Carto en algunos clientes)
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 18,
  }).addTo(map)
  marker = L.circleMarker([lat, lon], {
    radius: 12,
    color: '#fff',
    weight: 2,
    fillColor: colorNivel(nivelActual.value),
    fillOpacity: 0.95,
  }).addTo(map)
  marker.bindPopup(
    `<strong>${faenaMeta.value?.nombre || sitioId.value}</strong><br/>${lat.toFixed(4)}, ${lon.toFixed(4)}`,
  )
  // Contenedor acaba de montarse: forzar recálculo de tamaño
  requestAnimationFrame(() => {
    map?.invalidateSize()
    setTimeout(() => map?.invalidateSize(), 200)
  })
}

function refreshMarker() {
  if (!marker) return
  marker.setStyle({ fillColor: colorNivel(nivelActual.value) })
  const lat = Number(faenaMeta.value?.lat ?? site.center?.lat)
  const lon = Number(faenaMeta.value?.lon ?? site.center?.lon)
  if (Number.isFinite(lat) && Number.isFinite(lon)) marker.setLatLng([lat, lon])
}

watch(nivelActual, refreshMarker)
watch(horaIdx, () => {
  if (horaIdx.value < 0) horaIdx.value = 0
  if (horaIdx.value >= horas.value.length) horaIdx.value = Math.max(0, horas.value.length - 1)
})

async function ensureMap() {
  await nextTick()
  if (!mapEl.value) return
  if (!map) initMap()
  else {
    const lat = Number(faenaMeta.value?.lat ?? site.center?.lat)
    const lon = Number(faenaMeta.value?.lon ?? site.center?.lon)
    if (Number.isFinite(lat) && Number.isFinite(lon)) {
      map.setView([lat, lon], map.getZoom() || 12)
      refreshMarker()
    }
    map.invalidateSize()
  }
}

async function cargar() {
  loading.value = true
  error.value = null
  destroyMap()
  try {
    await wakeApi().catch(() => {})
    data.value = await fetchSpatiPronostico(sitioId.value)
    horaIdx.value = 0
  } catch (e) {
    error.value = e?.message || 'No se pudo cargar el pronóstico'
    data.value = null
  } finally {
    loading.value = false
  }
  // Importante: el div del mapa solo existe cuando loading=false && data
  if (data.value) await ensureMap()
}

watch(sitioId, () => cargar())

onMounted(() => cargar())
onBeforeUnmount(() => {
  destroyMap()
})
</script>

<style scoped>
.ahora {
  padding: 1rem 1.1rem 2rem;
  max-width: 960px;
  margin: 0 auto;
  color: var(--color-text);
}
.ahora-head {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.85rem;
}
.ahora-head h1 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 800;
}
.sub {
  margin: 0.2rem 0 0;
  color: var(--color-muted);
  font-size: 0.85rem;
}
.head-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.btn {
  border: none;
  background: var(--color-primary, #10b981);
  color: #0f172a;
  font-weight: 700;
  padding: 0.45rem 0.85rem;
  border-radius: 8px;
  cursor: pointer;
  text-decoration: none;
  font-size: 0.85rem;
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
  padding: 2rem 1rem;
  text-align: center;
  color: var(--color-muted);
}
.state.error {
  color: #f87171;
}
.aviso {
  background: rgba(245, 158, 11, 0.12);
  border-left: 3px solid #f59e0b;
  padding: 0.55rem 0.75rem;
  border-radius: 0 8px 8px 0;
  font-size: 0.85rem;
  margin-bottom: 0.75rem;
}

.badge-row {
  border-radius: 12px;
  padding: 0.9rem 1rem;
  margin-bottom: 0.85rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface, #111827);
}
.badge-row.nivel-0 { border-color: #10b98155; }
.badge-row.nivel-1 { border-color: #f59e0b66; }
.badge-row.nivel-2 { border-color: #f9731666; }
.badge-row.nivel-3 { border-color: #ef444466; }
.badge-main {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  font-size: 1.05rem;
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: currentColor;
}
.nivel-0 .dot, .nivel-0 .badge-main { color: #10b981; }
.nivel-1 .dot, .nivel-1 .badge-main { color: #f59e0b; }
.nivel-2 .dot, .nivel-2 .badge-main { color: #f97316; }
.nivel-3 .dot, .nivel-3 .badge-main { color: #ef4444; }
.vel { font-variant-numeric: tabular-nums; }
.badge-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 0.45rem;
  font-size: 0.82rem;
  color: var(--color-muted);
}
.reco {
  margin: 0.55rem 0 0;
  font-size: 0.9rem;
  font-weight: 600;
}

.map-wrap {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--color-border);
  margin-bottom: 0.85rem;
  height: min(42vh, 340px);
  min-height: 240px;
  background: #1e293b;
}
.map {
  width: 100%;
  height: 100%;
  min-height: 240px;
  background: #1e293b;
  z-index: 0;
}
.map :deep(.leaflet-container) {
  width: 100%;
  height: 100%;
  font: inherit;
  background: #1e293b;
}
.map :deep(.leaflet-control-attribution) {
  font-size: 10px;
  background: rgba(15, 23, 42, 0.75);
  color: #94a3b8;
}
.map :deep(.leaflet-control-attribution a) {
  color: #5eead4;
}
.map-overlay {
  position: absolute;
  left: 12px;
  bottom: 12px;
  z-index: 500;
  pointer-events: none;
}
.wind-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  color: #0f172a;
  font-weight: 800;
  font-size: 0.9rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
}
.arrow {
  display: inline-block;
  font-size: 1rem;
  line-height: 1;
}
.map-hint {
  margin: 0.35rem 0 0;
  font-size: 0.72rem;
  color: #cbd5e1;
  text-shadow: 0 1px 2px #000;
}

.timeline {
  margin-bottom: 1rem;
  padding: 0.65rem 0.25rem 1.4rem;
}
.timeline-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: var(--color-muted);
  margin-bottom: 0.35rem;
}
.timeline-label strong {
  color: var(--color-text);
  font-size: 1rem;
}
.slider {
  width: 100%;
  accent-color: #fbbf24;
  cursor: pointer;
}
.ticks {
  position: relative;
  height: 1.4rem;
  margin-top: 0.25rem;
}
.tick {
  position: absolute;
  transform: translateX(-50%);
  background: transparent;
  border: none;
  color: var(--color-muted);
  font-size: 0.7rem;
  cursor: pointer;
  padding: 0;
}
.tick.active { color: #fbbf24; font-weight: 800; }
.tick.crit { color: #f97316; }

.chart-sec, .strip-sec {
  margin-top: 0.5rem;
  margin-bottom: 1.25rem;
}
.chart-sec h2, .strip-sec h2 {
  margin: 0 0 0.4rem;
  font-size: 0.95rem;
  font-weight: 800;
}
.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  font-size: 0.72rem;
  color: var(--color-muted);
  margin-bottom: 0.5rem;
}
.lg::before {
  content: '';
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 2px;
  margin-right: 4px;
  vertical-align: middle;
}
.lg.verde::before { background: #10b981; }
.lg.amarillo::before { background: #f59e0b; }
.lg.naranja::before { background: #f97316; }
.lg.rojo::before { background: #ef4444; }

.bars {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 110px;
  padding: 4px 2px 0;
  border-bottom: 1px solid var(--color-border);
  background: linear-gradient(180deg, transparent 0%, rgba(15, 23, 42, 0.35) 100%);
  border-radius: 8px 8px 0 0;
  overflow: hidden;
}
.bar-col {
  flex: 1;
  min-width: 0;
  height: 100%;
  display: flex;
  align-items: flex-end;
  cursor: pointer;
  opacity: 0.85;
}
.bar-col.selected { opacity: 1; }
.bar-col.selected .bar {
  outline: 1px solid #fff;
}
.bar {
  width: 100%;
  border-radius: 2px 2px 0 0;
  min-height: 3px;
  transition: height 0.15s ease;
}
.bar-axis {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: var(--color-muted);
  margin-top: 0.25rem;
}
.thres-lines {
  display: none;
}

.strip-scroll {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  border: 1px solid var(--color-border);
  border-radius: 10px;
}
.strip {
  border-collapse: collapse;
  font-size: 0.72rem;
  min-width: 100%;
}
.strip th, .strip td {
  padding: 0.35rem 0.28rem;
  text-align: center;
  white-space: nowrap;
  border-bottom: 1px solid var(--color-border);
  font-variant-numeric: tabular-nums;
}
.strip th.sticky {
  position: sticky;
  left: 0;
  background: var(--color-surface, #0f172a);
  z-index: 2;
  text-align: left;
  padding-left: 0.55rem;
  font-weight: 700;
  color: var(--color-muted);
}
.strip thead th {
  color: var(--color-muted);
  font-weight: 600;
}
.strip .sel {
  outline: 1px solid #fbbf24;
  outline-offset: -1px;
}
.cell {
  cursor: pointer;
  font-weight: 700;
  color: #0f172a;
  min-width: 1.6rem;
}
.cell.n0 { background: #10b981; }
.cell.n1 { background: #f59e0b; }
.cell.n2 { background: #f97316; }
.cell.n3 { background: #ef4444; color: #fff; }
.cell.dir {
  background: transparent;
  color: var(--color-text);
}
.dir-arr {
  display: inline-block;
  font-size: 0.85rem;
}
.strip-note {
  margin: 0.4rem 0 0;
  font-size: 0.72rem;
  color: var(--color-muted);
}

@media (max-width: 640px) {
  .ahora { padding: 0.75rem 0.7rem 1.5rem; }
  .map-wrap { height: 38vh; min-height: 200px; }
  .bars { height: 88px; }
}
</style>
