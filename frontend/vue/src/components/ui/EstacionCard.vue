<script setup>
import { computed } from 'vue'
import { Thermometer, CloudRain, Wind, MapPin } from 'lucide-vue-next'
import { useFormatTemp } from '@/composables/useFormatTemp'
import { riesgoHelada, necesidadRiego } from '@/utils/agroInsights'

const props = defineProps({
  id: { type: String, required: true },
  nombre: { type: String, required: true },
  temperatura: { type: Number, default: null },
  temperaturaMax: { type: Number, default: null },
  temperaturaMin: { type: Number, default: null },
  precipitacion: { type: Number, default: null },
  humedad: { type: Number, default: null },
  viento: { type: Number, default: null },
  activa: { type: Boolean, default: false },
})

const emit = defineEmits(['select'])

const { formatTemperatura } = useFormatTemp()

const helada = computed(() => riesgoHelada(props.temperaturaMin))
const riego = computed(() => necesidadRiego(props.humedad, props.precipitacion))

const riesgoBadge = computed(() => {
  if (helada.value.nivel === 'high') return { label: 'Helada', cls: 'badge--danger' }
  if (riego.value.nivel === 'high') return { label: 'Riego', cls: 'badge--warning' }
  if (helada.value.nivel === 'medium' || riego.value.nivel === 'medium') {
    return { label: 'Vigilar', cls: 'badge--warning' }
  }
  return { label: 'OK', cls: 'badge--success' }
})
</script>

<template>
  <button
    type="button"
    class="est-card"
    :class="{ 'est-card--active': activa }"
    @click="emit('select', id)"
  >
    <div class="est-card__head">
      <span class="est-card__mark"><MapPin :size="16" /></span>
      <h3 class="est-card__name">{{ nombre }}</h3>
      <span class="badge" :class="riesgoBadge.cls">{{ riesgoBadge.label }}</span>
    </div>
    <div class="est-card__temp">
      <Thermometer :size="18" />
      <span v-if="temperatura != null">{{ formatTemperatura(temperatura) }}</span>
      <span v-else class="muted">—</span>
      <span v-if="temperaturaMin != null || temperaturaMax != null" class="est-card__range">
        {{ temperaturaMin != null ? formatTemperatura(temperaturaMin, 0) : '—' }}
        /
        {{ temperaturaMax != null ? formatTemperatura(temperaturaMax, 0) : '—' }}
      </span>
    </div>
    <div class="est-card__meta">
      <span><CloudRain :size="14" /> {{ precipitacion != null ? `${precipitacion} mm` : '—' }}</span>
      <span><Wind :size="14" /> {{ viento != null ? `${viento} m/s` : '—' }}</span>
    </div>
  </button>
</template>

<style scoped>
.est-card {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  text-align: left;
  padding: 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-family: inherit;
  color: var(--color-text);
  transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s;
  width: 100%;
}

.est-card:hover {
  border-color: var(--color-border-strong);
  box-shadow: var(--glow-primary);
  transform: translateY(-2px);
}

.est-card--active {
  border-color: var(--color-primary);
  background: var(--color-primary-subtle);
}

.est-card__head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.est-card__mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: var(--radius-sm);
  background: var(--color-primary-muted);
  color: var(--color-primary);
  flex-shrink: 0;
}

.est-card__name {
  flex: 1;
  font-size: 0.95rem;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.est-card__temp {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-primary);
}

.est-card__temp svg {
  color: var(--color-primary);
}

.est-card__range {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-left: 0.25rem;
}

.est-card__meta {
  display: flex;
  gap: 0.85rem;
  font-size: 0.8rem;
  color: var(--color-muted);
}

.est-card__meta span {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.muted {
  color: var(--color-muted);
  font-weight: 500;
}
</style>
