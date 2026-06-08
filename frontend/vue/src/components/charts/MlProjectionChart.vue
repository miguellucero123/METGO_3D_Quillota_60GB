<script setup>
import { computed, ref } from 'vue'
import ChartTooltip from '@/components/charts/ChartTooltip.vue'
import { exportarSvgPng } from '@/utils/exportChart'
import { exportarDatosCSV } from '@/utils/exportData'

const props = defineProps({
  items: { type: Array, default: () => [] },
  exportName: { type: String, default: 'ml_proyeccion' },
})

const svgRef = ref(null)
const tip = ref({ visible: false, x: 0, y: 0, row: null, slot: '' })

const DOMAIN = {
  temperatura_max: { label: 'T. máx', unit: '°C', min: 0, max: 38 },
  temperatura_min: { label: 'T. mín', unit: '°C', min: -6, max: 22 },
  humedad: { label: 'Humedad', unit: '%', min: 0, max: 100 },
  precipitacion: { label: 'Lluvia', unit: 'mm', min: 0, max: 30 },
  presion: { label: 'Presión', unit: 'hPa', min: 990, max: 1035 },
  viento: { label: 'Viento', unit: 'm/s', min: 0, max: 20 },
}

const W = 720
const H = 248
const pad = { t: 32, r: 12, b: 44, l: 12 }

const rows = computed(() =>
  (props.items || [])
    .filter((r) => r.prediccion != null && !Number.isNaN(Number(r.prediccion)))
    .map((r) => {
      const meta = DOMAIN[r.variable] || {
        label: r.label || r.variable,
        unit: (r.unidad || '').trim() || '',
        min: 0,
        max: 100,
      }
      const actual = Number(r.actual)
      const pred = Number(r.prediccion)
      const vals = [actual, pred].filter((n) => !Number.isNaN(n))
      let ymin = meta.min
      let ymax = meta.max
      if (vals.length) {
        const lo = Math.min(...vals)
        const hi = Math.max(...vals)
        const span = hi - lo || 2
        const margin =
          meta.unit === 'hPa' ? Math.max(3, span * 0.08) : Math.max(1.5, span * 0.18)
        ymin = Math.min(ymin, lo - margin)
        ymax = Math.max(ymax, hi + margin)
      }
      if (ymax <= ymin) ymax = ymin + 1
      const delta = !Number.isNaN(actual) ? pred - actual : null
      return {
        key: r.variable,
        label: meta.label || r.label,
        unit: meta.unit,
        actual: Number.isNaN(actual) ? null : actual,
        prediccion: pred,
        ymin,
        ymax,
        delta,
        predColor: predBarColor(delta, meta.unit),
      }
    })
)

const panelW = computed(() => {
  const n = Math.max(rows.value.length, 1)
  return (W - pad.l - pad.r) / n
})

const innerH = computed(() => H - pad.t - pad.b)

function predBarColor(delta, unit) {
  if (delta == null) return '#3d7ab8'
  const abs = Math.abs(delta)
  const warn =
    (unit === '%' && abs > 8) ||
    (unit === '°C' && abs > 3) ||
    (unit === 'mm' && abs > 5) ||
    (unit === 'hPa' && abs > 5) ||
    (unit === 'm/s' && abs > 3)
  if (warn) return abs > (unit === '%' ? 15 : 6) ? '#dc2626' : '#f97316'
  return '#3d7ab8'
}

function yAt(v, ymin, ymax) {
  const t = (Number(v) - ymin) / (ymax - ymin)
  return pad.t + innerH.value * (1 - t)
}

function yTicks(ymin, ymax) {
  const steps = 4
  const out = []
  for (let i = 0; i <= steps; i++) {
    const v = ymin + ((ymax - ymin) * i) / steps
    out.push({ v: Math.round(v * 10) / 10, y: yAt(v, ymin, ymax) })
  }
  return out
}

