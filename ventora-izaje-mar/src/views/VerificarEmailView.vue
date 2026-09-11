<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MailCheck, AlertCircle } from 'lucide-vue-next'
import { verifyEmail } from '@/services/authApi'

const route = useRoute()
const router = useRouter()
const msg = ref('Verificando…')
const ok = ref(false)
const showModal = ref(false)
const done = ref(false)

const puerto = computed(() => String(route.params.puerto || '').toLowerCase())
const loginPath = computed(() => (puerto.value ? `/p/${puerto.value}/login` : '/login'))

onMounted(async () => {
  const token = typeof route.query.token === 'string' ? route.query.token : ''
  if (!token) {
    msg.value = 'Falta token de verificación'
    done.value = true
    showModal.value = true
    return
  }
  try {
    const res = await verifyEmail(token)
    ok.value = true
    msg.value = res.message || 'Email verificado. Su cuenta está activada.'
  } catch (e) {
    msg.value = e.message || 'No se pudo verificar'
  } finally {
    done.value = true
    showModal.value = true
  }
})

function irLogin() {
  router.replace({
    path: loginPath.value,
    query: ok.value ? { verified: '1' } : undefined,
  })
}
</script>

<template>
  <div class="box">
    <h1>Verificación de email</h1>
    <p v-if="!done">{{ msg }}</p>

    <div v-if="showModal" class="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="act-title">
      <div class="modal">
        <div class="icon" :class="ok ? 'ok' : 'err'">
          <MailCheck v-if="ok" :size="36" aria-hidden="true" />
          <AlertCircle v-else :size="36" aria-hidden="true" />
        </div>
        <h2 id="act-title">{{ ok ? 'Cuenta activada' : 'No se pudo activar' }}</h2>
        <p>{{ msg }}</p>
        <button type="button" class="btn-primary" @click="irLogin">
          {{ ok ? 'Entrar a VENTORA' : 'Ir al login' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.box {
  min-height: 60vh;
  display: grid;
  place-content: center;
  text-align: center;
  color: var(--color-text);
  padding: 2rem;
}
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.72);
  display: grid;
  place-items: center;
  z-index: 80;
  padding: 1rem;
}
.modal {
  background: var(--color-surface, #1e293b);
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 16px;
  padding: 1.75rem 1.5rem;
  max-width: 420px;
  width: 100%;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.45);
}
.icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  margin: 0 auto 1rem;
}
.icon.ok {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
}
.icon.err {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}
.modal h2 {
  margin: 0 0 0.5rem;
  font-size: 1.35rem;
}
.modal p {
  margin: 0 0 1.25rem;
  color: var(--color-muted, #94a3b8);
  line-height: 1.45;
}
.btn-primary {
  width: 100%;
  border: 0;
  border-radius: 10px;
  padding: 0.75rem 1rem;
  font-weight: 700;
  cursor: pointer;
  background: #0ea5e9;
  color: #0f172a;
}
</style>
