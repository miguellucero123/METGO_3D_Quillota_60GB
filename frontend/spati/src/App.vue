<template>
  <div v-if="isPublicShell" class="app-login">
    <router-view />
  </div>
  <div v-else class="app-shell" :class="{ 'app-shell--nav-open': navOpen }">
    <a href="#contenido-principal" class="skip-link">{{ t('app.skipContent') }}</a>
    <OfflineBanner />
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

const PUBLIC_NAMES = new Set([
  'landing',
  'faenas-hub',
  'faena-login',
  'faena-registro',
  'faena-verificar',
])

const isPublicShell = computed(
  () => Boolean(route.meta?.public) || PUBLIC_NAMES.has(String(route.name || '')),
)

const currentFaena = computed(() => String(route.params.faena || 'escondida'))

watch(
  () => route.fullPath,
  () => {
    navOpen.value = false
  },
)

onMounted(async () => {
  if (isPublicShell.value) return
  const ok = await auth.ensureValidSession()
  if (!ok) {
    router.replace({
      path: `/f/${currentFaena.value}/login`,
      query: { redirect: route.fullPath },
    })
  }
})
</script>
