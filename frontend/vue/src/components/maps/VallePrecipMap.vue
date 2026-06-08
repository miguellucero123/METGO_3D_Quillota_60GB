<script setup>
import { ref, onMounted } from 'vue'
import { useMetgoStore } from '@/stores/metgo'
import { fetchPrecipitacionCalibrada, fetchAlertasPrecipitacion } from '@/api/metgoApi'
import { precipColor, severidadAlertaColor } from '@/utils/colorScale'

const store = useMetgoStore()
const estaciones = [
  { id: 'quillota', nombre: 'Quillota', x: 48, y: 52 },
  { id: 'los_nogales', nombre: 'Los Nogales', x: 62, y: 28 },
  { id: 'hijuelas', nombre: 'Hijuelas', x: 78, y: 42 },
  { id: 'limache', nombre: 'Limache', x: 35, y: 72 },
  { id: 'olmue', nombre: 'Olmue', x: 70, y: 68 },
]
const puntos = ref([])

async function cargar() {
  const results = await Promise.all(
    estaciones.map(async (e) => {
      let lluvia = 0
      let alerta = 'verde'
      try {
        const cal = await fetchPrecipitacionCalibrada(e.id, 1)
        lluvia = cal?.precipitacion_calibrada?.[0] ?? cal?.datos?.precipitacion?.[0] ?? 0
        const al = await fetchAlertasPrecipitacion(e.id)
        const roja = al?.alertas_activas?.find((a) => a.nivel_severidad === 'rojo')
        if (roja) alerta = 'rojo'
        else if (al?.alertas_activas?.length) alerta = 'naranja'
      } catch {
        /* ignore */
      }
      return { ...e, lluvia, alerta, color: precipColor(lluvia) }
    })
  )
  puntos.value = results
}

onMounted(cargar)
</script>

<template>
  <div class="valle-map">
    <h4>Mapa precipitación — Valle de Aconcagua</h4>
    <svg viewBox="0 0 100 100" class="map-svg" role="img" aria-label="Mapa estaciones precipitación">
      <rect width="100" height="100" fill="#ecfdf5" rx="4" />
      <ellipse cx="55" cy="50" rx="38" ry="32" fill="#d1fae5" opacity="0.6" />
      <g v-for="p in puntos" :key="p.id">
        <circle
          :cx="p.x"
          :cy="p.y"
          :r="6 + Math.min(p.lluvia, 20) * 0.15"
          :fill="p.color"
          stroke="#fff"
          stroke-width="1"
          class="station-dot"
          @click="store.setEstacion(p.id)"
        />
        <text :x="p.x" :y="p.y + 12" text-anchor="middle" font-size="3.5" fill="#374151">{{ p.nombre }}</text>
        <text :x="p.x" :y="p.y - 9" text-anchor="middle" font-size="3" fill="#1f2937">{{ p.lluvia }} mm</text>
        <circle
          v-if="p.alerta !== 'verde'"
          :cx="p.x + 7"
          :cy="p.y - 7"
          r="2.5"
          :fill="severidadAlertaColor(p.alerta)"
        />
      </g>
    </svg>
    <button type="button" class="refresh" @click="cargar">Actualizar mapa</button>
  </div>
</template>

<style scoped>
.valle-map h4 { margin: 0 0 0.5rem; font-size: 0.9rem; }
.map-svg { width: 100%; max-height: 280px; border-radius: 8px; border: 1px solid #e5e7eb; }
.station-dot { cursor: pointer; }
.refresh {
  margin-top: 0.5rem;
  padding: 0.35rem 0.65rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fff;
  font-size: 0.78rem;
  cursor: pointer;
}
</style>
