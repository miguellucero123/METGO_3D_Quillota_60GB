<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  fetchServiciosStreamlit,
  iniciarServicioStreamlit,
  detenerServicioStreamlit,
  detenerTodosStreamlit,
} from '@/api/metgoApi'
import SectionCard from '@/components/ui/SectionCard.vue'
import { Server, Play, Square, ExternalLink, Layers } from 'lucide-vue-next'

const router = useRouter()
const tab = ref('vue')
const servicios = ref([])
const cargando = ref(false)
const mensaje = ref('')
let pollTimer = null

const vueRutas = [
  { ruta: '/', label: 'Panel general' },
  { ruta: '/meteo', label: 'Meteorología' },
  { ruta: '/agricola', label: 'Agricultura' },
  { ruta: '/monitoreo', label: 'Alertas' },
  { ruta: '/modulos', label: 'Catálogo' },
  { ruta: '/configuracion', label: 'Configuración' },
]

async function refrescar() {
  try {
    servicios.value = await fetchServiciosStreamlit()
  } catch {
    servicios.value = []
  }
}

async function iniciar(id) {
  cargando.value = true
  mensaje.value = ''
  try {
    const r = await iniciarServicioStreamlit(id)
    mensaje.value = r.mensaje || (r.ok ? 'Iniciado' : r.error)
    await refrescar()
  } catch (e) {
    mensaje.value = e.message
  } finally {
    cargando.value = false
  }
}

async function detener(id) {
  cargando.value = true
  try {
    await detenerServicioStreamlit(id)
    await refrescar()
  } finally {
    cargando.value = false
  }
}

async function detenerTodos() {
  cargando.value = true
  await detenerTodosStreamlit()
  await refrescar()
  cargando.value = false
}

const esSitioPublico = typeof window !== 'undefined' &&
  !['localhost', '127.0.0.1'].includes(window.location.hostname)

function esUrlLocal(url) {
  return /^https?:\/\/(127\.0\.0\.1|localhost)(:\d+)?/i.test(url || '')
}

function abrir(url) {
  if (!url) return
  if (esSitioPublico && esUrlLocal(url)) {
    mensaje.value =
      'Los dashboards en puertos 850x solo funcionan en su PC (127.0.0.1), no desde Netlify. ' +
      'Use la pestaña «App Vue» o ejecute METGO en local.'
    return
  }
  window.open(url, '_blank', 'noopener,noreferrer')
}

