import { createRouter, createWebHistory } from 'vue-router'
import { fetchAccess, getToken } from '@/services/authApi'

const faenaChildren = [
  {
    path: 'login',
    name: 'faena-login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: 'Login', public: true },
  },
  {
    path: 'registro',
    name: 'faena-registro',
    component: () => import('@/views/RegistroView.vue'),
    meta: { title: 'Registro', public: true },
  },
  {
    path: '',
    name: 'faena-panel',
    component: () => import('@/views/SpatiPanelView.vue'),
    meta: { title: 'Pronóstico izaje', tab: 'panel' },
  },
  {
    path: 'dron',
    name: 'faena-dron',
    component: () => import('@/views/DronCalibracionView.vue'),
    meta: { title: 'Calibración dron', tab: 'dron' },
  },
  {
    path: 'umbrales',
    name: 'faena-umbrales',
    component: () => import('@/views/UmbralesSpatiView.vue'),
    meta: { title: 'Umbrales', tab: 'umbrales' },
  },
  {
    path: 'ambiente',
    name: 'faena-ambiente',
    component: () => import('@/views/AmbientalesView.vue'),
    meta: { title: 'Ambiente faena', tab: 'ambiente' },
  },
  {
    path: 'cuenta',
    name: 'faena-cuenta',
    component: () => import('@/views/CuentaView.vue'),
    meta: { title: 'Cuenta' },
  },
  {
    path: 'verificar',
    name: 'faena-verificar',
    component: () => import('@/views/VerificarEmailView.vue'),
    meta: { title: 'Verificar email', public: true },
  },
]

const routes = [
  {
    path: '/',
    name: 'faenas-hub',
    component: () => import('@/views/FaenasHubView.vue'),
    meta: { title: 'Faenas', public: true },
  },
  {
    path: '/f/:faena',
    component: () => import('@/views/FaenaShellView.vue'),
    children: faenaChildren,
  },
  // Compat rutas antiguas → Escondida por defecto
  { path: '/login', redirect: '/f/escondida/login' },
  { path: '/dron', redirect: '/f/escondida/dron' },
  { path: '/umbrales', redirect: '/f/escondida/umbrales' },
  { path: '/ambiente', redirect: '/f/escondida/ambiente' },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  if (to.meta?.public) return true
  if (!getToken()) {
    const faena = to.params.faena || 'escondida'
    return {
      name: 'faena-login',
      params: { faena },
      query: { redirect: to.fullPath },
    }
  }
  const tab = to.meta?.tab
  if (tab && to.params.faena) {
    try {
      const access = await fetchAccess({
        sitio: 'spati',
        faena: String(to.params.faena),
        tab: String(tab),
      })
      const denied =
        access.tab_allowed === false ||
        (access.tabs && access.tabs[tab] === false)
      if (denied) {
        return {
          name: 'faena-cuenta',
          params: { faena: to.params.faena },
          query: { blocked: String(tab) },
        }
      }
    } catch {
      // API fría / admin legacy sin org: no bloquear navegación
    }
  }
  return true
})

router.afterEach((to) => {
  const base = 'METGO SPATI'
  document.title = to.meta?.title ? `${to.meta.title} · ${base}` : base
})

export default router
