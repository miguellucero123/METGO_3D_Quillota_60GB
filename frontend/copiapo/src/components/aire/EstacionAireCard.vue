<template>
  <button type="button" class="est-card" :class="{ 'est-card--active': active }" @click="$emit('select')">
    <h3>{{ nombre }}</h3>
    <p v-if="aire" class="est-icap">
      ICAP <strong>{{ aire.icap ?? '—' }}</strong>
      <span class="est-nivel">{{ aire.etiqueta || '' }}</span>
    </p>
    <p v-else class="est-icap muted">Sin lectura</p>
    <dl v-if="aire" class="est-poll">
      <div><dt>PM2.5</dt><dd>{{ fmt(aire.pm2_5) }}</dd></div>
      <div><dt>PM10</dt><dd>{{ fmt(aire.pm10) }}</dd></div>
    </dl>
  </button>
</template>

<script setup>
defineProps({
  nombre: String,
  aire: { type: Object, default: null },
  active: Boolean,
})
defineEmits(['select'])

function fmt(v) {
  return v == null ? '—' : `${v} µg/m³`
}
</script>

<style scoped>
.est-card {
  text-align: left;
  width: 100%;
  padding: 1rem;
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: inherit;
  cursor: pointer;
  font: inherit;
}
.est-card:hover,
.est-card--active {
  border-color: var(--color-primary);
  box-shadow: var(--glow-primary);
}
.est-card h3 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
}
.est-icap {
  margin: 0 0 0.5rem;
  font-size: 0.9rem;
}
.est-icap strong { color: var(--color-primary); font-size: 1.15rem; }
.est-nivel {
  margin-left: 0.5rem;
  color: var(--color-text-secondary);
  font-size: 0.85rem;
}
.muted { color: var(--color-muted); }
.est-poll {
  display: flex;
  gap: 1rem;
  margin: 0;
}
.est-poll dt {
  font-size: 0.7rem;
  color: var(--color-muted);
}
.est-poll dd {
  margin: 0;
  font-weight: 600;
  font-size: 0.9rem;
}
</style>
