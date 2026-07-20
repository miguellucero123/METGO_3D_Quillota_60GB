<script setup>
import { computed } from 'vue'
import { tempColor } from '@/utils/agroColors'
import QuillotaMap3D from '@/components/maps/QuillotaMap3D.vue'

const props = defineProps({
  comparativo: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['estacion-click'])

const ESTACIONES_POS = {
  quillota: { nombre: 'Quillota' },
  los_nogales: { nombre: 'Los Nogales' },
  hijuelas: { nombre: 'Hijuelas' },
  limache: { nombre: 'Limache' },
  olmue: { nombre: 'Olmué' },
}

const hexToRgb = (hex) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? [
    parseInt(result[1], 16),
    parseInt(result[2], 16),
    parseInt(result[3], 16)
  ] : [255, 255, 255];
}

const estacionesMap = computed(() => {
  return Object.entries(ESTACIONES_POS).map(([id, info]) => {
    const datos = props.comparativo[id] ?? {}
    const tMax = datos.temperatura_max ?? '--'
    const colorHex = typeof tMax === 'number' ? tempColor(tMax) : '#888780'
    
    return {
      id,
      nombre: info.nombre,
      value: typeof tMax === 'number' ? tMax : 0,
      text: `${tMax}°`,
      color: hexToRgb(colorHex)
    }
  })
})

const mapLegend = {
  title: 'T° Máxima',
  gradient: 'linear-gradient(to right, #3b82f6, #22d3ee, #f59e0b, #ef4444)',
  labels: ['<5°C', '15°C', '25°C', '>25°C']
}
</script>

<template>
  <div class="valle-map-mini-wrapper">
    <QuillotaMap3D
      :estaciones="estacionesMap"
      :legend="mapLegend"
      layerType="column"
      @estacion-click="id => emit('estacion-click', id)"
    />
  </div>
</template>

<style scoped>
.valle-map-mini-wrapper {
  width: 100%;
  border-radius: var(--radius-md);
  overflow: hidden;
}
</style>
