<template>
  <div ref="host" class="airshed-map" role="img" :aria-label="ariaLabel" />
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch, computed, inject } from 'vue'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import {
  BOUNDS_MANTOS,
  MAP_STYLE_SATELLITE,
  largoFlechaViento,
  rotacionFlechaHacia,
  plumesGeoJSON,
} from '@/utils/faenaMap'

const site = inject('site')

const props = defineProps({
  puntos: { type: Array, default: () => [] },
  modo: { type: String, default: 'icap' },
  slugActivo: { type: String, default: null },
})

const emit = defineEmits(['select'])

const host = ref(null)
let map = null
const markers = []

const mapBounds = computed(() => site?.bounds || BOUNDS_MANTOS)

const ariaLabel = computed(() => {
  const n = props.puntos.length
  const label = site?.faena?.nombre || site?.siteLabel || 'Mantos Blancos'
  return `Mapa geográfico faena ${label} con ${n} estaciones, modo ${props.modo}`
})

function clearMarkers() {
  while (markers.length) {
    markers.pop().remove()
  }
}

function buildMarkerEl(p) {
  const wrap = document.createElement('button')
  wrap.type = 'button'
  wrap.className = 'ml-marker' + (p.activo ? ' ml-marker--active' : '')
  wrap.title = p.nombre
  wrap.setAttribute('aria-label', p.nombre)

  const circle = document.createElement('span')
  circle.className = 'ml-marker__dot'
  circle.style.background = p.color || '#6b7280'
  wrap.appendChild(circle)

  const vel = p.viento_velocidad
  const dir = p.viento_direccion
  const len = largoFlechaViento(vel)
  if (len > 0 && dir != null && !Number.isNaN(Number(dir))) {
    const arrow = document.createElement('span')
    arrow.className = 'ml-marker__wind'
    arrow.style.height = `${len}px`
    arrow.style.transform = `translateX(-50%) rotate(${rotacionFlechaHacia(dir)}deg)`
    arrow.innerHTML =
      '<svg viewBox="0 0 12 40" width="12" height="100%" aria-hidden="true">' +
      '<path d="M6 0 L10 14 L7 14 L7 40 L5 40 L5 14 L2 14 Z" fill="rgba(255,255,255,0.85)"/>' +
      '</svg>'
    wrap.appendChild(arrow)
  }

  wrap.addEventListener('click', (e) => {
    e.stopPropagation()
    emit('select', p.slug)
  })
  return wrap
}

function syncMarkers() {
  if (!map) return
  clearMarkers()
  for (const p of props.puntos) {
    if (p.lat == null || p.lon == null) continue
    const el = buildMarkerEl(p)
    const m = new maplibregl.Marker({ element: el, anchor: 'center' })
      .setLngLat([p.lon, p.lat])
      .setPopup(
        new maplibregl.Popup({ offset: 14, closeButton: false, className: 'ml-popup' }).setHTML(
          `<strong>${p.nombre}</strong><br/>` +
            `${props.modo === 'icap' ? 'ICAP' : 'Disp.'}: ` +
            `<b>${p.valor != null ? Math.round(p.valor) : '—'}</b>` +
            (p.pm25 != null ? `<br/>PM2.5: <b>${p.pm25}</b> µg/m³` : '') +
            (p.etiqueta ? `<br/>${p.etiqueta}` : '')
        )
      )
      .addTo(map)
    markers.push(m)
  }
}

function syncPlumes() {
  if (!map || !map.getSource('plumes')) return
  const show = props.modo === 'dispersion'
  const data = show ? plumesGeoJSON(props.puntos) : { type: 'FeatureCollection', features: [] }
  map.getSource('plumes').setData(data)
  map.setLayoutProperty('plumes-fill', 'visibility', show ? 'visible' : 'none')
  map.setLayoutProperty('plumes-line', 'visibility', show ? 'visible' : 'none')
}

function ensurePlumeLayers() {
  if (map.getSource('plumes')) return
  map.addSource('plumes', {
    type: 'geojson',
    data: { type: 'FeatureCollection', features: [] },
  })
  map.addLayer({
    id: 'plumes-fill',
    type: 'fill',
    source: 'plumes',
    layout: { visibility: 'none' },
    paint: {
      'fill-color': ['get', 'color'],
      'fill-opacity': 0.28,
    },
  })
  map.addLayer({
    id: 'plumes-line',
    type: 'line',
    source: 'plumes',
    layout: { visibility: 'none' },
    paint: {
      'line-color': ['get', 'color'],
      'line-width': 1.5,
      'line-opacity': 0.55,
    },
  })
}

onMounted(() => {
  if (!host.value) return
  const b = mapBounds.value
  map = new maplibregl.Map({
    container: host.value,
    style: MAP_STYLE_SATELLITE,
    bounds: [
      [b.west, b.south],
      [b.east, b.north],
    ],
    fitBoundsOptions: { padding: 36 },
    attributionControl: true,
  })
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right')
  map.on('load', () => {
    ensurePlumeLayers()
    syncMarkers()
    syncPlumes()
  })
})

onBeforeUnmount(() => {
  clearMarkers()
  if (map) {
    map.remove()
    map = null
  }
})

watch(
  () => [props.puntos, props.modo, props.slugActivo],
  () => {
    if (!map) return
    if (map.isStyleLoaded()) {
      syncMarkers()
      syncPlumes()
    } else {
      map.once('load', () => {
        syncMarkers()
        syncPlumes()
      })
    }
  },
  { deep: true }
)
</script>

<style scoped>
.airshed-map {
  width: 100%;
  height: min(62vh, 520px);
  min-height: 280px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: #0f172a;
}
@media (max-width: 640px) {
  .airshed-map {
    height: 55vh;
    min-height: 240px;
  }
}
</style>

<style>
.ml-marker {
  position: relative;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  padding: 0;
  cursor: pointer;
}
.ml-marker__dot {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 16px;
  height: 16px;
  margin: -8px 0 0 -8px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 0 1px rgba(15, 23, 42, 0.5);
  z-index: 2;
}
.ml-marker--active .ml-marker__dot {
  width: 22px;
  height: 22px;
  margin: -11px 0 0 -11px;
  box-shadow: 0 0 0 3px rgba(251, 146, 60, 0.55), 0 0 12px rgba(251, 146, 60, 0.45);
}
.ml-marker__wind {
  position: absolute;
  left: 50%;
  bottom: 50%;
  width: 12px;
  transform-origin: 50% 100%;
  pointer-events: none;
  z-index: 1;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.6));
}
.ml-popup .maplibregl-popup-content {
  background: #111827;
  color: #f3f4f6;
  border: 1px solid rgba(251, 146, 60, 0.35);
  border-radius: 8px;
  padding: 0.55rem 0.7rem;
  font-size: 0.8rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
}
.ml-popup .maplibregl-popup-tip {
  border-top-color: #111827;
}
</style>
