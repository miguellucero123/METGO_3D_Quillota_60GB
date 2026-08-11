<script setup>
import { ref, onMounted, computed } from 'vue'
import { useMetgoStore } from '@/stores/metgo'
import { fetchPrecipitacionCalibrada, fetchAlertasPrecipitacion } from '@/api/metgoApi'
import { precipColor, severidadAlertaColor } from '@/utils/colorScale'
import QuillotaMap3D from '@/components/maps/QuillotaMap3D.vue'

const store = useMetgoStore()
const estaciones = [
  { id: 'quillota', nombre: 'Quillota' },
  { id: 'los_nogales', nombre: 'Los Nogales' },
  { id: 'hijuelas', nombre: 'Hijuelas' },
  { id: 'limache', nombre: 'Limache' },
  { id: 'olmue', nombre: 'Olmue' },
]
const puntos = ref([])

const hexToRgb = (hex) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? [
    parseInt(result[1], 16),
    parseInt(result[2], 16),
    parseInt(result[3], 16)
  ] : [14, 165, 233];
}

async function cargar() {
  const results = await Promise.all(
    estaciones.map(async (e) => {
      let lluvia = 0
      let alerta = 'verde'
      try {
        const cal = await fetchPrecipitacionCalibrada(e.id, 1, 'dia')
        lluvia = cal?.precipitacion_calibrada?.[0] ?? cal?.datos?.precipitacion?.[0] ?? 0
        const al = await fetchAlertasPrecipitacion(e.id)
        const roja = al?.alertas_activas?.find((a) => a.nivel_severidad === 'rojo')
        if (roja) alerta = 'rojo'
        else if (al?.alertas_activas?.length) alerta = 'naranja'
      } catch {
        /* ignore */
      }
      
      const cHex = precipColor(lluvia)
      
      return { 
        ...e, 
        lluvia, 
        alerta,
        value: lluvia,
        text: `${lluvia} mm`,
        color: hexToRgb(cHex)
      }
    })
  )
  puntos.value = results
}

const mapLegend = {
  title: 'Precipitación',
  gradient: 'linear-gradient(to right, #9ca3af, #60a5fa, #3b82f6, #1d4ed8)',
  labels: ['0mm', '5mm', '15mm', '>25mm']
}

onMounted(cargar)
</script>

<template>
  <div class="valle-map">
    <div class="map-header">
      <h4>Mapa precipitación — Valle de Aconcagua</h4>
      <button type="button" class="refresh" @click="cargar">Actualizar mapa</button>
    </div>
    <div class="map-wrapper">
      <QuillotaMap3D
        :estaciones="puntos"
        :legend="mapLegend"
        layerType="column"
        @estacion-click="id => store.setEstacion(id)"
      />
    </div>
  </div>
</template>

<style scoped>
.valle-map {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.map-header h4 { margin: 0; font-size: 0.95rem; color: var(--color-text); }
.map-wrapper {
  width: 100%;
  border-radius: var(--radius-md);
  overflow: hidden;
}
.refresh {
  padding: 0.35rem 0.65rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 0.78rem;
  cursor: pointer;
  transition: all 0.2s;
}
.refresh:hover {
  background: var(--color-surface-hover);
}
</style>
