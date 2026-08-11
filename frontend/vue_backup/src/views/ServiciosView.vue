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
import { Server, Play, Square, ExternalLink, Layers, Cloud, Info, Monitor } from 'lucide-vue-next'

const router = useRouter()
const tab = ref('puertos')
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

const esSitioPublico =
  typeof window !== 'undefined' &&
  !['localhost', '127.0.0.1'].includes(window.location.hostname)

async function refrescar() {
  try {
    servicios.value = await fetchServiciosStreamlit()
  } catch {
    servicios.value = []
  }
}

function esUrlLocal(url) {
  return /^https?:\/\/(127\.0\.0\.1|localhost)(:\d+)?/i.test(url || '')
}

function abrir(url) {
  if (!url) return
  if (esSitioPublico && esUrlLocal(url)) {
    mensaje.value =
      'Este puerto solo existe en su PC. Use «Activar en nube» o «Ver en Vue».'
    return
  }
  window.open(url, '_blank', 'noopener,noreferrer')
}

async function activar(s) {
  cargando.value = true
  mensaje.value = ''
  try {
    const r = await iniciarServicioStreamlit(s.id)
    mensaje.value = r.mensaje || r.error || (r.ok ? 'Listo' : 'Error')
    if (r.ok && r.url) {
      abrir(r.url)
    }
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
    const r = await detenerServicioStreamlit(id)
    mensaje.value = r.mensaje || ''
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

function irVue(ruta) {
  if (ruta) router.push(ruta)
}

function verEnVisor(id) {
  router.push({ name: 'puertos', query: { id } })
}

function etiquetaEstado(estado) {
  const map = {
    corriendo: 'Activo (PC)',
    detenido: 'Detenido',
    disponible_nube: 'Listo en nube',
    solo_local: 'Solo PC',
  }
  return map[estado] || estado
}

onMounted(() => {
  refrescar()
  pollTimer = setInterval(refrescar, esSitioPublico ? 20000 : 8000)
})
onUnmounted(() => clearInterval(pollTimer))
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Centro de servicios</h2>
      <p class="page-subtitle">
        Puertos 8501–8513 (Streamlit en PC), equivalentes en Vue y portal en la nube
      </p>
      <router-link to="/puertos" class="link-visor">
        <Monitor /> Abrir visor integrado (ver dashboards aquí)
      </router-link>
    </header>

    <div class="tabs">
      <button type="button" :class="{ active: tab === 'puertos' }" @click="tab = 'puertos'">
        <Server /> Puertos y utilidad
      </button>
      <button type="button" :class="{ active: tab === 'vue' }" @click="tab = 'vue'">
        <Layers /> App Vue
      </button>
    </div>

    <p v-if="mensaje" class="banner">{{ mensaje }}</p>

    <p v-if="esSitioPublico" class="banner banner--info">
      <Info class="banner-icon" />
      En Netlify cada puerto <strong>no</strong> corre en el servidor: es una etiqueta del módulo en su PC.
      Use <strong>Activar en nube</strong> (portal Streamlit) o <strong>Ver en Vue</strong> para el mismo fin.
    </p>

    <div v-if="tab === 'puertos'" class="tab-panel">
      <SectionCard
        title="Módulos Streamlit (8501–8513)"
        :subtitle="
          esSitioPublico
            ? 'Estado desde la API · activación en portal en la nube'
            : 'Inicie cada dashboard en su PC; la API orquesta el puerto'
        "
      >
        <template v-if="!esSitioPublico" #actions>
          <button type="button" class="btn btn--ghost" :disabled="cargando" @click="detenerTodos">
            Detener todos (API local)
          </button>
        </template>

        <div v-if="!servicios.length && !cargando" class="muted">Cargando servicios…</div>

        <div class="service-list">
          <article v-for="s in servicios" :key="s.id" class="service-row">
            <div class="service-info">
              <span class="service-name">{{ s.nombre }}</span>
              <span class="service-meta">
                Módulo {{ s.modulo_num }} · puerto <strong>{{ s.puerto }}</strong>
              </span>
              <p class="service-utilidad">{{ s.utilidad || s.descripcion }}</p>
            </div>
            <span :class="['status', s.estado]">{{ etiquetaEstado(s.estado) }}</span>
            <div class="service-actions">
              <button
                v-if="s.ruta_vue_alternativa"
                type="button"
                class="btn btn-sm btn--ghost"
                title="Misma función en la app Vue"
                @click="irVue(s.ruta_vue_alternativa)"
              >
                <Layers /> Ver en Vue
              </button>
              <button
                type="button"
                class="btn btn-sm btn--primary-soft"
                title="Ver en iframe dentro de METGO"
                @click="verEnVisor(s.id)"
              >
                <Monitor /> Ver en visor
              </button>
              <button
                v-if="s.estado === 'disponible_nube' || s.url_nube"
                type="button"
                class="btn btn-sm"
                :disabled="cargando"
                title="Abrir portal Streamlit en Render"
                @click="activar(s)"
              >
                <Cloud /> Activar en nube
              </button>
              <template v-if="!esSitioPublico">
                <button
                  v-if="s.estado !== 'corriendo'"
                  type="button"
                  class="btn btn-sm"
                  :disabled="cargando"
                  title="Iniciar en 127.0.0.1"
                  @click="activar(s)"
                >
                  <Play /> Iniciar PC
                </button>
                <button
                  v-else
                  type="button"
                  class="btn btn-sm btn--ghost"
                  :disabled="cargando"
                  @click="detener(s.id)"
                >
                  <Square /> Detener
                </button>
                <button
                  v-if="s.estado === 'corriendo' && s.url"
                  type="button"
                  class="btn btn-sm btn--ghost"
                  @click="abrir(s.url)"
                >
                  <ExternalLink /> Abrir :{{ s.puerto }}
                </button>
              </template>
            </div>
          </article>
        </div>
      </SectionCard>

      <div class="arch-note card">
        <h4>¿Para qué sirve cada puerto?</h4>
        <p>
          Cada número (8501, 8502, …) es un <strong>proceso Streamlit</strong> en su computador con gráficos
          Plotly y pantallas legacy. La app Vue (:5173) cubre meteorología, agricultura y alertas sin abrir
          esos puertos. En internet, el portal en Render concentra el acceso (un solo URL, no trece servidores).
        </p>
      </div>
    </div>

    <div v-else class="tab-panel">
      <SectionCard title="Módulos integrados en Vue" subtitle="Recomendado en Netlify y en local">
        <p class="muted intro">
          Datos en vivo vía API, JWT y navegación unificada — sin depender de puertos 850x.
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
  </div>
</template>

<style scoped>
.page {
  max-width: 1024px;
}

.link-visor {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-primary);
  text-decoration: none;
}

.link-visor:hover {
  text-decoration: underline;
}

.link-visor :deep(svg) {
  width: 1rem;
  height: 1rem;
}

.btn--primary-soft {
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
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
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.banner--info {
  background: #e8f0eb;
  color: var(--color-text-secondary);
}

.banner-icon {
  width: 1.1rem;
  height: 1.1rem;
  flex-shrink: 0;
  margin-top: 0.1rem;
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

.service-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.service-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 0.75rem;
  padding: 0.85rem;
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
  font-size: 0.92rem;
  display: block;
}

.service-meta {
  font-size: 0.72rem;
  color: var(--color-muted);
}

.service-utilidad {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  margin-top: 0.35rem;
  line-height: 1.45;
}

.status {
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-sm);
  align-self: start;
  grid-column: 2;
  grid-row: 1;
}

@media (max-width: 720px) {
  .status {
    grid-column: 1;
    grid-row: auto;
    justify-self: start;
  }
}

.status.corriendo {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.status.detenido {
  background: var(--color-border);
  color: var(--color-muted);
}

.status.disponible_nube {
  background: #d4e8dc;
  color: var(--color-primary);
}

.status.solo_local {
  background: var(--color-warning-bg);
  color: var(--color-warning);
}

.service-actions {
  grid-column: 1 / -1;
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
