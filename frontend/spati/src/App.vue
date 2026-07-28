<template>
  <div v-if="isLogin" class="app-login">
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

const isLogin = computed(() => route.name === 'login')

watch(
  () => route.fullPath,
  () => {
    navOpen.value = false
  },
)

onMounted(async () => {
  if (isLogin.value) return
  const ok = await auth.ensureValidSession()
  if (!ok) router.replace({ name: 'login', query: { redirect: route.fullPath } })
})
</script>
