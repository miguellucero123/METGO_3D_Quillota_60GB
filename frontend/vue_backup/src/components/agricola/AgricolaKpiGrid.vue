<script setup>
import { computed } from 'vue'
import { Thermometer, Droplets, CloudRain } from 'lucide-vue-next'
import { tempColor, humedadColor, riegoColor } from '@/utils/agroColors'

const props = defineProps({
  resumen: { type: Object, required: true },
  riegoMm: { type: Number, default: 0 },
  cultivo: { type: String, default: 'palto' },
})

const tMedia = computed(() => props.resumen.temperatura ?? props.resumen.temperatura_media)
const humedad = computed(() => props.resumen.humedad ?? props.resumen.humedad_relativa)
const tipoDato = computed(() => props.resumen.tipo_dato ?? 'pronostico')

const kpis = computed(() => [
  {
    key: 'temp',
    label: 'T° media',
    icon: Thermometer,
    valor: `${tMedia.value != null ? Number(tMedia.value).toFixed(1) : '--'}°C`,
    sub: `Mín ${props.resumen.temperatura_min ?? '--'}°C · Máx ${props.resumen.temperatura_max ?? '--'}°C`,
    color: tempColor(tMedia.value ?? 15),
    badge: tipoDato.value === 'observado' ? 'Observado' : 'Pronóstico',
    badgeClass: tipoDato.value === 'observado' ? 'badge-obs' : 'badge-pron',
  },
  {
    key: 'humedad',
    label: 'Humedad',
    icon: Droplets,
    valor: `${humedad.value != null ? Number(humedad.value).toFixed(0) : '--'}%`,
    sub: 'HR ambiente actual',
    color: humedadColor(humedad.value ?? 60),
  },
  {
    key: 'precip',
    label: 'Precipitación',
    icon: CloudRain,
    valor: `${props.resumen.precipitacion ?? 0} mm`,
    sub: 'Acumulado hoy',
    color: 'var(--color-text)',
  },
  {
    key: 'riego',
    label: 'Riego sugerido',
    icon: Droplets,
    valor: `${props.riegoMm} mm`,
    sub: props.riegoMm === 0 ? 'Suspendido (helada/lluvia)' : `Para ${props.cultivo} hoy`,
    color: riegoColor(props.riegoMm),
  },
])
</script>

<template>
  <div class="kpi-grid">
    <div v-for="kpi in kpis" :key="kpi.key" class="kpi-card">
      <div class="kpi-label">
        <component :is="kpi.icon" :size="14" aria-hidden="true" />
        {{ kpi.label }}
        <span v-if="kpi.badge" class="kpi-badge" :class="kpi.badgeClass">{{ kpi.badge }}</span>
      </div>
      <div class="kpi-value" :style="{ color: kpi.color }">{{ kpi.valor }}</div>
      <div class="kpi-sub">{{ kpi.sub }}</div>
    </div>
  </div>
</template>

<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
}
.kpi-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.kpi-label {
  font-size: 11px;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  display: flex;
  align-items: center;
  gap: 5px;
  flex-wrap: wrap;
}
.kpi-badge {
  font-size: 9px;
  padding: 1px 6px;
  border-radius: 100px;
  text-transform: none;
  letter-spacing: 0;
}
.badge-obs {
  background: var(--color-success-bg);
  color: var(--color-success);
}
.badge-pron {
  background: var(--color-warning-bg);
  color: var(--color-warning);
}
.kpi-value {
  font-size: 22px;
  font-weight: 600;
  line-height: 1;
}
.kpi-sub {
  font-size: 11px;
  color: var(--color-muted);
}
</style>
