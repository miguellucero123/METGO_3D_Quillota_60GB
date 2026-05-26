<script setup>
import { ref, onMounted } from 'vue'
import { Link2, RefreshCw, Database, Sprout, BellRing, Radio, Cpu, FileText } from 'lucide-vue-next'
import { useMetgoStore } from '@/stores/metgo'
import SectionCard from '@/components/ui/SectionCard.vue'
import {
  fetchIntegracionEstado,
  syncDatosEtl,
  syncMlRegistry,
  fetchDatosFuentes,
  fetchMeteoStore,
  fetchStreamlitCobertura,
  fetchReportesUltimos,
  fetchDeployInfo,
  fetchTestingResumen,
  probarNotificaciones,
  fetchEtlStatus,
} from '@/api/metgoApi'

const store = useMetgoStore()
const estado = ref(null)
const fuentes = ref(null)
const meteoStore = ref(null)
const cobertura = ref(null)
const reportes = ref([])
const deploy = ref(null)
const tests = ref(null)
const etlStatus = ref(null)
const log = ref('')
const busy = ref(false)

async function addLog(msg) {
  log.value = `${new Date().toLocaleTimeString('es-CL')} — ${msg}\n` + log.value
}

async function cargar() {
  busy.value = true
  try {
    etlStatus.value = await fetchEtlStatus().catch(() => null)
    estado.value = await fetchIntegracionEstado()
    fuentes.value = await fetchDatosFuentes()
    meteoStore.value = await fetchMeteoStore()
    cobertura.value = await fetchStreamlitCobertura()
    reportes.value = await fetchReportesUltimos(5)
    deploy.value = await fetchDeployInfo()
    tests.value = await fetchTestingResumen()
  } catch (e) {
    await addLog(`Error carga: ${e.message}`)
  } finally {
    busy.value = false
  }
}

async function etlSync() {
  busy.value = true
  try {
    const r = await syncDatosEtl(14, true)
    await addLog(`ETL OK: ${JSON.stringify(r.store || r)}`)
    meteoStore.value = await fetchMeteoStore()
    etlStatus.value = await fetchEtlStatus().catch(() => etlStatus.value)
  } catch (e) {
    await addLog(`ETL falló: ${e.message}`)
  } finally {
    busy.value = false
  }
}

async function mlSync() {
  busy.value = true
  try {
    const r = await syncMlRegistry()
    await addLog(`ML registry: ${r.servibles}/${r.total} servibles`)
  } catch (e) {
    await addLog(`ML sync: ${e.message}`)
  } finally {
    busy.value = false
  }
}

async function notifTest() {
  try {
    const r = await probarNotificaciones(`Prueba desde Vue · ${store.estacionNombre}`)
    await addLog(`Notificación: ${r.canal} — ${r.mensaje || r.nota}`)
  } catch (e) {
    await addLog(`Notif: ${e.message}`)
  }
}

