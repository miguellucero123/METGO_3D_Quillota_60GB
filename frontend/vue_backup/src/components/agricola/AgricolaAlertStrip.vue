<script setup>
import { ref, computed } from 'vue'
import { Snowflake, X } from 'lucide-vue-next'
import { riesgoHelada } from '@/utils/agroColors'

const props = defineProps({
  tMin: { type: Number, required: true },
  cultivo: { type: String, default: 'palto' },
})

const visible = ref(true)
const riesgo = computed(() => riesgoHelada(props.tMin))

const MENSAJES = {
  palto: 'Suspender riego por aspersión · Cubrir plantines jóvenes',
  citricos: 'Activar calefacción de huerto · Suspender riego nocturno',
  vid: 'Suspender riego · Monitorear brotes según fenología',
  tomate: 'Cubrir cultivo con manta térmica',
  lechuga: 'Cosechar si está maduro · Cubrir bancales',
}

const mensajePrincipal = computed(() =>
  props.tMin <= 3 ? MENSAJES[props.cultivo] ?? 'Activar medidas de protección térmica' : ''
)
</script>

<template>
  <Transition name="alert-slide">
    <div
      v-if="visible"
      class="alert-strip"
      :class="`alert-${riesgo.nivel}`"
      role="alert"
      :aria-label="riesgo.label"
    >
      <Snowflake class="alert-icon" aria-hidden="true" />
      <div class="alert-content">
        <span class="alert-title">{{ riesgo.label }} — T° mín {{ tMin }}°C</span>
        <span v-if="mensajePrincipal" class="alert-desc">{{ mensajePrincipal }}</span>
      </div>
      <button type="button" class="alert-dismiss" aria-label="Cerrar alerta" @click="visible = false">
        <X :size="16" aria-hidden="true" />
      </button>
    </div>
  </Transition>
</template>

<style scoped>
.alert-strip {
  border-radius: var(--radius-md);
  padding: 10px 14px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 13px;
}
.alert-critico,
.alert-alto {
  background: #fcebeb;
  color: #a32d2d;
  border: 1px solid #f09595;
}
.alert-moderado {
  background: #faeeda;
  color: #633806;
  border: 1px solid #fac775;
}
.alert-icon {
  flex-shrink: 0;
  margin-top: 2px;
}
.alert-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.alert-title {
  font-weight: 600;
}
.alert-desc {
  font-size: 11px;
  opacity: 0.9;
}
.alert-dismiss {
  background: none;
  border: none;
  cursor: pointer;
  color: inherit;
  opacity: 0.65;
  padding: 0;
  display: flex;
}
.alert-slide-enter-from,
.alert-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
