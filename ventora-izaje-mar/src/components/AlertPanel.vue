<template>
  <div class="alert-panel">
    <div class="panel-header">
      <AlertTriangle class="panel-icon" :size="16" />
      <span class="panel-title">Alertas Operacionales</span>
      <div class="badge-counts">
        <span class="count-badge badge-critical" v-if="countBySeverity.critical">
          {{ countBySeverity.critical }}
        </span>
        <span class="count-badge badge-warning" v-if="countBySeverity.warning">
          {{ countBySeverity.warning }}
        </span>
        <span class="count-badge badge-info" v-if="countBySeverity.info">
          {{ countBySeverity.info }}
        </span>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="!activeAlerts.length" class="empty-state">
      <CheckCircle class="empty-icon" :size="24" />
      <span>Sin alertas activas</span>
    </div>

    <!-- Alert list -->
    <transition-group name="alert-list" tag="div" class="alerts-list" v-else>
      <div
        v-for="alert in activeAlerts"
        :key="alert.id"
        class="alert-item"
        :class="'sev-' + alert.severity"
      >
        <div class="alert-left">
          <span class="sev-indicator" :class="'ind-' + alert.severity"/>
          <div class="alert-body">
            <div class="alert-title">{{ alert.title }}</div>
            <div class="alert-detail">{{ alert.detail }}</div>
            <div class="alert-meta">
              <span class="alert-source">{{ alert.source }}</span>
              <span class="alert-time">{{ alert.time }}</span>
            </div>
          </div>
        </div>
        <div class="alert-actions">
          <button class="ack-btn" @click="acknowledge(alert.id)" v-if="!alert.acked" title="Reconocer">✓</button>
          <button class="dismiss-btn" @click="dismiss(alert.id)" title="Descartar">×</button>
        </div>
      </div>
    </transition-group>

    <div class="panel-footer">
      <span class="footer-ts">Actualizado: {{ lastUpdate }}</span>
      <button class="clear-btn" @click="clearAcked" v-if="ackedCount">
        Limpiar reconocidas ({{ ackedCount }})
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { AlertTriangle, CheckCircle } from 'lucide-vue-next'

const props = defineProps({
  initialAlerts: {
    type: Array,
    default: () => [
      {
        id: 'ALT001', severity: 'critical',
        title: 'Viento supera límite MHC-01',
        detail: 'Viento 21kt > límite operacional 20kt. Izaje suspendido.',
        source: 'SeaStateEngine', time: '14:32',
      },
      {
        id: 'ALT002', severity: 'warning',
        title: 'Hs en umbral de alerta',
        detail: 'Altura significativa de ola Hs = 1.8m (límite: 2.0m).',
        source: 'OceanModule', time: '14:28',
      },
      {
        id: 'ALT003', severity: 'warning',
        title: 'Resonancia pendular detectada',
        detail: 'Tp/T_pendulo ≈ 0.92 en STS-01. Reducir velocidad de izaje.',
        source: 'CraneDyn', time: '14:15',
      },
      {
        id: 'ALT004', severity: 'info',
        title: 'Marea bajante — acceso canal',
        detail: 'Nivel actual −0.4m sobre MLLW. Próxima pleamar en 3h40m.',
        source: 'TideModule', time: '13:55',
      },
    ]
  }
})

const alerts = ref(props.initialAlerts.map(a => ({ ...a, acked: false, dismissed: false })))

const activeAlerts = computed(() =>
  alerts.value
    .filter(a => !a.dismissed)
    .sort((a, b) => {
      const order = { critical: 0, warning: 1, info: 2 }
      return order[a.severity] - order[b.severity]
    })
)

const countBySeverity = computed(() => ({
  critical: activeAlerts.value.filter(a => a.severity === 'critical').length,
  warning:  activeAlerts.value.filter(a => a.severity === 'warning').length,
  info:     activeAlerts.value.filter(a => a.severity === 'info').length,
}))

const ackedCount = computed(() => activeAlerts.value.filter(a => a.acked).length)

const lastUpdate = computed(() => {
  const now = new Date()
  return `${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}`
})

