<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { verifyEmail } from '@/services/authApi'

const route = useRoute()
const router = useRouter()
const msg = ref('Verificando…')
const ok = ref(false)

onMounted(async () => {
  const token = typeof route.query.token === 'string' ? route.query.token : ''
  if (!token) {
    msg.value = 'Falta token de verificación'
    return
  }
  try {
    const res = await verifyEmail(token)
    ok.value = true
    msg.value = res.message || 'Email verificado'
    setTimeout(() => router.replace('/login'), 1500)
  } catch (e) {
    msg.value = e.message || 'No se pudo verificar'
  }
})
</script>

<template>
  <div class="box">
    <h1>Verificación de email</h1>
    <p :class="{ ok }">{{ msg }}</p>
    <router-link to="/login">Ir a ingresar</router-link>
  </div>
</template>

<style scoped>
.box {
  min-height: 100vh;
  display: grid;
  place-content: center;
  text-align: center;
  color: #f8fafc;
  padding: 2rem;
  background: #0b1120;
  gap: 0.75rem;
}
.ok {
  color: #fbbf24;
}
a {
  color: #fbbf24;
}
</style>
