<template>
  <div class="ventora-portal">
    <!-- ENCABEZADO -->
    <header class="ventora-header">
      <div class="header-content">
        <h1>VENTORA Izaje Portuario</h1>
        <p class="subtitle">Pronóstico y Alerta para Operaciones Costeras</p>
      </div>
      <div class="header-time">
        <span>{{ currentTime }}</span>
      </div>
    </header>

    <!-- SELECTOR DE PUERTO -->
    <section class="port-selector">
      <div class="selector-group">
        <label>Puerto Operativo</label>
        <select v-model="selectedPortId" @change="onPortChange" class="port-select">
          <option value="">-- Selecciona Puerto --</option>
          <option v-for="(port, id) in appConfig.ports" :key="id" :value="id">
            {{ port.name }} ({{ port.region }})
          </option>
        </select>
      </div>

      <!-- SELECTOR DE ALTURA DE CARGA -->
      <div v-if="selectedPort" class="selector-group">
        <label>Altura de Carga</label>
        <div class="height-buttons">
          <button
            v-for="(config, height) in appConfig.liftRestrictions"
            :key="height"
            @click="selectedHeight = height"
            :class="['height-btn', { active: selectedHeight === height }]"
            :style="{ borderColor: config.color }"
          >
            {{ height }}
            <small>{{ config.label.split('(')[1] }}</small>
          </button>
        </div>
      </div>
    </section>

    <!-- NAVEGACIÓN DE PESTAÑAS (TABS) -->
    <nav v-if="selectedPort" class="portal-tabs">
      <button :class="{ active: activeTab === 'resumen' }" @click="activeTab = 'resumen'">
        <Activity class="tab-icon" :size="16" /> Resumen Operativo
      </button>
      <button :class="{ active: activeTab === 'meteo' }" @click="activeTab = 'meteo'">
        <Cloud class="tab-icon" :size="16" /> Meteorología
      </button>
      <button :class="{ active: activeTab === 'mareas' }" @click="activeTab = 'mareas'">
        <Anchor class="tab-icon" :size="16" /> Mareas & Fondeo
      </button>
      <button :class="{ active: activeTab === 'experto' }" @click="activeTab = 'experto'">
        <Activity class="tab-icon" :size="16" /> Análisis Experto
      </button>
      <button :class="{ active: activeTab === 'informes' }" @click="activeTab = 'informes'">
        <FileText class="tab-icon" :size="16" /> Informes
      </button>
    </nav>

    <!-- CONTENIDO PRINCIPAL -->
    <div v-if="selectedPort && selectedHeight" class="portal-main">
      
      <!-- PESTAÑA 1: RESUMEN OPERATIVO -->
      <div v-if="activeTab === 'resumen'" class="tab-content summary-grid">
        <div class="primary-col">
          <StatusIndicator :status="currentStatus.status" :reason="currentStatus.reason" />
        </div>
        <div class="secondary-col">
          <CraneStatus v-if="selectedPort.cranes" :cranes="selectedPort.cranes" :currentWind="currentWeather.windKmh / 1.852" />
          <AlertPanel :initialAlerts="activeAlerts.length ? activeAlerts : undefined" />
        </div>
      </div>

      <!-- PESTAÑA 2: METEOROLOGÍA -->
      <div v-if="activeTab === 'meteo'" class="tab-content meteo-grid">
        <div class="full-width">
          <WeatherWidget :weather="currentWeather" />
        </div>
        <div class="half-col">
          <WindProfile :layers="windLayers" :opLimit="selectedHeightConfig.thresholds?.YELLOW?.wind / 1.852 || 30" />
        </div>
        <div class="half-col">
          <ITEGauge :value="currentITE.ITE / 100" />
        </div>
        <div class="full-width">
          <MeteoModelsChart :port="selectedPort" />
        </div>
      </div>

      <!-- PESTAÑA 3: MAREAS Y FONDEO -->
      <div v-if="activeTab === 'mareas'" class="tab-content tides-grid">
        <div class="half-col">
          <AnchorageMap :port="selectedPort" :windDir="currentWeather.windDirection" :windSpeed="currentWeather.windKmh / 1.852" />
        </div>
        <div class="half-col">
          <TideChart :tides="tidesForecast" />
        </div>
      </div>

      <!-- PESTAÑA 4: ANÁLISIS EXPERTO -->
      <div v-if="activeTab === 'experto'" class="tab-content experto-grid">
        <SpatiPanelView />
      </div>

      <!-- PESTAÑA 5: INFORMES -->
      <div v-if="activeTab === 'informes'" class="tab-content reports-grid">
        <InformesView />
      </div>

    </div>

    <!-- ESTADO: Sin Puerto Seleccionado -->
    <div v-else class="empty-state">
      <p>Seleccione un terminal marítimo para iniciar el monitoreo</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted, provide } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Activity, Cloud, Anchor, FileText } from 'lucide-vue-next';

