<script setup>
import { ref, onMounted } from 'vue'
import { submitLeadData } from '@/api/metgoApi'
import { trackEvent } from '@/utils/analytics'
import { X, Zap } from 'lucide-vue-next'

const STORAGE_KEY = 'metgo_lead_bar_dismissed'
const email = ref('')
const visible = ref(false)
const sending = ref(false)
const sent = ref(false)

onMounted(() => {
  const dismissed = localStorage.getItem(STORAGE_KEY)
  if (!dismissed) {
    // Delay apparition for better UX (don't flash immediately)
    setTimeout(() => { visible.value = true }, 4000)
  }
})

function dismiss() {
  visible.value = false
  localStorage.setItem(STORAGE_KEY, '1')
}

async function submit() {
  if (!email.value || sending.value) return
  sending.value = true
  try {
    await submitLeadData({
      email: email.value,
      nombre: '',
      empresa: '',
      sector: '',
      telefono: '',
      mensaje: 'Lead magnet: Alerta helada 7 días gratis',
      source: 'lead_magnet_bar',
    })
    sent.value = true
    trackEvent('lead_magnet_submit', { source: 'bottom_bar' })
    setTimeout(dismiss, 4000)
  } catch {
    // Silently fail — don't disrupt UX
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <Transition name="slide-up">
    <div v-if="visible" class="lead-bar" role="complementary" aria-label="Oferta de alerta gratis">
      <div class="lead-bar-inner">
        <div class="lead-bar-content">
          <Zap :size="18" class="lead-bar-icon" />
          <span class="lead-bar-text">
            <strong>Alertas de helada gratis por 7 días</strong>
            <span class="lead-bar-sub">— recibe pronósticos directamente en tu email</span>
          </span>
        </div>

        <form v-if="!sent" class="lead-bar-form" @submit.prevent="submit">
          <input
            v-model="email"
            type="email"
            required
            placeholder="tu@email.com"
            class="lead-bar-input"
            aria-label="Email para alertas gratis"
          />
          <button type="submit" class="lead-bar-btn" :disabled="sending">
            {{ sending ? '...' : 'Quiero mis alertas' }}
          </button>
        </form>
        <p v-else class="lead-bar-success">
          ✓ ¡Listo! Te contactaremos pronto con tu acceso.
        </p>

        <button class="lead-bar-close" @click="dismiss" aria-label="Cerrar barra de oferta">
          <X :size="16" />
        </button>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.lead-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 90;
  background: linear-gradient(135deg, #0a1628 0%, #0d1f3c 100%);
  border-top: 1px solid rgba(0, 255, 170, 0.2);
  box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(12px);
}

.lead-bar-inner {
  max-width: 1120px;
  margin: 0 auto;
  padding: 14px 28px;
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.lead-bar-content {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 200px;
}

.lead-bar-icon {
  color: #00ffaa;
  flex-shrink: 0;
  filter: drop-shadow(0 0 6px rgba(0, 255, 170, 0.5));
  animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
  0%, 100% { filter: drop-shadow(0 0 4px rgba(0, 255, 170, 0.3)); }
  50% { filter: drop-shadow(0 0 10px rgba(0, 255, 170, 0.6)); }
}

.lead-bar-text {
  font-size: 14px;
  color: #f4f7fa;
  line-height: 1.4;
}

.lead-bar-text strong {
  color: #00ffaa;
}

.lead-bar-sub {
  color: #8fa0b3;
}

.lead-bar-form {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.lead-bar-input {
  padding: 8px 14px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.06);
  color: #f4f7fa;
  font-size: 13px;
  font-family: inherit;
  width: 200px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.lead-bar-input::placeholder {
  color: #4c5a70;
}

.lead-bar-input:focus {
  outline: none;
  border-color: #00ffaa;
  box-shadow: 0 0 0 2px rgba(0, 255, 170, 0.15);
}

.lead-bar-btn {
  padding: 8px 20px;
  border-radius: 8px;
  border: none;
  background: #00ffaa;
  color: #04140e;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: transform 0.15s, box-shadow 0.15s;
}

.lead-bar-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(0, 255, 170, 0.3);
}

.lead-bar-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.lead-bar-success {
  color: #00ffaa;
  font-size: 14px;
  font-weight: 600;
  margin: 0;
  animation: fade-in 0.4s ease;
}

.lead-bar-close {
  background: transparent;
  border: none;
  color: #4c5a70;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  transition: color 0.15s;
  flex-shrink: 0;
}

.lead-bar-close:hover {
  color: #f4f7fa;
}

/* Transition */
.slide-up-enter-active {
  transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.4s;
}
.slide-up-leave-active {
  transition: transform 0.3s ease-in, opacity 0.2s;
}
.slide-up-enter-from {
  transform: translateY(100%);
  opacity: 0;
}
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 700px) {
  .lead-bar-inner {
    flex-direction: column;
    align-items: stretch;
    padding: 12px 16px;
    gap: 10px;
  }
  .lead-bar-sub {
    display: none;
  }
  .lead-bar-form {
    flex-direction: column;
  }
  .lead-bar-input {
    width: 100%;
  }
  .lead-bar-close {
    position: absolute;
    top: 8px;
    right: 8px;
  }
  .lead-bar {
    position: relative;
  }
}
</style>
