<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import * as icons from 'lucide-vue-next'
import { ExternalLink, ArrowRight, Cloud, Layers, Monitor } from 'lucide-vue-next'

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

const textoUtilidad = computed(
  () => props.modulo.utilidad || props.modulo.descripcion || ''
)

function esUrlLocal(url) {
  return /^https?:\/\/(127\.0\.0\.1|localhost)(:\d+)?/i.test(url || '')
}

function abrirStreamlit(url) {
  if (!url) return
  if (esSitioPublico && esUrlLocal(url)) return
  window.open(url, '_blank', 'noopener,noreferrer')
}

function onCardClick() {
  const m = props.modulo
  if (m.tipo_acceso === 'vue' && m.ruta_vue) {
    router.push(m.ruta_vue)
    return
  }
  if (m.tipo_acceso === 'streamlit') {
    if (m.url_nube && esSitioPublico) {
      abrirStreamlit(m.url_nube)
      return
    }
    if (m.url_streamlit && !esSitioPublico && !m.solo_local) {
      abrirStreamlit(m.url_streamlit)
    }
  }
}

function irVue(e) {
  e.stopPropagation()
  if (props.modulo.ruta_vue_alternativa) {
    router.push(props.modulo.ruta_vue_alternativa)
  }
}

function abrirNube(e) {
  e.stopPropagation()
  const url = props.modulo.url_nube || props.modulo.url_streamlit
  if (url) abrirStreamlit(url)
}

function abrirVisor(e) {
  e.stopPropagation()
  router.push({ name: 'puertos', query: { id: props.modulo.id } })
}
</script>

<template>
  <article class="module-card" @click="onCardClick">
    <div class="module-card__head">
      <span class="module-card__icon">
        <component :is="IconComp" />
      </span>
      <span class="module-card__badge">{{ modulo.modulo_num }}</span>
    </div>
    <h4 class="module-card__title">{{ modulo.nombre }}</h4>
    <p class="module-card__desc">{{ textoUtilidad }}</p>
    <ul v-if="modulo.atributos?.length" class="module-card__attrs">
      <li v-for="a in modulo.atributos.slice(0, 4)" :key="a">{{ a }}</li>
      <li v-if="modulo.atributos.length > 4">+{{ modulo.atributos.length - 4 }} más</li>
    </ul>
    <div class="module-card__foot">
      <span class="module-card__type">{{ modulo.tipo_acceso }}</span>
      <span v-if="modulo.puerto" class="module-card__port" :title="modulo.utilidad">
        :{{ modulo.puerto }}
      </span>
      <span v-else-if="modulo.solo_local" class="module-card__port">solo PC</span>
      <div class="module-card__actions" @click.stop>
        <button
          v-if="modulo.ruta_vue_alternativa"
          type="button"
          class="module-card__mini"
          title="Equivalente en Vue"
          @click="irVue"
        >
          <Layers />
        </button>
        <button
          v-if="modulo.tipo_acceso === 'streamlit'"
          type="button"
          class="module-card__mini"
          title="Visor integrado"
          @click="abrirVisor"
        >
          <Monitor />
        </button>
        <button
          v-if="modulo.url_nube || (modulo.acceso_nube && modulo.url_streamlit)"
          type="button"
          class="module-card__mini"
          title="Portal en la nube"
          @click="abrirNube"
        >
          <Cloud />
        </button>
      </div>
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

.module-card__actions {
  display: flex;
  gap: 0.25rem;
  margin-left: auto;
  margin-right: 0.25rem;
}

.module-card__mini {
  border: none;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  padding: 0.2rem 0.35rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
}

.module-card__mini :deep(svg) {
  width: 0.85rem;
  height: 0.85rem;
}

.module-card__arrow {
  width: 0.9rem;
  height: 0.9rem;
  color: var(--color-primary);
}
</style>
