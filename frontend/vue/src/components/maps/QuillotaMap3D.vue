<template>
  <div class="map-container-3d">
    <div v-if="loading" class="map-loading">
      <div class="spinner"></div>
      <p>Cargando Mallas Topográficas (DEM) del Valle de Aconcagua...</p>
    </div>
    <div ref="mapContainer" class="deckgl-canvas"></div>
    
    <div v-if="legend" class="map-legend">
      <h4>{{ legend.title }}</h4>
      <div class="gradient-bar" :style="{ background: legend.gradient }"></div>
      <div class="legend-labels">
        <span v-for="label in legend.labels" :key="label">{{ label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import { useMetgoStore } from '@/stores/metgo';

const props = defineProps({
  estaciones: {
    type: Array,
    default: () => []
    // Example: [{ id: 'quillota', nombre: 'Quillota', lon: -71.25, lat: -32.88, value: 15.8, color: [239, 68, 68], text: '15.8°C' }]
  },
  legend: {
    type: Object,
    default: null
    // Example: { title: 'T° Máxima', gradient: 'linear-gradient(...)', labels: ['0°', '30°'] }
  },
  layerType: {
    type: String,
    default: 'column' // 'column' | 'scatterplot' | 'heatmap'
  }
});

const emit = defineEmits(['estacion-click']);
const store = useMetgoStore();

const mapContainer = ref(null);
const loading = ref(true);
let deckInstance = null;
let layersConfig = [];

const DEFAULT_COORDS = {
  quillota: { lon: -71.25, lat: -32.88 },
  los_nogales: { lon: -71.21, lat: -32.73 },
  hijuelas: { lon: -71.14, lat: -32.80 },
  limache: { lon: -71.27, lat: -33.00 },
  olmue: { lon: -71.18, lat: -33.00 }
};

const getLayers = async () => {
  const { TerrainLayer } = await import('@deck.gl/geo-layers');
  const { ColumnLayer, ScatterplotLayer, TextLayer } = await import('@deck.gl/layers');
  const { HeatmapLayer } = await import('@deck.gl/aggregation-layers');

  // Enrich data with coordinates
  const data = props.estaciones.map(e => ({
    ...e,
    lon: e.lon || DEFAULT_COORDS[e.id]?.lon || -71.25,
    lat: e.lat || DEFAULT_COORDS[e.id]?.lat || -32.88
  }));

  const layers = [
    new TerrainLayer({
      id: 'terrain-layer',
      elevationDecoder: {
        rScaler: 256,
        gScaler: 1,
        bScaler: 1 / 256,
        offset: -32768
      },
      elevationData: 'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png',
      texture: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      wireframe: false,
      color: [255, 255, 255] // White base to let satellite imagery colors through
    })
  ];

  if (props.layerType === 'heatmap') {
    layers.push(
      new HeatmapLayer({
        id: 'heatmap-layer',
        data,
        getPosition: d => [d.lon, d.lat],
        getWeight: d => d.value || 1,
        radiusPixels: 80,
        intensity: 1.5,
        threshold: 0.05,
        colorRange: [
          [0, 255, 170, 50],
          [14, 165, 233, 150],
          [239, 68, 68, 200]
        ]
      })
    );
  } else if (props.layerType === 'column') {
    layers.push(
      new ColumnLayer({
        id: 'column-layer',
        data,
        diskResolution: 12,
        radius: 1200,
        extruded: true,
        pickable: true,
        elevationScale: 50,
        getPosition: d => [d.lon, d.lat],
        getFillColor: d => d.color || [14, 165, 233, 200],
        getLineColor: [0, 0, 0],
        getElevation: d => d.value || 10,
        onClick: ({ object }) => object && emit('estacion-click', object.id)
      })
    );
  } else {
    layers.push(
      new ScatterplotLayer({
        id: 'scatter-layer',
        data,
        pickable: true,
        opacity: 0.8,
        stroked: true,
        filled: true,
        radiusScale: 1,
        radiusMinPixels: 8,
        radiusMaxPixels: 25,
        lineWidthMinPixels: 2,
        getPosition: d => [d.lon, d.lat],
        getFillColor: d => d.color || [14, 165, 233, 200],
        getLineColor: [255, 255, 255],
        getRadius: 1500,
        onClick: ({ object }) => object && emit('estacion-click', object.id)
      })
    );
  }

  // Text labels floating above
  layers.push(
    new TextLayer({
      id: 'text-layer',
      data,
      getPosition: d => [d.lon, d.lat, (d.value || 10) * (props.layerType === 'column' ? 50 : 0) + 150],
      getText: d => `${d.text || d.nombre}`,
      getSize: 16,
      getColor: [255, 255, 255],
      getAngle: 0,
      getTextAnchor: 'middle',
      getAlignmentBaseline: 'center',
      background: true,
      getBackgroundColor: d => [...(d.color || [0,0,0]), 200],
      fontFamily: 'system-ui, sans-serif',
      fontWeight: 'bold',
      billboard: true
    })
  );

  return layers;
};

const initDeckGL = async () => {
  try {
    const { Deck } = await import('@deck.gl/core');
    
    const INITIAL_VIEW_STATE = {
      longitude: -71.21,
      latitude: -32.88,
      zoom: 10.5,
      pitch: 60,
      bearing: 15,
      maxZoom: 14,
      maxPitch: 85
    };

    layersConfig = await getLayers();

    deckInstance = new Deck({
      parent: mapContainer.value,
      initialViewState: INITIAL_VIEW_STATE,
      controller: true,
      layers: layersConfig,
      getTooltip: ({object}) => object && `${object.nombre}\n${object.text || ''}`,
      onLoad: () => {
        loading.value = false;
      }
    });
  } catch (e) {
    console.error("Deck.GL falló al cargar.", e);
    setTimeout(() => { loading.value = false; }, 1000);
  }
};

watch(() => props.estaciones, async () => {
  if (deckInstance) {
    deckInstance.setProps({ layers: await getLayers() });
  }
}, { deep: true });

onMounted(() => {
  initDeckGL();
});

onBeforeUnmount(() => {
  if (deckInstance) {
    deckInstance.finalize();
  }
});
</script>

<style scoped>
.map-container-3d {
  position: relative;
  width: 100%;
  height: 400px;
  background: var(--surface-color, #0b1120);
  border: 1px solid var(--border-color, #1f2937);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}

.deckgl-canvas {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  outline: none;
}

.map-loading {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
  background: rgba(11, 17, 32, 0.9);
  color: #22d3ee;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(34, 211, 238, 0.1);
  border-top-color: #22d3ee;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin { 
  to { transform: rotate(360deg); } 
}

.map-legend {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: rgba(17, 24, 39, 0.85);
  backdrop-filter: blur(8px);
  padding: 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #fff;
  z-index: 5;
  width: 220px;
}

.map-legend h4 {
  margin: 0 0 0.5rem 0;
  font-size: 0.8rem;
  text-align: center;
  color: #9ca3af;
}

.gradient-bar {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  margin-bottom: 0.4rem;
}

.legend-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: #9ca3af;
}
</style>
