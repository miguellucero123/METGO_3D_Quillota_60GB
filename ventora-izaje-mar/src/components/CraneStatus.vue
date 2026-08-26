<template>
  <div class="crane-status">
    <div class="panel-header">
      <Anchor class="panel-icon" :size="16" />
      <span class="panel-title">Estado de Grúas</span>
      <span class="panel-unit">{{ activeCount }}/{{ cranes.length }} activas</span>
    </div>

    <div class="cranes-grid">
      <div
        v-for="crane in cranes"
        :key="crane.id"
        class="crane-card"
        :class="craneCardClass(crane)"
      >
        <!-- Crane silhouette icon -->
        <div class="crane-icon-wrap">
          <svg viewBox="0 0 32 40" class="crane-icon">
            <!-- Vertical mast -->
            <rect x="14" y="8" width="4" height="28" fill="currentColor" opacity="0.8" rx="1"/>
            <!-- Boom -->
            <line x1="16" y1="8" x2="28" y2="2" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
            <line x1="16" y1="8" x2="4"  y2="18" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
            <!-- Hoist cable -->
            <line x1="26" y1="4" x2="24" y2="18" stroke="currentColor" stroke-width="1" opacity="0.5" stroke-dasharray="2 1"/>
            <!-- Hook -->
            <rect x="22" y="18" width="4" height="3" fill="currentColor" opacity="0.7" rx="1"/>
            <!-- Base wheels for RTG -->
            <rect v-if="crane.type === 'RTG'" x="10" y="35" width="12" height="3" fill="currentColor" opacity="0.5" rx="1"/>
          </svg>
        </div>

        <div class="crane-info">
          <div class="crane-id">{{ crane.id }}</div>
          <div class="crane-type-badge" :class="'type-' + crane.type.toLowerCase()">{{ crane.type }}</div>

          <div class="crane-metrics">
            <div class="metric">
              <span class="metric-label">Carga</span>
              <span class="metric-val" :class="loadClass(crane)">{{ crane.load }}t</span>
            </div>
            <div class="metric">
              <span class="metric-label">Límite</span>
              <span class="metric-val">{{ crane.maxLoad }}t</span>
            </div>
          </div>

          <div class="load-bar-track">
            <div
              class="load-bar-fill"
              :class="loadClass(crane)"
              :style="{ width: loadPct(crane) + '%' }"
            />
          </div>

          <div class="crane-status-row">
            <span class="status-dot" :class="statusDotClass(crane)"/>
            <span class="status-text">{{ crane.status }}</span>
            <span class="wind-limit" v-if="crane.windLimit">
              <Wind :size="10" /> &lt;{{ crane.windLimit }}kt
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Global wind alarm banner -->
    <div class="wind-banner" v-if="showWindAlert" :class="'alert-' + windAlertLevel">
      <AlertTriangle :size="14" class="wind-alert-icon" />
      <span>Viento {{ currentWind }}kt — verificar límites de izaje</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Anchor, Wind, AlertTriangle } from 'lucide-vue-next'

const props = defineProps({
  cranes: {
    type: Array,
    default: () => [
      { id: 'STS-01', type: 'STS', status: 'OPERANDO',  load: 38, maxLoad: 65, windLimit: 28, color: 'ok'      },
      { id: 'STS-02', type: 'STS', status: 'EN PAUSA',  load: 0,  maxLoad: 65, windLimit: 28, color: 'idle'    },
      { id: 'RTG-03', type: 'RTG', status: 'OPERANDO',  load: 22, maxLoad: 40, windLimit: 30, color: 'ok'      },
      { id: 'MHC-01', type: 'MHC', status: 'SUSPENDIDO',load: 0,  maxLoad: 30, windLimit: 20, color: 'critical'},
    ]
  },
  currentWind: { type: Number, default: 21 },
})

const activeCount = computed(() => props.cranes.filter(c => c.status === 'OPERANDO').length)

const showWindAlert = computed(() => props.cranes.some(c => props.currentWind >= (c.windLimit || 99) * 0.85))

const windAlertLevel = computed(() => {
  if (props.cranes.some(c => props.currentWind >= c.windLimit)) return 'critical'
  return 'warning'
})

