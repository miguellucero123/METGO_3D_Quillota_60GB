<template>
  <button type="button" class="punto-card" :class="[`nivel-${nivel}`, { active }]" @click="$emit('select')">
    <div class="punto-head">
      <span class="nombre">{{ nombre }}</span>
      <span class="semaforo" :class="`s-${nivel}`">{{ etiquetaNivel(nivel) }}</span>
    </div>
    <p class="desc">{{ descripcion }}</p>
    <ul class="acts">
      <li v-for="act in actividades" :key="act.id">
        <span>{{ act.label }}</span>
        <strong :class="`s-${act.nivel}`">{{ etiquetaNivel(act.nivel) }}</strong>
      </li>
    </ul>
  </button>
</template>

<script setup>
defineProps({
  nombre: { type: String, required: true },
  descripcion: { type: String, default: '' },
  nivel: { type: String, default: 'verde' },
  actividades: { type: Array, default: () => [] },
  active: { type: Boolean, default: false },
})
defineEmits(['select'])

function etiquetaNivel(n) {
  return { verde: 'Verde', amarillo: 'Amarillo', rojo: 'Rojo' }[n] || '—'
}
</script>

<style scoped>
.punto-card {
  text-align: left;
  width: 100%;
  padding: 0.9rem 1rem;
  border-radius: 10px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
  border-left: 4px solid var(--color-success);
}
.punto-card.nivel-amarillo { border-left-color: var(--color-warning); }
.punto-card.nivel-rojo { border-left-color: var(--color-danger); }
.punto-card.active { box-shadow: var(--glow-primary); border-color: var(--color-primary); }
.punto-head { display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; }
.nombre { font-weight: 600; }
.semaforo {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
}
.s-verde { color: var(--color-success); background: var(--color-success-bg); }
.s-amarillo { color: var(--color-warning); background: var(--color-warning-bg); }
.s-rojo { color: var(--color-danger); background: var(--color-danger-bg); }
.desc { margin: 0.4rem 0 0.65rem; font-size: 0.8rem; color: var(--color-text-secondary); }
.acts { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.3rem; }
.acts li { display: flex; justify-content: space-between; font-size: 0.82rem; }
</style>
