import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'panel',
    component: () => import('@/views/AirePanelView.vue'),
    meta: { title: 'Panel aire' },
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

router.afterEach((to) => {
  const base = 'METGO Copiapó'
  document.title = to.meta?.title ? `${to.meta.title} · ${base}` : base
})

export default router
