<script setup>
import { computed, ref } from 'vue'
import ChartTooltip from '@/components/charts/ChartTooltip.vue'

const props = defineProps({
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  /** IDs de estación (mismo orden que labels) para clic */
  stationIds: { type: Array, default: () => [] },
  unit: { type: String, default: '' },
  color: { type: String, default: '' },
  kind: { type: String, default: 'default' },
  clickable: { type: Boolean, default: false },
  /** Texto secundario por barra: fuente, fecha, etc. */
  hints: { type: Array, default: () => [] },
})

const emit = defineEmits(['bar-click'])

const tip = ref({ visible: false, x: 0, y: 0, i: -1 })

const nums = computed(() => props.values.map(Number).filter((n) => !Number.isNaN(n)))

const stats = computed(() => {
  const min = nums.value.length ? Math.min(...nums.value) : 0
  const max = nums.value.length ? Math.max(...nums.value) : 1
  const span = max - min || 1
  return { min, max, span }
})

function barWidth(v) {
  const n = Number(v)
  if (Number.isNaN(n)) return 4
  const { min, span } = stats.value
  if (props.kind === 'precip') {
    const hi = Math.max(stats.value.max * 1.15, 1)
    return 8 + (n / hi) * 90
  }
  return 10 + ((n - min) / span) * 86
}

function barColor(v, i) {
  if (props.color) return props.color
  const n = Number(v)
  if (Number.isNaN(n)) return 'var(--color-primary)'
  const { min, max } = stats.value
  const t = max === min ? 0.5 : (n - min) / (max - min)
  if (props.kind === 'temp') {
    const r = Math.round(40 + t * 175)
    const b = Math.round(140 - t * 120)
    return `rgb(${r}, ${Math.round(90 + t * 40)}, ${b})`
  }
  if (props.kind === 'precip') {
    return n > 0 ? '#2980b9' : '#b0bec5'
  }
  if (props.kind === 'humedad') {
    return `hsl(200, ${55 + t * 25}%, ${42 + t * 18}%)`
  }
  const hues = ['#1a5f4a', '#2d7a5f', '#3d8a6e', '#5a9b72']
  return hues[i % hues.length]
}

function onEnter(e, i) {
  tip.value = { visible: true, x: e.clientX, y: e.clientY, i }
}

function onMove(e) {
  if (tip.value.visible) {
    tip.value.x = e.clientX
    tip.value.y = e.clientY
  }
}

function onLeave() {
  tip.value.visible = false
  tip.value.i = -1
}

function onClick(i) {
  if (!props.clickable) return
  const id = props.stationIds[i]
  emit('bar-click', { index: i, stationId: id, label: props.labels[i], value: props.values[i] })
}
</script>

<template>
  <div class="h-bar-chart" role="img" :aria-label="`Gráfico meteorológico, ${labels.length} estaciones`">
    <div
      v-for="(label, i) in labels"
      :key="label"
      class="h-bar-row"
      :class="{ 'h-bar-row--click': clickable }"
      @mouseenter="onEnter($event, i)"
      @mousemove="onMove"
      @mouseleave="onLeave"
      @click="onClick(i)"
    >
      <span class="h-bar-label" :title="label">{{ label }}</span>
      <div class="h-bar-track">
        <div
          class="h-bar-fill"
          :style="{ width: `${barWidth(values[i])}%`, background: barColor(values[i], i) }"
        />
      </div>
      <span class="h-bar-value">{{ values[i] }}{{ unit }}</span>
    </div>
    <p v-if="kind === 'temp'" class="h-bar-hint">
      Escala relativa al rango del mapa. {{ clickable ? 'Clic en barra → detalle estación.' : '' }}
    </p>

    <ChartTooltip :x="tip.x" :y="tip.y" :visible="tip.visible && tip.i >= 0">
      <strong>{{ labels[tip.i] }}</strong>
      {{ values[tip.i] }}{{ unit }}
      <span v-if="hints[tip.i]"><br />{{ hints[tip.i] }}</span>
    </ChartTooltip>
  </div>
</template>

<style scoped>
.h-bar-chart {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  position: relative;
}
.h-bar-row {
  display: grid;
  grid-template-columns: minmax(5.5rem, 30%) 1fr 4rem;
  align-items: center;
  gap: 0.65rem;
}
.h-bar-row--click {
  cursor: pointer;
  border-radius: 6px;
  padding: 0.15rem 0.25rem;
  margin: -0.15rem -0.25rem;
  transition: background 0.15s;
}
.h-bar-row--click:hover {
  background: rgba(2, 132, 199, 0.06);
}
.h-bar-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.h-bar-track {
  height: 1.5rem;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--color-border);
}
.h-bar-fill {
  height: 100%;
  border-radius: 5px;
  min-width: 4px;
  transition: width 0.3s ease;
  box-shadow: inset 0 -1px 0 rgba(0, 0, 0, 0.08);
}
.h-bar-value {
  font-size: 0.82rem;
  font-variant-numeric: tabular-nums;
  font-weight: 700;
  text-align: right;
  color: var(--color-text);
}
.h-bar-hint {
  margin: 0.15rem 0 0;
  font-size: 0.65rem;
  color: var(--color-muted);
}
</style>
