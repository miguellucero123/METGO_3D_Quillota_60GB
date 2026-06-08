<script setup>
import { computed, ref } from 'vue'
import { formatoDiaCorto } from '@/utils/meteoDates'
import ChartTooltip from '@/components/charts/ChartTooltip.vue'
import { exportarSvgPng } from '@/utils/exportChart'
import { exportarDatosCSV } from '@/utils/exportData'

const props = defineProps({
  labels: { type: Array, default: () => [] },
  temperaturas: { type: Array, default: () => [] },
  precipitacion: { type: Array, default: () => [] },
  tempUnit: { type: String, default: '°C' },
  height: { type: Number, default: 240 },
  exportName: { type: String, default: 'combo_meteo' },
})

const svgRef = ref(null)
const tip = ref({ visible: false, x: 0, y: 0, i: -1 })

const W = 640
const H = computed(() => props.height)
const pad = { t: 20, r: 48, b: 32, l: 44 }

const maxPrecip = computed(() => Math.max(2, ...props.precipitacion.map(Number)))
const temps = computed(() => props.temperaturas.map(Number).filter((n) => !Number.isNaN(n)))
const tRange = computed(() => {
  if (!temps.value.length) return { min: 0, max: 30 }
  let lo = Math.min(...temps.value)
  let hi = Math.max(...temps.value)
  if (lo === hi) { lo -= 2; hi += 2 }
  const m = (hi - lo) * 0.1 || 1
  return { min: lo - m, max: hi + m }
})

const innerW = computed(() => W - pad.l - pad.r)
const innerH = computed(() => H.value - pad.t - pad.b)
const n = computed(() => props.labels.length || 1)
const barW = computed(() => (innerW.value / n.value) * 0.55)

function xCenter(i) {
  return pad.l + (i + 0.5) * (innerW.value / n.value)
}

function yTemp(v) {
  const { min, max } = tRange.value
  return pad.t + innerH.value * (1 - (v - min) / (max - min))
}

function yPrecip(v) {
  const p = Number(v) || 0
  return pad.t + innerH.value * (1 - p / maxPrecip.value)
}

const linePath = computed(() =>
  props.temperaturas
    .map((v, i) => `${i ? 'L' : 'M'} ${xCenter(i).toFixed(1)} ${yTemp(Number(v)).toFixed(1)}`)
    .join(' ')
)

function onEnter(e, i) {
  tip.value = { visible: true, x: e.clientX, y: e.clientY, i }
}
function onMove(e) {
  if (tip.value.visible) { tip.value.x = e.clientX; tip.value.y = e.clientY }
}
function onLeave() {
  tip.value.visible = false
  tip.value.i = -1
}

function exportPng() {
  if (svgRef.value) exportarSvgPng(svgRef.value, props.exportName)
}

function exportCsv() {
  const rows = props.labels.map((f, i) => ({
    fecha: f,
    temperatura_max: props.temperaturas[i],
    precipitacion_mm: props.precipitacion[i],
  }))
  exportarDatosCSV(rows, props.exportName)
}
</script>

<template>
  <div class="combo-chart">
    <div class="combo-chart__toolbar">
      <span class="legend">
        <i class="swatch swatch--temp" /> T° máx ({{ tempUnit }})
        <i class="swatch swatch--rain" /> Lluvia (mm)
      </span>
      <span class="actions">
        <button type="button" @click="exportCsv">CSV</button>
        <button type="button" @click="exportPng">PNG</button>
      </span>
    </div>
    <svg
      ref="svgRef"
      class="combo-chart__svg"
      :viewBox="`0 0 ${W} ${H}`"
      preserveAspectRatio="xMidYMid meet"
      @mouseleave="onLeave"
    >
      <g v-for="i in n" :key="'g' + i">
        <line
          :x1="pad.l"
          :x2="W - pad.r"
          :y1="pad.t + (innerH * (i - 1)) / 4"
          :y2="pad.t + (innerH * (i - 1)) / 4"
          stroke="#e5e7eb"
          stroke-dasharray="4 4"
        />
      </g>
      <text :x="8" :y="pad.t + innerH / 2" class="axis-lbl" transform="rotate(-90 8 120)">{{ tempUnit }}</text>
      <text :x="W - 8" :y="pad.t + innerH / 2" class="axis-lbl" transform="rotate(90 632 120)">mm</text>
      <g v-for="(p, i) in precipitacion" :key="'b' + i">
        <rect
          :x="xCenter(i) - barW / 2"
          :y="yPrecip(p)"
          :width="barW"
          :height="Math.max(0, pad.t + innerH - yPrecip(p))"
          :fill="p > 0 ? '#2980b9' : '#d1d5db'"
          rx="2"
          opacity="0.85"
          @mouseenter="onEnter($event, i)"
          @mousemove="onMove"
        />
      </g>
      <path :d="linePath" fill="none" stroke="#c45c26" stroke-width="2.5" stroke-linecap="round" />
      <g v-for="(t, i) in temperaturas" :key="'d' + i">
        <circle
          :cx="xCenter(i)"
          :cy="yTemp(Number(t))"
          r="5"
          fill="#c45c26"
          stroke="#fff"
          stroke-width="1.5"
          @mouseenter="onEnter($event, i)"
          @mousemove="onMove"
        />
      </g>
      <g class="xlabels">
        <text
          v-for="(lbl, i) in labels"
          :key="'x' + i"
          :x="xCenter(i)"
          :y="H - 8"
          text-anchor="middle"
        >
          {{ formatoDiaCorto(lbl) }}
        </text>
      </g>
    </svg>
    <ChartTooltip :x="tip.x" :y="tip.y" :visible="tip.visible && tip.i >= 0">
      <strong>{{ formatoDiaCorto(labels[tip.i]) }}</strong>
      T° máx: {{ temperaturas[tip.i] }}{{ tempUnit }}<br />
      Lluvia: {{ precipitacion[tip.i] }} mm
    </ChartTooltip>
  </div>
</template>

<style scoped>
.combo-chart { width: 100%; position: relative; }
.combo-chart__toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.35rem;
  font-size: 0.72rem;
  color: var(--color-muted);
}
.legend { display: flex; gap: 0.75rem; align-items: center; }
.swatch {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 2px;
  margin-right: 0.25rem;
}
.swatch--temp { background: #c45c26; }
.swatch--rain { background: #2980b9; }
.actions button {
  margin-left: 0.35rem;
  padding: 0.2rem 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
  font-size: 0.68rem;
}
.combo-chart__svg { width: 100%; height: auto; display: block; }
.axis-lbl { font-size: 9px; fill: #6b7280; font-weight: 600; }
.xlabels text { font-size: 10px; fill: #6b7280; }
</style>
