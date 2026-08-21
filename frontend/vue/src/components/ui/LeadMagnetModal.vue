<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { submitLeadData } from '@/api/metgoApi'
import { trackEvent } from '@/utils/analytics'
import { X, FileDown, Shield } from 'lucide-vue-next'

const STORAGE_KEY = 'metgo_lead_modal_shown'
const DELAY_MS = 30000 // 30 seconds
const visible = ref(false)

const form = ref({ email: '', nombre: '', empresa: '' })
const sending = ref(false)
const sent = ref(false)

let exitTimer = null

function showModal() {
  if (localStorage.getItem(STORAGE_KEY)) return
  visible.value = true
  localStorage.setItem(STORAGE_KEY, '1')
  trackEvent('lead_magnet_view', { source: 'exit_intent_modal' })
}

function close() {
  visible.value = false
}

function onMouseLeave(e) {
  if (e.clientY <= 0 && !visible.value) {
    showModal()
  }
}

onMounted(() => {
  if (localStorage.getItem(STORAGE_KEY)) return

  // Exit intent (desktop)
  document.addEventListener('mouseout', onMouseLeave)

  // Fallback: show after 30s if not triggered
  exitTimer = setTimeout(() => {
    if (!visible.value) showModal()
  }, DELAY_MS)
})

onUnmounted(() => {
  document.removeEventListener('mouseout', onMouseLeave)
  if (exitTimer) clearTimeout(exitTimer)
})

async function submit() {
  if (!form.value.email || sending.value) return
  sending.value = true
  try {
    await submitLeadData({
      email: form.value.email,
      nombre: form.value.nombre,
      empresa: form.value.empresa,
      sector: '',
      telefono: '',
      mensaje: 'Lead magnet: Guía Pronóstico Heladas',
      source: 'lead_magnet_modal',
    })
    sent.value = true
    trackEvent('lead_magnet_submit', { source: 'exit_intent_modal' })
    setTimeout(close, 5000)
  } catch {
    // Silent fail
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="visible" class="modal-overlay" @click.self="close">
        <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="lead-modal-title">
          <button class="modal-close" @click="close" aria-label="Cerrar">
            <X :size="20" />
          </button>

          <div class="modal-icon-wrap">
            <FileDown :size="32" />
          </div>

          <h2 id="lead-modal-title" class="modal-title">
            Guía gratuita: Pronóstico de Heladas
          </h2>
          <p class="modal-subtitle">
            Descarga nuestra guía técnica con umbrales de riesgo por cultivo 
            para el Valle de Aconcagua. Incluye protocolo de acción ante alertas.
          </p>

          <template v-if="!sent">
            <form class="modal-form" @submit.prevent="submit">
              <div class="modal-field">
                <input
                  v-model="form.email"
                  type="email"
                  required
                  placeholder="tu@email.com"
                  aria-label="Email"
                />
              </div>
              <div class="modal-field-row">
                <input
                  v-model="form.nombre"
                  type="text"
                  placeholder="Nombre (opcional)"
                  aria-label="Nombre"
                />
                <input
                  v-model="form.empresa"
                  type="text"
                  placeholder="Empresa (opcional)"
                  aria-label="Empresa"
                />
              </div>
              <button type="submit" class="modal-btn" :disabled="sending">
                <FileDown :size="16" />
                {{ sending ? 'Enviando...' : 'Descargar guía gratuita' }}
              </button>
            </form>
            <p class="modal-privacy">
              <Shield :size="12" />
              No compartimos tu email. Puedes cancelar cuando quieras.
            </p>
          </template>

          <div v-else class="modal-success">
            <div class="modal-success-icon">✓</div>
            <h3>¡Listo!</h3>
            <p>Revisa tu bandeja de entrada. Te enviaremos la guía y acceso a alertas de prueba.</p>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 500;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-card {
  position: relative;
  background: linear-gradient(165deg, #101d32 0%, #0a1221 100%);
  border: 1px solid rgba(0, 255, 170, 0.15);
  border-radius: 20px;
  padding: 48px 40px 36px;
  max-width: 480px;
  width: 100%;
  text-align: center;
  box-shadow:
    0 24px 80px rgba(0, 0, 0, 0.5),
    0 0 60px rgba(0, 255, 170, 0.06);
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: transparent;
  border: none;
  color: #4c5a70;
  cursor: pointer;
  padding: 4px;
  transition: color 0.15s;
}

.modal-close:hover {
  color: #f4f7fa;
}

.modal-icon-wrap {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: linear-gradient(145deg, rgba(0, 255, 170, 0.15), rgba(0, 255, 170, 0.05));
  border: 1px solid rgba(0, 255, 170, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  color: #00ffaa;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.3px;
  margin-bottom: 12px;
  color: #f4f7fa;
}

.modal-subtitle {
  font-size: 14px;
  color: #8fa0b3;
  line-height: 1.65;
  margin-bottom: 28px;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.modal-field input,
.modal-field-row input {
  width: 100%;
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  color: #f4f7fa;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.modal-field input::placeholder,
.modal-field-row input::placeholder {
  color: #4c5a70;
}

.modal-field input:focus,
.modal-field-row input:focus {
  outline: none;
  border-color: #00ffaa;
  box-shadow: 0 0 0 3px rgba(0, 255, 170, 0.12);
}

.modal-field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.modal-btn {
  margin-top: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 24px;
  border-radius: 10px;
  border: none;
  background: #00ffaa;
  color: #04140e;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}

.modal-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 255, 170, 0.3);
}

.modal-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.modal-privacy {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 14px;
  font-size: 11px;
  color: #4c5a70;
}

.modal-success {
  padding: 20px 0;
  animation: fade-in 0.5s ease;
}

.modal-success-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(0, 255, 170, 0.12);
  border: 2px solid #00ffaa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  font-size: 24px;
  color: #00ffaa;
}

.modal-success h3 {
  font-size: 1.2rem;
  margin-bottom: 8px;
  color: #f4f7fa;
}

.modal-success p {
  font-size: 14px;
  color: #8fa0b3;
  line-height: 1.6;
}

/* Transitions */
.modal-fade-enter-active {
  transition: opacity 0.3s ease;
}
.modal-fade-enter-active .modal-card {
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.3s;
}
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}
.modal-fade-leave-active .modal-card {
  transition: transform 0.2s ease-in, opacity 0.2s;
}
.modal-fade-enter-from {
  opacity: 0;
}
.modal-fade-enter-from .modal-card {
  transform: scale(0.92) translateY(20px);
  opacity: 0;
}
.modal-fade-leave-to {
  opacity: 0;
}
.modal-fade-leave-to .modal-card {
  transform: scale(0.95);
  opacity: 0;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 560px) {
  .modal-card {
    padding: 36px 24px 28px;
  }
  .modal-field-row {
    grid-template-columns: 1fr;
  }
}
</style>
