<template>
  <div v-if="isLogin" class="app-login">
    <router-view />
  </div>
  <div v-else class="app-shell">
    <AppHeader />
    <div class="app-body">
      <AppSidebar />
      <main class="app-main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import { useAuth } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuth()

const isLogin = computed(() => route.name === 'login')

onMounted(async () => {
  if (isLogin.value) return
  const ok = await auth.ensureValidSession()
  if (!ok) router.replace({ name: 'login', query: { redirect: route.fullPath } })
})
</script>
