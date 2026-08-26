<template>
  <div class="status-indicator-card">
    <!-- ENCABEZADO -->
    <div class="card-header">
      <h3>Estado Operativo</h3>
      <span class="timestamp">{{ currentTime }}</span>
    </div>

    <!-- SEMÁFORO PRINCIPAL -->
    <div class="semaphore-container">
      <div class="semaphore-lights">
        <!-- LUZ ROJA -->
        <div
          class="light red"
          :class="{ active: status === 'RED' }"
          :title="`SUSPENSIÓN - ${reason}`"
        >
          <div class="light-glow"></div>
          <span class="label">ROJO</span>
        </div>

        <!-- LUZ AMARILLA -->
        <div
          class="light yellow"
          :class="{ active: status === 'YELLOW' }"
          :title="`ALERTA - ${reason}`"
        >
          <div class="light-glow"></div>
          <span class="label">AMARILLO</span>
        </div>

        <!-- LUZ VERDE -->
        <div
          class="light green"
          :class="{ active: status === 'GREEN' }"
          :title="reason"
        >
          <div class="light-glow"></div>
          <span class="label">VERDE</span>
        </div>
      </div>

      <!-- ICONO DE ESTADO -->
      <div class="status-icon" :style="{ color: statusColor }">
        <component :is="getStatusIcon(status)" :size="64" :stroke-width="1.5" />
      </div>
    </div>

    <!-- INFORMACIÓN DE ESTADO -->
    <div class="status-info">
      <div class="status-title" :style="{ color: statusColor }">
        {{ statusText }}
      </div>
      <p class="status-reason">{{ reason }}</p>
    </div>

    <!-- CONDICIONES CRÍTICAS (si aplica) -->
    <div v-if="criticalConditions.length > 0" class="critical-section">
      <div class="critical-header">
        <AlertTriangle :size="16" class="critical-icon" />
        <h4 class="critical-title">Condiciones Críticas</h4>
      </div>
      <ul class="critical-list">
        <li v-for="(cond, idx) in criticalConditions" :key="idx" class="critical-item">
          {{ cond }}
        </li>
      </ul>
    </div>

    <!-- RECOMENDACIONES -->
    <div v-if="recommendations.length > 0" class="recommendations-section">
      <div class="recommendations-header">
        <Lightbulb :size="16" class="recommendations-icon" />
        <h4 class="recommendations-title">Recomendaciones</h4>
      </div>
      <ul class="recommendations-list">
        <li v-for="(rec, idx) in recommendations" :key="idx" class="recommendation-item">
          {{ rec }}
        </li>
      </ul>
    </div>

    <!-- BARRA DE INDICADORES RÁPIDOS -->
    <div class="quick-indicators">
      <div class="indicator-badge" :class="windClass">
        <Wind :size="14" /> {{ windKmh }} km/h
      </div>
      <div class="indicator-badge" :class="wavesClass">
        <Waves :size="14" /> {{ waveHeightM }}m
      </div>
      <div class="indicator-badge" :class="visibilityClass">
        <Eye :size="14" /> {{ visibilityKm }} km
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import {
  AlertOctagon,
  AlertTriangle,
  CheckCircle,
  Wind,
  Waves,
  Eye,
  Lightbulb
} from 'lucide-vue-next';

const props = defineProps({
  status: {
    type: String,
    required: true,
    validator: (v) => ['GREEN', 'YELLOW', 'RED', 'CRITICAL', 'UNKNOWN'].includes(v),
  },
  reason: {
    type: String,
    default: 'Estado desconocido',
  },
  windKmh: {
    type: Number,
    default: 0,
  },
  waveHeightM: {
    type: Number,
    default: 0,
  },
  visibilityM: {
    type: Number,
    default: 5000,
  },
  iteValue: {
    type: Number,
    default: 50,
  },
  hasResonance: {
    type: Boolean,
    default: false,
  },
});

