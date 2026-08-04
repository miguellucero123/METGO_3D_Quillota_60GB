<script setup>
import { computed, onMounted, provide, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMetgoStore } from '@/stores/metgo'
import { usePreferencesStore } from '@/stores/preferences'
import { useFavoritesStore } from '@/stores/favorites'
import MetgoHeader from '@/components/layout/MetgoHeader.vue'
import MetgoSidebar from '@/components/layout/MetgoSidebar.vue'
import OfflineBanner from '@/components/layout/OfflineBanner.vue'

const route = useRoute()
const auth = useAuthStore()
const store = useMetgoStore()
const preferences = usePreferencesStore()
const favorites = useFavoritesStore()

const navOpen = ref(false)
provide('navOpen', navOpen)
provide('toggleNav', () => {
  navOpen.value = !navOpen.value
})
provide('closeNav', () => {
  navOpen.value = false
})

const isPublicShell = computed(
  () =>
    route.name === 'login' ||
    route.name === 'registro' ||
    route.name === 'verificar' ||
    route.name === 'landing',
)

const isEmbedded = computed(
  () => route.query.embed === '1' || (typeof window !== 'undefined' && window.self !== window.top),
)

watch(
  () => route.fullPath,
  () => {
    navOpen.value = false
  }
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
  <div v-if="isPublicShell" class="app-login" :class="{ 'app-login--landing': route.name === 'landing' }">
    <RouterView />
  </div>
  <div v-else class="app-shell" :class="{ 'app-shell--embed': isEmbedded, 'app-shell--nav-open': navOpen }">
    <a href="#contenido-principal" class="skip-link">{{ $t('app.skipContent') }}</a>
    <OfflineBanner />
    <MetgoHeader />
    <div class="app-body">
      <div
        class="nav-backdrop"
        :class="{ 'nav-backdrop--visible': navOpen }"
        aria-hidden="true"
        @click="navOpen = false"
      />
      <MetgoSidebar />
      <main id="contenido-principal" class="app-main" tabindex="-1">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-login--landing {
  min-height: 100vh;
  padding: 0;
  background: transparent;
}
</style>
