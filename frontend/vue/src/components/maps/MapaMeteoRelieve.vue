<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { grillaADataUrl, boundsLeaflet } from '@/utils/gridToMapOverlay'
import { rangoMapa } from '@/utils/mapColorScale'

const props = defineProps({
  grilla: { type: Object, default: null },
  variable: { type: String, default: 'temperatura' },
  unidad: { type: String, default: '°C' },
  nombreVar: { type: String, default: '' },
  fechaFrame: { type: String, default: '' },
  ambito: { type: String, default: 'regional' },
})

const mapRoot = ref(null)
const overlayOn = ref(true)
const escala = () => rangoMapa(props.variable)

let map = null
let baseLayers = {}
let overlayLayer = null
let stationsLayer = null
let layerControl = null

const ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · ' +
  '<a href="https://opentopomap.org">OpenTopoMap</a> · METGO 3D'

function initMap() {
  if (!mapRoot.value || map) return

  map = L.map(mapRoot.value, {
    center: [-32.95, -71.2],
    zoom: props.ambito === 'regional' ? 11 : 3,
    zoomControl: true,
    scrollWheelZoom: true,
  })

  baseLayers = {
    '🏔️ Relieve': L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
      maxZoom: 17,
      attribution: ATTRIBUTION,
    }),
    '🗺️ Calles': L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: ATTRIBUTION,
    }),
    '🛰️ Satélite': L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      { maxZoom: 18, attribution: 'Esri · METGO 3D' }
    ),
  }

  baseLayers['🏔️ Relieve'].addTo(map)
  stationsLayer = L.layerGroup().addTo(map)

  layerControl = L.control.layers(baseLayers, {}, { position: 'topright', collapsed: false }).addTo(map)

  L.control.scale({ metric: true, imperial: false, position: 'bottomleft' }).addTo(map)

  const bounds = boundsLeaflet(props.grilla, props.ambito)
  map.fitBounds(bounds, { padding: [24, 24] })

  updateOverlay()
}

function clearOverlay() {
  if (overlayLayer && map) {
    map.removeLayer(overlayLayer)
    overlayLayer = null
  }
}

function clearStations() {
  if (stationsLayer) stationsLayer.clearLayers()
}

function updateOverlay() {
  if (!map || !props.grilla) {
    clearOverlay()
    clearStations()
    return
  }

  clearOverlay()
  clearStations()

  if (overlayOn.value) {
    const url = grillaADataUrl(props.grilla, props.variable)
    const bounds = boundsLeaflet(props.grilla, props.ambito)
    if (url) {
      overlayLayer = L.imageOverlay(url, bounds, {
        opacity: 0.85,
        interactive: true,
        className: 'metgo-meteo-overlay',
      })
      overlayLayer.addTo(map)
      overlayLayer.on('mousemove', (e) => {
        const { lat, lng } = e.latlng
        overlayLayer.bindPopup(
          `<strong>${props.nombreVar}</strong><br>${lat.toFixed(3)}°, ${lng.toFixed(3)}°`
        )
      })
    }
  }

  for (const p of props.grilla.puntos_estacion || []) {
    const marker = L.circleMarker([p.lat, p.lon], {
      radius: 9,
      fillColor: '#ffffff',
      color: '#0f172a',
      weight: 2.5,
      fillOpacity: 1,
    })
    marker.bindPopup(
      `<strong>${p.nombre}</strong><br>` +
        `${props.nombreVar}: <b>${p.valor}</b> ${props.unidad}<br>` +
        (props.fechaFrame ? `Día: ${props.fechaFrame}` : '')
    )
    marker.bindTooltip(`${p.nombre}: ${p.valor} ${props.unidad}`, {
      permanent: false,
      direction: 'top',
      offset: [0, -8],
    })
    stationsLayer.addLayer(marker)
  }

  if (props.ambito === 'regional') {
    map.fitBounds(boundsLeaflet(props.grilla, props.ambito), { padding: [20, 20], maxZoom: 12 })
  }
}

function centrarValle() {
  if (!map) return
  const bounds = boundsLeaflet(props.grilla, props.ambito)
  map.fitBounds(bounds, { padding: [24, 24], maxZoom: props.ambito === 'regional' ? 12 : 4 })
}

function toggleOverlay() {
  overlayOn.value = !overlayOn.value
  updateOverlay()
}

watch(
  () => [props.grilla, props.variable, props.ambito],
  async () => {
    await nextTick()
    if (!map) initMap()
    else updateOverlay()
  },
  { deep: true }
)

onMounted(async () => {
  await nextTick()
  initMap()
  setTimeout(() => map?.invalidateSize(), 120)
})

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<template>
  <div class="relieve-wrap">
    <div ref="mapRoot" class="map-leaflet" role="application" aria-label="Mapa meteorológico interactivo" />
    <div class="map-hud">
      <div class="hud-box">
        <span>{{ nombreVar }}</span>
        <span v-if="fechaFrame">Día {{ fechaFrame }}</span>
      </div>
      <div class="hud-actions">
        <button type="button" title="Centrar valle" @click="centrarValle">⊙</button>
        <button type="button" :title="overlayOn ? 'Ocultar capa meteo' : 'Mostrar capa meteo'" @click="toggleOverlay">
          {{ overlayOn ? '🌡️' : '⬜' }}
        </button>
      </div>
    </div>
    <div class="colorbar">
      <span>{{ escala().min }}{{ unidad }}</span>
      <div class="bar" />
      <span>{{ escala().max }}{{ unidad }}</span>
    </div>
    <p class="map-hint">Arrastre, zoom con rueda o pellizco · Capas: Relieve / Calles / Satélite (esquina superior derecha)</p>
  </div>
</template>

<style scoped>
.relieve-wrap {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--color-border, #334155);
}
.map-leaflet {
  width: 100%;
  height: 460px;
  min-height: 360px;
  background: #e2e8f0;
  z-index: 0;
}
.map-hud {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  pointer-events: none;
}
.hud-box {
  background: rgba(15, 23, 42, 0.82);
  color: #fff;
  padding: 0.45rem 0.65rem;
  border-radius: 6px;
  font-size: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.hud-actions {
  display: flex;
  gap: 0.35rem;
  pointer-events: auto;
}
.hud-actions button {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: var(--color-surface, #1e293b);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
}
.colorbar {
  position: absolute;
  bottom: 36px;
  left: 10px;
  right: 10px;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.68rem;
  color: #f8fafc;
  background: rgba(15, 23, 42, 0.72);
  padding: 0.35rem 0.55rem;
  border-radius: 6px;
  pointer-events: none;
}
.colorbar .bar {
  flex: 1;
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(to right, #1e40af, #22c55e, #eab308, #ef4444);
}
.map-hint {
  margin: 0;
  padding: 0.4rem 0.65rem;
  font-size: 0.7rem;
  color: #64748b;
  background: var(--color-surface, #1e293b);
  border-top: 1px solid var(--color-border, #334155);
}
:deep(.leaflet-control-layers) {
  font-size: 0.78rem;
  border-radius: 8px;
}
:deep(.metgo-meteo-overlay) {
  image-rendering: pixelated;
}
</style>
