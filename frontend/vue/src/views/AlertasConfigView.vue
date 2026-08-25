<script setup>
import { ref, onMounted } from 'vue'
import { Settings2, Plus, Trash2 } from 'lucide-vue-next'
import { useMetgoStore } from '@/stores/metgo'
import SectionCard from '@/components/ui/SectionCard.vue'
import { useRbac } from '@/composables/useRbac'
import {
  fetchAlertasConfig,
  crearAlertaConfig,
  eliminarAlertaConfig,
  fetchNotificacionesConfig,
  guardarNotificacionesConfig,
  probarNotificaciones,
  fetchNotificacionesStatus,
  fetchNotificacionesOutbox,
  reintentarNotificacionesOutbox,
} from '@/api/metgoApi'
import { useApiCall } from '@/composables/useApiCall'

const store = useMetgoStore()
const { canManageAlertas, canDeleteAlertas } = useRbac()
const reglas = ref([])

const form = ref({
  estacion: 'quillota',
  variable: 'temperatura_max',
  operador: '>',
  umbral: 30,
  activa: true,
})
const notif = ref({
  email_habilitado: false,
  email_destino: '',
  webhook_url: '',
  webhook_habilitado: true,
  alertas_auto_email: true,
})
const notifMsg = ref('')
const notifStatus = ref(null)
const outbox = ref([])
const { loading: cargando, error, run: runCargar } = useApiCall(async () => {
  reglas.value = await fetchAlertasConfig()
  const nc = await fetchNotificacionesConfig()
  notif.value = { ...notif.value, ...nc }
  notifStatus.value = await fetchNotificacionesStatus().catch(() => null)
  const ob = await fetchNotificacionesOutbox(15).catch(() => ({ items: [] }))
  outbox.value = ob.items || []
})

async function cargar() {
  await runCargar()
  if (error.value) {
    reglas.value = []
  }
}

async function agregar() {
  if (!canManageAlertas()) return
  try {
    await crearAlertaConfig({ ...form.value })
    await cargar()
  } catch (e) {
    error.value = e.message
  }
}

async function borrar(id) {
  if (!canDeleteAlertas()) return
  try {
    await eliminarAlertaConfig(id)
    await cargar()
  } catch (e) {
    error.value = e.message
  }
}

async function guardarNotif() {
  try {
    notif.value = await guardarNotificacionesConfig(notif.value)
    notifMsg.value = 'Configuración guardada'
  } catch (e) {
    notifMsg.value = e.message
  }
}

async function probarNotif() {
  try {
    const r = await probarNotificaciones('Prueba alertas METGO3D')
    const canal = r.canal || (r.canales || []).map((c) => c.canal).join(', ')
    notifMsg.value = `Enviado: ${canal || 'ok'}`
    await cargar()
  } catch (e) {
    notifMsg.value = e.message
  }
}

async function reintentarOutbox() {
  try {
    const r = await reintentarNotificacionesOutbox(10)
    notifMsg.value = `Outbox: ${r.enviados} enviados, ${r.fallidos} fallidos`
    await cargar()
  } catch (e) {
    notifMsg.value = e.message
  }
}

