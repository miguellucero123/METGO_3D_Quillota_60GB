<script setup>
import { onMounted } from 'vue'
import { Gauge, Thermometer, CloudRain, BellRing, Wind } from 'lucide-vue-next'
import MetricCard from '@/components/ui/MetricCard.vue'
import SectionCard from '@/components/ui/SectionCard.vue'
import { useApiCall } from '@/composables/useApiCall'
import { fetchMetricasGlobales } from '@/api/metgoApi'

const { data: m, loading, error, run } = useApiCall(fetchMetricasGlobales)

onMounted(run)
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Métricas globales</h2>
      <p class="page-subtitle">KPIs consolidados del valle</p>
    </header>

    <p v-if="loading" class="skeleton">Cargando métricas…</p>
    <p v-else-if="error" class="error-text">{{ error }}</p>
    <template v-else-if="m">
      <div class="card-grid card-grid--wide">
        <MetricCard label="Estaciones activas" :value="m.estaciones_activas" :icon="Gauge" />
        <MetricCard
          label="T° media máx"
          :value="`${m.temperatura_media_max ?? '—'}°C`"
          :icon="Thermometer"
        />
        <MetricCard
          label="T° media mín"
          :value="`${m.temperatura_media_min ?? '—'}°C`"
          :icon="Thermometer"
        />
        <MetricCard
          label="Precip. total"
          :value="`${m.precipitacion_total} mm`"
          :icon="CloudRain"
        />
        <MetricCard label="Viento máx" :value="`${m.viento_max} km/h`" :icon="Wind" />
        <MetricCard label="Alertas" :value="m.alertas_activas" :icon="BellRing" />
      </div>
      <SectionCard title="Estaciones incluidas" :subtitle="m.actualizado">
        <p class="muted">{{ (m.estaciones || []).join(' · ') }}</p>
      </SectionCard>
    </template>
  </div>
</template>

<style scoped>
.error-text {
  color: var(--color-danger, #b91c1c);
}
</style>
