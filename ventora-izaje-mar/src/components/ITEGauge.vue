<template>
  <div class="ite-gauge">
    <div class="panel-header">
      <Activity class="panel-icon" :size="16" />
      <span class="panel-title">ITE — Turbulencia</span>
      <span class="panel-unit">índice</span>
    </div>

    <div class="gauge-wrapper">
      <svg viewBox="0 0 200 120" class="gauge-svg">
        <!-- Track arc -->
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke="rgba(255,255,255,0.07)"
          stroke-width="14"
          stroke-linecap="round"
        />
        <!-- Colored progress arc -->
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          :stroke="arcColor"
          stroke-width="14"
          stroke-linecap="round"
          :stroke-dasharray="`${arcLength * normalizedValue} ${arcLength}`"
          class="gauge-arc"
        />
        <!-- Zone ticks -->
        <line v-for="tick in ticks" :key="tick.angle"
          :x1="tickPos(tick.angle, 60).x" :y1="tickPos(tick.angle, 60).y"
          :x2="tickPos(tick.angle, 68).x" :y2="tickPos(tick.angle, 68).y"
          stroke="rgba(255,255,255,0.2)" stroke-width="1.5"
        />
        <!-- Needle -->
        <line
          :x1="100" :y1="100"
          :x2="needleEnd.x" :y2="needleEnd.y"
          stroke="#e2eaf6"
          stroke-width="2"
          stroke-linecap="round"
          class="needle"
        />
        <circle cx="100" cy="100" r="5" fill="#e2eaf6" opacity="0.9"/>
        <!-- Center value -->
        <text x="100" y="88" text-anchor="middle" class="gauge-value-text" :fill="arcColor">
          {{ displayValue }}
        </text>
        <text x="100" y="113" text-anchor="middle" class="gauge-label-text">
          {{ statusLabel }}
        </text>
      </svg>
    </div>

    <div class="ite-details">
      <div class="detail-row" v-for="comp in components" :key="comp.label">
        <span class="detail-label">{{ comp.label }}</span>
        <div class="detail-bar-wrap">
          <div class="detail-bar" :style="{ width: comp.pct + '%', background: comp.color }" />
        </div>
        <span class="detail-val">{{ comp.value }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Activity } from 'lucide-vue-next'

const props = defineProps({
  value: { type: Number, default: 0.42 }, // 0–1
  sigma_u: { type: Number, default: 1.8 },
  tke: { type: Number, default: 0.65 },
  ri: { type: Number, default: 0.18 },
})

const arcLength = 251.2 // half-circle ~π*80
const normalizedValue = computed(() => Math.min(Math.max(props.value, 0), 1))

const arcColor = computed(() => {
  if (normalizedValue.value < 0.35) return '#4fc3f7'
  if (normalizedValue.value < 0.65) return '#f59e0b'
  if (normalizedValue.value < 0.85) return '#f97316'
  return '#ef4444'
})

const statusLabel = computed(() => {
  if (normalizedValue.value < 0.35) return 'ESTABLE'
  if (normalizedValue.value < 0.65) return 'MODERADO'
  if (normalizedValue.value < 0.85) return 'TURBULENTO'
  return 'CRÍTICO'
})

const displayValue = computed(() => (props.value * 100).toFixed(0))

const ticks = [
  { angle: 180 }, // 0%
  { angle: 144 }, // 20%
  { angle: 108 }, // 40%
  { angle: 72  }, // 60%
  { angle: 36  }, // 80%
  { angle: 0   }, // 100%
]

function deg2rad(d) { return (d * Math.PI) / 180 }

function tickPos(angleDeg, r) {
  const a = deg2rad(angleDeg)
  return {
    x: 100 + r * Math.cos(Math.PI - a),
    y: 100 - r * Math.sin(a),
  }
}

const needleEnd = computed(() => {
  const angle = normalizedValue.value * 180 // 0→180 degrees over half circle
  const rad = deg2rad(180 - angle)
  return {
    x: 100 + 70 * Math.cos(rad),
    y: 100 - 70 * Math.sin(deg2rad(angle)),
  }
})

const components = computed(() => [
  { label: 'σu', value: props.sigma_u.toFixed(1) + ' m/s', pct: Math.min(props.sigma_u / 5 * 100, 100), color: '#4fc3f7' },
  { label: 'TKE', value: props.tke.toFixed(2) + ' J/kg', pct: Math.min(props.tke / 2 * 100, 100), color: '#f59e0b' },
  { label: 'Ri',  value: props.ri.toFixed(2), pct: Math.min(props.ri / 0.5 * 100, 100), color: '#a78bfa' },
])
</script>

<style scoped>
.ite-gauge {
  background: rgba(10, 20, 40, 0.72);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(100, 160, 255, 0.15);
  border-radius: 12px;
  padding: 16px;
  color: #e2eaf6;
  font-family: 'JetBrains Mono', 'Fira Mono', monospace;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #7ab0e8;
  border-bottom: 1px solid rgba(100, 160, 255, 0.1);
  padding-bottom: 8px;
}
.panel-unit { margin-left: auto; color: rgba(120,160,220,0.5); font-size: 0.7rem; }

.gauge-wrapper { display: flex; justify-content: center; }

.gauge-svg { width: 180px; }

.gauge-arc {
  transition: stroke-dasharray 0.8s ease, stroke 0.5s ease;
}

.needle {
  transition: all 0.8s ease;
  transform-origin: 100px 100px;
}

.gauge-value-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 22px;
  font-weight: 700;
}

.gauge-label-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  fill: rgba(180, 210, 255, 0.5);
  letter-spacing: 0.12em;
}

.ite-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-top: 4px;
  border-top: 1px solid rgba(100,160,255,0.08);
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.68rem;
}

.detail-label {
  min-width: 28px;
  color: rgba(120,160,220,0.6);
  font-style: italic;
}

.detail-bar-wrap {
  flex: 1;
  height: 5px;
  background: rgba(255,255,255,0.06);
  border-radius: 3px;
  overflow: hidden;
}

.detail-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
  opacity: 0.75;
}

.detail-val {
  min-width: 72px;
  text-align: right;
  color: #c8dcf8;
}
</style>
