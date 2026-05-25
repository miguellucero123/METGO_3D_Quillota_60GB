<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import * as icons from 'lucide-vue-next'
import { ExternalLink, ArrowRight } from 'lucide-vue-next'

const props = defineProps({
  modulo: { type: Object, required: true },
})

const router = useRouter()

const IconComp = computed(() => {
  const name = props.modulo.icono || 'box'
  const key = name
    .split('-')
    .map((p, i) => (i ? p.charAt(0).toUpperCase() + p.slice(1) : p))
    .join('')
  return icons[key] || icons.Box
})

const esSitioPublico =
  typeof window !== 'undefined' &&
  !['localhost', '127.0.0.1'].includes(window.location.hostname)

function esUrlLocal(url) {
  return /^https?:\/\/(127\.0\.0\.1|localhost)(:\d+)?/i.test(url || '')
}

function abrir() {
  const m = props.modulo
  if (m.tipo_acceso === 'vue' && m.ruta_vue) {
    router.push(m.ruta_vue)
    return
  }
  if (m.solo_local || (esSitioPublico && m.puerto)) {
    return
  }
  if (m.tipo_acceso === 'streamlit' && m.url_streamlit) {
    if (esSitioPublico && esUrlLocal(m.url_streamlit)) return
    window.open(m.url_streamlit, '_blank', 'noopener,noreferrer')
  }
}
</script>

<template>
  <article class="module-card" @click="abrir">
    <div class="module-card__head">
      <span class="module-card__icon">
        <component :is="IconComp" />
      </span>
      <span class="module-card__badge">{{ modulo.modulo_num }}</span>
    </div>
    <h4 class="module-card__title">{{ modulo.nombre }}</h4>
    <p class="module-card__desc">{{ modulo.descripcion }}</p>
    <ul v-if="modulo.atributos?.length" class="module-card__attrs">
      <li v-for="a in modulo.atributos.slice(0, 4)" :key="a">{{ a }}</li>
      <li v-if="modulo.atributos.length > 4">+{{ modulo.atributos.length - 4 }} más</li>
    </ul>
    <div class="module-card__foot">
      <span class="module-card__type">{{ modulo.tipo_acceso }}</span>
      <span v-if="modulo.solo_local" class="module-card__port">solo PC</span>
      <span v-else-if="modulo.puerto" class="module-card__port">:{{ modulo.puerto }}</span>
      <component
        :is="modulo.tipo_acceso === 'streamlit' ? ExternalLink : ArrowRight"
        class="module-card__arrow"
      />
    </div>
  </article>
</template>

<style scoped>
.module-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.1rem;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s, transform 0.12s;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.module-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.module-card__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.65rem;
}

.module-card__icon {
  color: var(--color-primary);
  display: flex;
}

.module-card__icon :deep(svg) {
  width: 1.35rem;
  height: 1.35rem;
}

.module-card__badge {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 0.15rem 0.45rem;
  background: var(--color-primary-muted);
  color: var(--color-primary);
  border-radius: var(--radius-sm);
}

.module-card__title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-text);
}

.module-card__desc {
  font-size: 0.8rem;
  color: var(--color-muted);
  margin-top: 0.35rem;
  flex: 1;
  line-height: 1.4;
}

.module-card__attrs {
  list-style: none;
  margin-top: 0.5rem;
  font-size: 0.7rem;
  color: var(--color-text-secondary);
}

.module-card__attrs li::before {
  content: '· ';
  color: var(--color-accent);
}

.module-card__foot {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin-top: 0.75rem;
  padding-top: 0.65rem;
  border-top: 1px solid var(--color-border);
  font-size: 0.72rem;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.module-card__arrow {
  width: 0.9rem;
  height: 0.9rem;
  margin-left: auto;
  color: var(--color-primary);
}
</style>
