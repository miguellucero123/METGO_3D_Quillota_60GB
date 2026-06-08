<script setup>
import { computed, ref } from 'vue'
import { formatoDiaCorto } from '@/utils/meteoDates'
import ChartTooltip from '@/components/charts/ChartTooltip.vue'
import { exportarSvgPng } from '@/utils/exportChart'

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
  seriesMaxLabel: { type: String, default: 'Máxima' },
  seriesMinLabel: { type: String, default: 'Mínima' },
  exportName: { type: String, default: '' },
})

const showMax = ref(true)
const showMin = ref(true)
const svgRef = ref(null)
const tip = ref({ visible: false, x: 0, y: 0, i: -1 })

function exportPng() {
  if (svgRef.value) exportarSvgPng(svgRef.value, props.exportName || 'serie_temporal')
}

const W = 640
const H = computed(() => props.height)
const pad = { t: 16, r: 12, b: 28, l: 40 }

const nums = computed(() => props.values.map((v) => Number(v)).filter((n) => !Number.isNaN(n)))
const numsMin = computed(() =>
  props.showBand ? props.valuesMin.map((v) => Number(v)).filter((n) => !Number.isNaN(n)) : []
)

const yRange = computed(() => {
  const all = [
    ...(showMax.value ? nums.value : []),
    ...(props.showBand && showMin.value ? numsMin.value : []),
  ]
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
  if (!showMax.value) return ''
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

const lineMinPath = computed(() => {
  if (!props.showBand || !showMin.value) return ''
  const n = props.labels.length
  if (!n) return ''
  return props.valuesMin
    .map((v, i) => {
      const x = xAt(i, n)
      const y = yAt(v)
      return `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`
    })
    .join(' ')
})

const areaPath = computed(() => {
  if (!props.showArea || !props.labels.length || !linePath.value || props.showBand) return ''
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
  if (!props.showBand || !props.labels.length || !showMax.value || !showMin.value) return ''
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

function onDotEnter(e, i) {
  tip.value = { visible: true, x: e.clientX, y: e.clientY, i }
}

function onDotMove(e) {
  if (tip.value.visible) {
    tip.value.x = e.clientX
    tip.value.y = e.clientY
  }
}

function onDotLeave() {
  tip.value.visible = false
  tip.value.i = -1
}
</script>

<template>
  <div class="ts-chart" role="img" :aria-label="`Serie temporal, ${labels.length} puntos`">
    <div class="ts-head">
      <div v-if="showBand" class="ts-legend">
        <button type="button" :class="{ off: !showMax }" @click="showMax = !showMax">
          <span class="dot" :style="{ background: color }" /> {{ seriesMaxLabel }}
        </button>
        <button type="button" :class="{ off: !showMin }" @click="showMin = !showMin">
          <span class="dot dot--min" /> {{ seriesMinLabel }}
        </button>
      </div>
      <button v-if="exportName" type="button" class="ts-export" @click="exportPng">PNG</button>
    </div>
    <svg
      ref="svgRef"
      class="ts-chart__svg"
      :viewBox="`0 0 ${W} ${H}`"
      preserveAspectRatio="xMidYMid meet"
      @mouseleave="onDotLeave"
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
      <path v-if="showArea && areaPath" class="ts-chart__area" :d="areaPath" :fill="fillColor" />
      <path v-if="bandPath" class="ts-chart__band" :d="bandPath" :fill="fillColor" />
      <path v-if="lineMinPath" class="ts-chart__line ts-chart__line--min" :d="lineMinPath" stroke="#3b82f6" fill="none" />
      <path v-if="linePath" class="ts-chart__line" :d="linePath" :stroke="color" fill="none" />
      <g class="ts-chart__dots">
        <circle
          v-for="(v, i) in values"
          v-show="showMax"
          :key="'max' + i"
          :cx="xAt(i, labels.length)"
          :cy="yAt(v)"
          r="5"
          :fill="color"
          stroke="#fff"
          stroke-width="1.5"
          class="ts-dot"
          @mouseenter="onDotEnter($event, i)"
          @mousemove="onDotMove"
        />
        <circle
          v-for="(v, i) in valuesMin"
          v-show="showBand && showMin"
          :key="'min' + i"
          :cx="xAt(i, labels.length)"
          :cy="yAt(v)"
          r="4"
          fill="#3b82f6"
          stroke="#fff"
          stroke-width="1.5"
          class="ts-dot"
          @mouseenter="onDotEnter($event, i)"
          @mousemove="onDotMove"
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

    <ChartTooltip :x="tip.x" :y="tip.y" :visible="tip.visible && tip.i >= 0">
      <strong>{{ formatoDiaCorto(labels[tip.i]) }}</strong>
      <template v-if="showMax && values[tip.i] != null">
        {{ seriesMaxLabel }}: {{ values[tip.i] }}{{ unit }}<br />
      </template>
      <template v-if="showBand && valuesMin[tip.i] != null">
        {{ seriesMinLabel }}: {{ valuesMin[tip.i] }}{{ unit }}
      </template>
    </ChartTooltip>
  </div>
</template>

<style scoped>
.ts-chart {
  width: 100%;
  position: relative;
}
.ts-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.35rem;
  gap: 0.5rem;
}
.ts-export {
  padding: 0.2rem 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
  font-size: 0.68rem;
}
.ts-legend {
  display: flex;
  gap: 0.65rem;
  font-size: 0.72rem;
}
.ts-legend button {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border: 1px solid var(--color-border);
  background: #fff;
  border-radius: 999px;
  padding: 0.2rem 0.55rem;
  cursor: pointer;
  color: var(--color-text);
}
.ts-legend button.off {
  opacity: 0.45;
  text-decoration: line-through;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-primary);
}
.dot--min {
  background: #3b82f6;
}
.ts-chart__svg {
  width: 100%;
  height: auto;
  display: block;
}
.ts-dot {
  cursor: crosshair;
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
.ts-chart__line--min {
  stroke-width: 2;
  stroke-dasharray: 4 3;
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
