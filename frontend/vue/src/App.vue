<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMetgoStore } from '@/stores/metgo'
import MetgoHeader from '@/components/layout/MetgoHeader.vue'
import MetgoSidebar from '@/components/layout/MetgoSidebar.vue'

const route = useRoute()
const auth = useAuthStore()
const store = useMetgoStore()

const isLoginPage = computed(() => route.name === 'login')

onMounted(() => {
  if (auth.isAuthenticated) {
    store.inicializar()
  }
})
</script>

<template>
  <div v-if="isLoginPage" class="app-login">
    <RouterView />
  </div>
  <div v-else class="app-shell">
    <MetgoHeader />
    <div class="app-body">
      <MetgoSidebar />
      <main class="app-main">
        <RouterView />
      </main>
    </div>
  </div>
</template>