function loadPct(crane) {
  return Math.min((crane.load / crane.maxLoad) * 100, 100)
}

function loadClass(crane) {
  const pct = loadPct(crane)
  if (pct >= 90) return 'load-critical'
  if (pct >= 70) return 'load-warning'
  return 'load-ok'
}

function statusDotClass(crane) {
  if (crane.status === 'OPERANDO')   return 'dot-ok'
  if (crane.status === 'EN PAUSA')   return 'dot-idle'
  if (crane.status === 'SUSPENDIDO') return 'dot-critical'
  return 'dot-idle'
}

function craneCardClass(crane) {
  if (crane.status === 'SUSPENDIDO') return 'card-critical'
  if (crane.status === 'EN PAUSA')   return 'card-idle'
  return 'card-ok'
}
</script>

<style scoped>
.crane-status {
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
.panel-unit { margin-left: auto; color: rgba(120,160,220,0.5); font-size: 0.7rem; }

.cranes-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.crane-card {
  border-radius: 8px;
  padding: 10px;
  display: flex;
  gap: 10px;
  align-items: flex-start;
  transition: border-color 0.3s;
}
.card-ok       { background: rgba(40,120,220,0.06); border: 1px solid rgba(79,195,247,0.2); }
.card-idle     { background: rgba(80,80,80,0.08);   border: 1px solid rgba(150,150,180,0.15); }
.card-critical { background: rgba(180,30,30,0.10);  border: 1px solid rgba(239,68,68,0.35); }

.crane-icon-wrap {
  flex-shrink: 0;
  width: 28px;
}

.crane-icon {
  width: 28px;
  height: 36px;
  color: rgba(120,180,255,0.5);
}
.card-critical .crane-icon { color: rgba(239,68,68,0.5); }
.card-idle     .crane-icon { color: rgba(150,160,180,0.4); }

.crane-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.crane-id   { font-size: 0.75rem; font-weight: 700; color: #c8dcf8; }

.crane-type-badge {
  display: inline-block;
  font-size: 0.6rem;
  padding: 1px 5px;
  border-radius: 4px;
  letter-spacing: 0.06em;
  align-self: flex-start;
}
.type-sts { background: rgba(79,195,247,0.15); color: #4fc3f7; }
.type-rtg { background: rgba(167,139,250,0.15); color: #a78bfa; }
.type-mhc { background: rgba(245,158,11,0.15);  color: #f59e0b; }

.crane-metrics {
  display: flex;
  gap: 10px;
}
.metric { font-size: 0.65rem; }
.metric-label { color: rgba(120,160,220,0.5); }
.metric-val   { font-weight: 700; margin-left: 3px; }

.load-ok       { color: #4fc3f7; }
.load-warning  { color: #f59e0b; }
.load-critical { color: #ef4444; }

.load-bar-track {
  width: 100%;
  height: 4px;
  background: rgba(255,255,255,0.07);
  border-radius: 3px;
  overflow: hidden;
}
.load-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}
.load-bar-fill.load-ok       { background: #4fc3f7; }
.load-bar-fill.load-warning  { background: #f59e0b; }
.load-bar-fill.load-critical { background: #ef4444; }

.crane-status-row {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.62rem;
}
.status-dot {
  width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0;
}
.dot-ok       { background: #4fc3f7; box-shadow: 0 0 6px #4fc3f7; }
.dot-idle     { background: #6b7280; }
.dot-critical { background: #ef4444; box-shadow: 0 0 6px #ef4444; animation: blink 1s ease infinite; }

@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

.status-text { color: rgba(160,200,240,0.7); text-transform: uppercase; letter-spacing: 0.06em; }
.wind-limit  { margin-left: auto; color: rgba(120,160,220,0.45); font-size: 0.6rem; }

.wind-banner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 0.72rem;
  padding: 8px 12px;
  border-radius: 8px;
}
.alert-warning  { background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.35); color: #f59e0b; }
.alert-critical { background: rgba(239,68,68,0.12);  border: 1px solid rgba(239,68,68,0.35);  color: #ef4444; }
</style>
