<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  fetchServiciosStreamlit,
  fetchVisorPuerto,
  iniciarServicioStreamlit,
} from '@/api/metgoApi'
import SectionCard from '@/components/ui/SectionCard.vue'
import {
  Monitor,
  Play,
  RefreshCw,
  Maximize2,
  ChevronRight,
  Cloud,
  Layers,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const servicios = ref([])
const seleccionado = ref(null)
const embedUrl = ref('')
const cargando = ref(false)
const errorVisor = ref('')
const iframeKey = ref(0)

const esSitioPublico =
  typeof window !== 'undefined' &&
  !['localhost', '127.0.0.1'].includes(window.location.hostname)

const moduloActual = computed(() =>
  servicios.value.find((s) => s.id === seleccionado.value)
)

async function cargarLista() {
  try {
    servicios.value = await fetchServiciosStreamlit()
  } catch {
    servicios.value = []
  }
}

async function abrirVisor(id, opts = {}) {
  if (!id) return
  seleccionado.value = id
  cargando.value = true
  errorVisor.value = ''
  embedUrl.value = ''

  try {
    if (!esSitioPublico && opts.iniciarSiLocal) {
      const s = servicios.value.find((x) => x.id === id)
      if (s?.estado === 'detenido') {
        await iniciarServicioStreamlit(id)
        await cargarLista()
      }
    }

    const v = await fetchVisorPuerto(id)
    if (!v.ok) {
      errorVisor.value = v.error || 'No se pudo obtener URL del visor'
      return
    }
    const url = v.url_embed || v.url_visor || v.url
    if (!url) {
      errorVisor.value =
        v.requiere_iniciar_local
          ? 'Inicie el módulo en su PC (botón Iniciar) o use la nube.'
          : 'Sin URL de visor configurada.'
      return
    }
    embedUrl.value = url.includes('embed=') ? url : `${url}${url.includes('?') ? '&' : '?'}embed=true`
    iframeKey.value += 1
    router.replace({ query: { id } })
  } catch (e) {
    errorVisor.value = e.message
  } finally {
    cargando.value = false
  }
}

function pantallaCompleta() {
  const el = document.getElementById('metgo-puerto-iframe')
  if (el?.requestFullscreen) el.requestFullscreen()
}

function irVue() {
  const r = moduloActual.value?.ruta_vue_alternativa
  if (r) router.push(r)
}

onMounted(async () => {
  await cargarLista()
  const id = route.query.id
  if (id && typeof id === 'string') {
    await abrirVisor(id, { iniciarSiLocal: true })
  } else if (servicios.value.length) {
    await abrirVisor(servicios.value[0].id, { iniciarSiLocal: false })
  }
})

watch(
  () => route.query.id,
  async (id) => {
    if (id && id !== seleccionado.value) {
      await abrirVisor(String(id), { iniciarSiLocal: true })
    }
  }
)
</script>

<template>
  <div class="puertos-page">
    <header class="page-header">
      <h2 class="page-title">Visor de puertos</h2>
      <p class="page-subtitle">
        Acceso integrado a los dashboards 8501–8513: iframe en la nube (Render) o en su PC (local)
      </p>
    </header>

    <div v-if="esSitioPublico" class="banner-nube">
      <Cloud class="banner-icon" />
      <div>
        <strong>Modo en línea (Netlify)</strong>
        <p>
          Los dashboards en puertos <code>8501–8513</code> solo funcionan con METGO en su PC.
          Use <strong>Ver en nube</strong> (visor Streamlit) o las pantallas Vue del menú.
        </p>
        <a
          href="https://metgo-3d-quillota-60gb.streamlit.app"
          target="_blank"
          rel="noopener noreferrer"
          class="link-nube"
        >
          Abrir portal Streamlit Cloud
        </a>
      </div>
    </div>

    <div class="puertos-layout">
      <aside class="puertos-list card">
        <div class="list-head">
          <span class="list-title">Puertos</span>
          <button type="button" class="btn-icon" title="Actualizar" @click="cargarLista">
            <RefreshCw />
          </button>
        </div>
        <ul class="port-items">
          <li v-for="s in servicios" :key="s.id">
            <button
              type="button"
              class="port-item"
              :class="{ active: seleccionado === s.id }"
              @click="abrirVisor(s.id, { iniciarSiLocal: !esSitioPublico })"
            >
              <span class="port-num">:{{ s.puerto }}</span>
              <span class="port-name">{{ s.nombre }}</span>
              <ChevronRight class="port-chevron" />
            </button>
            <p class="port-util">{{ s.utilidad || s.descripcion }}</p>
          </li>
        </ul>
      </aside>

      <main class="puertos-viewer card">
        <div v-if="moduloActual" class="viewer-toolbar">
          <div>
            <strong>{{ moduloActual.nombre }}</strong>
            <span class="muted"> · puerto {{ moduloActual.puerto }}</span>
          </div>
          <div class="toolbar-actions">
            <button
              v-if="moduloActual.ruta_vue_alternativa"
              type="button"
              class="btn btn-sm btn--ghost"
              @click="irVue"
            >
              <Layers /> Vue
            </button>
            <span v-if="esSitioPublico" class="badge badge--cloud">
              <Cloud /> Visor nube
            </span>
            <span v-else-if="moduloActual.estado === 'corriendo'" class="badge badge--ok">
              PC activo
            </span>
            <button
              v-if="embedUrl"
              type="button"
              class="btn btn-sm btn--ghost"
              @click="pantallaCompleta"
            >
              <Maximize2 /> Pantalla completa
            </button>
          </div>
        </div>

        <p v-if="moduloActual?.utilidad" class="viewer-utilidad">
          {{ moduloActual.utilidad }}
        </p>

        <div v-if="cargando" class="viewer-placeholder">
          <RefreshCw class="spin" /> Cargando visor…
        </div>
        <p v-else-if="errorVisor" class="viewer-error">{{ errorVisor }}</p>
        <iframe
          v-else-if="embedUrl"
          id="metgo-puerto-iframe"
          :key="iframeKey"
          :src="embedUrl"
          class="viewer-iframe"
          title="Dashboard Streamlit METGO"
          allow="fullscreen"
        />
        <div v-else class="viewer-placeholder">
          <Monitor />
          <p>Seleccione un puerto de la lista</p>
        </div>

        <SectionCard
          v-if="!esSitioPublico && moduloActual?.estado === 'detenido'"
          class="viewer-hint"
          title="Modo local"
          subtitle="El proceso en este puerto no está activo"
        >
          <p class="muted">
            Pulse <strong>Iniciar y ver</strong> para levantar Streamlit en
            <code>127.0.0.1:{{ moduloActual.puerto }}</code>, o use el visor en la nube (no requiere puerto local).
          </p>
          <button
            type="button"
            class="btn"
            :disabled="cargando"
            @click="abrirVisor(moduloActual.id, { iniciarSiLocal: true })"
          >
            <Play /> Iniciar y ver
          </button>
        </SectionCard>
      </main>
    </div>
  </div>
</template>

<style scoped>
.puertos-page {
  max-width: 1400px;
  height: calc(100vh - 4rem);
  display: flex;
  flex-direction: column;
}

.banner-nube {
  display: flex;
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  margin-bottom: 1rem;
  background: #e8f0eb;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.banner-nube p {
  margin: 0.25rem 0 0;
}

.banner-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
  color: var(--color-primary);
}

