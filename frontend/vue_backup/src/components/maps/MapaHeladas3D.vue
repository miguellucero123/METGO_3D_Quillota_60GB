<template>
  <div class="map-container-3d">
    <div v-if="loading" class="map-loading">
      <div class="spinner"></div>
      <p>Cargando Mallas Topográficas (DEM) del Valle de Aconcagua...</p>
    </div>
    <div ref="mapContainer" class="deckgl-canvas"></div>
    
    <div class="map-legend">
      <h4>Inversión Térmica (Heladas)</h4>
      <div class="gradient-bar"></div>
      <div class="legend-labels">
        <span>-2°C (Letal)</span>
        <span>0°C</span>
        <span>+3°C (Seguro)</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

// Notas de Arquitectura: 
// Esto asume que el usuario instaló deck.gl. Si no, fallará silenciosamente o mostrará error en consola.
// En un entorno de producción, las elevaciones se cargan desde un servidor de tiles (Mapzen/AWS).

const mapContainer = ref(null);
const loading = ref(true);
let deckInstance = null;

const initDeckGL = async () => {
  try {
    // Importación dinámica para evitar errores si no está instalado aún en el entorno local
    const { Deck } = await import('@deck.gl/core');
    const { TerrainLayer } = await import('@deck.gl/geo-layers');
    const { HeatmapLayer } = await import('@deck.gl/aggregation-layers');

    const TERRAIN_IMAGE = 'https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/terrain.png';
    const SURFACE_IMAGE = 'https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/terrain-mask.png';
    
    // Coordenadas aproximadas de Quillota/Valle Aconcagua
    const INITIAL_VIEW_STATE = {
      longitude: -71.25,
      latitude: -32.88,
      zoom: 11,
      pitch: 60, // Ángulo 3D inclinado
      bearing: 45, // Mirando hacia la cordillera
      maxZoom: 15,
      maxPitch: 85
    };

    // Datos simulados de acumulación de frío (coordenadas bajas en el valle)
    const frostData = [
      { coordinates: [-71.25, -32.88], weight: 10 },
      { coordinates: [-71.26, -32.89], weight: 8 },
      { coordinates: [-71.24, -32.87], weight: 12 },
    ];

    deckInstance = new Deck({
      parent: mapContainer.value,
      initialViewState: INITIAL_VIEW_STATE,
      controller: true,
      layers: [
        new TerrainLayer({
          id: 'terrain-layer',
          elevationDecoder: {
            rScaler: 256,
            gScaler: 1,
            bScaler: 1 / 256,
            offset: -32768
          },
          // Usamos tiles genéricos de Mapzen para demostración. 
          // Para Quillota real, se debe usar un DEM de Alos PALSAR o similar.
          elevationData: 'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png',
          texture: 'https://s3.amazonaws.com/elevation-tiles-prod/normal/{z}/{x}/{y}.png',
          wireframe: false,
          color: [255, 255, 255]
        }),
        new HeatmapLayer({
          id: 'frost-heatmap',
          data: frostData,
          getPosition: d => d.coordinates,
          getWeight: d => d.weight,
          radiusPixels: 60,
          intensity: 1,
          threshold: 0.1,
          colorRange: [
            [0, 255, 170, 50], // Verde (Seguro)
            [14, 165, 233, 150], // Azul (Frío)
            [239, 68, 68, 200]  // Rojo/Morado (Helada letal)
          ]
        })
      ],
      onLoad: () => {
        loading.value = false;
      }
    });
  } catch (e) {
    console.error("Deck.GL no está instalado o falló al cargar.", e);
    // Simular carga para no bloquear UI
    setTimeout(() => { loading.value = false; }, 2000);
  }
};

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
  height: 500px;
  background: #0b1120;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

.deckgl-canvas {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}

.map-loading {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
  background: rgba(11, 17, 32, 0.8);
  color: var(--color-primary);
}

.spinner {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(0, 255, 170, 0.1);
  border-top-color: var(--color-primary);
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
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: #fff;
  z-index: 5;
  width: 250px;
}

.map-legend h4 {
  margin: 0 0 0.5rem 0;
  font-size: 0.85rem;
  text-align: center;
  color: var(--color-text-secondary);
}

.gradient-bar {
  width: 100%;
  height: 12px;
  background: linear-gradient(to right, rgba(0, 255, 170, 0.8), rgba(14, 165, 233, 0.9), rgba(239, 68, 68, 1));
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.legend-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: var(--color-muted);
}
</style>
