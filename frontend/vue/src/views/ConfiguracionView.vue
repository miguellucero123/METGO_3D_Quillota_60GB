<script setup>
import { ref, watch, onMounted } from 'vue'
import { Settings, Link2 } from 'lucide-vue-next'
import { useMetgoStore } from '@/stores/metgo'
import {
  fetchSistemaResumen,
  fetchConfiguracionEstacion,
  fetchModulos,
} from '@/api/metgoApi'
import SectionCard from '@/components/ui/SectionCard.vue'
import ModuleCard from '@/components/ui/ModuleCard.vue'

const store = useMetgoStore()
const config = ref(null)
const resumen = ref(null)
const streamlitModulos = ref([])
const tipoAnalisis = ref('pronostico')
const intervalo = ref('manual')

async function cargar() {
  try {
    const [cfg, r, mods] = await Promise.all([
      fetchConfiguracionEstacion(store.estacionActiva),
      fetchSistemaResumen(),
      fetchModulos('streamlit'),
    ])
    config.value = cfg
    resumen.value = r
    streamlitModulos.value = mods
  } catch {
    config.value = null
  }
}

function aplicarAnalisis() {
  store.tipoAnalisis = tipoAnalisis.value
  store.cargarDatosMeteo()
}

onMounted(cargar)
watch(() => store.estacionActiva, cargar)
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Configuración del sistema</h2>
      <p class="page-subtitle">Parámetros por estación, análisis e integraciones — {{ store.estacionNombre }}</p>
    </header>

    <div class="layout-split">
      <SectionCard title="Estación activa" :subtitle="config?.estacion">
        <template #icon><Settings /></template>
        <dl v-if="config" class="config-dl">
          <dt>Zona agroclimática</dt>
          <dd>{{ config.zona }}</dd>
          <dt>Superficie agrícola</dt>
          <dd>{{ config.superficie }}</dd>
          <dt>Actividad principal</dt>
          <dd>{{ config.actividad }}</dd>
        </dl>
      </SectionCard>

      <SectionCard title="Panel de control" subtitle="Equivalente al dashboard Streamlit principal">
        <template #icon><Settings /></template>
        <div class="form-grid">
          <label>
            Tipo de análisis
            <select v-model="tipoAnalisis" @change="aplicarAnalisis">
              <option v-for="t in resumen?.tipos_analisis" :key="t.id" :value="t.id">
                {{ t.nombre }} ({{ t.dias_default }} días ref.)
              </option>
            </select>
          </label>
          <label>
            Intervalo de actualización
            <select v-model="intervalo">
              <option v-for="i in resumen?.intervalos" :key="i" :value="i">{{ i }}</option>
            </select>
          </label>
        </div>
        <p class="muted">El tipo de análisis afecta la carga de datos en Meteorología al actualizar.</p>
        <button type="button" class="btn" style="margin-top: 0.75rem" @click="store.cargarDatosMeteo()">
          Aplicar y actualizar datos
        </button>
      </SectionCard>
    </div>

    <SectionCard
      title="Acceso rápido — dashboards Streamlit"
      :subtitle="`Host Streamlit: ${resumen?.streamlit_host || 'http://127.0.0.1'}`"
      class="streamlit-section"
    >
      <template #icon><Link2 /></template>
      <p class="muted section-hint">
        Inicie cada dashboard con Streamlit en el puerto indicado, luego abra desde aquí o desde
        <router-link to="/modulos">Catálogo de módulos</router-link>.
      </p>
      <div class="modules-grid">
        <ModuleCard v-for="m in streamlitModulos" :key="m.id" :modulo="m" />
      </div>
    </SectionCard>
  </div>
</template>

<style scoped>
.page {
  max-width: 1280px;
}

.config-dl {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.5rem 1rem;
  font-size: 0.875rem;
}

.config-dl dt {
  font-weight: 600;
  color: var(--color-muted);
}

.form-grid {
  display: grid;
  gap: 1rem;
}

.form-grid label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-muted);
  text-transform: uppercase;
}

.form-grid select {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: inherit;
}

.streamlit-section {
  margin-top: 1.25rem;
}

.section-hint {
  margin-bottom: 1rem;
}

.section-hint a {
  color: var(--color-primary);
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.85rem;
}
</style>