function barRect(v, ymin, ymax, panelIndex, slot) {
  const pw = panelW.value
  const x0 = pad.l + panelIndex * pw
  const frac = slot === 'actual' ? 0.34 : 0.66
  const bw = pw * 0.26
  const cx = x0 + pw * frac
  const yTop = yAt(v, ymin, ymax)
  const yBase = H - pad.b
  return {
    x: cx - bw / 2,
    y: yTop,
    w: bw,
    h: Math.max(2, yBase - yTop),
    labelY: yTop - 6,
    cx,
  }
}

function fmtVal(v, unit) {
  if (v == null || Number.isNaN(v)) return '—'
  const n = Number(v)
  if (unit === 'hPa') return `${n.toFixed(1)}`
  if (unit === 'mm') return `${n.toFixed(1)}`
  if (unit === '%') return `${n.toFixed(0)}`
  return `${n.toFixed(1)}`
}

function onBarEnter(e, row, slot) {
  tip.value = { visible: true, x: e.clientX, y: e.clientY, row, slot }
}
function onBarMove(e) {
  if (tip.value.visible) {
    tip.value.x = e.clientX
    tip.value.y = e.clientY
  }
}
function onBarLeave() {
  tip.value.visible = false
}

function exportPng() {
  if (svgRef.value) exportarSvgPng(svgRef.value, props.exportName)
}

function exportCsv() {
  exportarDatosCSV(
    rows.value.map((r) => ({
      variable: r.key,
      observado: r.actual,
      modelo_ml: r.prediccion,
      delta: r.delta,
      unidad: r.unit,
    })),
    props.exportName
  )
}
</script>

<template>
  <div v-if="rows.length" class="ml-chart" role="img" aria-label="Comparación observado vs modelo ML por variable">
    <div class="ml-chart__head">
      <div class="ml-chart__legend">
        <span><i class="swatch swatch--actual" /> Observado (hoy)</span>
        <span><i class="swatch swatch--pred" /> Modelo ML</span>
        <span class="warn-note">Naranja/rojo = error alto</span>
      </div>
      <span class="actions">
        <button type="button" @click="exportCsv">CSV</button>
        <button type="button" @click="exportPng">PNG</button>
      </span>
    </div>
    <svg
      ref="svgRef"
      class="ml-chart__svg"
      :viewBox="`0 0 ${W} ${H}`"
      preserveAspectRatio="xMidYMid meet"
      @mouseleave="onBarLeave"
    >
      <g v-for="(row, pi) in rows" :key="row.key">
        <rect
          :x="pad.l + pi * panelW + 2"
          :y="pad.t - 4"
          :width="panelW - 4"
          :height="innerH + 8"
          class="ml-chart__panel-bg"
          rx="6"
        />
        <text
          :x="pad.l + pi * panelW + panelW / 2"
          :y="16"
          text-anchor="middle"
          class="ml-chart__title"
        >
          {{ row.label }}
        </text>
        <g class="ml-chart__grid">
          <line
            v-for="tick in yTicks(row.ymin, row.ymax)"
            :key="tick.v"
            :x1="pad.l + pi * panelW + 6"
            :x2="pad.l + (pi + 1) * panelW - 6"
            :y1="tick.y"
            :y2="tick.y"
          />
        </g>
        <template v-if="row.actual != null">
          <rect
            v-bind="barRect(row.actual, row.ymin, row.ymax, pi, 'actual')"
            class="ml-chart__bar ml-chart__bar--actual"
            rx="3"
            @mouseenter="onBarEnter($event, row, 'actual')"
            @mousemove="onBarMove"
          />
          <text
            :x="barRect(row.actual, row.ymin, row.ymax, pi, 'actual').cx"
            :y="barRect(row.actual, row.ymin, row.ymax, pi, 'actual').labelY"
            text-anchor="middle"
            class="ml-chart__val"
          >
            {{ fmtVal(row.actual, row.unit) }}
          </text>
        </template>
        <rect
          v-bind="barRect(row.prediccion, row.ymin, row.ymax, pi, 'pred')"
          class="ml-chart__bar"
          :fill="row.predColor"
          rx="3"
          @mouseenter="onBarEnter($event, row, 'pred')"
          @mousemove="onBarMove"
        />
        <text
          :x="barRect(row.prediccion, row.ymin, row.ymax, pi, 'pred').cx"
          :y="barRect(row.prediccion, row.ymin, row.ymax, pi, 'pred').labelY"
          text-anchor="middle"
          class="ml-chart__val ml-chart__val--pred"
        >
          {{ fmtVal(row.prediccion, row.unit) }}
        </text>
        <text
          :x="pad.l + pi * panelW + panelW / 2"
          :y="H - 10"
          text-anchor="middle"
          :class="['ml-chart__delta', row.delta != null && Math.abs(row.delta) > 5 && row.unit === '%' ? 'ml-chart__delta--warn' : '']"
        >
          <template v-if="row.delta != null">Δ {{ row.delta > 0 ? '+' : '' }}{{ row.delta.toFixed(1) }}{{ row.unit }}</template>
        </text>
      </g>
    </svg>
    <ChartTooltip :x="tip.x" :y="tip.y" :visible="tip.visible && tip.row">
      <strong>{{ tip.row?.label }}</strong>
      {{ tip.slot === 'actual' ? 'Observado' : 'Modelo ML' }}:
      {{ fmtVal(tip.slot === 'actual' ? tip.row?.actual : tip.row?.prediccion, tip.row?.unit) }}
      {{ tip.row?.unit }}<br />
      <template v-if="tip.row?.delta != null">
        Δ {{ tip.row.delta > 0 ? '+' : '' }}{{ tip.row.delta.toFixed(1) }}{{ tip.row.unit }}
      </template>
    </ChartTooltip>
    <p class="ml-chart__note">
      Cada panel usa su propia escala. No comparar alturas entre variables distintas.
    </p>
  </div>
  <p v-else class="muted">Sin proyecciones ML disponibles.</p>
