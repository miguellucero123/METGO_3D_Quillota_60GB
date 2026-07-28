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
    component: () => import('@/views/SpatiPanelView.vue'),
    meta: { title: 'Pronóstico izaje' },
  },
  {
    path: '/dron',
    name: 'dron',
    component: () => import('@/views/DronCalibracionView.vue'),
    meta: { title: 'Calibración dron' },
  },
  {
    path: '/umbrales',
    name: 'umbrales',
    component: () => import('@/views/UmbralesSpatiView.vue'),
    meta: { title: 'Umbrales' },
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
  const base = 'METGO SPATI'
  document.title = to.meta?.title ? `${to.meta.title} · ${base}` : base
})

export default router
