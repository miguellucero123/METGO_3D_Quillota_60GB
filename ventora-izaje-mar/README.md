# VENTORA Izaje Mar — arranque en otro PC

SPA Vue 3 + Vite (izaje / puertos). API de datos: **https://metgo-api.onrender.com/api** (proxy en `npm run dev`).

Producción relacionada:
- Esta carpeta → Cloudflare Pages `ventora-izaje-mar`
- Hermano casi idéntico: `frontend/spati` → https://metgo-spati.pages.dev

---

## Requisitos (PC destino)

| Herramienta | Versión |
|-------------|---------|
| Node.js | **20 LTS** o 22 (incluye `npm`) |
| Git | opcional si recibes ZIP |
| Navegador | Chrome / Edge |

No hace falta Python ni Supabase en el PC para **solo** correr el frontend.

---

## Opción A — Carpeta ZIP (rápida)

En el PC origen:

1. Copia la carpeta `ventora-izaje-mar` (sin `node_modules`, sin `dist`, sin `.wrangler`).
2. Incluye este `README.md` y `.env.example`.
3. Opcional: un archivo `CREDENCIALES.local.txt` (fuera de Git) con usuario/clave de prueba que te dé el admin METGO.

En el PC destino:

```powershell
cd ruta\ventora-izaje-mar
copy .env.example .env
npm install
npm run dev
```

Abrir: **http://localhost:5178**

La primera llamada a la API puede tardar (Render free cold start ~30–60 s).

---

## Opción B — Clone del monorepo METGO

```powershell
git clone https://github.com/miguellucero123/METGO_3D_Quillota_60GB.git
cd METGO_3D_Quillota_60GB\ventora-izaje-mar
copy .env.example .env
npm install
npm run dev
```

Invitar al colaborador en GitHub (Settings → Collaborators) si el repo es privado.

---

## Variables `.env` (frontend)

Ver `.env.example`. Mínimo para desarrollo local:

```env
VITE_METGO_API=https://metgo-api.onrender.com/api
```

`VITE_TURNSTILE_SITE_KEY` solo si van a probar registro con captcha (misma site key que Pages).

**Nunca** pegues `SUPABASE_SERVICE_ROLE`, `CRON_SECRET`, `WP_APP_PASSWORD` ni passwords de Render en esta carpeta. Eso es backend/ops.

---

## Entrar a la app (login)

1. Landing pública funciona sin login.
2. Login / registro: cuenta en sitio `spati` (identity) o break-glass ops (`METGO_PASSWORD_*` en Render) — **el dueño del proyecto te pasa email/clave por canal seguro**, no van en el README.
3. Registro nuevo: `/registro` o `/f/{faena}/registro` (piloto 15 días si la API está OK).

Smoke API (PowerShell):

```powershell
Invoke-RestMethod "https://metgo-api.onrender.com/api/health/live"
Invoke-RestMethod "https://metgo-api.onrender.com/api/public/planes?sitio=spati"
```

---

## Scripts útiles

| Comando | Uso |
|---------|-----|
| `npm run dev` | Local puerto **5178** |
| `npm run build` | Build `dist/` |
| `npm run preview` | Preview del build |
| `npm run pages:deploy` | Solo si tiene Wrangler + acceso Cloudflare al proyecto |

Deploy Pages requiere cuenta Cloudflare del equipo; no es necesario para desarrollar.

---

## Qué NO compartir

- `node_modules/`, `dist/`, `.wrangler/`, `.lighthouseci/`
- Vault `local/METGO_VAULT.local.env` del monorepo
- Service role Supabase / secretos Render

## Docs relacionadas (monorepo)

- `PROMPT_VENTORA_IZAJE.md` — reglas para agentes/Cursor
- `docs/ops/BOOTSTRAP_OTRO_PC.md` — vault cifrado (stack completo METGO)
- `docs/manuales/DESPLIEGUE_VUE_CLOUDFLARE.md` — Pages

## Checklist entrega (origen → destino)

- [ ] ZIP o acceso Git a `ventora-izaje-mar`
- [ ] Node 20+ instalado en destino
- [ ] `.env` desde `.env.example`
- [ ] `npm install` + `npm run dev` OK
- [ ] Usuario de prueba enviado por WhatsApp/correo (no en el ZIP público)
- [ ] Aviso: cold start API Render