</template>

<style scoped>
.ml-chart { width: 100%; position: relative; }
.ml-chart__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
  gap: 0.35rem;
}
.ml-chart__legend {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: var(--color-muted);
  align-items: center;
  flex-wrap: wrap;
}
.warn-note { font-size: 0.68rem; color: #c45c26; }
.actions button {
  padding: 0.2rem 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
  font-size: 0.68rem;
  margin-left: 0.25rem;
}
.swatch {
  display: inline-block;
  width: 0.65rem;
  height: 0.9rem;
  border-radius: 2px;
  margin-right: 0.35rem;
  vertical-align: middle;
}
.swatch--actual { background: #1a5f4a; }
.swatch--pred { background: #3d7ab8; }
.ml-chart__svg { width: 100%; height: auto; display: block; }
.ml-chart__panel-bg {
  fill: rgba(26, 95, 74, 0.04);
  stroke: var(--color-border);
  stroke-width: 1;
}
.ml-chart__title { font-size: 12px; font-weight: 700; fill: var(--color-text); }
.ml-chart__grid line {
  stroke: var(--color-border);
  stroke-width: 1;
  stroke-dasharray: 3 4;
}
.ml-chart__bar--actual { fill: #1a5f4a; }
.ml-chart__val { font-size: 10px; font-weight: 700; fill: #1a5f4a; }
.ml-chart__val--pred { fill: #2a5f8f; }
.ml-chart__delta { font-size: 9px; fill: var(--color-text-secondary); font-variant-numeric: tabular-nums; }
.ml-chart__delta--warn { fill: #c45c26; font-weight: 600; }
.ml-chart__note {
  margin: 0.4rem 0 0;
  font-size: 0.68rem;
  color: var(--color-muted);
  text-align: center;
}
.muted { color: var(--color-muted); font-size: 0.8rem; }
</style>
