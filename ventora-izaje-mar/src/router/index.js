import { createRouter, createWebHistory } from 'vue-router'
import { fetchAccess, fetchMe, getToken, clearSession } from '@/services/authApi'
import { getHubCache, setHubCache, invalidateHubCache } from '@/stores/hubCache'

export { invalidateHubCache }

const puertoChildren = [
  {
    path: 'login',
    name: 'puerto-login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: 'Login', public: true },
  },
  {
    path: 'registro',
    name: 'puerto-registro',
    component: () => import('@/views/RegistroView.vue'),
    meta: { title: 'Registro', public: true },
  },
  {
    path: '',
    name: 'puerto-dashboard',
    component: () => import('@/components/PortalDashboard.vue'),
    meta: { title: 'Condiciones Izaje Mar' },
  },
  {
    path: 'cuenta',
    name: 'puerto-cuenta',
    component: () => import('@/views/CuentaView.vue'),
    meta: { title: 'Cuenta' },
  },
  {
    path: 'verificar',
    name: 'puerto-verificar',
    component: () => import('@/views/VerificarEmailView.vue'),
    meta: { title: 'Verificar email', public: true },
  },
]

const routes = [
  {
    path: '/',
    name: 'landing',
    component: () => import('@/views/LandingSpatiView.vue'),
    meta: { title: 'VENTORA IZAJE MAR', public: true },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: 'Ingresar', public: true },
  },
  {
    path: '/registro',
    name: 'registro',
    component: () => import('@/views/RegistroView.vue'),
    meta: { title: 'Registro', public: true },
  },
  {
    path: '/app',
    name: 'puertos-hub',
    component: () => import('@/views/PuertosHubView.vue'),
    meta: { title: 'Mis puertos', public: true },
  },
  {
    path: '/ops',
    name: 'ops-board',
    component: () => import('@/views/OpsBoardView.vue'),
    meta: { title: 'Ops multi-puerto', requiresAuth: true },
  },
  {
    path: '/p/:puerto',
    component: () => import('@/views/PuertoShellView.vue'),
    children: puertoChildren,
  },
  { path: '/dron', redirect: '/login' },
  { path: '/umbrales', redirect: '/login' },
  { path: '/ambiente', redirect: '/login' },
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

function loginRedirect(to) {
  const q = to.fullPath && to.fullPath !== '/' ? `?redirect=${encodeURIComponent(to.fullPath)}` : ''
  return `/login${q}`
}

router.beforeEach(async (to) => {
  if (to.meta?.public) return true
  if (!getToken()) {
    return loginRedirect(to)
  }

  const targetPuerto = to.params.puerto ? String(to.params.puerto).toLowerCase() : ''
  if (targetPuerto) {
    try {
      const hub = await loadHub()
      if (!hub.catalogo_completo && hub.slugs.size > 0 && !hub.slugs.has(targetPuerto)) {
        const first = [...hub.slugs][0]
        return `/app?blocked_puerto=${encodeURIComponent(targetPuerto)}`
      }
    } catch (e) {
      if (e?.status === 401) {
        clearSession()
        invalidateHubCache()
        return loginRedirect(to)
      }
      /* API fría: no bloquear */
    }
  }

  const tab = to.meta?.tab
  if (tab && targetPuerto) {
    try {
      // "ahora" comparte entitlement con panel (vista simplificada del mismo sistema)
      const entitlementTab = tab === 'ahora' ? 'panel' : String(tab)
      const access = await fetchAccess({
        sitio: 'spati',
        faena: targetPuerto,
        tab: entitlementTab,
      })
      const denied =
        access.tab_allowed === false ||
        (access.tabs && access.tabs[entitlementTab] === false)
      if (denied) {
        return `/p/${targetPuerto}/?blocked=${encodeURIComponent(String(tab))}`
      }
    } catch (e) {
      if (e?.status === 401) {
        clearSession()
        invalidateHubCache()
        return loginRedirect(to)
      }
      /* allow */
    }
  }
  return true
})

router.afterEach((to) => {
  const base = 'VENTORA IZAJE MAR'
  document.title = to.meta?.title ? `${to.meta.title} · ${base}` : base
})

export default router
