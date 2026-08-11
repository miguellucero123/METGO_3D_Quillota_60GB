<script setup>
import { ShieldOff } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>

<template>
  <div class="page forbidden">
    <ShieldOff class="forbidden__icon" aria-hidden="true" />
    <h2>Acceso no permitido</h2>
    <p>
      Su rol <strong>{{ auth.user?.role }}</strong> no puede abrir esta sección.
    </p>
    <router-link to="/" class="btn-link">Volver al panel</router-link>
  </div>
</template>

<style scoped>
.forbidden {
  text-align: center;
  padding: 3rem 1rem;
  max-width: 28rem;
  margin: 0 auto;
}
.forbidden__icon {
  width: 3rem;
  height: 3rem;
  color: var(--color-warning, #c2410c);
  margin-bottom: 1rem;
}
.btn-link {
  display: inline-block;
  margin-top: 1.25rem;
  color: var(--color-primary);
  font-weight: 600;
}
</style>
