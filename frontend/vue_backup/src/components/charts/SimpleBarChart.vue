<script setup>
import { computed } from 'vue'

const props = defineProps({
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  unit: { type: String, default: '' },
  color: { type: String, default: 'var(--color-primary)' },
})

const maxVal = computed(() => Math.max(...props.values.map(Number), 1))
</script>

<template>
  <div class="bar-chart" role="img" :aria-label="`Gráfico de barras, ${labels.length} puntos`">
    <div v-for="(label, i) in labels" :key="i" class="bar-row">
      <span class="bar-label" :title="label">{{ label }}</span>
      <div class="bar-track">
        <div
          class="bar-fill"
          :style="{
            width: `${(Number(values[i]) / maxVal) * 100}%`,
            background: color,
          }"
        />
      </div>
      <span class="bar-value">{{ values[i] }}{{ unit }}</span>
    </div>
  </div>
</template>

<style scoped>
.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}
.bar-row {
  display: grid;
  grid-template-columns: 4.5rem 1fr 3rem;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
}
.bar-label {
  color: var(--color-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.bar-track {
  height: 0.55rem;
  background: var(--color-border);
  border-radius: 4px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 4px;
  min-width: 2px;
  transition: width 0.2s;
}
.bar-value {
  text-align: right;
  font-variant-numeric: tabular-nums;
  color: var(--color-text-secondary);
}
</style>
