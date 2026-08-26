<template>
  <div class="weather-widget-card">
    <!-- ENCABEZADO -->
    <div class="widget-header">
      <div class="title-with-icon">
        <Cloud class="title-icon" :size="18" />
        <h3>Condiciones Meteorológicas Actuales</h3>
      </div>
      <span class="update-badge">Actualizado hace {{ minutesAgo }}min</span>
    </div>

    <!-- GRID DE VARIABLES -->
    <div class="weather-grid">
      <!-- VIENTO 10m -->
      <div class="weather-item wind-item">
        <div class="item-header">
          <Wind :size="24" class="item-icon" />
          <span class="item-label">Viento 10m</span>
        </div>
        <div class="item-value" :style="{ color: getWindColor(weather.windKmh) }">
          {{ weather.windKmh.toFixed(1) }}
          <span class="item-unit">km/h</span>
        </div>
        <div class="item-subtext">Intensidad: {{ weather.windMs.toFixed(1) }} m/s</div>
        <div class="item-direction">Dirección: {{ getWindDirection(weather.windDirection) }} ({{ weather.windDirection }}°)</div>
      </div>

      <!-- RÁFAGAS -->
      <div class="weather-item gust-item">
        <div class="item-header">
          <Zap :size="24" class="item-icon" />
          <span class="item-label">Ráfagas</span>
        </div>
        <div class="item-value" :style="{ color: getGustColor(weather.gustKmh) }">
          {{ weather.gustKmh.toFixed(1) }}
          <span class="item-unit">km/h</span>
        </div>
        <div class="item-subtext">Pico: {{ getWindGustLevel(weather.gustKmh) }}</div>
        <div class="item-bar">
          <div class="bar-fill" :style="{ width: getBarWidth(weather.gustKmh, 100), backgroundColor: getGustColor(weather.gustKmh) }"></div>
        </div>
      </div>

      <!-- OLEAJE - ALTURA -->
      <div class="weather-item waves-item">
        <div class="item-header">
          <Waves :size="24" class="item-icon" />
          <span class="item-label">Altura Oleaje (Hs)</span>
        </div>
        <div class="item-value" :style="{ color: getWavesColor(weather.waveHeightM) }">
          {{ weather.waveHeightM.toFixed(2) }}
          <span class="item-unit">m</span>
        </div>
        <div class="item-subtext">Significativa</div>
        <div class="item-bar">
          <div class="bar-fill" :style="{ width: getBarWidth(weather.waveHeightM, 5), backgroundColor: getWavesColor(weather.waveHeightM) }"></div>
        </div>
      </div>

      <!-- OLEAJE - PERÍODO -->
      <div class="weather-item period-item">
        <div class="item-header">
          <Tide :size="24" class="item-icon" />
          <span class="item-label">Período Pico (Tp)</span>
        </div>
        <div class="item-value" :style="{ color: getPeriodColor(weather.wavePeriodS) }">
          {{ weather.wavePeriodS.toFixed(1) }}
          <span class="item-unit">s</span>
        </div>
        <div class="item-subtext">{{ getPeriodClass(weather.wavePeriodS) }}</div>
        <div class="item-note" v-if="weather.wavePeriodS >= 14">
          <AlertTriangle :size="12" class="note-icon" /> Período largo - Riesgo de resonancia
        </div>
      </div>

      <!-- VISIBILIDAD -->
      <div class="weather-item visibility-item">
        <div class="item-header">
          <Eye :size="24" class="item-icon" />
          <span class="item-label">Visibilidad</span>
        </div>
        <div class="item-value" :style="{ color: getVisibilityColor(weather.visibilityM) }">
          {{ (weather.visibilityM / 1000).toFixed(1) }}
          <span class="item-unit">km</span>
        </div>
        <div class="item-subtext">{{ getVisibilityLevel(weather.visibilityM) }}</div>
      </div>

      <!-- PRESIÓN -->
      <div class="weather-item pressure-item">
        <div class="item-header">
          <Gauge :size="24" class="item-icon" />
          <span class="item-label">Presión</span>
        </div>
        <div class="item-value">
          {{ weather.pressureMb.toFixed(1) }}
          <span class="item-unit">mb</span>
        </div>
        <div class="item-subtext">{{ getPressureTrend(weather.pressureTrend) }}</div>
      </div>

      <!-- CIELO Y NUBOSIDAD -->
      <div class="weather-item sky-item">
        <div class="item-header">
          <Cloud :size="24" class="item-icon" />
          <span class="item-label">Cielo y Nubosidad</span>
        </div>
        <div class="item-value">
          {{ weather.cloudCover }}
          <span class="item-unit">%</span>
        </div>
        <div class="item-subtext">{{ weather.skyCondition }}</div>
        <div class="item-bar">
          <div class="bar-fill" :style="{ width: weather.cloudCover + '%', backgroundColor: '#94a3b8' }"></div>
        </div>
      </div>
    </div>

    <!-- ALERTAS METEOROLÓGICAS -->
    <div v-if="alerts.length > 0" class="weather-alerts">
      <div class="alerts-title">
        <AlertTriangle :size="14" />
        <h4>Alertas Meteorológicas</h4>
      </div>
      <div v-for="(alert, idx) in alerts" :key="idx" class="alert-item" :class="alert.level">
        <div class="alert-content">
          <component :is="alert.icon" :size="16" class="alert-icon" />
          <span class="alert-text">{{ alert.message }}</span>
        </div>
      </div>
    </div>

    <!-- PRONÓSTICO CORTO 6H -->
    <div class="forecast-mini">
      <div class="forecast-title">
        <TrendingUp :size="14" />
        <h4>Tendencia 6 horas</h4>
      </div>
      <div class="forecast-items">
        <div v-for="hour in [2, 4, 6]" :key="hour" class="mini-forecast-item">
          <span class="hour-label">+{{ hour }}h</span>
          <span class="wind-forecast">{{ estimateWindAtHour(hour) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import {
  Wind,
  Zap,
  Waves,
  Eye,
  Gauge,
  TrendingUp,
  TrendingDown,
  Minus,
  Cloud,
  AlertTriangle,
  Timer,
  CloudFog
} from 'lucide-vue-next';
// Usamos Waves temporalmente para Tide si no está disponible Tide en Lucide
const Tide = Waves;

const props = defineProps({
  weather: {
    type: Object,
    default: () => ({
      windMs: 10,
      windKmh: 36,
      gustKmh: 55,
      waveHeightM: 1.2,
      wavePeriodS: 12,
      visibilityM: 3000,
      pressureMb: 1013.25,
      pressureTrend: 'stable',
      windDirection: 215,
      cloudCover: 75,
      skyCondition: 'Parcialmente nublado',
      timestamp: new Date(),
    }),
  },
});

// COMPUTED
const minutesAgo = computed(() => {
  if (!props.weather.timestamp) return '?';
  const now = new Date();
  const diff = Math.round((now - props.weather.timestamp) / 60000);
  return diff === 0 ? '<1' : diff;
});

const alerts = computed(() => {
  const alerts = [];

  if (props.weather.windKmh > 50) {
    alerts.push({
      level: 'critical',
      icon: Wind,
      message: `Viento muy fuerte: ${props.weather.windKmh.toFixed(1)} km/h`,
    });
  }

  if (props.weather.gustKmh > 70) {
    alerts.push({
      level: 'critical',
      icon: Zap,
      message: `Ráfagas peligrosas: ${props.weather.gustKmh.toFixed(1)} km/h`,
    });
  }

  if (props.weather.waveHeightM > 3) {
    alerts.push({
      level: 'warning',
      icon: Waves,
      message: `Oleaje significativo: ${props.weather.waveHeightM.toFixed(2)}m`,
    });
  }

  if (props.weather.wavePeriodS >= 16) {
    alerts.push({
      level: 'warning',
      icon: Timer,
      message: `Período largo crítico: ${props.weather.wavePeriodS.toFixed(1)}s`,
    });
  }

  if (props.weather.visibilityM < 500) {
    alerts.push({
      level: 'warning',
      icon: CloudFog,
      message: `Visibilidad baja: ${(props.weather.visibilityM / 1000).toFixed(2)}km`,
    });
  }

  return alerts;
});

// MÉTODOS HELPER - COLORES
const getWindColor = (windKmh) => {
  if (windKmh > 50) return '#dc2626'; // RED
  if (windKmh > 35) return '#f59e0b'; // YELLOW
  return '#10b981'; // GREEN
};

const getGustColor = (gustKmh) => {
  if (gustKmh > 70) return '#dc2626';
  if (gustKmh > 50) return '#f59e0b';
  return '#10b981';
};

const getWavesColor = (heightM) => {
  if (heightM > 2.5) return '#dc2626';
  if (heightM > 1.5) return '#f59e0b';
  return '#10b981';
};

const getPeriodColor = (periodS) => {
  if (periodS >= 16) return '#dc2626';
  if (periodS >= 14) return '#f59e0b';
  return '#10b981';
};

const getVisibilityColor = (visM) => {
  if (visM < 200) return '#dc2626';
  if (visM < 500) return '#f59e0b';
  return '#10b981';
};

// MÉTODOS HELPER - TEXTOS
const getWindDirection = (deg) => {
  const directions = {
    N: (d) => d >= 348.75 || d < 11.25,
    NNE: (d) => d >= 11.25 && d < 33.75,
    NE: (d) => d >= 33.75 && d < 56.25,
    ENE: (d) => d >= 56.25 && d < 78.75,
    E: (d) => d >= 78.75 && d < 101.25,
    ESE: (d) => d >= 101.25 && d < 123.75,
    SE: (d) => d >= 123.75 && d < 146.25,
    SSE: (d) => d >= 146.25 && d < 168.75,
    S: (d) => d >= 168.75 && d < 191.25,
    SSW: (d) => d >= 191.25 && d < 213.75,
    SW: (d) => d >= 213.75 && d < 236.25,
    WSW: (d) => d >= 236.25 && d < 258.75,
    W: (d) => d >= 258.75 && d < 281.25,
    WNW: (d) => d >= 281.25 && d < 303.75,
    NW: (d) => d >= 303.75 && d < 326.25,
    NNW: (d) => d >= 326.25 && d < 348.75,
  };

  for (const [dir, checker] of Object.entries(directions)) {
    if (checker(deg)) return dir;
  }
  return 'N/A';
};

const getWindGustLevel = (gustKmh) => {
  if (gustKmh < 30) return 'Ligeras';
  if (gustKmh < 50) return 'Moderadas';
  if (gustKmh < 70) return 'Fuertes';
  return 'Extremas';
};

const getPeriodClass = (periodS) => {
  if (periodS < 8) return 'Corto (viento-mar)';
  if (periodS < 12) return 'Medio';
  if (periodS < 16) return 'Largo (swell)';
  return 'Muy largo (crítico)';
};

const getVisibilityLevel = (visM) => {
  if (visM > 5000) return 'Excelente';
  if (visM > 2000) return 'Buena';
  if (visM > 500) return 'Regular';
  if (visM > 200) return 'Pobre';
  return 'Crítica';
};

const getPressureTrend = (trend) => {
  if (trend === 'rising') return 'Subiendo';
  if (trend === 'falling') return 'Bajando';
  return 'Estable';
};

const getBarWidth = (value, max) => {
  return `${Math.min(100, (value / max) * 100)}%`;
};

const estimateWindAtHour = (hour) => {
  // Simulación simple: tendencia lineal suave
  const variation = Math.sin((hour / 6) * Math.PI) * 5;
  const estimated = props.weather.windKmh + variation;
  return `${Math.max(0, estimated).toFixed(0)} km/h`;
};
</script>

<style scoped>
.weather-widget-card {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
  border: 1px solid #334155;
  border-radius: 0.75rem;
  padding: 1.25rem;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  color: #f1f5f9;
}

.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid #475569;
  padding-bottom: 0.75rem;
}

.title-with-icon {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  color: #38bdf8;
}

.widget-header h3 {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #e2e8f0;
}

.update-badge {
  font-size: 0.7rem;
  color: #94a3b8;
  background: rgba(51, 65, 85, 0.5);
  padding: 0.2rem 0.5rem;
  border-radius: 1rem;
}

/* GRID DE VARIABLES */
.weather-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.weather-item {
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid #334155;
  border-radius: 0.5rem;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.item-icon {
  color: #38bdf8;
}

.item-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #cbd5e1;
  text-transform: uppercase;
}

.item-value {
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.item-unit {
  font-size: 0.875rem;
  font-weight: 500;
}

.item-subtext {
  font-size: 0.75rem;
  color: #94a3b8;
}

.item-direction {
  font-size: 0.75rem;
  color: #0ea5e9;
  font-weight: 600;
  margin-top: 0.25rem;
}

.item-bar {
  margin-top: 0.5rem;
  width: 100%;
  height: 4px;
  background: #334155;
  border-radius: 2px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.item-note {
  font-size: 0.7rem;
  color: #f59e0b;
  margin-top: 0.5rem;
}

/* ALERTAS METEOROLÓGICAS */
.weather-alerts {
  margin-top: 1.5rem;
}

.alerts-title {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0 0 0.75rem 0;
  color: #cbd5e1;
}

.alerts-title h4 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.alert-item {
  padding: 0.75rem;
  border-radius: 0.375rem;
  margin-bottom: 0.5rem;
  border: 1px solid transparent;
}

.alert-item.critical {
  background: rgba(220, 38, 38, 0.1);
  border-color: rgba(220, 38, 38, 0.2);
}

.alert-item.warning {
  background: rgba(245, 158, 11, 0.1);
  border-color: rgba(245, 158, 11, 0.2);
}

.alert-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.alert-text {
  font-size: 0.8125rem;
  color: #e2e8f0;
}

/* PRONÓSTICO CORTO */
.forecast-mini {
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid #475569;
}

.forecast-title {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0 0 0.75rem 0;
  color: #cbd5e1;
}

.forecast-title h4 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.forecast-items {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
}

.mini-forecast-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid #334155;
  border-radius: 0.375rem;
  padding: 0.5rem;
}

.hour-label {
  font-size: 0.7rem;
  color: #94a3b8;
  margin-bottom: 0.25rem;
}

.wind-forecast {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #e2e8f0;
}
</style>
