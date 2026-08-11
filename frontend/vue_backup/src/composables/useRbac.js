import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const ROLE_ORDER = ['lectura', 'operador', 'agronomo', 'admin']

export function useRbac() {
  const auth = useAuthStore()
  const role = computed(() => auth.user?.role || 'lectura')

  function hasRole(...allowed) {
    if (role.value === 'admin') return true
    return allowed.includes(role.value)
  }

  function canManageAlertas() {
    return hasRole('admin', 'agronomo', 'operador')
  }

  function canDeleteAlertas() {
    return hasRole('admin', 'agronomo')
  }

  function canControlStreamlit() {
    return hasRole('admin', 'operador')
  }

  return { role, hasRole, canManageAlertas, canDeleteAlertas, canControlStreamlit }
}
