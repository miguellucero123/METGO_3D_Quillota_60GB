# Despliegue Vue en Cloudflare Pages (migración desde Netlify)

> Contexto: Netlify free se quedó corto de créditos/banda. La API Flask **sigue en Render**; solo cambia el hosting de las SPAs.

## Arquitectura

```text
Usuario → Cloudflare Pages (SPA) → /api/* (proxy 200) → https://metgo-api.onrender.com/api
```

| Sitio | Carpeta | Proyecto CF sugerido | `wrangler.toml` |
|-------|---------|----------------------|-----------------|
| Quillota | `frontend/vue` | `metgo-quillota` | sí |
| Copiapó | `frontend/copiapo` | `metgo-copiapo` | sí |
| Mantos Blancos | `frontend/mantos_blancos` | `metgo-mantos` | sí |
| SPATI Izaje | `frontend/spati` | `metgo-spati` | sí |
| Paine | repo `metgo-paine` (`D:\metgo-paine`) | `metgo-paine` | sí (`wrangler.toml` en ese repo) |

`netlify.toml` se mantiene por compatibilidad; no hace falta borrarlo.

### Paine (repo aparte)

1. Cloudflare Pages → Connect to Git → repo `metgo-paine` (root = `/`).
2. Build: `npm ci && npm run build` · output `dist` · Node 20.
3. Env: `VITE_METGO_API`, opcional `VITE_SUPABASE_*` (Realtime tramos). Mapa `/carretera` = Leaflet + OpenStreetMap (**sin** API key de Google).
4. CLI: `npm run pages:deploy` desde `D:\metgo-paine`.
5. Cutover: stop builds en Netlify tras validar `https://metgo-paine.pages.dev`.
6. Login JWT E9: cuenta con `METGO_PASSWORD_PAINE` (u otra) en Render. Demos solo local: `docs/DESARROLLO_LOCAL.md`.

---

## 1. Crear proyecto en Cloudflare (dashboard)

1. [Cloudflare Dashboard](https://dash.cloudflare.com) → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
2. Repo: `METGO_3D_Quillota_60GB` (o el remoto actual).
3. Por sitio:

| Campo | Quillota | Copiapó | Mantos |
|-------|----------|---------|--------|
| Project name | `metgo-quillota` | `metgo-copiapo` | `metgo-mantos` |
| Production branch | `master` (o `main`) | igual | igual |
| Root directory | `frontend/vue` | `frontend/copiapo` | `frontend/mantos_blancos` |
| Build command | `npm ci && npm run build` | igual | igual |
| Build output | `dist` | `dist` | `dist` |
| Node version | `20` | `20` | `20` |

4. **Variables de entorno** (opcionales):
   - Quillota en `*.pages.dev` ya usa Render directo desde el cliente (`metgoApi.js`, igual que Netlify) para evitar 504 por cold start.
   - `_redirects` con proxy `/api` queda como respaldo y para previews locales.
   - Opcional: `VITE_METGO_API` / `VITE_API_BASE` si quieres forzar otra base.

5. Deploy → URL tipo `https://metgo-quillota.pages.dev`.

### Ahorro de builds (monorepo)

En **Build configuration → Build watch paths** (o “Skip build if…”):

- Quillota: `frontend/vue/**`
- Copiapó: `frontend/copiapo/**`
- Mantos: `frontend/mantos_blancos/**`

Así un push que solo toca Copiapó no reconstruye Quillota.

---

## 2. Proxy `/api` y SPA

Cada SPA tiene `public/_redirects` (se copia a `dist/` en el build):

```text
/api/*  https://metgo-api.onrender.com/api/:splat  200
/*      /index.html  200
```

Cloudflare Pages interpreta `_redirects` al estilo Netlify (status `200` = proxy/rewrite).

---

## 3. CORS en Render (obligatorio)

Tras el primer deploy, anota las URLs `*.pages.dev` (y dominio custom si lo hay) y añádelas a `METGO_CORS_ORIGINS` en Render:

```text
https://metgo3d.netlify.app,https://metgo-quillota.pages.dev,https://metgo-copiapo.pages.dev,https://metgo-mantos.pages.dev,https://metgo-paine.pages.dev,https://metgo-3d-quillota-60gb.streamlit.app,...
```

La API también acepta **previews** automáticamente (`https://{hash}.metgo-copiapo.pages.dev`) vía regex en `expand_cors_origins` — no hace falta listar cada deploy preview. Tras cambiar CORS en código: **redeploy Render**.

También actualiza `METGO_VUE_URL` (Streamlit) al dominio Cloudflare de Quillota cuando sea el canónico.

Plantilla en repo: `render.yaml` → clave `METGO_CORS_ORIGINS` (ajusta tras el deploy real).

---

## 4. Deploy manual con Wrangler (sin gastar build en CF)

```powershell
cd frontend\vue
npm ci
npm run build
npx wrangler pages deploy dist --project-name=metgo-quillota
```

Repite con `frontend\copiapo` → `metgo-copiapo`, `frontend\mantos_blancos` → `metgo-mantos`, y Paine:

```powershell
cd D:\metgo-paine
npm ci
npm run pages:deploy
```

Requiere `npx wrangler login` una vez.

---

## 5. Cutover desde Netlify

1. Desplegar en CF y validar login + dashboard + `/api/health` vía proxy.
2. Actualizar CORS + `METGO_VUE_URL`.
3. En Netlify: **Stop builds** (ya recomendado por créditos).
4. (Opcional) Dominio custom: DNS en Cloudflare → Pages custom domain; luego redirigir o apagar Netlify.
5. Actualizar docs/manuales que cite `metgo3d.netlify.app` cuando el dominio CF sea estable.

---

## 6. Smoke checklist

```powershell
# Sustituir por tu URL pages.dev
$UI = "https://metgo-quillota.pages.dev"
Invoke-WebRequest "$UI/" | Select-Object StatusCode
Invoke-WebRequest "$UI/api/health" | Select-Object StatusCode
# Navegador: login con cuenta de Render (METGO_PASSWORD_*) · Dashboard · Proyecciones ML
```

Copiapó / Mantos / Paine / SPATI: mismas cuentas vía env en Render. Demos locales: `docs/DESARROLLO_LOCAL.md`.

Minería M7 (API):

```powershell
python scripts/smoke_mineria_m7.py --base https://metgo-api.onrender.com --faena paipote
# SPA: /ambiente → Descargar CSV · PDF · MVO (metgo-spati / metgo-mantos)
```

---

## Fase

Ops / plataforma (migración hosting) · minería multi-faena M1–M7 en API + SPA `/ambiente`.
