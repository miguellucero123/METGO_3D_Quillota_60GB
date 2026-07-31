import { computed, reactive } from 'vue'
import { fetchAccess, getToken } from '@/services/authApi'

const TTL_MS = 60_000

const state = reactive({
  /** @type {Record<string, { tabs: Record<string, boolean>, plan_code?: string, sub_status?: string, at: number }>} */
  byFaena: {},
  loading: false,
  error: '',
})

function keyOf(faena) {
  return String(faena || '').toLowerCase()
}

export function useAccess() {
  const loading = computed(() => state.loading)

  function snapshot(faena) {
    return state.byFaena[keyOf(faena)] || null
  }

  function canTab(faena, tab) {
    const snap = snapshot(faena)
    if (!snap?.tabs) return true
    if (tab == null || tab === '') return true
    // Vista Ahora hereda entitlement del panel (planes legacy sin key "ahora")
    if (tab === 'ahora') {
      return Boolean(snap.tabs.ahora || snap.tabs.panel)
    }
    return Boolean(snap.tabs[tab])
  }

  function invalidate(faena) {
    if (faena) {
      delete state.byFaena[keyOf(faena)]
      return
    }
    state.byFaena = {}
  }

  async function refresh(faena, { force = false } = {}) {
    const k = keyOf(faena)
    if (!k || !getToken()) return null
    const prev = state.byFaena[k]
    if (!force && prev?.at && Date.now() - prev.at < TTL_MS) return prev
    state.loading = true
    state.error = ''
    try {
      const data = await fetchAccess({ sitio: 'spati', faena: k })
      const snap = {
        tabs: data.tabs || {},
        plan_code: data.plan_code,
        sub_status: data.sub_status,
        sistemas: data.sistemas || {},
        at: Date.now(),
      }
      state.byFaena[k] = snap
      return snap
    } catch (e) {
      state.error = e?.message || 'access error'
      // Sin romper nav: si ya había cache, se conserva
      return state.byFaena[k] || null
    } finally {
      state.loading = false
    }
  }

  return {
    state,
    loading,
    snapshot,
    canTab,
    invalidate,
    refresh,
  }
}
