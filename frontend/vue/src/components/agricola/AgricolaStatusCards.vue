<script setup>
import { computed } from 'vue'
import { ThermometerSnowflake, Droplets, Wind, Bug } from 'lucide-vue-next'
import {
  riesgoHeladaPorCultivo,
  necesidadRiego,
  condicionViento,
} from '@/utils/agroInsights'
import { riesgoHelada } from '@/utils/agroColors'

const props = defineProps({
  resumen: { type: Object, required: true },
  recomendaciones: { type: Array, default: () => [] },
  cultivo: { type: String, default: 'palto' },
})

const slugHelada = computed(() => (props.cultivo === 'uva' ? 'vid' : props.cultivo))

const cards = computed(() => {
  const r = props.resumen
  const hel = riesgoHelada(r.temperatura_min)
  const helCult = riesgoHeladaPorCultivo(r.temperatura_min, slugHelada.value)
  const riego = necesidadRiego(r.humedad, r.precipitacion)
  const viento = condicionViento(r.viento)
  const plaga = props.recomendaciones.find(
    (rec) =>
      String(rec.codigo || rec.cultivo || '').toLowerCase().includes('plaga') ||
      String(rec.accion || rec.texto || '').toLowerCase().includes('plaga')
  )

  return [
    {
      key: 'helada',
      icon: ThermometerSnowflake,
      title: 'Helada',
      value: hel.label,
      hint: helCult.label,
      nivel: hel.nivel,
      style: { color: hel.color, background: hel.bg },
    },
    {
      key: 'humedad',
      icon: Droplets,
      title: 'Humedad / riego',
      value: riego.label,
      hint: `${r.humedad ?? '—'}% HR`,
      nivel: riego.nivel,
    },
    {
      key: 'viento',
      icon: Wind,
      title: 'Viento',
      value: viento.label,
      hint: r.viento != null ? `${r.viento} m/s` : 'Sin dato',
      nivel: viento.nivel,
    },
    {
      key: 'plagas',
      icon: Bug,
      title: 'Plagas / sanidad',
      value: plaga ? plaga.accion || plaga.texto || 'Alerta activa' : 'Sin alertas',
      hint: plaga?.motivo || 'Motor módulo 02',
      nivel: plaga ? 'medium' : 'low',
    },
  ]
})

function cardClass(nivel) {
  if (nivel === 'high' || nivel === 'critico' || nivel === 'alto') return 'card-danger'
  if (nivel === 'medium' || nivel === 'moderado') return 'card-warn'
  return 'card-ok'
}
</script>

<template>
  <div class="status-grid">
    <article
      v-for="c in cards"
      :key="c.key"
      class="status-card"
      :class="cardClass(c.nivel)"
      :style="c.style"
    >
      <component :is="c.icon" :size="18" class="status-icon" aria-hidden="true" />
      <div>
        <h4>{{ c.title }}</h4>
        <p class="status-value">{{ c.value }}</p>
        <p class="status-hint">{{ c.hint }}</p>
      </div>
    </article>
  </div>
</template>

<style scoped>
.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}
.status-card {
  display: flex;
  gap: 10px;
  padding: 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
}
.status-card h4 {
  margin: 0;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-muted);
}
.status-value {
  margin: 4px 0 0;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text);
}
.status-hint {
  margin: 2px 0 0;
  font-size: 11px;
  color: var(--color-muted);
}
.status-icon {
  flex-shrink: 0;
  margin-top: 2px;
  color: var(--color-primary);
}
.card-danger {
  border-color: #f09595;
}
.card-warn {
  border-color: #fac775;
}
.card-ok {
  border-color: var(--color-border);
}
</style>