.link-nube {
  display: inline-block;
  margin-top: 0.35rem;
  font-weight: 600;
  color: var(--color-primary);
}

.puertos-layout {
  display: grid;
  grid-template-columns: minmax(220px, 280px) 1fr;
  gap: 1rem;
  flex: 1;
  min-height: 0;
}

@media (max-width: 900px) {
  .puertos-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }
}

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.puertos-list {
  display: flex;
  flex-direction: column;
  max-height: 100%;
}

.list-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
}

.list-title {
  font-weight: 600;
  font-size: 0.9rem;
}

.btn-icon {
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--color-primary);
  padding: 0.25rem;
}

.btn-icon :deep(svg) {
  width: 1rem;
  height: 1rem;
}

.port-items {
  list-style: none;
  overflow-y: auto;
  flex: 1;
  padding: 0.35rem;
}

.port-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.6rem;
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-family: inherit;
  text-align: left;
}

.port-item:hover,
.port-item.active {
  background: var(--color-primary-muted);
}

.port-num {
  font-weight: 700;
  font-size: 0.75rem;
  color: var(--color-primary);
  min-width: 2.8rem;
}

.port-name {
  flex: 1;
  font-size: 0.78rem;
  color: var(--color-text);
}

.port-chevron {
  width: 0.85rem;
  height: 0.85rem;
  opacity: 0.4;
}

.port-util {
  font-size: 0.68rem;
  color: var(--color-muted);
  padding: 0 0.6rem 0.5rem 3.2rem;
  line-height: 1.35;
}

.puertos-viewer {
  display: flex;
  flex-direction: column;
  min-height: 400px;
}

.viewer-toolbar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1rem;
  border-bottom: 1px solid var(--color-border);
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.badge {
  font-size: 0.68rem;
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-sm);
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.badge--cloud {
  background: #d4e8dc;
  color: var(--color-primary);
}

.badge--ok {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.badge :deep(svg) {
  width: 0.75rem;
  height: 0.75rem;
}

.viewer-utilidad {
  font-size: 0.8rem;
  color: var(--color-muted);
  padding: 0.4rem 1rem 0;
}

.viewer-iframe {
  flex: 1;
  width: 100%;
  min-height: 480px;
  border: none;
  background: #fff;
}

.viewer-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: var(--color-muted);
  min-height: 320px;
}

.viewer-placeholder :deep(svg) {
  width: 2.5rem;
  height: 2.5rem;
  opacity: 0.35;
}

.viewer-error {
  color: var(--color-warning);
  padding: 1rem;
  font-size: 0.875rem;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.viewer-hint {
  margin: 0.75rem 1rem 1rem;
}

.btn-sm :deep(svg) {
  width: 0.85rem;
  height: 0.85rem;
}
</style>
