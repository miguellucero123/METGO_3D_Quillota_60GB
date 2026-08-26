<template>
  <div class="models-chart-card">
    <header class="chart-head">
      <h3>Comparativa de Modelos Numéricos (Open-Meteo)</h3>
      <p class="subtitle">GFS (EEUU) · ECMWF (Europa) · ICON (Alemania) - Viento a 10m (km/h)</p>
    </header>

    <div v-if="loading" class="state-indicator">
      <div class="spinner"></div>
      <p>Consultando modelos en Open-Meteo...</p>
    </div>
    
    <div v-else-if="error" class="state-indicator error">
      <p>{{ error }}</p>
      <button @click="loadData" class="btn-retry">Reintentar</button>
    </div>

    <div v-else class="chart-container">
      <v-chart class="chart" :option="chartOption" autoresize />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, DataZoomComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent, DataZoomComponent])

const props = defineProps({
  port: {
    type: Object,
    required: true
  }
})

const loading = ref(true)
const error = ref(null)
const apiData = ref(null)

const loadData = async () => {
  if (!props.port || !props.port.coordinates) return
  
  loading.value = true
  error.value = null
  
  const [lat, lon] = props.port.coordinates
  // Solicita los 3 modelos globales para la velocidad del viento a 10m (en km/h automáticamente por OM)
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&hourly=wind_speed_10m&models=gfs_seamless,ecmwf_ifs04,icon_seamless&timezone=auto&wind_speed_unit=kmh`
  
  try {
    const res = await fetch(url)
    if (!res.ok) throw new Error(`HTTP Error ${res.status}`)
    const data = await res.json()
    apiData.value = data
  } catch (err) {
    console.error('Error fetching Open-Meteo models:', err)
    error.value = 'No se pudo cargar la comparativa de modelos desde Open-Meteo.'
  } finally {
    loading.value = false
  }
}

const chartOption = computed(() => {
  if (!apiData.value) return {}
  
  const h = apiData.value.hourly || {}
  const times = (h.time || []).map(t => {
    // Formatear a DD MMM HH:mm
    const d = new Date(t)
    return d.toLocaleString('es-CL', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
  })
  
  return {
    animation: false,
    tooltip: { 
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: '#334155',
      textStyle: { color: '#e2e8f0' }
    },
    legend: {
      data: ['GFS', 'ECMWF', 'ICON'],
      top: 0,
      textStyle: { color: '#cbd5e1' }
    },
    grid: { left: 45, right: 20, top: 40, bottom: 65 },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      { type: 'slider', start: 0, end: 100, bottom: 5, height: 20,
        textStyle: { color: '#94a3b8' },
        borderColor: '#334155',
        fillerColor: 'rgba(14, 165, 233, 0.2)' 
      }
    ],
    xAxis: {
      type: 'category',
      data: times,
      axisLabel: { color: '#94a3b8', fontSize: 10, rotate: 30 },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      name: 'Viento 10m (km/h)',
      nameTextStyle: { color: '#94a3b8', fontSize: 10, padding: [0, 0, 0, 20] },
      axisLabel: { color: '#94a3b8', fontSize: 11 },
      splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } }
    },
    series: [
      {
        name: 'GFS',
        type: 'line',
        data: h.wind_speed_10m_gfs_seamless || [],
        showSymbol: false,
        lineStyle: { width: 2, color: '#3b82f6' }, // Azul
        itemStyle: { color: '#3b82f6' }
      },
      {
        name: 'ECMWF',
        type: 'line',
        data: h.wind_speed_10m_ecmwf_ifs04 || [],
        showSymbol: false,
        lineStyle: { width: 2, color: '#10b981' }, // Verde
        itemStyle: { color: '#10b981' }
      },
      {
        name: 'ICON',
        type: 'line',
        data: h.wind_speed_10m_icon_seamless || [],
        showSymbol: false,
        lineStyle: { width: 2, color: '#f59e0b' }, // Amarillo
        itemStyle: { color: '#f59e0b' }
      }
    ]
  }
})

watch(() => props.port, loadData, { deep: true })
onMounted(loadData)
</script>

<style scoped>
.models-chart-card {
  background: var(--color-surface, rgba(30, 41, 59, 0.6));
  border: 1px solid var(--color-border, #334155);
  border-radius: 12px;
  padding: 1.25rem;
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
}

.chart-head h3 {
  margin: 0 0 0.25rem;
  font-size: 1.1rem;
  color: #f1f5f9;
}

.chart-head .subtitle {
  margin: 0 0 1rem;
  font-size: 0.85rem;
  color: #94a3b8;
}

.state-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #94a3b8;
}

.state-indicator.error {
  color: #fca5a5;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  border-top-color: #0ea5e9;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn-retry {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.chart-container {
  height: 350px;
  width: 100%;
}

.chart {
  width: 100%;
  height: 100%;
}
</style>
