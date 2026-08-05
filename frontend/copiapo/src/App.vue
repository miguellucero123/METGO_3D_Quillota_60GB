<template>
  <div v-if="isPublicShell" class="app-login" :class="{ 'app-login--landing': route.name === 'landing' }">
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

const isPublicShell = computed(
  () => route.name === 'login' || route.name === 'landing' || route.name === 'registro' || route.name === 'verificar',
)

watch(
  () => route.fullPath,
  () => {
    navOpen.value = false
  },
)

onMounted(async () => {
  if (isPublicShell.value) return
  const ok = await auth.ensureValidSession()
  if (!ok) router.replace({ name: 'login', query: { redirect: route.fullPath } })
})
</script>

<style scoped>
.app-login--landing {
  min-height: 100vh;
  padding: 0;
  background: transparent;
}
</style>
