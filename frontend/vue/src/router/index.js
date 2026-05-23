import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true, title: 'Ingresar' },
  },
  {
    path: '/',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { title: 'Dashboard' },
  },
  {
    path: '/meteo',
    name: 'meteo',
    component: () => import('@/views/MeteoView.vue'),
    meta: { title: 'Meteorologia' },
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
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
})

router.afterEach((to) => {
  document.title = `${to.meta.title ?? 'METGO'} — Quillota`
})

export default router
