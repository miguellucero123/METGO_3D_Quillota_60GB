import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/services/authApi'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: () => import('@/views/LandingCopiapoView.vue'),
    meta: { title: 'Inicio', public: true },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: 'Login', public: true },
  },
  {
    path: '/registro',
    name: 'registro',
    component: () => import('@/views/RegistroView.vue'),
    meta: { title: 'Registro', public: true },
  },
  {
    path: '/verificar',
    name: 'verificar',
    component: () => import('@/views/VerificarEmailView.vue'),
    meta: { title: 'Verificar email', public: true },
  },
  {
    path: '/app',
    name: 'panel',
    component: () => import('@/views/AirePanelView.vue'),
    meta: { title: 'Panel aire' },
  },
  {
    path: '/panel',
    redirect: { name: 'panel' },
  },
  {
    path: '/mapa',
    name: 'mapa',
    component: () => import('@/views/MapaView.vue'),
    meta: { title: 'Mapa' },
  },
  {
    path: '/dispersion',
    name: 'dispersion',
    component: () => import('@/views/DispersionView.vue'),
    meta: { title: 'Dispersión' },
  },
  {
    path: '/airshed',
    name: 'airshed',
    component: () => import('@/views/AirshedModelView.vue'),
    meta: { title: 'Airshed Modeler' },
  },
  {
    path: '/operaciones',
    name: 'operaciones',
    component: () => import('@/views/OperacionesPaipoteView.vue'),
    meta: { title: 'Operaciones Paipote' },
  },
  {
    path: '/sounding',
    name: 'sounding',
    component: () => import('@/views/SoundingView.vue'),
    meta: { title: 'Sounding' },
  },
  {
    path: '/satelite',
    name: 'satelite',
    component: () => import('@/views/SateliteAtmosView.vue'),
    meta: { title: 'Satélite' },
  },
  {
    path: '/olas-calor',
    name: 'olas-calor',
    component: () => import('@/views/OlasCalorView.vue'),
    meta: { title: 'Olas de calor' },
  },
  {
    path: '/conjunto',
    name: 'conjunto',
    component: () => import('@/views/VariablesConjuntoView.vue'),
    meta: { title: 'Variables conjunto' },
  },
  {
    path: '/pronostico',
    name: 'pronostico',
    component: () => import('@/views/AirePronosticoView.vue'),
    meta: { title: 'Pronóstico' },
  },
  {
    path: '/historico',
    name: 'historico',
    component: () => import('@/views/AireHistoricoView.vue'),
    meta: { title: 'Histórico' },
  },
  {
    path: '/cuenta',
    name: 'cuenta',
    component: () => import('@/views/CuentaView.vue'),
    meta: { title: 'Cuenta' },
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, saved) {
    if (saved) return saved
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth', top: 72 }
    }
    if (to.path !== from.path) return { top: 0 }
    return false
  },
})

router.beforeEach(async (to) => {
  const token = getToken()
  if (to.name === 'login' && token) {
    const { useAuth } = await import('@/stores/auth')
    const auth = useAuth()
    const ok = await auth.ensureValidSession()
    if (ok) return { name: 'panel' }
    return true
  }
  if (to.meta?.public) return true
  if (!token) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  return true
})

router.afterEach((to) => {
  const base = 'METGO Copiapó'
  document.title = to.meta?.title ? `${to.meta.title} · ${base}` : base
})

export default router
