<template>
  <div class="wind-profile">
    <div class="panel-header">
      <Wind class="panel-icon" :size="16" />
      <span class="panel-title">Perfil de Viento</span>
      <span class="panel-unit">kt / °</span>
    </div>

    <div class="profile-chart">
      <div class="y-axis">
        <span v-for="layer in layers" :key="layer.height" class="y-label">
          {{ layer.height }}m
        </span>
      </div>

      <div class="bars-area">
        <div
          v-for="layer in layers"
          :key="layer.height"
          class="bar-row"
        >
          <div class="bar-track">
            <div
              class="bar-fill"
              :class="speedClass(layer.speed)"
              :style="{ width: barWidth(layer.speed) + '%' }"
            />
          </div>
          <div class="bar-label">
            <span class="speed-val">{{ layer.speed }}kt</span>
            <span class="dir-badge">{{ layer.dir }}°</span>
            <span class="arrow" :style="{ transform: `rotate(${layer.dir}deg)` }">↑</span>
          </div>
        </div>
      </div>
    </div>

    <div class="op-threshold">
      <span class="threshold-label">Límite operacional izaje:</span>
      <span class="threshold-val" :class="thresholdStatus">{{ maxSpeed }}kt / {{ opLimit }}kt</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Wind } from 'lucide-vue-next'

const props = defineProps({
  layers: {
    type: Array,
    default: () => [
      { height: 10,  speed: 12, dir: 210 },
      { height: 20,  speed: 15, dir: 215 },
      { height: 40,  speed: 19, dir: 220 },
      { height: 60,  speed: 22, dir: 225 },
      { height: 80,  speed: 26, dir: 228 },
      { height: 100, speed: 29, dir: 230 },
    ]
  },
  opLimit: {
    type: Number,
    default: 30
  }
})

const maxSpeed = computed(() => Math.max(...props.layers.map(l => l.speed)))

const thresholdStatus = computed(() => {
  const ratio = maxSpeed.value / props.opLimit
  if (ratio >= 1)   return 'status-critical'
  if (ratio >= 0.8) return 'status-warning'
  return 'status-ok'
})

function barWidth(speed) {
  return Math.min((speed / props.opLimit) * 100, 100)
}

function speedClass(speed) {
  const ratio = speed / props.opLimit
  if (ratio >= 1)   return 'bar-critical'
  if (ratio >= 0.8) return 'bar-warning'
  return 'bar-ok'
}
</script>

<style scoped>
.wind-profile {
  background: rgba(10, 20, 40, 0.72);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(100, 160, 255, 0.15);
  border-radius: 12px;
  padding: 16px;
  color: #e2eaf6;
  font-family: 'JetBrains Mono', 'Fira Mono', monospace;
  display: flex;
  flex-direction: column;
  gap: 12px;
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

.panel-unit {
  margin-left: auto;
  color: rgba(120, 160, 220, 0.5);
  font-size: 0.7rem;
}

.profile-chart {
  display: flex;
  gap: 8px;
}

.y-axis {
  display: flex;
  flex-direction: column-reverse;
  justify-content: space-between;
  min-width: 42px;
  font-size: 0.65rem;
  color: rgba(120, 160, 220, 0.55);
  text-align: right;
  padding-right: 4px;
}

.bars-area {
  flex: 1;
  display: flex;
  flex-direction: column-reverse;
  gap: 6px;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bar-track {
  flex: 1;
  height: 10px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 5px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.6s ease;
}

.bar-ok       { background: linear-gradient(90deg, #2a6dd9, #4fc3f7); }
.bar-warning  { background: linear-gradient(90deg, #c9810a, #f59e0b); }
.bar-critical { background: linear-gradient(90deg, #991b1b, #ef4444); }

.bar-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.68rem;
  min-width: 110px;
}

.speed-val { color: #c8dcf8; font-weight: 600; }
.dir-badge {
  color: rgba(120, 160, 220, 0.6);
  background: rgba(255,255,255,0.05);
  border-radius: 4px;
  padding: 1px 4px;
}
.arrow { font-size: 0.75rem; display: inline-block; color: #7ab0e8; }

.op-threshold {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  padding-top: 8px;
  border-top: 1px solid rgba(100, 160, 255, 0.08);
  color: rgba(120, 160, 220, 0.7);
}

.threshold-val { font-weight: 700; }
.status-ok       { color: #4fc3f7; }
.status-warning  { color: #f59e0b; }
.status-critical { color: #ef4444; }
</style>
