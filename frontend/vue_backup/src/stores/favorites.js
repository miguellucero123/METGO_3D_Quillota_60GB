import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { fetchPreferencias, savePreferencias } from '@/api/metgoApi'
import { SITIO_QUILLOTA } from '@/stores/preferences'

function storageKey(userId) {
  return `metgo_favorites_${userId || 'anon'}`
}

export const useFavoritesStore = defineStore('favorites', () => {
  const stationIds = ref([])
  const syncing = ref(false)

  const auth = useAuthStore()

  function loadLocal() {
    const key = storageKey(auth.user?.id || auth.user?.username)
    try {
      const raw = JSON.parse(localStorage.getItem(key) || '[]')
      stationIds.value = Array.isArray(raw) ? raw : []
    } catch {
      stationIds.value = []
    }
  }

  function persistLocal() {
    const key = storageKey(auth.user?.id || auth.user?.username)
    localStorage.setItem(key, JSON.stringify(stationIds.value))
  }

  async function persistServer() {
    if (!auth.isAuthenticated || syncing.value) return
    try {
      await savePreferencias({
        sitio: SITIO_QUILLOTA,
        favorites: [...stationIds.value],
      })
    } catch {
      // offline / Supabase: localStorage ya ok
    }
  }

  function persist() {
    persistLocal()
    void persistServer()
  }

  const ids = computed(() => stationIds.value)

  function isFavorite(id) {
    return stationIds.value.includes(id)
  }

  function toggle(id) {
    if (!id) return
    if (isFavorite(id)) {
      stationIds.value = stationIds.value.filter((x) => x !== id)
    } else {
      stationIds.value = [...stationIds.value, id]
    }
    persist()
  }

  async function syncFromServer() {
    if (!auth.isAuthenticated) {
      loadLocal()
      return
    }
    syncing.value = true
    try {
      const data = await fetchPreferencias(SITIO_QUILLOTA)
      const remote = Array.isArray(data?.favorites) ? data.favorites : []
      if (data?.existe && remote.length) {
        stationIds.value = remote.map(String)
        persistLocal()
      } else if (stationIds.value.length) {
        await persistServer()
      } else {
        loadLocal()
        if (stationIds.value.length) await persistServer()
      }
    } catch {
      loadLocal()
    } finally {
      syncing.value = false
    }
  }

  function load() {
    loadLocal()
  }

  watch(
    () => auth.user?.username,
    () => {
      loadLocal()
    },
    { immediate: true }
  )

  return { ids, isFavorite, toggle, load, syncFromServer, syncing }
})
