<script setup>
import { computed } from 'vue'
import { useFormatTemp } from '@/composables/useFormatTemp'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  unit: { type: String, default: '' },
  hint: { type: String, default: '' },
  variant: { type: String, default: 'default' },
  /** Si se indica, formatea según preferencias °C/°F (M7). */
  tempCelsius: { type: Number, default: null },
})

const { formatTemperatura } = useFormatTemp()

const displayValue = computed(() => {
  if (props.tempCelsius != null && !Number.isNaN(Number(props.tempCelsius))) {
    return formatTemperatura(props.tempCelsius)
  }
  return String(props.value)
})

const displayUnit = computed(() => {
  if (props.tempCelsius != null) return ''
  return props.unit
})
</script>

<template>
  <article class="metric-card" :class="`metric-card--${variant}`">
    <div class="metric-card__icon" v-if="$slots.icon">
      <slot name="icon" />
    </div>
    <div class="metric-card__body">
      <p class="metric-card__label">{{ label }}</p>
      <p class="metric-card__value">
        {{ displayValue }}<span v-if="displayUnit" class="metric-card__unit">{{ displayUnit }}</span>
      </p>
      <p v-if="hint" class="metric-card__hint">{{ hint }}</p>
    </div>
  </article>
</template>

<style scoped>
.metric-card {
  display: flex;
  gap: 0.75rem;
  padding: 1rem 1.1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  transition: border-color 0.15s, box-shadow 0.15s;
}

.metric-card:hover {
  border-color: var(--color-border-strong);
  box-shadow: var(--shadow-md);
}

.metric-card__icon {
  display: flex;
  align-items: flex-start;
  padding-top: 0.15rem;
  color: var(--color-primary);
}

.metric-card__icon :deep(svg) {
  width: 1.25rem;
  height: 1.25rem;
  stroke-width: 1.75;
}

.metric-card__label {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-muted);
}

.metric-card__value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text);
  line-height: 1.2;
  margin-top: 0.15rem;
}

.metric-card__unit {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-muted);
  margin-left: 0.15rem;
}

.metric-card__hint {
  font-size: 0.75rem;
  color: var(--color-muted);
  margin-top: 0.25rem;
}

.metric-card--warning .metric-card__value {
  color: var(--color-warning);
}

.metric-card--alert .metric-card__value {
  color: var(--color-danger);
}
</style>
