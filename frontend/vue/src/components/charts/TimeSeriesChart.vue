<script setup>
import { computed } from 'vue'
import { formatoDiaCorto } from '@/utils/meteoDates'

const props = defineProps({
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  valuesMin: { type: Array, default: () => [] },
  unit: { type: String, default: '' },
  color: { type: String, default: 'var(--color-primary)' },
  fillColor: { type: String, default: 'rgba(26, 95, 74, 0.12)' },
  height: { type: Number, default: 200 },
  showBand: { type: Boolean, default: false },
  showArea: { type: Boolean, default: true },
  yAxisTitle: { type: String, default: '' },
})

const W = 640
const H = computed(() => props.height)
const pad = { t: 16, r: 12, b: 28, l: 40 }

const nums = computed(() => props.values.map((v) => Number(v)).filter((n) => !Number.isNaN(n)))
const numsMin = computed(() =>
  props.showBand ? props.valuesMin.map((v) => Number(v)).filter((n) => !Number.isNaN(n)) : []
)

const yRange = computed(() => {
  const all = [...nums.value, ...(props.showBand ? numsMin.value : [])]
  if (!all.length) return { min: 0, max: 1 }
  let lo = Math.min(...all)
  let hi = Math.max(...all)
  if (lo === hi) {
    lo -= 1
    hi += 1
  }
  const margin = (hi - lo) * 0.08 || 0.5
  return { min: lo - margin, max: hi + margin }
})

const innerW = computed(() => W - pad.l - pad.r)
const innerH = computed(() => H.value - pad.t - pad.b)

function xAt(i, n) {
  if (n <= 1) return pad.l + innerW.value / 2
  return pad.l + (i / (n - 1)) * innerW.value
}

function yAt(v) {
  const { min, max } = yRange.value
  const t = (Number(v) - min) / (max - min)
  return pad.t + innerH.value * (1 - t)
}

const linePath = computed(() => {
  const n = props.labels.length
  if (!n) return ''
  return props.values
    .map((v, i) => {
      const x = xAt(i, n)
      const y = yAt(v)
      return `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`
    })
    .join(' ')
})

const areaPath = computed(() => {
  if (!props.showArea || !props.labels.length || !linePath.value) return ''
  const n = props.labels.length
  const baseY = pad.t + innerH.value
  const pts = props.values
    .map((v, i) => `${xAt(i, n).toFixed(1)},${yAt(v).toFixed(1)}`)
    .join(' L ')
  const x0 = xAt(0, n).toFixed(1)
  const x1 = xAt(n - 1, n).toFixed(1)
  return `M ${x0} ${baseY} L ${pts} L ${x1} ${baseY} Z`
})

const bandPath = computed(() => {
  if (!props.showBand || !props.labels.length) return ''
  const n = props.labels.length
  const top = props.values
    .map((v, i) => `${xAt(i, n).toFixed(1)},${yAt(v).toFixed(1)}`)
    .join(' L ')
  const bottom = props.valuesMin
    .map((v, i) => `${xAt(n - 1 - i, n).toFixed(1)},${yAt(v).toFixed(1)}`)
    .join(' L ')
  return `M ${top} L ${bottom} Z`
})

const yTicks = computed(() => {
  const { min, max } = yRange.value
  const steps = 4
  const out = []
  for (let i = 0; i <= steps; i++) {
    const v = min + ((max - min) * i) / steps
    out.push({ v: Math.round(v * 10) / 10, y: yAt(v) })
  }
  return out
})

const xTickIndices = computed(() => {
  const n = props.labels.length
  if (n <= 6) return props.labels.map((_, i) => i)
  const pick = [0, Math.floor(n / 3), Math.floor((2 * n) / 3), n - 1]
  return [...new Set(pick)]
})
</script>

<template>
  <div class="ts-chart" role="img" :aria-label="`Serie temporal, ${labels.length} puntos`">
    <svg
      class="ts-chart__svg"
      :viewBox="`0 0 ${W} ${H}`"
      preserveAspectRatio="xMidYMid meet"
    >
      <g class="ts-chart__grid">
        <line
          v-for="tick in yTicks"
          :key="tick.v"
          :x1="pad.l"
          :x2="W - pad.r"
          :y1="tick.y"
          :y2="tick.y"
        />
      </g>
      <g class="ts-chart__ylabels">
        <text
          v-for="tick in yTicks"
          :key="'y' + tick.v"
          :x="pad.l - 6"
          :y="tick.y + 4"
          text-anchor="end"
        >
          {{ tick.v }}{{ unit }}
        </text>
      </g>
      <text
        v-if="yAxisTitle"
        :x="12"
        :y="pad.t + innerH / 2"
        class="ts-chart__ytitle"
        transform="rotate(-90 12 110)"
      >
        {{ yAxisTitle }}
      </text>
      <path v-if="showArea && areaPath && !showBand" class="ts-chart__area" :d="areaPath" :fill="fillColor" />
      <path v-if="showBand && bandPath" class="ts-chart__band" :d="bandPath" :fill="fillColor" />
      <path class="ts-chart__line" :d="linePath" :stroke="color" fill="none" />
      <g class="ts-chart__dots">
        <circle
          v-for="(v, i) in values"
          :key="i"
          :cx="xAt(i, labels.length)"
          :cy="yAt(v)"
          r="4"
          :fill="color"
          stroke="#fff"
          stroke-width="1.5"
        />
      </g>
      <g class="ts-chart__xlabels">
        <text
          v-for="i in xTickIndices"
          :key="'x' + i"
          :x="xAt(i, labels.length)"
          :y="H - 6"
          text-anchor="middle"
        >
          {{ formatoDiaCorto(labels[i]) }}
        </text>
      </g>
    </svg>
    <p v-if="labels.length" class="ts-chart__range">
      {{ formatoDiaCorto(labels[0]) }} — {{ formatoDiaCorto(labels[labels.length - 1]) }}
      · {{ labels.length }} días
    </p>
  </div>
</template>

<style scoped>
.ts-chart {
  width: 100%;
}
.ts-chart__svg {
  width: 100%;
  height: auto;
  display: block;
}
.ts-chart__grid line {
  stroke: var(--color-border);
  stroke-width: 1;
  stroke-dasharray: 4 4;
}
.ts-chart__ylabels text,
.ts-chart__xlabels text {
  font-size: 11px;
  fill: var(--color-muted);
}
.ts-chart__ytitle {
  font-size: 10px;
  fill: var(--color-muted);
  font-weight: 600;
}
.ts-chart__area {
  stroke: none;
  opacity: 0.85;
}
.ts-chart__line {
  stroke-width: 2.75;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.ts-chart__band {
  stroke: none;
}
.ts-chart__range {
  margin: 0.35rem 0 0;
  font-size: 0.72rem;
  color: var(--color-muted);
  text-align: center;
}
</style>