onMounted(cargar)
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Conexiones del sistema</h2>
      <p class="page-subtitle">
        Integración módulos 01–11 · API ↔ Vue
        <span class="badge badge--neutral">Fase 5–10</span>
      </p>
      <div class="actions">
        <button type="button" class="btn btn-sm" :disabled="busy" @click="cargar">
          <RefreshCw /> Actualizar
        </button>
        <button type="button" class="btn btn-sm btn-primary" :disabled="busy" @click="etlSync">
          <Database /> Sync ETL meteo
        </button>
        <button type="button" class="btn btn-sm btn-primary" :disabled="busy" @click="mlSync">
          <Cpu /> Sync registro ML
        </button>
        <button type="button" class="btn btn-sm" :disabled="busy" @click="notifTest">
          <BellRing /> Probar notificación
        </button>
      </div>
    </header>

    <SectionCard
      v-if="estado"
      title="Grado de integración"
      :subtitle="`Promedio ${estado.promedio_integracion}% · fase ${estado.fase}`"
    >
      <template #icon><Link2 /></template>
      <ul class="mod-grid">
        <li v-for="m in estado.modulos" :key="m.id" :class="{ ok: m.porcentaje >= 90 }">
          <span class="pct">{{ m.porcentaje }}%</span>
          <strong>{{ m.id }}</strong> {{ m.nombre }}
        </li>
      </ul>
    </SectionCard>

    <div class="grid-2">
      <SectionCard title="Datos (08 + 01)" subtitle="Store SQLite y fuentes">
        <template #icon><Database /></template>
        <p v-if="meteoStore">
          Registros: <strong>{{ meteoStore.registros }}</strong> · Estaciones:
          <strong>{{ meteoStore.estaciones }}</strong>
        </p>
        <p v-if="etlStatus?.ultimo" class="muted small">
          Último ETL: {{ etlStatus.ultimo.timestamp_utc }} · origen {{ etlStatus.ultimo.origen }}
          · registros {{ etlStatus.ultimo.store?.registros ?? '—' }}
        </p>
        <p v-else class="muted small">Sin corridas ETL registradas aún (cron o botón Sync).</p>
        <p v-if="fuentes" class="muted small">
          CSV 5 años: {{ fuentes.csv_disponible ? 'sí' : 'no' }}
        </p>
        <router-link to="/meteo/historico">Ver histórico →</router-link>
      </SectionCard>

      <SectionCard title="Streamlit → Vue" :subtitle="`${cobertura?.cobertura_pct ?? '—'}% con ruta Vue`">
        <p class="muted">{{ cobertura?.con_ruta_vue }}/{{ cobertura?.total_streamlit }} dashboards</p>
        <router-link to="/puertos">Visor de puertos →</router-link>
      </SectionCard>

      <SectionCard title="Agrícola · IoT · ML">
        <template #icon><Sprout /></template>
        <ul class="link-list">
          <li><router-link to="/agricola">Gestión agrícola (02)</router-link></li>
          <li><router-link to="/iot">Sensores y drones (03)</router-link></li>
          <li><router-link to="/ml">Modelos ML (06)</router-link></li>
        </ul>
      </SectionCard>

      <SectionCard title="Monitoreo y reportes (07)">
        <template #icon><FileText /></template>
        <ul class="link-list">
          <li><router-link to="/monitoreo">Alertas activas</router-link></li>
          <li><router-link to="/alertas/config">Config. alertas y notificaciones</router-link></li>
        </ul>
        <ul v-if="reportes.length" class="reportes">
          <li v-for="r in reportes" :key="r.archivo">{{ r.archivo }}</li>
        </ul>
      </SectionCard>

      <SectionCard v-if="deploy" title="Deploy (10)" subtitle="Scripts de producción">
        <p class="muted">{{ deploy.scripts?.length }} scripts · Docker dev: {{ deploy.docker_compose_dev ? 'sí' : 'no' }}</p>
      </SectionCard>

      <SectionCard v-if="tests" title="Testing (09)">
        <p>Tests raíz: {{ tests.tests_raiz }} · CI: {{ tests.ci_github ? 'GitHub Actions' : 'no' }}</p>
      </SectionCard>
    </div>

    <SectionCard v-if="log" title="Registro de acciones" class="log-card">
      <pre class="log">{{ log }}</pre>
    </SectionCard>
  </div>
</template>

<style scoped>
.page {
  max-width: 1100px;
}
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
.mod-grid {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.35rem;
  font-size: 0.78rem;
  padding: 0;
}
.mod-grid li {
  padding: 0.35rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
}
.mod-grid li.ok {
  border-color: var(--color-success);
}
.pct {
  font-weight: 700;
  color: var(--color-primary);
  margin-right: 0.35rem;
}
.grid-2 {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}
.link-list {
  list-style: none;
  padding: 0;
  font-size: 0.85rem;
}
.link-list a {
  color: var(--color-primary);
}
.reportes {
  margin-top: 0.5rem;
  font-size: 0.72rem;
  color: var(--color-muted);
}
.small {
  font-size: 0.75rem;
}
.log {
  font-size: 0.72rem;
  max-height: 120px;
  overflow: auto;
  margin: 0;
}
</style>