import appConfig from '@/site.config.js';
import { determineStatus, windProfileMulti, calculateITE, predictTides } from '@/utils/oceanPhysics.js';
import { fetchSpatiPuertoPronostico } from '@/services/spatiApi.js';

import StatusIndicator from './StatusIndicator.vue';
import WeatherWidget from './WeatherWidget.vue';
import WindProfile from './WindProfile.vue';
import ITEGauge from './ITEGauge.vue';
import AnchorageMap from './AnchorageMap.vue';
import CraneStatus from './CraneStatus.vue';
import AlertPanel from './AlertPanel.vue';
import TideChart from './TideChart.vue';
import MeteoModelsChart from './MeteoModelsChart.vue';
import InformesView from '@/views/InformesView.vue';
import SpatiPanelView from '@/views/SpatiPanelView.vue';

// ESTADO REACTIVO
const route = useRoute();
const router = useRouter();

const selectedPortId = ref('IQQ');
const selectedHeight = ref('40m');
const activeTab = ref('resumen');
const currentTime = ref('');

const currentWeather = reactive({
  windMs: 12.5,
  windKmh: 45,
  gustKmh: 65,
  waveHeightM: 1.2,
  wavePeriodS: 12,
  visibilityM: 2000,
  pressureMb: 1013.2,
  pressureTrend: 'stable',
  windDirection: 215,
  cloudCover: 75,
  skyCondition: 'Parcialmente nublado',
  timestamp: new Date(),
});
const activeAlerts = ref([]);
const tidesForecast = ref([]);
const windProfiles = reactive({});

// COMPUTED
const selectedPort = computed(() => appConfig.ports[selectedPortId.value]);

const currentStatus = computed(() => {
  if (!selectedPort.value || !selectedHeight.value) return { status: 'UNKNOWN' };
  return determineStatus(
    currentWeather.windKmh,
    currentWeather.gustKmh,
    currentWeather.waveHeightM,
    currentWeather.visibilityM,
    selectedHeight.value
  );
});

const currentITE = computed(() => {
  if (!selectedHeight.value) return { ITE: 0, riskLevel: 'GREEN' };
  return calculateITE(
    currentWeather.windMs,
    currentWeather.waveHeightM,
    currentWeather.wavePeriodS
  );
});

const selectedHeightConfig = computed(() => {
  return appConfig.liftRestrictions[selectedHeight.value] || {};
});

const windLayers = computed(() => {
  return [10, 40, 100, 200].map(h => ({
    height: h,
    speed: ((windProfiles[h] || currentWeather.windMs) * 1.94384).toFixed(1), // m/s to knots
    dir: currentWeather.windDirection
  }));
});

// PROVISIÓN PARA COMPONENTE DE INFORMES
// Se inyectan estas variables para que InformesView las consuma nativamente
provide('faena', selectedPortId);
provide('faenaMeta', computed(() => ({
  nombre: selectedPort.value ? selectedPort.value.name : 'Puerto',
  slug: selectedPortId.value
})));

// MÉTODOS
const onPortChange = async () => {
  selectedHeight.value = '40m';
  if (selectedPortId.value) {
    try {
      const data = await fetchSpatiPuertoPronostico(selectedPortId.value);
      const current = data?.hourly_states?.[0] || {};
      
      currentWeather.windKmh = current.wind_surface_kmh || 45;
      currentWeather.windMs = currentWeather.windKmh / 3.6;
      currentWeather.gustKmh = current.gust_kmh || currentWeather.windKmh * 1.3;
      currentWeather.waveHeightM = current.wave_params?.Hs || 1.2;
      currentWeather.wavePeriodS = current.wave_params?.Tp || 12;
      currentWeather.visibilityM = current.visibility_m || 3000;
      currentWeather.pressureMb = current.pressure_mb || 1013.5;
      currentWeather.pressureTrend = current.pressure_trend || 'stable';
      currentWeather.windDirection = current.wind_dir || 215;
      currentWeather.cloudCover = current.cloud_cover ?? 75;
      currentWeather.skyCondition = current.sky_condition || (currentWeather.cloudCover > 80 ? 'Nublado' : currentWeather.cloudCover > 40 ? 'Parcialmente nublado' : 'Despejado');
      currentWeather.timestamp = new Date();

      Object.assign(windProfiles, windProfileMulti(currentWeather.windMs));
      tidesForecast.value = predictTides(new Date(), 24);

      if (data.alerts && data.alerts.length > 0) {
        activeAlerts.value = data.alerts.map((a, i) => ({
          id: `API-${i}`,
          severity: a.level === 3 ? 'critical' : a.level === 2 ? 'warning' : 'info',
          title: a.type || 'Alerta Meteorológica',
          detail: a.description || 'Condiciones límite detectadas',
          source: 'Modelo Spati',
          time: new Date().toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' })
        }));
      } else {
        activeAlerts.value = [];
      }
    } catch (error) {
      console.error('Error fetching forecast:', error);
    }
  }
};

