<script setup>
import { computed, inject, onMounted, ref } from 'vue'
import { fetchCuenta, checkoutPlan, wakeApi, invitarUsuario, exportMyData, deleteMyAccount } from '@/services/authApi'
import { useAuth } from '@/stores/auth'

const site = inject('site')
const auth = useAuth()
const sitioId = computed(() => site?.sitio || 'copiapo')
const faenaId = computed(() => site?.faena?.id || undefined)

const loading = ref(true)
const error = ref('')
const msg = ref('')
const data = ref(null)
const applying = ref('')
const invite = ref({ email: '', password: '', nombres: '', apellidos: '', role: 'operador' })
const inviting = ref(false)
const inviteMsg = ref('')
const inviteErr = ref('')
const inviteVerifyUrl = ref('')
const inviteCopied = ref(false)

const privacyBusy = ref('')
const privacyMsg = ref('')
const privacyErr = ref('')
const confirmDelete = ref('')

async function descargarMisDatos() {
  privacyMsg.value = ''
  privacyErr.value = ''
  privacyBusy.value = 'export'
  try {
    const payload = await exportMyData()
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'metgo-mis-datos-' + new Date().toISOString().slice(0, 10) + '.json'
    a.click()
    URL.revokeObjectURL(url)
    privacyMsg.value = 'Exportacion descargada (JSON).'
  } catch (e) {
    privacyErr.value = e.message || 'No se pudo exportar'
  } finally {
    privacyBusy.value = ''
  }
}

async function solicitarOlvido(logoutFn, loginPath) {
  privacyMsg.value = ''
  privacyErr.value = ''
  if (confirmDelete.value.trim().toUpperCase() !== 'ELIMINAR') {
    privacyErr.value = 'Escribe ELIMINAR para confirmar el derecho al olvido.'
    return
  }
  privacyBusy.value = 'delete'
  try {
    const res = await deleteMyAccount()
    privacyMsg.value = res.message || 'Cuenta anonimizada.'
    if (logoutFn) logoutFn()
    if (loginPath) window.location.assign(loginPath)
  } catch (e) {
    privacyErr.value = e.message || 'No se pudo eliminar'
  } finally {
    privacyBusy.value = ''
  }
}

async function onOlvido() {
  await solicitarOlvido(() => { try { auth.logout() } catch (_) {} }, '/login')
}


onMounted(async () => {
  wakeApi().catch(() => {})
  await reload()
})

async function reload() {
  loading.value = true
  error.value = ''
  try {
    data.value = await fetchCuenta(faenaId.value)
  } catch (e) {
    error.value = e.message || 'No se pudo cargar la cuenta'
  } finally {
    loading.value = false
  }
}

async function elegirPlan(planCode) {
  msg.value = ''
  applying.value = planCode
  try {
    const res = await checkoutPlan({
      plan_code: planCode,
      sitio: sitioId.value,
      faena: faenaId.value,
      org_id: auth.state.user?.org_id || data.value?.usuario?.org_id,
      success_url: `${window.location.origin}/cuenta?checkout=success`,
      cancel_url: `${window.location.origin}/cuenta?checkout=cancel`,
    })
    if (res.checkout_url) {
      window.location.href = res.checkout_url
      return
    }
    msg.value = res.message || (res.applied ? 'Plan aplicado' : 'OK')
    await reload()
  } catch (e) {
    error.value = e.message || 'Error al cambiar plan'
  } finally {
    applying.value = ''
  }
}

async function enviarInvitacion() {
  inviteMsg.value = ''
  inviteErr.value = ''
  inviteVerifyUrl.value = ''
  inviteCopied.value = false
  inviting.value = true
  try {
    const res = await invitarUsuario({
      ...invite.value,
      nombres: invite.value.nombres || 'Invitado',
      apellidos: invite.value.apellidos || 'METGO',
      org_id: auth.state.user?.org_id || data.value?.usuario?.org_id,
    })
    inviteMsg.value = res.message || 'Invitación creada. El usuario debe verificar el email.'
    inviteVerifyUrl.value = res.verify_url || ''
    if (inviteVerifyUrl.value) {
      inviteMsg.value += ' Podés copiar el link de verificación abajo.'
    }
    invite.value = { email: '', password: '', nombres: '', apellidos: '', role: 'operador' }
  } catch (e) {
    inviteErr.value = e.message || 'No se pudo invitar'
  } finally {
    inviting.value = false
  }
}