onMounted(cargar)
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h2 class="page-title">Configuración de alertas</h2>
      <p class="page-subtitle">Umbrales personalizados por estación y variable</p>
    </header>

    <SectionCard title="Mis reglas" :subtitle="`${reglas.length} regla(s)`">
      <template #icon><Settings2 /></template>
      <p v-if="cargando" class="skeleton">Cargando…</p>
      <p v-else-if="error" class="error-text">{{ error }}</p>
      <ul v-else class="rule-list">
        <li v-for="r in reglas" :key="r.id" class="rule-item">
          <span>
            {{ r.estacion }} · {{ r.variable }} {{ r.operador }} {{ r.umbral }}
            <span v-if="!r.activa" class="badge badge--neutral">inactiva</span>
          </span>
          <button
            v-if="canDeleteAlertas()"
            type="button"
            class="icon-btn"
            title="Eliminar"
            @click="borrar(r.id)"
          >
            <Trash2 aria-hidden="true" />
          </button>
        </li>
      </ul>
      <p v-if="!cargando && !reglas.length" class="muted">Sin reglas. Cree una abajo.</p>
    </SectionCard>

    <SectionCard v-if="canManageAlertas()" title="Nueva regla">
      <form class="form-grid" @submit.prevent="agregar">
        <label>
          Estación
          <select v-model="form.estacion">
            <option v-for="e in store.estaciones" :key="e.id" :value="e.id">
              {{ e.nombre }}
            </option>
          </select>
        </label>
        <label>
          Variable
          <select v-model="form.variable">
            <option value="temperatura_max">T° máx</option>
            <option value="temperatura_min">T° mín</option>
            <option value="precipitacion">Precipitación</option>
            <option value="viento">Viento</option>
            <option value="humedad">Humedad</option>
          </select>
        </label>
        <label>
          Operador
          <select v-model="form.operador">
            <option value=">">&gt;</option>
            <option value="<">&lt;</option>
            <option value=">=">&gt;=</option>
            <option value="<=">&lt;=</option>
          </select>
        </label>
        <label>
          Umbral
          <input v-model.number="form.umbral" type="number" step="0.1" />
        </label>
        <button type="submit" class="btn-primary">
          <Plus class="btn-icon" aria-hidden="true" /> Agregar
        </button>
      </form>
    </SectionCard>
    <p v-else class="muted">Su rol no puede crear reglas de alerta.</p>

    <SectionCard title="Notificaciones (07)" subtitle="Multicanal · Fase 9">
      <p v-if="notifStatus" class="muted small">
        Canal recomendado: <strong>{{ notifStatus.canal_recomendado }}</strong>
        · SMTP {{ notifStatus.smtp_configurado ? 'sí' : 'no' }}
        · Webhook {{ notifStatus.webhook_activo ? 'sí' : 'no' }}
        · Outbox pendientes: {{ notifStatus.outbox_pendientes }}
      </p>
      <label class="chk">
        <input v-model="notif.email_habilitado" type="checkbox" />
        Email habilitado
      </label>
      <label class="chk">
        <input v-model="notif.alertas_auto_email" type="checkbox" />
        Enviar alertas warning/critical automáticamente
      </label>
      <label>
        Email destino
        <input v-model="notif.email_destino" type="email" placeholder="miguel.lucero@metgo3d.com" />
      </label>
      <label class="chk">
        <input v-model="notif.webhook_habilitado" type="checkbox" />
        Webhook habilitado
      </label>
      <label>
        Webhook URL
        <input v-model="notif.webhook_url" type="url" placeholder="https://hooks.example.com/..." />
      </label>
      <div class="notif-actions">
        <button type="button" class="btn-primary" @click="guardarNotif">Guardar</button>
        <button type="button" class="btn btn-sm" @click="probarNotif">Probar</button>
        <button
          v-if="canManageAlertas()"
          type="button"
          class="btn btn-sm"
          @click="reintentarOutbox"
        >
          Reintentar outbox
        </button>
      </div>
      <p v-if="notifMsg" class="muted small">{{ notifMsg }}</p>
      <ul v-if="outbox.length" class="outbox-list">
        <li v-for="o in outbox" :key="o.id || o.timestamp_utc">
          {{ o.estado }} · {{ o.asunto }} → {{ o.destino }}
        </li>
      </ul>
    </SectionCard>
  </div>
</template>

<style scoped>
.chk {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}
.notif-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
}
.small {
  font-size: 0.75rem;
  margin-top: 0.5rem;
}
.outbox-list {
  list-style: none;
  padding: 0;
  margin: 0.75rem 0 0;
  font-size: 0.75rem;
  color: var(--color-muted);
}
.outbox-list li {
  padding: 0.25rem 0;
  border-bottom: 1px solid var(--color-border);
}

.rule-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.rule-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-border);
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0.75rem;
  align-items: end;
}
.form-grid label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8rem;
}
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}
.btn-icon {
  width: 1rem;
  height: 1rem;
}
.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-muted);
}
.error-text {
  color: var(--color-danger, #b91c1c);
}
</style>
