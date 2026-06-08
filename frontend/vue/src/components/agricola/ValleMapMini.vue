<script setup>
import { computed } from 'vue'
import { tempColor } from '@/utils/agroColors'

const props = defineProps({
  comparativo: { type: Object, default: () => ({}) },
})

defineEmits(['estacion-click'])

const ESTACIONES_POS = {
  quillota: { x: 155, y: 108, nombre: 'Quillota' },
  los_nogales: { x: 105, y: 73, nombre: 'Los Nogales' },
  hijuelas: { x: 195, y: 78, nombre: 'Hijuelas' },
  limache: { x: 115, y: 135, nombre: 'Limache' },
  olmue: { x: 210, y: 138, nombre: 'Olmué' },
}

const COLOR_TEXT = {
  '#3b82f6': '#042c53',
  '#60a5fa': '#042c53',
  '#22d3ee': '#04342c',
  '#f59e0b': '#412402',
  '#ef4444': '#501313',
  '#7c3aed': '#26215c',
}

const estacionesConDatos = computed(() =>
  Object.entries(ESTACIONES_POS).map(([id, pos]) => {
    const datos = props.comparativo[id] ?? {}
    const tMax = datos.temperatura_max ?? '--'
    const color = typeof tMax === 'number' ? tempColor(tMax) : '#888780'
    return { id, ...pos, tMax, color, colorText: COLOR_TEXT[color] ?? '#333' }
  })
)

const hayHelada = computed(() =>
  Object.values(props.comparativo).some((d) => (d.temperatura_min ?? 99) <= 3)
)

const leyenda = [
  { color: '#3b82f6', label: '<5°C' },
  { color: '#22d3ee', label: '5–15°C' },
  { color: '#f59e0b', label: '15–25°C' },
  { color: '#ef4444', label: '>25°C' },
]
</script>

<template>
  <div class="map-container">
    <svg
      viewBox="0 0 320 185"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="Mapa del Valle de Aconcagua con temperatura máxima por estación"
    >
      <title>Valle de Aconcagua — T° máx por estación</title>
      <path
        d="M35,22 Q90,12 150,27 Q210,40 268,24
           Q288,42 283,82 Q278,124 248,150
           Q185,170 135,163 Q82,155 42,132
           Q16,112 20,72 Z"
        fill="#C0DD97"
        fill-opacity="0.2"
        stroke="#3B6D11"
        stroke-width="0.8"
        stroke-opacity="0.35"
      />
      <g
        v-for="est in estacionesConDatos"
        :key="est.id"
        :transform="`translate(${est.x},${est.y})`"
        class="station-group"
        role="button"
        :aria-label="`${est.nombre}: ${est.tMax}°C`"
        @click="$emit('estacion-click', est.id)"
      >
        <circle :r="13" :fill="est.color" fill-opacity="0.15" />
        <circle :r="7" :fill="est.color" stroke="white" stroke-width="1.5" />
        <text
          y="4"
          text-anchor="middle"
          font-size="7"
          fill="white"
          font-family="system-ui, sans-serif"
          font-weight="600"
        >
          {{ est.tMax }}°
        </text>
        <text
          y="-15"
          text-anchor="middle"
          font-size="8.5"
          :fill="est.colorText"
          font-family="system-ui, sans-serif"
          font-weight="600"
        >
          {{ est.nombre }}
        </text>
      </g>
      <g v-if="hayHelada" transform="translate(16,16)">
        <rect width="78" height="18" rx="4" fill="#FCEBEB" stroke="#F09595" stroke-width="0.5" />
        <text x="8" y="12" font-size="8" fill="#A32D2D" font-family="system-ui, sans-serif" font-weight="600">
          Riesgo helada
        </text>
      </g>
    </svg>
    <div class="map-legend">
      <div v-for="l in leyenda" :key="l.label" class="legend-item">
        <span class="legend-dot" :style="{ background: l.color }" />
        <span>{{ l.label }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.map-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
svg {
  width: 100%;
  height: auto;
}
.station-group {
  cursor: pointer;
  transition: transform 0.15s;
}
.station-group:hover {
  transform: scale(1.2);
}
.map-legend {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--color-muted);
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
</style>