async function copiarVerifyUrl() {
  if (!inviteVerifyUrl.value) return
  try {
    await navigator.clipboard.writeText(inviteVerifyUrl.value)
    inviteCopied.value = true
    setTimeout(() => {
      inviteCopied.value = false
    }, 2000)
  } catch {
    inviteErr.value = 'No se pudo copiar al portapapeles'
  }
}

const planes = computed(() => data.value?.planes?.planes || [])
const sub = computed(() => data.value?.suscripcion)
const tabs = computed(() => data.value?.access?.tabs || {})
</script>

<template>
  <div class="cuenta">
    <header>
      <h1>Cuenta · {{ site?.siteLabel || sitioId }}</h1>
      <p>Suscripción, piloto y planes del producto.</p>
    </header>

    <p v-if="loading">Cargando…</p>
    <p v-else-if="error" class="err" role="alert">{{ error }}</p>
    <p v-if="msg" class="ok">{{ msg }}</p>

    <section v-if="data" class="card">
      <h2>Usuario</h2>
      <dl>
        <div><dt>Email</dt><dd>{{ data.usuario?.email }}</dd></div>
        <div>
          <dt>Estado</dt>
          <dd>{{ data.usuario?.status }} · verificado: {{ data.usuario?.email_verified ? 'sí' : 'no' }}</dd>
        </div>
        <div><dt>Sitio</dt><dd>{{ data.usuario?.sitio }}</dd></div>
      </dl>
    </section>

    <section v-if="sub" class="card">
      <h2>Suscripción actual</h2>
      <p>
        Plan <strong>{{ sub.plan_code }}</strong> ·
        estado <strong>{{ sub.status }}</strong>
        <template v-if="sub.current_period_end"> · hasta {{ String(sub.current_period_end).slice(0, 10) }}</template>
      </p>
      <ul v-if="Object.keys(tabs).length" class="tabs">
        <li v-for="(ok, tab) in tabs" :key="tab" :class="{ on: ok }">
          {{ tab }}: {{ ok ? 'habilitado' : 'bloqueado' }}
        </li>
      </ul>
    </section>

    <section class="card">
      <h2>Planes</h2>
      <p class="hint">Sin Stripe: el checkout mock aplica el plan de inmediato.</p>
      <ul class="planes">
        <li v-for="p in planes" :key="p.plan_code">
          <div>
            <strong>{{ p.nombre }}</strong>
            <em>{{ p.descripcion || (p.features || []).join(', ') }}</em>
          </div>
          <button
            type="button"
            class="btn"
            :disabled="!!applying || p.contacto || sub?.plan_code === p.plan_code"
            @click="elegirPlan(p.plan_code)"
          >
            {{ applying === p.plan_code ? '…' : sub?.plan_code === p.plan_code ? 'Actual' : 'Elegir' }}
          </button>
        </li>
      </ul>
    </section>

    
    <section v-if="data" class="card privacy-card">
      <h2>Privacidad y derechos (Ley 21.719)</h2>
      <p class="hint">
        Portabilidad y cancelacion.
        <a href="https://metgo3d.com/privacidad/" target="_blank" rel="noopener noreferrer">Politica</a>.
      </p>
      <div class="privacy-actions">
        <button type="button" class="btn" :disabled="!!privacyBusy" @click="descargarMisDatos">
          {{ privacyBusy === 'export' ? '...' : 'Descargar mis datos (JSON)' }}
        </button>
        <label class="delete-confirm">
          Confirmar olvido
          <input v-model="confirmDelete" type="text" placeholder="Escribe ELIMINAR" autocomplete="off" />
        </label>
        <button type="button" class="btn btn-danger" :disabled="!!privacyBusy" @click="onOlvido">
          {{ privacyBusy === 'delete' ? '...' : 'Solicitar eliminacion de cuenta' }}
        </button>
      </div>
      <p v-if="privacyMsg" class="ok">{{ privacyMsg }}</p>
      <p v-if="privacyErr" class="err">{{ privacyErr }}</p>
    </section>

    <section v-if="data" class="card">
      <h2>Invitar usuario a esta org</h2>
      <p class="hint">Mismo RUT/org · otro email. El invitado verifica correo y entra con la clave indicada.</p>
      <form class="invite-form" @submit.prevent="enviarInvitacion">
        <label>Email <input v-model="invite.email" type="email" required /></label>
        <label>Contraseña inicial <input v-model="invite.password" type="password" required minlength="10" /></label>
        <label>Nombres <input v-model="invite.nombres" type="text" /></label>
        <label>Apellidos <input v-model="invite.apellidos" type="text" /></label>
        <label>
          Rol
          <select v-model="invite.role">
            <option value="operador">Operador</option>
            <option value="viewer">Viewer</option>
            <option value="admin">Admin</option>
          </select>
        </label>
        <button type="submit" class="btn" :disabled="inviting">{{ inviting ? '…' : 'Invitar' }}</button>
      </form>
      <p v-if="inviteMsg" class="ok">{{ inviteMsg }}</p>
      <div v-if="inviteVerifyUrl" class="invite-link">
        <code>{{ inviteVerifyUrl }}</code>
        <button type="button" class="btn btn-ghost" @click="copiarVerifyUrl">
          {{ inviteCopied ? 'Copiado' : 'Copiar link' }}
        </button>
      </div>
      <p v-if="inviteErr" class="err">{{ inviteErr }}</p>
    </section>
  </div>
