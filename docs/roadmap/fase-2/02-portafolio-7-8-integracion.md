# Portafolio 7 + 8 → METGO 3D (integración developer)

Documento de trazabilidad: requisitos tipo **ClimaTorre** (rúbricas Portafolio 7 y 8) aplicados al producto **METGO 3D** sin duplicar stack innecesario.

**Principio:** METGO **ya supera** el MVP académico (API Flask/JWT, RBAC, ETL, ML, Streamlit local). Aquí se mapea qué exige la rúbrica y **dónde vive en código**, más los huecos cerrados en Fase 2.

---

## Equivalencias de stack

| Rúbrica (ClimaTorre) | METGO 3D (producto) |
|----------------------|---------------------|
| Vue Router | `frontend/vue/src/router/index.js` |
| Vuex usuario | **Pinia** `stores/auth.js` + `stores/preferences.js` + `stores/favorites.js` |
| Vuex clima | **Pinia** `stores/metgo.js` (estaciones, pronóstico, flags API) |
| Auth mock | **JWT real** `POST /api/auth/login`, `fetchMe`, guards |
| Lugares / favoritos | **Estaciones** del valle (`quillota`, `los_nogales`, …) |
| Preferencias °C/°F, tema | `stores/preferences.js` + `/preferencias` |
| API clima fetch | `api/metgoApi.js` → Render `metgo-api.onrender.com` |
| Estadísticas + alertas | `DashboardView`, `MeteoView`, `fetchAlertas`, `agroInsights.js` |
| Netlify deploy | Raíz `netlify.toml` + `frontend/vue/dist` |
| Rutas protegidas | `router.beforeEach` + `meta.public` / `meta.roles` |

---

## Portafolio 7 — ya cubierto o equivalente

| Requisito M7 | Estado METGO | Evidencia |
|--------------|--------------|-----------|
| Vue Router (home, detalle, auth) | Hecho | `/`, `/meteo`, `/login`, … |
| Estado de sesión | Hecho | `stores/auth.js`, localStorage JWT |
| Login / logout / errores | Hecho | `LoginView.vue`, API Flask |
| Rutas protegidas | Hecho | Guard global; `/favoritos`, `/preferencias` requieren sesión |
| UI según sesión | Hecho | `MetgoHeader.vue` (usuario, rol, tenant) |
| Favoritos | **Añadido Fase 2.6** | `stores/favorites.js`, `/favoritos` |
| Preferencias (unidad, tema) | **Añadido Fase 2.6** | `stores/preferences.js`, `/preferencias` |
| Redirect post-login seguro | **Añadido Fase 2.6** | `utils/sanitizeRedirectPath.js` |

---

## Portafolio 8 — cierre integrado

| Requisito M8 | METGO |
|--------------|-------|
| API + loading/error | `useApiCall`, `metgoStore.error`, banner en panel |
| Lista lugares + selección + pronóstico | `metgoStore.estaciones`, `estacionActiva`, `fetchPronostico` |
| Estadísticas en detalle | `MeteoView` (histórico 14d, pronóstico 7d, acumulados) |
| Alertas meteorológicas | `fetchAlertas`, `MonitoreoView`, badges helada |
| Mensaje error API en Home | Banner `role="alert"` en `DashboardView` |
| Despliegue público | Netlify SPA + Render API |

---

## Checklist demo (evaluador / video)

1. **Sin login:** no aplica — METGO exige JWT (producto profesional). Usar cuenta demo (`admin`/`admin123`).
2. **Con login:** Panel → Meteo (detalle estación) → alertas → **Favoritos** → **Preferencias** (°C/°F, tema) → logout.
3. **Multi-estación:** `/meteo/comparativo` (ex puerto 8506), comparativo API 5 estaciones.
4. **Repo:** `npm install && npm run dev` en `frontend/vue`; API según `docs/DESARROLLO_LOCAL.md`.
5. **Producción:** https://metgo3d.netlify.app · API https://metgo-api.onrender.com/api

---

## Qué no se copia de ClimaTorre

- Vuex → Pinia (estándar Vue 3 en METGO).
- Auth simulada → JWT + RBAC (`admin`, `agronomo`, `operador`, `lector`).
- “Lugares” genéricos → estaciones agrometeorológicas del Valle de Aconcagua.
- Puertos Streamlit 8501–8513 en Netlify (solo local; ver `docs/manuales/QUE_VER_EN_NUBE.md`).

---

## Fase

**2.6** — Integración rúbrica P7/P8 · **DT-x** trazabilidad evaluador
