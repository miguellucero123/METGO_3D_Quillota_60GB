# Cumplimiento rúbrica Módulo 7 — METGO 3D

Auditoría **completa** frente al enunciado Portafolio 7, con evidencia en código METGO (producto profesional AgriTech).

> **Nota evaluador:** Vue 3 usa **Pinia** en lugar de Vuex; equivalencia documentada en `frontend/vue/src/stores/index.js`.

---

## §1 Propósito

| Criterio | Estado | Evidencia METGO |
|----------|--------|-----------------|
| Vue + Router + estado global | ✅ | `frontend/vue/src/router/index.js`, `stores/index.js` |
| Axios o mock | ✅ | `api/metgoApi.js` (Axios → API Render) |
| Auth + preferencias global | ✅ | `stores/auth.js`, `preferences.js`, `favorites.js` |
| UI según sesión | ✅ | `MetgoHeader.vue`, favoritos en Meteo/Comparativo |

---

## §2 Objetivos

| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| Login y registro | ✅ | `LoginView.vue`, `RegistroView.vue` |
| Store auth + prefs + favoritos | ✅ | Pinia (ver `stores/index.js`) |
| Rutas protegidas | ✅ | Guard `router.beforeEach`, `meta.public` |
| UI autenticada | ✅ | Header, sidebar Favoritos/Preferencias |
| Git descriptivo | ⚠️ | Responsabilidad del equipo (commits por feature) |

---

## §3 Alcance

| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| `/login` | ✅ | `router/index.js` |
| `/registro` | ✅ | `RegistroView.vue` |
| Login → store → redirect | ✅ | `auth.login`, `sanitizeRedirectPath`, `?redirect=` |
| Error login explícito | ✅ | `Usuario o contraseña incorrectos` — `authService.js`, API |
| Favoritos + preferencias clima | ✅ | `/favoritos`, `/preferencias`, alias `/preferencias-clima` |
| API simulada o real | ✅ | JWT Flask + registro en `POST /api/auth/register` |

---

## §4 Funcionales mínimos

| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| Login usuario + contraseña | ✅ | `LoginView.vue` |
| Éxito → sesión + redirect | ✅ | `auth.setSession`, `router.push` |
| Error claro | ✅ | `AUTH_ERROR_INVALID` |
| Nombre + logout | ✅ | `MetgoHeader.vue` |
| Logout limpia sesión | ✅ | `auth.logout()`, redirect login |
| Prefs desde store | ✅ | `preferences.js`, `MetricCard` + `useFormatTemp` |
| Ruta privada sin sesión | ✅ | Redirect `/login?redirect=` |

---

## §5 Técnicos

| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| State + `isAuthenticated` | ✅ | `auth.js` computed |
| Mutations equivalentes | ✅ | `setSession`, `clearSession`, `setTempUnit`, `toggle` |
| Actions async login/registro/logout | ✅ | `auth.js`, `authService.js` |
| Componentes leen store | ✅ | Composition API `useAuthStore()`, etc. |
| Formularios v-model + submit | ✅ | Login, Registro |
| Credenciales API | ✅ | `metgo_auth.py`, registro JSON runtime |
| Router login/registro/guard | ✅ | `router/index.js` |
| Redirect seguro | ✅ | `utils/sanitizeRedirectPath.js` |

---

## Demo evaluador (5 min)

1. `/registro` → usuario `campo_norte` / contraseña → entra con rol **lectura**
2. `/meteo` → ★ favorita → `/favoritos`
3. `/preferencias` (o `/preferencias-clima`) → °F + tema oscuro
4. `/` panel → temperaturas en °F, alertas API si hay error
5. Logout → login

**Producción:** https://metgo3d.netlify.app · API https://metgo-api.onrender.com/api

---

## Fase

**2.6** · Módulo 7 cerrado · **2.x** Vue · **DT-x** trazabilidad
