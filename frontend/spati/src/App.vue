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
import { computed, inject, onMounted, provide, ref, watch } from 'vue'
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
const site = inject('site', { spatiDefaultSitio: 'quebrada_blanca' })

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

function isPublicRoute(r) {
  if (!r) return true
  if (r.meta?.public) return true
  if (PUBLIC_NAMES.has(String(r.name || ''))) return true
  // Landing siempre pública (evita carrera router.isReady → login Escondida)
  const p = String(r.path || '')
  if (p === '/' || p === '') return true
  if (p.endsWith('/login') || p.endsWith('/registro') || p.endsWith('/verificar')) return true
  return false
}

const isPublicShell = computed(() => isPublicRoute(route))

const defaultFaena = computed(() => site.spatiDefaultSitio || 'quebrada_blanca')
const currentFaena = computed(() => String(route.params.faena || defaultFaena.value))

watch(
  () => route.fullPath,
  () => {
    navOpen.value = false
  },
)

onMounted(async () => {
  await router.isReady()
  if (isPublicRoute(route)) return
  const ok = await auth.ensureValidSession()
  if (!ok) {
    router.replace({
      path: `/f/${currentFaena.value}/login`,
      query: { redirect: route.fullPath },
    })
  }
})
</script>
