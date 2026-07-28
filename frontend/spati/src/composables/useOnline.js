import { ref, onMounted, onUnmounted } from 'vue'

/** Conectividad del navegador (E11 offline banner). */
export function useOnline() {
  const online = ref(typeof navigator !== 'undefined' ? navigator.onLine : true)

  function sync() {
    online.value = navigator.onLine
  }

  onMounted(() => {
    window.addEventListener('online', sync)
    window.addEventListener('offline', sync)
  })
  onUnmounted(() => {
    window.removeEventListener('online', sync)
    window.removeEventListener('offline', sync)
  })

  return { online }
}
