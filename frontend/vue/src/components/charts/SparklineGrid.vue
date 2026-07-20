<script setup>
import { computed } from 'vue'
import { formatoDiaCorto } from '@/utils/meteoDates'

const props = defineProps({
  /** [{ id, nombre, fechas: [], valores: [], unidad }] */
  series: { type: Array, default: () => [] },
  kind: { type: String, default: 'temp' },
})

const W = 120
const H = 48
const pad = 4

function pathFor(vals) {
  const nums = vals.map(Number).filter((n) => !Number.isNaN(n))
  if (nums.length < 2) return ''
  const lo = Math.min(...nums)
  const hi = Math.max(...nums)
  const span = hi - lo || 1
  const iw = W - pad * 2
  const ih = H - pad * 2
  return nums
    .map((v, i) => {
      const x = pad + (i / (nums.length - 1)) * iw
      const y = pad + ih * (1 - (v - lo) / span)
      return `${i ? 'L' : 'M'} ${x.toFixed(1)} ${y.toFixed(1)}`
    })
    .join(' ')
}

const stroke = computed(() => (props.kind === 'precip' ? '#2980b9' : '#c45c26'))
</script>

<template>
  <div class="spark-grid">
    <article v-for="s in series" :key="s.id" class="spark-card">
      <header>
        <strong>{{ s.nombre }}</strong>
        <span v-if="s.valores?.length">{{ s.valores[s.valores.length - 1] }}{{ s.unidad }}</span>
      </header>
      <svg :viewBox="`0 0 ${W} ${H}`" class="spark-svg">
        <path v-if="s.valores?.length > 1" :d="pathFor(s.valores)" fill="none" :stroke="stroke" stroke-width="2" />
        <text v-else :x="W / 2" :y="H / 2" text-anchor="middle" class="no-data">Sin serie</text>
      </svg>
      <footer v-if="s.fechas?.length">
        {{ formatoDiaCorto(s.fechas[0]) }} — {{ formatoDiaCorto(s.fechas[s.fechas.length - 1]) }}
      </footer>
    </article>
  </div>
</template>

<style scoped>
.spark-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.65rem;
}
.spark-card {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 0.45rem 0.55rem;
  background: rgba(255, 255, 255, 0.02);
}
.spark-card header {
  display: flex;
  justify-content: space-between;
  font-size: 0.72rem;
  margin-bottom: 0.2rem;
}
.spark-card footer {
  font-size: 0.62rem;
  color: var(--color-muted);
  margin-top: 0.15rem;
}
.spark-svg { width: 100%; height: 48px; display: block; }
.no-data { font-size: 8px; fill: #9ca3af; }
</style>
