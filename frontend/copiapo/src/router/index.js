import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/services/authApi'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: 'Login', public: true },
  },
  {
    path: '/',
    name: 'panel',
    component: () => import('@/views/AirePanelView.vue'),
    meta: { title: 'Panel aire' },
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
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (to.meta?.public) return true
  if (!getToken()) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  return true
})

router.afterEach((to) => {
  const base = 'METGO Copiapó'
  document.title = to.meta?.title ? `${to.meta.title} · ${base}` : base
})

export default router
