# Desplegar Vue METGO en Netlify

Guía para publicar `frontend/vue` y enlazarla con Streamlit Cloud vía iframe (`3 Panel Vue embebido`).

## Requisitos

- Cuenta en [netlify.com](https://www.netlify.com)
- Repositorio en GitHub: `miguellucero123/METGO_3D_Quillota_60GB`
- API REST accesible por HTTPS (Render, Railway, etc.) — ver sección 4

---

## 1. Crear sitio en Netlify

1. **Add new site** → **Import an existing project** → **GitHub**.
2. Autorizar Netlify y elegir el repo **METGO_3D_Quillota_60GB**.
3. Netlify detectará `netlify.toml` en la **raíz del repo** (no hace falta tocar Base directory manualmente).

| Campo | Valor (automático con `netlify.toml`) |
|-------|----------------------------------------|
| Base directory | `frontend/vue` |
| Build command | `npm ci && npm run build` |
| Publish directory | `dist` |
| Node | 20 |

4. Antes del primer deploy, en **Site configuration → Environment variables → Production** añada:

   | Key | Value (ejemplo) |
   |-----|-----------------|
   | `VITE_METGO_API` | `https://metgo-api.onrender.com/api` |

   Sin esta variable, el build usará `/api` (solo válido con proxy local).

5. **Deploy site**.

6. Copie la URL del sitio, p. ej. `https://metgo-quillota.netlify.app`  
   (en **Domain management** puede cambiar el subdominio `*.netlify.app`).

---

## 2. Probar la SPA en Netlify

Abra en el navegador:

- `https://SU-SITIO.netlify.app/login`
- `https://SU-SITIO.netlify.app/servicios`
- `https://SU-SITIO.netlify.app/modulos`

Si recarga una ruta y sale **404**, revise que exista `netlify.toml` o `public/_redirects` con regla SPA.

---

## 3. Conectar Streamlit Cloud (iframe)

1. [share.streamlit.io](https://share.streamlit.io) → su app → **Settings** → **Secrets**.
2. Pegue (sin barra final):

```toml
METGO_VUE_URL = "https://metgo-quillota.netlify.app"
```

3. **Save** → **Reboot app**.
4. En la app: menú lateral → **3 Panel Vue embebido**.

Debe cargar la misma UI que en Netlify, dentro de Streamlit.

---

## 4. Error `/api/auth/login` 404 en Netlify

Si en la consola del navegador aparece:

```text
/api/auth/login  Failed to load resource: 404
```

**Causa:** Vue llama a `https://metgo3d.netlify.app/api/...`, pero Netlify solo sirve archivos estáticos (Vue). **La API Flask no está en Netlify.**

`form detection precheck` → extensión del navegador (gestor de contraseñas); ignorar.

**Solución A (recomendada, sin rebuild):** el `netlify.toml` del repo incluye proxy:

`/api/*` → `https://metgo-api.onrender.com/api/*`

Haga push a GitHub y **Trigger deploy** en Netlify. Vue puede seguir con `VITE_METGO_API=/api`.

**Solución B:** variable en Netlify → Production (valor **público**, no marcar como *secret*):

```env
VITE_METGO_API=/api
```

El proxy `_redirects` envía `/api` a Render. **No** suba URLs al repo (Netlify secrets-scan bloquea el build).

Si el build falla por *secrets scanning*: elimine `VITE_METGO_API` de variables marcadas como secret, o añada `SECRETS_SCAN_OMIT_KEYS=VITE_METGO_API` solo si usa URL absoluta en el build.

**Credenciales por defecto** (si no definió `METGO_PASSWORD_*` en Render):

| Usuario | Contraseña |
|---------|------------|
| `admin` | `admin123` |
| `user` | `user123` |
| `metgo` | `metgo2025` |

Prueba API: `https://SU-API.onrender.com/api/health` debe responder JSON.

---

## 5. API REST en internet (obligatorio para datos reales)

Vue en Netlify llama a la API **desde el navegador del usuario**. `127.0.0.1:8080` no funciona.

1. Despliegue Flask (`backend/05_APIs_Externas/api_rest`) en un host con HTTPS.
2. En ese servidor:

```bash
METGO_CORS_ORIGINS=https://metgo-quillota.netlify.app,https://metgo-3d-quillota-60gb.streamlit.app
METGO_JWT_SECRET=su_secreto_largo
```

3. En Netlify, variable de build:

```env
VITE_METGO_API=https://su-api.onrender.com/api
```

4. **Trigger deploy** (rebuild) para que Vite embeba la URL en el bundle.

---

## 6. Build local (opcional)

```powershell
cd d:\METGO_3D_Quillota_60GB\frontend\vue
copy .env.production.example .env.production
# Editar VITE_METGO_API con la URL pública de la API
npm ci
npm run build
npx serve dist
```

---

## 7. Solución de problemas

| Problema | Qué hacer |
|----------|-----------|
| iframe en blanco en Streamlit | Compruebe `METGO_VUE_URL` y Reboot; abra la URL Netlify directamente. |
| Login no guarda sesión en iframe | Use **Abrir en pestaña nueva** en la página Streamlit; algunos navegadores bloquean cookies en iframe. |
| Error CORS al cargar datos | Añada la URL `https://*.netlify.app` en `METGO_CORS_ORIGINS` del servidor API. |
| Build falla en Netlify | Revise logs; suele faltar `npm ci` o Node &lt; 18. |
| Rutas 404 al refrescar | Confirme `[[redirects]]` en `netlify.toml` raíz. |

---

## 8. Archivos del repo

| Archivo | Uso |
|---------|-----|
| `netlify.toml` (raíz) | Config principal para importar el repo |
| `frontend/vue/netlify.toml` | Si configura Base directory = `frontend/vue` en la UI |
| `frontend/vue/public/_redirects` | Respaldo SPA (`/* /index.html 200`) |
| `metgo_vue_embed.py` | Lee `METGO_VUE_URL` para el iframe |

Ver también: [`DESPLIEGUE_VUE_IFRAME.md`](DESPLIEGUE_VUE_IFRAME.md) (visión general iframe + Vercel).
