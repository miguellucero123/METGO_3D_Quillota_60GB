<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  siteKey: { type: String, default: '' },
})
const emit = defineEmits(['token'])

const host = ref(null)
let widgetId = null
let scriptPromise = null

function loadScript() {
  if (window.turnstile) return Promise.resolve()
  if (scriptPromise) return scriptPromise
  scriptPromise = new Promise((resolve, reject) => {
    const s = document.createElement('script')
    s.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit'
    s.async = true
    s.onload = () => resolve()
    s.onerror = () => reject(new Error('No se pudo cargar Turnstile'))
    document.head.appendChild(s)
  })
  return scriptPromise
}

async function renderWidget() {
  if (!props.siteKey || !host.value) return
  await loadScript()
  if (widgetId != null && window.turnstile) {
    try {
      window.turnstile.remove(widgetId)
    } catch {
      /* ignore */
    }
    widgetId = null
  }
  widgetId = window.turnstile.render(host.value, {
    sitekey: props.siteKey,
    theme: 'auto',
    callback: (tok) => emit('token', tok || ''),
    'expired-callback': () => emit('token', ''),
    'error-callback': () => emit('token', ''),
  })
}

onMounted(() => {
  if (props.siteKey) renderWidget().catch(() => emit('token', ''))
})

watch(
  () => props.siteKey,
  (k) => {
    if (k) renderWidget().catch(() => emit('token', ''))
  },
)

onBeforeUnmount(() => {
  if (widgetId != null && window.turnstile) {
    try {
      window.turnstile.remove(widgetId)
    } catch {
      /* ignore */
    }
  }
})
</script>

<template>
  <div v-if="siteKey" ref="host" class="turnstile-host" aria-label="Verificación anti-bot" />
</template>

<style scoped>
.turnstile-host {
  min-height: 65px;
  display: flex;
  justify-content: center;
}
</style>