function acknowledge(id) {
  const a = alerts.value.find(x => x.id === id)
  if (a) a.acked = true
}

function dismiss(id) {
  const a = alerts.value.find(x => x.id === id)
  if (a) a.dismissed = true
}

function clearAcked() {
  alerts.value.forEach(a => { if (a.acked) a.dismissed = true })
}
</script>

<style scoped>
.alert-panel {
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

.badge-counts { margin-left: auto; display: flex; gap: 4px; }
.count-badge {
  font-size: 0.62rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 10px;
}
.badge-critical { background: rgba(239,68,68,0.25);  color: #fca5a5; }
.badge-warning  { background: rgba(245,158,11,0.20); color: #fcd34d; }
.badge-info     { background: rgba(79,195,247,0.15); color: #7dd3fc; }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 20px;
  color: rgba(120,160,220,0.4);
  font-size: 0.72rem;
}
.empty-icon { color: rgba(16, 185, 129, 0.6); }

.alerts-list { display: flex; flex-direction: column; gap: 6px; }

.alert-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  border-radius: 8px;
  padding: 10px 12px;
  transition: opacity 0.3s;
}

.sev-critical { background: rgba(180,20,20,0.12);  border: 1px solid rgba(239,68,68,0.30); }
.sev-warning  { background: rgba(180,100,0,0.10);  border: 1px solid rgba(245,158,11,0.25); }
.sev-info     { background: rgba(10,80,160,0.10);  border: 1px solid rgba(79,195,247,0.20); }

.alert-left { display: flex; gap: 10px; flex: 1; min-width: 0; }

.sev-indicator {
  width: 3px;
  border-radius: 4px;
  flex-shrink: 0;
  align-self: stretch;
}
.ind-critical { background: #ef4444; box-shadow: 0 0 8px #ef4444; }
.ind-warning  { background: #f59e0b; box-shadow: 0 0 8px #f59e0b; }
.ind-info     { background: #4fc3f7; }

.alert-body { display: flex; flex-direction: column; gap: 2px; min-width: 0; }

.alert-title {
  font-size: 0.72rem;
  font-weight: 700;
  color: #dde8f8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.alert-detail {
  font-size: 0.65rem;
  color: rgba(160,200,240,0.65);
  line-height: 1.4;
}

.alert-meta {
  display: flex;
  gap: 8px;
  font-size: 0.6rem;
  color: rgba(100,140,200,0.45);
  margin-top: 2px;
}

.alert-source { font-style: italic; }

.alert-actions { display: flex; gap: 4px; flex-shrink: 0; }

.ack-btn, .dismiss-btn {
  width: 22px; height: 22px;
  border-radius: 5px;
  border: none;
  cursor: pointer;
  font-size: 0.8rem;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s;
}
.ack-btn     { background: rgba(79,195,247,0.12); color: #4fc3f7; }
.ack-btn:hover { background: rgba(79,195,247,0.25); }
.dismiss-btn   { background: rgba(100,100,120,0.12); color: rgba(180,190,210,0.5); }
.dismiss-btn:hover { background: rgba(200,50,50,0.2); color: #ef4444; }

.panel-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.62rem;
  color: rgba(100,140,200,0.4);
  border-top: 1px solid rgba(100,160,255,0.08);
  padding-top: 8px;
}

.clear-btn {
  background: rgba(100,100,120,0.15);
  border: 1px solid rgba(150,160,200,0.2);
  border-radius: 5px;
  padding: 2px 8px;
  font-size: 0.62rem;
  color: rgba(160,190,230,0.6);
  cursor: pointer;
  font-family: inherit;
  transition: background 0.2s;
}
.clear-btn:hover { background: rgba(100,100,120,0.3); }

/* Transition animations */
.alert-list-enter-active { transition: all 0.35s ease; }
.alert-list-leave-active { transition: all 0.25s ease; }
.alert-list-enter-from   { opacity: 0; transform: translateY(-8px); }
.alert-list-leave-to     { opacity: 0; transform: translateX(12px); }
</style>
