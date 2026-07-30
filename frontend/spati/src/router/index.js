import { createRouter, createWebHistory } from 'vue-router'
import { fetchAccess, fetchMe, getToken } from '@/services/authApi'
import { getHubCache, setHubCache, invalidateHubCache } from '@/stores/hubCache'

export { invalidateHubCache }

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
    path: '/ops',
    name: 'ops-board',
    component: () => import('@/views/OpsBoardView.vue'),
    meta: { title: 'Ops multi-faena', requiresAuth: true },
  },
  {
    path: '/f/:faena',
    component: () => import('@/views/FaenaShellView.vue'),
    children: faenaChildren,
  },
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

const HUB_TTL = 60_000

async function loadHub() {
  const cached = getHubCache()
  if (cached && Date.now() - cached.at < HUB_TTL) return cached
  const me = await fetchMe()
  const hub = me.hub || {}
  const slugs = new Set((hub.faenas || me.faenas || []).map((f) => f.slug || f))
  if (me.faena) slugs.add(String(me.faena).toLowerCase())
  const next = {
    at: Date.now(),
    catalogo_completo: Boolean(
      hub.catalogo_completo ||
        me.catalogo_completo ||
        ['admin', 'administrador', 'superadmin'].includes(String(me.role || '').toLowerCase()),
    ),
    slugs,
  }
  setHubCache(next)
  return next
}

router.beforeEach(async (to) => {
  if (to.meta?.public) return true
  if (!getToken()) {
    const faena = to.params.faena || 'escondida'
    return `/f/${faena}/login?redirect=${encodeURIComponent(to.fullPath)}`
  }

  const targetFaena = to.params.faena ? String(to.params.faena).toLowerCase() : ''
  if (targetFaena) {
    try {
      const hub = await loadHub()
      if (!hub.catalogo_completo && hub.slugs.size > 0 && !hub.slugs.has(targetFaena)) {
        const first = [...hub.slugs][0]
        return `/f/${first}/cuenta?blocked_faena=${encodeURIComponent(targetFaena)}`
      }
    } catch {
      /* API fría: no bloquear */
    }
  }

  const tab = to.meta?.tab
  if (tab && targetFaena) {
    try {
      const access = await fetchAccess({
        sitio: 'spati',
        faena: targetFaena,
        tab: String(tab),
      })
      const denied =
        access.tab_allowed === false ||
        (access.tabs && access.tabs[tab] === false)
      if (denied) {
        return `/f/${targetFaena}/cuenta?blocked=${encodeURIComponent(String(tab))}`
      }
    } catch {
      /* allow */
    }
  }
  return true
})

router.afterEach((to) => {
  const base = 'METGO SPATI'
  document.title = to.meta?.title ? `${to.meta.title} · ${base}` : base
})

export default router
