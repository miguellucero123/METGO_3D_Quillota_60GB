<template>
  <div ref="host" class="mam-map" role="img" :aria-label="ariaLabel" />
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch, computed } from 'vue'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import {
  BOUNDS_COPIAPO,
  MAP_STYLE_SATELLITE,
  windVectorsToGeoJSON,
  fuentesToGeoJSON,
} from '@/utils/airshedMap'

const props = defineProps({
  heatGeojson: { type: Object, default: null },
  windVectors: { type: Array, default: () => [] },
  fuentes: { type: Array, default: () => [] },
  maxValue: { type: Number, default: 1 },
})

const host = ref(null)
let map = null

const ariaLabel = computed(
  () =>
    `Campo de concentración proxy METGO Airshed Modeler; máximo ${props.maxValue ?? '—'} µg/m³`
)

function emptyFc() {
  return { type: 'FeatureCollection', features: [] }
}

function ensureLayers() {
  if (!map.getSource('heat')) {
    map.addSource('heat', { type: 'geojson', data: emptyFc() })
    map.addLayer({
      id: 'heat-circles',
      type: 'circle',
      source: 'heat',
      paint: {
        'circle-radius': [
          'interpolate',
          ['linear'],
          ['get', 'c'],
          0,
          4,
          0.5,
          8,
          1,
          12,
          2,
          16,
        ],
        'circle-color': [
          'interpolate',
          ['linear'],
          ['get', 'c'],
          0.05,
          'rgba(22, 101, 52, 0.15)',
          0.15,
          '#166534',
          0.3,
          '#22c55e',
          0.5,
          '#84cc16',
          0.7,
          '#eab308',
          1.0,
          '#f59e0b',
          2.0,
          '#ea580c',
          5.0,
          '#dc2626',
        ],
        'circle-opacity': 0.72,
        'circle-blur': 0.55,
      },
    })
  }
  if (!map.getSource('wind')) {
    map.addSource('wind', { type: 'geojson', data: emptyFc() })
    map.addLayer({
      id: 'wind-lines',
      type: 'line',
      source: 'wind',
      paint: {
        'line-color': '#ef4444',
        'line-width': 1.6,
        'line-opacity': 0.85,
      },
    })
  }
  if (!map.getSource('fuentes')) {
    map.addSource('fuentes', { type: 'geojson', data: emptyFc() })
    map.addLayer({
      id: 'fuentes-halo',
      type: 'circle',
      source: 'fuentes',
      paint: {
        'circle-radius': 10,
        'circle-color': '#f87171',
        'circle-opacity': 0.25,
      },
    })
    map.addLayer({
      id: 'fuentes-dot',
      type: 'circle',
      source: 'fuentes',
      paint: {
        'circle-radius': 5,
        'circle-color': '#dc2626',
        'circle-stroke-width': 2,
        'circle-stroke-color': '#fff',
      },
    })
  }
}

function syncData() {
  if (!map || !map.getSource('heat')) return
  map.getSource('heat').setData(props.heatGeojson || emptyFc())
  map.getSource('wind').setData(windVectorsToGeoJSON(props.windVectors))
  map.getSource('fuentes').setData(fuentesToGeoJSON(props.fuentes))
}

onMounted(() => {
  if (!host.value) return
  map = new maplibregl.Map({
    container: host.value,
    style: MAP_STYLE_SATELLITE,
    bounds: [
      [BOUNDS_COPIAPO.west, BOUNDS_COPIAPO.south],
      [BOUNDS_COPIAPO.east, BOUNDS_COPIAPO.north],
    ],
    fitBoundsOptions: { padding: 40 },
    attributionControl: true,
  })
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right')
  map.on('load', () => {
    ensureLayers()
    syncData()
  })
})

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }
})

watch(
  () => [props.heatGeojson, props.windVectors, props.fuentes],
  () => {
    if (!map) return
    if (map.isStyleLoaded()) syncData()
    else map.once('load', syncData)
  },
  { deep: true }
)
</script>

<style scoped>
.mam-map {
  width: 100%;
  height: min(58vh, 560px);
  min-height: 300px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: #1a1a1a;
}
@media (max-width: 640px) {
  .mam-map {
    height: 52vh;
    min-height: 260px;
  }
}
</style>