</template>

<style scoped>
.cuenta { padding: 1.25rem; max-width: 820px; color: var(--color-text); }
header h1 { margin: 0 0 0.25rem; font-size: 1.35rem; }
header p, .hint { color: var(--color-muted, var(--color-text-secondary)); font-size: 0.9rem; }
.card {
  margin-top: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 1rem;
  background: var(--color-surface, rgba(17, 24, 39, 0.55));
}
dl { display: grid; gap: 0.5rem; margin: 0; }
dt { font-size: 0.7rem; text-transform: uppercase; color: var(--color-muted, var(--color-text-secondary)); }
dd { margin: 0; }
.tabs, .planes { list-style: none; padding: 0; margin: 0.75rem 0 0; }
.tabs li { font-size: 0.85rem; color: var(--color-muted, var(--color-text-secondary)); }
.tabs li.on { color: var(--color-primary); font-weight: 600; }
.planes li {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 0.65rem 0;
  border-top: 1px solid var(--color-border);
}
.planes em { display: block; font-style: normal; font-size: 0.8rem; color: var(--color-muted, var(--color-text-secondary)); }
.btn {
  border: none;
  border-radius: 8px;
  padding: 0.45rem 0.85rem;
  font-weight: 600;
  cursor: pointer;
  background: var(--color-primary);
  color: #0f172a;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.err { color: var(--color-danger, #f87171); }
.ok { color: var(--color-primary); }
.invite-form {
  display: grid;
  gap: 0.65rem;
  margin-top: 0.75rem;
  grid-template-columns: 1fr 1fr;
}
.invite-form label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: var(--color-muted, var(--color-text-secondary));
}
.invite-form input,
.invite-form select {
  padding: 0.45rem 0.55rem;
  border-radius: 8px;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text);
}
.invite-form .btn { grid-column: 1 / -1; justify-self: start; }
.invite-link {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
  margin-top: 0.65rem;
}
.invite-link code {
  flex: 1;
  min-width: 12rem;
  font-size: 0.75rem;
  word-break: break-all;
  padding: 0.4rem 0.5rem;
  border-radius: 6px;
  border: 1px solid var(--color-border);
}
.btn-ghost {
  background: transparent;
  color: var(--color-primary);
  border: 1px solid var(--color-border);
}
@media (max-width: 640px) {
  .invite-form { grid-template-columns: 1fr; }
}

.privacy-actions { display:flex; flex-wrap:wrap; gap:0.75rem; align-items:end; margin-top:0.75rem; }
.delete-confirm { display:flex; flex-direction:column; gap:0.25rem; font-size:0.8rem; }
.delete-confirm input { padding:0.45rem 0.55rem; border-radius:8px; border:1px solid var(--color-border); background:transparent; color:var(--color-text); }
.btn-danger { background:#b91c1c; color:#fff; }

</style>
