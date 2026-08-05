<template>
  <div v-if="isPublicShell" class="app-login" :class="{ 'app-login--landing': isLanding }">
    <router-view />
  </div>
  <div v-else class="app-shell" :class="{ 'app-shell--nav-open': navOpen }">
    <a href="#contenido-principal" class="skip-link">{{ t('app.skipContent') }}</a>
    <OfflineBanner />
    <TrialBanner />
    <AppHeader />
    <div class="app-body">
      <div
        class="nav-backdrop"
        :class="{ 'nav-backdrop--visible': navOpen }"
        aria-hidden="true"
        @click="navOpen = false"
      />
      <AppSidebar />
      <main id="contenido-principal" class="app-main" tabindex="-1">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, provide, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import OfflineBanner from '@/components/layout/OfflineBanner.vue'
import TrialBanner from '@/components/layout/TrialBanner.vue'
import { useAuth } from '@/stores/auth'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const auth = useAuth()

const navOpen = ref(false)
provide('navOpen', navOpen)
provide('toggleNav', () => {
  navOpen.value = !navOpen.value
})
provide('closeNav', () => {
  navOpen.value = false
})

const PUBLIC_NAMES = new Set(['landing', 'login', 'registro', 'verificar'])

function isPublicRoute(r) {
  if (!r) return true
  if (r.meta?.public) return true
  if (PUBLIC_NAMES.has(String(r.name || ''))) return true
  const p = String(r.path || '')
  if (p === '/' || p === '') return true
  if (p === '/login' || p === '/registro' || p === '/verificar') return true
  return false
}

const isPublicShell = computed(() => isPublicRoute(route))
const isLanding = computed(() => route.name === 'landing' || route.path === '/')

watch(
  () => route.fullPath,
  () => {
    navOpen.value = false
  },
)

onMounted(async () => {
  await router.isReady()
  if (isPublicRoute(route)) return
  await auth.ensureValidSession()
})
</script>

<style scoped>
.app-login--landing {
  min-height: 100vh;
  padding: 0;
  background: transparent;
}
</style>
