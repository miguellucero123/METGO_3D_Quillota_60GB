import { ref } from 'vue'

/**
 * Carga async con estado loading/error (Fase 2 — DT-3).
 * @param {() => Promise<any>} fetcher
 */
export function useApiCall(fetcher) {
  const data = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function run(...args) {
    loading.value = true
    error.value = null
    try {
      data.value = await fetcher(...args)
      return data.value
    } catch (e) {
      error.value = e?.message || 'Error de API'
      data.value = null
      throw e
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, run }
}