const updateClock = () => {
  const now = new Date();
  currentTime.value = now.toLocaleTimeString('es-CL', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

// LIFECYCLE
let clockInterval;
onMounted(() => {
  updateClock();
  clockInterval = setInterval(updateClock, 1000);
  
  if (route.params.puerto && appConfig.ports[route.params.puerto]) {
    selectedPortId.value = route.params.puerto;
  }
  
  if (selectedPortId.value) onPortChange();
});

watch(() => selectedPortId.value, (newVal) => {
  if (newVal !== route.params.puerto && newVal) {
    router.push(`/p/${newVal}/`);
  }
});

onUnmounted(() => clearInterval(clockInterval));
</script>

<style scoped>
.ventora-portal {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #f1f5f9;
  font-family: var(--font-family, 'Inter, sans-serif');
  overflow: hidden;
}

/* ENCABEZADO */
.ventora-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: rgba(15, 23, 42, 0.95);
  border-bottom: 2px solid #0ea5e9;
  flex-shrink: 0;
}

.header-content h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
}

.subtitle {
  margin: 0.25rem 0 0;
  color: #94a3b8;
  font-size: 0.875rem;
}

.header-time {
  font-size: 1.125rem;
  font-weight: 500;
  font-family: 'Courier New', monospace;
  color: #38bdf8;
}

/* SELECTOR DE PUERTO */
.port-selector {
  display: flex;
  gap: 2rem;
  padding: 1rem 2rem;
  background: rgba(30, 41, 59, 0.8);
  border-bottom: 1px solid #334155;
  align-items: flex-end;
  flex-shrink: 0;
}

.selector-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.selector-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #cbd5e1;
}

.port-select {
  padding: 0.5rem 0.75rem;
  background: #1e293b;
  color: #f1f5f9;
  border: 1px solid #0ea5e9;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
}

.height-buttons {
  display: flex;
  gap: 0.75rem;
}

.height-btn {
  padding: 0.5rem 1rem;
  background: transparent;
  border: 2px solid #475569;
  border-radius: 0.375rem;
  color: #cbd5e1;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.height-btn.active {
  background: rgba(14, 165, 233, 0.2);
  color: #38bdf8;
  border-color: #0ea5e9;
}

/* TABS NAVEGACIÓN */
.portal-tabs {
  display: flex;
  gap: 1rem;
  padding: 0 2rem;
  background: rgba(15, 23, 42, 0.95);
  border-bottom: 1px solid #334155;
  flex-shrink: 0;
}

.portal-tabs button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  padding: 1rem 0.5rem;
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.portal-tabs button:hover {
  color: #e2e8f0;
}

.portal-tabs button.active {
  color: #38bdf8;
  border-bottom-color: #0ea5e9;
}

.tab-icon {
  opacity: 0.8;
}

/* CONTENIDO PRINCIPAL */
.portal-main {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
}

.tab-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

/* LAYOUTS ESPECÍFICOS POR PESTAÑA */
.summary-grid {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 1.5rem;
}

.secondary-col {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.meteo-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.full-width {
  grid-column: 1 / -1;
}

.tides-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.experto-grid {
  display: flex;
  flex-direction: column;
}

.reports-grid {
  display: flex;
  justify-content: center;
  padding-top: 1rem;
}

.reports-grid > * {
  width: 100%;
  max-width: 800px;
}

/* ESTADO VACÍO */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  font-size: 1.25rem;
  color: #64748b;
}

/* RESPONSIVIDAD */
@media (max-width: 1024px) {
  .summary-grid, .meteo-grid, .tides-grid {
    grid-template-columns: 1fr;
  }
}
</style>
