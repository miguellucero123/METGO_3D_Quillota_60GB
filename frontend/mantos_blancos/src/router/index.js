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
    component: () => import('@/views/OperacionesPanelView.vue'),
    meta: { title: 'Panel turno' },
  },
  {
    path: '/ventanas',
    name: 'ventanas',
    component: () => import('@/views/VentanasView.vue'),
    meta: { title: 'Ventanas' },
  },
  {
    path: '/umbrales',
    name: 'umbrales',
    component: () => import('@/views/UmbralesView.vue'),
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
  const base = 'METGO Mantos Blancos'
  document.title = to.meta?.title ? `${to.meta.title} · ${base}` : base
})

export default router
