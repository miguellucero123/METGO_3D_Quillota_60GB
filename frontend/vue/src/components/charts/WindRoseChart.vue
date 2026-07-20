<script setup>
import { computed } from 'vue'

const props = defineProps({
  directions: { type: Array, default: () => [] },
  speeds: { type: Array, default: () => [] },
  unit: { type: String, default: 'm/s' },
  size: { type: Number, default: 200 },
})

const SECTORS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

const countUnit = computed(() => (props.directions.length > 15 ? 'h' : 'd'))

const buckets = computed(() => {
  const counts = SECTORS.map(() => 0)
  const speedSum = SECTORS.map(() => 0)
  props.directions.forEach((deg, i) => {
    const d = Number(deg)
    const s = Number(props.speeds[i]) || 0
    if (Number.isNaN(d)) return
    const idx = Math.round(d / 45) % 8
    counts[idx] += 1
    speedSum[idx] += s
  })
  const max = Math.max(1, ...counts)
  return SECTORS.map((label, i) => ({
    label,
    count: counts[i],
    avgSpeed: counts[i] ? Math.round((speedSum[i] / counts[i]) * 10) / 10 : 0,
    ratio: counts[i] / max,
  }))
})

const cx = computed(() => props.size / 2)
const cy = computed(() => props.size / 2)
const rMax = computed(() => props.size * 0.38)

function wedgePath(i, ratio) {
  const a0 = ((i * 45 - 22.5) * Math.PI) / 180
  const a1 = ((i * 45 + 22.5) * Math.PI) / 180
  const r = rMax.value * Math.max(0.12, ratio)
  const x0 = cx.value + r * Math.sin(a0)
  const y0 = cy.value - r * Math.cos(a0)
  const x1 = cx.value + r * Math.sin(a1)
  const y1 = cy.value - r * Math.cos(a1)
  const large = 0
  return `M ${cx.value} ${cy.value} L ${x0} ${y0} A ${r} ${r} 0 ${large} 1 ${x1} ${y1} Z`
}
</script>

<template>
  <div class="wind-rose" role="img" aria-label="Rosa de vientos">
    <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`">
      <circle :cx="cx" :cy="cy" :r="rMax" fill="none" stroke="var(--color-border, #e5e7eb)" stroke-width="1" />
      <circle :cx="cx" :cy="cy" :r="rMax * 0.66" fill="none" stroke="var(--color-border, #f3f4f6)" stroke-width="1" />
      <circle :cx="cx" :cy="cy" :r="rMax * 0.33" fill="none" stroke="var(--color-border, #f3f4f6)" stroke-width="1" />
      <path
        v-for="(b, i) in buckets"
        :key="b.label"
        :d="wedgePath(i, b.ratio)"
        :fill="b.count ? `var(--color-primary, rgba(2, 132, 199, ${0.25 + b.ratio * 0.55}))` : 'transparent'"
        stroke="var(--color-primary, #0284c7)"
        stroke-width="0.5"
      />
      <text :x="cx" :y="14" text-anchor="middle" class="lbl">N</text>
      <text :x="size - 8" :y="cy + 4" text-anchor="end" class="lbl">E</text>
      <text :x="cx" :y="size - 6" text-anchor="middle" class="lbl">S</text>
      <text :x="8" :y="cy + 4" class="lbl">O</text>
    </svg>
    <ul class="legend">
      <li v-for="b in buckets.filter((x) => x.count)" :key="b.label">
        <strong>{{ b.label }}</strong> {{ b.count }}{{ countUnit }} · {{ b.avgSpeed }} {{ unit }}
      </li>
    </ul>
    <p v-if="!directions.length" class="empty">Sin datos de dirección de viento</p>
  </div>
</template>

<style scoped>
.wind-rose { display: flex; flex-wrap: wrap; gap: 1rem; align-items: flex-start; }
.lbl { font-size: 10px; fill: #6b7280; font-weight: 600; }
.legend {
  list-style: none;
  margin: 0;
  padding: 0;
  font-size: 0.75rem;
  color: #4b5563;
  display: grid;
  gap: 0.25rem;
}
.empty { font-size: 0.8rem; color: #6b7280; margin: 0; }
</style>
