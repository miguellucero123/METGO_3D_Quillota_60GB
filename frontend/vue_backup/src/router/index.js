import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: () => import('@/views/LandingQuillotaView.vue'),
    meta: { public: true, title: 'METGO Quillota' },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true, title: 'Ingresar' },
  },
  {
    path: '/registro',
    name: 'registro',
    component: () => import('@/views/RegistroView.vue'),
    meta: { public: true, title: 'Registro' },
  },
  {
    path: '/verificar',
    name: 'verificar',
    component: () => import('@/views/VerificarEmailView.vue'),
    meta: { public: true, title: 'Verificar email' },
  },
  {
    path: '/estado',
    name: 'estado',
    component: () => import('@/views/EstadoView.vue'),
    meta: { public: true, title: 'Estado del sistema' },
  },
  {
    path: '/contacto',
    name: 'contacto',
    component: () => import('@/views/ContactoView.vue'),
    meta: { public: true, title: 'Contacto comercial' },
  },
  {
    path: '/planes',
    name: 'planes',
    component: () => import('@/views/PlanesView.vue'),
    meta: { public: true, title: 'Planes y precios' },
  },
  {
    path: '/izaje',
    name: 'izaje',
    component: () => import('@/views/IzajeView.vue'),
    meta: { public: true, title: 'Pronósticos para Izaje' },
  },
  {
    path: '/mineria',
    name: 'mineria',
    component: () => import('@/views/MineriaView.vue'),
    meta: { public: true, title: 'Minería y alta montaña' },
  },
  {
    path: '/calidad-del-aire',
    name: 'calidad-aire',
    component: () => import('@/views/CalidadAireView.vue'),
    meta: { public: true, title: 'Calidad del aire' },
  },
  {
    path: '/nosotros',
    name: 'nosotros',
    component: () => import('@/views/NosotrosView.vue'),
    meta: { public: true, title: 'Nosotros' },
  },
  {
    path: '/pronostico-extendido',
    name: 'pronostico-ext',
    component: () => import('@/views/PronosticoExtendidoView.vue'),
    meta: { public: true, title: 'Pronóstico extendido' },
  },
  {
    path: '/integracion',
    name: 'integracion',
    component: () => import('@/views/IntegracionView.vue'),
    meta: { title: 'Conexiones del sistema' },
  },
  {
    path: '/403',
    name: 'forbidden',
    component: () => import('@/views/ForbiddenView.vue'),
    meta: { title: 'Sin permiso' },
  },
  {
    path: '/app',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { title: 'Dashboard' },
  },
  {
    path: '/dashboard',
    redirect: { name: 'dashboard' },
  },
  {
    path: '/meteo',
    name: 'meteo',
    component: () => import('@/views/MeteoView.vue'),
    meta: { title: 'Meteorologia' },
  },
  {
    path: '/meteo/historico',
    name: 'meteo-historico',
    component: () => import('@/views/MeteoHistoricoView.vue'),
    meta: { title: 'Histórico meteo' },
  },
  {
    path: '/meteo/comparativo',
    name: 'meteo-comparativo',
    component: () => import('@/views/ComparativoEstacionesView.vue'),
    meta: { title: 'Visualizaciones · comparativo' },
  },
  {
    path: '/meteo/precipitacion',
    name: 'meteo-precipitacion',
    component: () => import('@/views/PrecipitacionView.vue'),
    meta: { title: 'Precipitación y heladas' },
  },
  {
    path: '/meteo/avanzado',
    name: 'meteo-avanzado',
    component: () => import('@/views/MeteoAvanzadoView.vue'),
    meta: { title: 'Meteorología avanzada' },
  },
  {
    path: '/favoritos',
    name: 'favoritos',
    component: () => import('@/views/FavoritosView.vue'),
    meta: { title: 'Estaciones favoritas', requiresAuth: true },
  },
  {
    path: '/preferencias',
    name: 'preferencias',
    component: () => import('@/views/PreferenciasView.vue'),
    meta: { title: 'Preferencias', requiresAuth: true },
  },
  {
    path: '/preferencias-clima',
    redirect: { name: 'preferencias' },
  },
  {
    path: '/metricas',
    name: 'metricas',
    component: () => import('@/views/MetricasGlobalesView.vue'),
    meta: { title: 'Métricas globales' },
  },
  {
    path: '/iot',
    name: 'iot',
    component: () => import('@/views/IotView.vue'),
    meta: { title: 'Sensores IoT' },
  },
  {
    path: '/ml',
    name: 'ml',
    component: () => import('@/views/MlView.vue'),
    meta: { title: 'Modelos ML' },
  },
  {
    path: '/agricola',
    name: 'agricola',
    component: () => import('@/views/AgricolaView.vue'),
    meta: { title: 'Agricultura' },
  },
  {
    path: '/monitoreo',
    name: 'monitoreo',
    component: () => import('@/views/MonitoreoView.vue'),
    meta: { title: 'Monitoreo' },
  },
  {
    path: '/alertas/config',
    name: 'alertas-config',
    component: () => import('@/views/AlertasConfigView.vue'),
    meta: { title: 'Config alertas', roles: ['admin', 'agronomo', 'operador'] },
  },
  {
    path: '/modulos',
    name: 'modulos',
    component: () => import('@/views/ModulosView.vue'),
    meta: { title: 'Módulos' },
  },
  {
    path: '/configuracion',
    name: 'configuracion',
    component: () => import('@/views/ConfiguracionView.vue'),
    meta: { title: 'Configuración' },
  },
  {
    path: '/servicios',
    name: 'servicios',
    component: () => import('@/views/ServiciosView.vue'),
    meta: { title: 'Centro de servicios' },
  },
  {
    path: '/puertos',
    name: 'puertos',
    component: () => import('@/views/PuertosView.vue'),
    meta: { title: 'Visor de puertos' },
  },
  {
    path: '/cuenta',
    name: 'cuenta',
    component: () => import('@/views/CuentaView.vue'),
    meta: { title: 'Cuenta / planes' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

function roleAllowed(userRole, required) {
  if (!required?.length) return true
  if (userRole === 'admin') return true
  return required.includes(userRole)
}

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!to.meta.public) {
    if (!auth.isAuthenticated) {
      return { name: 'login', query: { redirect: to.fullPath } }
    }
    const ok = await auth.ensureValidSession()
    if (!ok) {
      return { name: 'login', query: { redirect: to.fullPath } }
    }
    if (to.meta.roles && !roleAllowed(auth.user?.role, to.meta.roles)) {
      return { name: 'forbidden' }
    }
  }
  if (to.name === 'registro') {
    if (auth.isAuthenticated) {
      const ok = await auth.ensureValidSession()
      if (ok) return { name: 'dashboard' }
    }
  }
  if (to.name === 'login' && auth.isAuthenticated) {
    const ok = await auth.ensureValidSession()
    if (ok) return { name: 'dashboard' }
  }
})

router.afterEach((to) => {
  document.title = `${to.meta.title ?? 'METGO'} — Quillota`
})

// Catch chunk loading errors caused by new deployments and force a page reload
router.onError((error) => {
  if (error.message.includes('Failed to fetch dynamically imported module') || error.name === 'ChunkLoadError') {
    console.warn('Chunk load error detected, reloading page to fetch new chunks...')
    window.location.reload()
  }
})

export default router