// STATE
const currentTime = ref('');
let timeInterval;

// COMPUTED
const statusColor = computed(() => {
  const colors = {
    RED: '#dc2626',
    YELLOW: '#f59e0b',
    GREEN: '#10b981',
    CRITICAL: '#7c3aed',
  };
  return colors[props.status] || '#64748b';
});

const statusText = computed(() => {
  const texts = {
    RED: 'OPERACIÓN SUSPENDIDA',
    YELLOW: 'ALERTA OPERATIVA',
    GREEN: 'OPERACIÓN NORMAL',
    CRITICAL: 'CONDICIÓN CRÍTICA',
  };
  return texts[props.status] || 'DESCONOCIDO';
});

const windClass = computed(() => {
  if (props.windKmh > 50) return 'badge-red';
  if (props.windKmh > 35) return 'badge-yellow';
  return 'badge-green';
});

const wavesClass = computed(() => {
  if (props.waveHeightM > 2.5) return 'badge-red';
  if (props.waveHeightM > 1.5) return 'badge-yellow';
  return 'badge-green';
});

const visibilityClass = computed(() => {
  if (props.visibilityM < 200) return 'badge-red';
  if (props.visibilityM < 500) return 'badge-yellow';
  return 'badge-green';
});

const visibilityKm = computed(() => (props.visibilityM / 1000).toFixed(1));

const criticalConditions = computed(() => {
  const conds = [];
  if (props.hasResonance) conds.push('Resonancia pendular detectada (Tpendulum ≈ Tswell)');
  if (props.iteValue > 85) conds.push(`ITE Crítico: ${props.iteValue}% (>85%)`);
  if (props.status === 'CRITICAL') conds.push('Condición de emergencia operativa');
  return conds;
});

const recommendations = computed(() => {
  const recs = [];

  if (props.status === 'RED') {
    recs.push('SUSPENDER izaje inmediatamente');
    recs.push('Esperar a que condiciones mejoren a AMARILLO/VERDE');
    recs.push('Contactar a coordinador operativo');
  }

  if (props.status === 'YELLOW') {
    recs.push('Proceder con vigilancia intensiva');
    recs.push('Monitorear continuamente viento y oleaje');
    recs.push('Reducir altura de carga si es posible');
    recs.push('Mantener comunicación permanente con control de puerto');
  }

  if (props.status === 'GREEN') {
    recs.push('Operación autorizada');
    recs.push('Verificar todos los puntos de amarre');
    recs.push('Mantener radio contacto con grúa');
  }

  if (props.iteValue > 70) {
    recs.push(`ITE en ${props.iteValue}%: Monitorear tensión en espigas`);
  }

  return recs;
});

// MÉTODOS
const getStatusIcon = (status) => {
  const icons = {
    RED: AlertOctagon,
    YELLOW: AlertTriangle,
    GREEN: CheckCircle,
    CRITICAL: AlertOctagon,
  };
  return icons[status] || AlertTriangle;
};

