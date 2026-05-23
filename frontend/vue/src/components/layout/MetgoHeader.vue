<script setup>
import { useRouter } from 'vue-router'
import { MapPin, LogOut, Activity } from 'lucide-vue-next'
import { useMetgoStore } from '@/stores/metgo'
import { useAuthStore } from '@/stores/auth'

const store = useMetgoStore()
const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <header class="header">
    <div class="header__left">
      <div class="header__title-block">
        <h1 class="header__title">Sistema de monitoreo</h1>
        <p class="header__subtitle">
          <MapPin class="header__pin" aria-hidden="true" />
          Región de Quillota · Valle del Aconcagua
        </p>
      </div>
    </div>
    <div class="header__right">
      <div class="status-pill" :class="store.apiOnline ? 'status-pill--on' : 'status-pill--off'">
        <Activity class="status-pill__icon" aria-hidden="true" />
        {{ store.apiOnline ? 'En línea' : 'Sin conexión' }}
      </div>
      <div v-if="auth.user" class="user-chip">{{ auth.user.username }}</div>
      <label class="station-select">
        <span class="station-select__label">Estación</span>
        <select v-model="store.estacionActiva" @change="store.cargarDatosMeteo()">
          <option v-for="e in store.estaciones" :key="e.id" :value="e.id">
            {{ e.nombre }}
          </option>
        </select>
      </label>
      <button type="button" class="btn-logout" title="Cerrar sesión" @click="logout">
        <LogOut aria-hidden="true" />
        <span>Salir</span>
      </button>
    </div>
  </header>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 0.9rem 1.5rem;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  flex-wrap: wrap;
}

.header__title {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--color-text);
}

.header__subtitle {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  color: var(--color-muted);
  margin-top: 0.15rem;
}

.header__pin {
  width: 0.9rem;
  height: 0.9rem;
}

.header__right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.3rem 0.65rem;
  border-radius: 999px;
}

.status-pill__icon {
  width: 0.85rem;
  height: 0.85rem;
}

.status-pill--on {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.status-pill--off {
  background: var(--color-danger-bg);
  color: var(--color-danger);
}

.user-chip {
  font-size: 0.8rem;
  font-weight: 500;
  padding: 0.3rem 0.65rem;
  background: var(--color-primary-muted);
  color: var(--color-primary);
  border-radius: var(--radius-sm);
}

.station-select {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.station-select__label {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-muted);
  font-weight: 600;
}

.station-select select {
  padding: 0.4rem 0.65rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  font-family: inherit;
  color: var(--color-text);
  background: var(--color-surface);
  min-width: 130px;
}

.btn-logout {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text-secondary);
  font-size: 0.8rem;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.12s, border-color 0.12s;
}

.btn-logout svg {
  width: 1rem;
  height: 1rem;
}

.btn-logout:hover {
  background: var(--color-primary-muted);
  border-color: var(--color-border-strong);
  color: var(--color-primary);
}
</style>
