# METGO site template

Plantilla multi-sitio (etapa **E6**). Base viva: repo **`metgo-paine`**. Identidad, módulos y seed viven en **un solo archivo**: `src/site.config.js`.

## Checklist — nuevo sitio en 1 día

1. **Crear repo** desde GitHub template de `metgo-paine` (o clonar y renombrar remoto).
2. **Editar** `src/site.config.js` (ver `site.config.example.js` en esta carpeta):
   - `sitio` (slug API, minúsculas, sin espacios)
   - `siteLabel`, `tagline`, `theme.primary`, `modules`, `stations[]`
3. **Backend Quillota** (`METGO_3D_Quillota_60GB`):
   - Añadir slug a `SITIOS` / `SITIOS_META` / `ESTACIONES_POR_SITIO` en `estaciones_catalogo.py`
   - Registrar nombres/coords en `datos_reales_openmeteo.py`
   - Migración SQL: fila en `sitios` + filas en `estaciones` (ver `supabase/migrations/20260723140000_sitios_multisitio.sql`)
   - Ampliar enum `sitio` en `openapi.yaml`
4. **CORS / env**:
   - Netlify: `VITE_METGO_API=https://metgo-api.onrender.com/api`
   - Render: añadir origen Netlify a `METGO_CORS_ORIGINS` si no es `*`
5. **Deploy** Netlify (build `npm run build`, publish `dist`).
6. **Auth E9:** login `POST /api/auth/login` con `{ username, password, sitio: '<slug>' }` + guard de rutas
   (referencia: `frontend/copiapo/src/services/authApi.js`). Credenciales: `METGO_PASSWORD_*` en el API (local: `docs/DESARROLLO_LOCAL.md`).
7. **Verificar**:
   - `GET /api/public/sitios` incluye el slug
   - `GET /api/public/estaciones?sitio=<slug>`
   - SPA muestra colores del `theme` y datos (o fallback Open-Meteo)
   - Login SPA → `/api/auth/me` con `sitio` correcto

Sitio de prueba ya registrado en API: **`demo`**. Copiapó (E7): SPA en `frontend/copiapo/` del monorepo Quillota.

## Archivos de esta carpeta

| Archivo | Uso |
|---------|-----|
| `site.config.example.js` | Config del sitio `demo` (ficticio) |
| `applySiteTheme.js` | Copia de referencia (en Paine: `src/utils/applySiteTheme.js`) |
| `README.md` | Este checklist |

## Contrato mínimo `site.config.js`

```js
export default {
  sitio: 'demo',           // ?sitio= en metgo-api
  productName: 'METGO',
  siteLabel: 'Demo',
  tagline: '…',
  theme: { primary: '#a78bfa', primaryHover: '…', accent: '…' },
  modules: { meteo: true, precipitacion: true, lugares: true, aire: false, operaciones: false },
  storagePrefix: 'metgo_demo',
  stations: [{ id: 1, slug: 'demo_norte', nombre: '…', lat, lon }],
}
```

## Fase

**E6** — `docs/roadmap/PLAN_MAESTRO_METGO_MULTISITIO.md`