const updateTime = () => {
  const now = new Date();
  currentTime.value = now.toLocaleTimeString('es-CL', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

// LIFECYCLE
onMounted(() => {
  updateTime();
  timeInterval = setInterval(updateTime, 1000);
});

onUnmounted(() => clearInterval(timeInterval));
</script>

<style scoped>
.status-indicator-card {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
  border: 1px solid #334155;
  border-radius: 0.75rem;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

/* ENCABEZADO */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #475569;
  padding-bottom: 1rem;
}

.card-header h3 {
  margin: 0;
  color: #f1f5f9;
  font-size: 1rem;
  font-weight: 600;
}

.timestamp {
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
  color: #64748b;
}

/* SEMÁFORO */
.semaphore-container {
  display: flex;
  gap: 2rem;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rem;
}

.semaphore-lights {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 0.5rem;
  border: 1px solid #334155;
}

.light {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  cursor: default;
  transition: all 0.3s ease;
  border: 2px solid;
}

.light.red {
  background: rgba(220, 38, 38, 0.15);
  border-color: rgba(220, 38, 38, 0.3);
}

.light.red.active {
  background: rgba(220, 38, 38, 0.4);
  border-color: #dc2626;
  box-shadow: 0 0 30px rgba(220, 38, 38, 0.6);
}

.light.yellow {
  background: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.3);
}

.light.yellow.active {
  background: rgba(245, 158, 11, 0.4);
  border-color: #f59e0b;
  box-shadow: 0 0 30px rgba(245, 158, 11, 0.6);
}

.light.green {
  background: rgba(16, 185, 129, 0.15);
  border-color: rgba(16, 185, 129, 0.3);
}

.light.green.active {
  background: rgba(16, 185, 129, 0.4);
  border-color: #10b981;
  box-shadow: 0 0 30px rgba(16, 185, 129, 0.6);
}

.light-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
  border-radius: 50%;
  animation: pulse-glow 2s ease-in-out infinite;
  opacity: 0;
}

.light.active .light-glow {
  opacity: 1;
}

.light .label {
  font-size: 0.6rem;
  font-weight: 700;
  color: #cbd5e1;
  position: relative;
  z-index: 1;
}

@keyframes pulse-glow {
  0%,
  100% {
    box-shadow: inset 0 0 0 2px currentColor;
    opacity: 0;
  }
  50% {
    box-shadow: inset 0 0 0 2px currentColor;
    opacity: 1;
  }
}

.status-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse-icon 1s ease-in-out infinite;
}

@keyframes pulse-icon {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

/* INFORMACIÓN DE ESTADO */
.status-info {
  text-align: center;
  margin-bottom: 1.5rem;
}

.status-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.status-reason {
  margin: 0;
  color: #cbd5e1;
  font-size: 0.875rem;
  line-height: 1.4;
}

/* SECCIÓN CRÍTICA */
.critical-section {
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.2);
  border-radius: 0.375rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.critical-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 0.75rem;
  color: #fca5a5;
}

.critical-title {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.critical-list {
  margin: 0;
  padding: 0 0 0 1.5rem;
  list-style: none;
}

.critical-item {
  color: #cbd5e1;
  font-size: 0.8125rem;
  line-height: 1.5;
  margin-bottom: 0.375rem;
}

.critical-item:before {
  content: '• ';
  color: #dc2626;
  font-weight: bold;
  margin-right: 0.5rem;
}

/* SECCIÓN RECOMENDACIONES */
.recommendations-section {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 0.375rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.recommendations-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 0.75rem;
  color: #6ee7b7;
}

.recommendations-title {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.recommendations-list {
  margin: 0;
  padding: 0 0 0 1.5rem;
  list-style: none;
}

.recommendation-item {
  color: #cbd5e1;
  font-size: 0.8125rem;
  line-height: 1.5;
  margin-bottom: 0.375rem;
}

.recommendation-item:before {
  content: '✓ ';
  color: #10b981;
  font-weight: bold;
  margin-right: 0.5rem;
}

/* INDICADORES RÁPIDOS */
.quick-indicators {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #334155;
}

.indicator-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 0.625rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 600;
  text-align: center;
  transition: all 0.3s ease;
  border: 1px solid;
}

.badge-green {
  background: rgba(16, 185, 129, 0.15);
  color: #6ee7b7;
  border-color: rgba(16, 185, 129, 0.3);
}

.badge-yellow {
  background: rgba(245, 158, 11, 0.15);
  color: #fcd34d;
  border-color: rgba(245, 158, 11, 0.3);
}

.badge-red {
  background: rgba(220, 38, 38, 0.15);
  color: #fca5a5;
  border-color: rgba(220, 38, 38, 0.3);
}

.badge-green:hover,
.badge-yellow:hover,
.badge-red:hover {
  transform: scale(1.05);
}
</style>