onMounted(() => {
  if (esSitioPublico) {
    tab.value = 'vue'
    return
  }
  refrescar()
  pollTimer = setInterval(refrescar, 8000)
})
onUnmounted(() => clearInterval(pollTimer))
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Centro de servicios</h2>
      <p class="page-subtitle">
        Un solo lugar para la app Vue y para iniciar cada dashboard Streamlit solo cuando lo necesite
      </p>
    </header>

    <div class="tabs">
      <button type="button" :class="{ active: tab === 'vue' }" @click="tab = 'vue'">
        <Layers /> App Vue (siempre activa)
      </button>
      <button
        v-if="!esSitioPublico"
        type="button"
        :class="{ active: tab === 'streamlit' }"
        @click="tab = 'streamlit'"
      >
        <Server /> Streamlit (bajo demanda)
      </button>
    </div>

    <p v-if="mensaje" class="banner">{{ mensaje }}</p>

    <div v-if="tab === 'vue'" class="tab-panel">
      <SectionCard title="Módulos integrados en Vue" subtitle="Un servidor: Vite :5173 + API :8080">
        <p class="muted intro">
          Es la opción recomendada para uso diario: datos en vivo, JWT y navegación unificada sin abrir más puertos.
        </p>
        <div class="vue-links">
          <button
            v-for="v in vueRutas"
            :key="v.ruta"
            type="button"
            class="vue-link"
            @click="router.push(v.ruta)"
          >
            {{ v.label }}
          </button>
        </div>
      </SectionCard>
    </div>

    <div v-else-if="!esSitioPublico" class="tab-panel">
      <SectionCard
        title="Dashboards Streamlit"
        subtitle="Solo en PC local con API en :8080; cada módulo usa su puerto"
      >
        <template #actions>
          <button type="button" class="btn btn--ghost" :disabled="cargando" @click="detenerTodos">
            Detener todos (gestionados por API)
          </button>
        </template>

        <div class="service-list">
          <div v-for="s in servicios" :key="s.id" class="service-row">
            <div class="service-info">
              <span class="service-name">{{ s.nombre }}</span>
              <span class="service-meta">Módulo {{ s.modulo_num }} · puerto {{ s.puerto }}</span>
            </div>
            <span :class="['status', s.estado]">{{ s.estado }}</span>
            <div class="service-actions">
              <button
                v-if="s.estado !== 'corriendo' && s.estado !== 'solo_local'"
                type="button"
                class="btn btn-sm"
                :disabled="cargando || esSitioPublico"
                title="Iniciar servidor Streamlit"
                @click="iniciar(s.id)"
              >
                <Play /> Iniciar
              </button>
              <button
                v-else-if="s.estado === 'corriendo'"
                type="button"
                class="btn btn-sm btn--ghost"
                :disabled="cargando"
                @click="detener(s.id)"
              >
                <Square /> Detener
              </button>
              <button
                type="button"
                class="btn btn-sm btn--ghost"
                :disabled="s.estado !== 'corriendo' || !s.url"
                @click="abrir(s.url)"
              >
                <ExternalLink /> Abrir
              </button>
            </div>
          </div>
        </div>
      </SectionCard>

      <div class="arch-note card">
        <h4>¿Por qué varios servidores?</h4>
        <p>
          Streamlit levanta una app Python completa por dashboard. La API solo <strong>orquesta</strong>
          el arranque; Vue es la puerta de entrada unificada. A medio plazo se pueden migrar más pantallas
          a Vue para reducir puertos.
        </p>
      </div>
    </div>

    <div v-else class="tab-panel">
      <p class="banner banner--warn">
        Los dashboards Streamlit (puertos 8501, 8502, …) solo funcionan en su PC con METGO local.
        En producción use la pestaña <strong>App Vue</strong>.
      </p>
    </div>
  </div>
</template>

<style scoped>
.page {
  max-width: 960px;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.tabs button {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 1rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  font-family: inherit;
  font-size: 0.85rem;
  cursor: pointer;
  color: var(--color-text-secondary);
}

.tabs button.active {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}

.tabs button :deep(svg) {
  width: 1rem;
  height: 1rem;
}

.banner {
  background: var(--color-primary-muted);
  color: var(--color-primary);
  padding: 0.6rem 1rem;
  border-radius: var(--radius-md);
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.banner--warn {
  background: var(--color-warning-bg);
  color: var(--color-warning);
}

.intro {
  margin-bottom: 1rem;
}

.vue-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.vue-link {
  padding: 0.45rem 0.85rem;
  border: 1px solid var(--color-border);
  background: var(--color-primary-subtle);
  border-radius: var(--radius-md);
  font-family: inherit;
  font-size: 0.85rem;
  cursor: pointer;
  color: var(--color-primary);
}

.vue-link:hover {
  background: var(--color-primary-muted);
}

.service-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.service-row {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 0.75rem;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-primary-subtle);
}

@media (max-width: 720px) {
  .service-row {
    grid-template-columns: 1fr;
  }
}

.service-name {
  font-weight: 600;
  font-size: 0.9rem;
  display: block;
}

.service-meta {
  font-size: 0.72rem;
  color: var(--color-muted);
}

.status {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-sm);
}

.status.corriendo {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.status.detenido {
  background: var(--color-border);
  color: var(--color-muted);
}

.status.solo_local {
  background: var(--color-warning-bg);
  color: var(--color-warning);
}

.service-actions {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.btn-sm {
  padding: 0.35rem 0.65rem;
  font-size: 0.75rem;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.btn-sm :deep(svg) {
  width: 0.85rem;
  height: 0.85rem;
}

.arch-note {
  margin-top: 1.25rem;
  padding: 1rem;
}

.arch-note h4 {
  font-size: 0.95rem;
  margin-bottom: 0.5rem;
}

.arch-note p {
  font-size: 0.85rem;
  color: var(--color-muted);
  line-height: 1.5;
}
</style>
