<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMetgoStore } from '@/stores/metgo'
import { usePreferencesStore } from '@/stores/preferences'
import { useFavoritesStore } from '@/stores/favorites'
import MetgoHeader from '@/components/layout/MetgoHeader.vue'
import MetgoSidebar from '@/components/layout/MetgoSidebar.vue'

const route = useRoute()
const auth = useAuthStore()
const store = useMetgoStore()
const preferences = usePreferencesStore()
const favorites = useFavoritesStore()

const isAuthPage = computed(() => route.name === 'login' || route.name === 'registro')

const isEmbedded = computed(
  () => route.query.embed === '1' || (typeof window !== 'undefined' && window.self !== window.top),
)

onMounted(async () => {
  preferences.init()
  if (!auth.isAuthenticated) return
  const ok = await auth.ensureValidSession()
  if (ok) {
    await Promise.all([preferences.syncFromServer(), favorites.syncFromServer()])
    await store.inicializar()
  }
})
</script>

<template>
  <div v-if="isAuthPage" class="app-login">
    <RouterView />
  </div>
  <div v-else class="app-shell" :class="{ 'app-shell--embed': isEmbedded }">
    <MetgoHeader />
    <div class="app-body">
      <MetgoSidebar />
      <main class="app-main">
        <RouterView />
      </main>
    </div>
  </div>
</template>
