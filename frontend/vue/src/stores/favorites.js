import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'

function storageKey(userId) {
  return `metgo_favorites_${userId || 'anon'}`
}

export const useFavoritesStore = defineStore('favorites', () => {
  const stationIds = ref([])

  const auth = useAuthStore()

  function load() {
    const key = storageKey(auth.user?.id || auth.user?.username)
    try {
      const raw = JSON.parse(localStorage.getItem(key) || '[]')
      stationIds.value = Array.isArray(raw) ? raw : []
    } catch {
      stationIds.value = []
    }
  }

  function persist() {
    const key = storageKey(auth.user?.id || auth.user?.username)
    localStorage.setItem(key, JSON.stringify(stationIds.value))
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

  watch(
    () => auth.user?.username,
    () => load(),
    { immediate: true }
  )

  return { ids, isFavorite, toggle, load }
})
