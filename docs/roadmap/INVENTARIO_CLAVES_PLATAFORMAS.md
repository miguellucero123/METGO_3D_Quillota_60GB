# Inventario detallado de claves por plataforma

> **Corte:** 2026-08-03 · Guía operativa de secretos y variables.  
> **Nunca** pegues valores reales en chat, Issues o commits.  
> Diagnóstico vivo: `GET https://metgo-api.onrender.com/api/health` → `s5_ops` / `e12_ops`.  
> Relacionado: [`PASOS_PENDIENTES_OPS.md`](PASOS_PENDIENTES_OPS.md) · [`GUIA_ARRANQUE_OPS_P0.md`](GUIA_ARRANQUE_OPS_P0.md) · [`CHECKLIST_AUTH_PROD.md`](CHECKLIST_AUTH_PROD.md) · [`.env.example`](../../.env.example)

---

## Mapa de plataformas

| Plataforma | Proyecto / servicio | URL típica | Rol |
|------------|---------------------|------------|-----|
| **Render** | `metgo-api` | https://metgo-api.onrender.com | API Flask + JWT + identity + crons |
| **Render** | `metgo-streamlit` | https://metgo-streamlit.onrender.com | Portal Streamlit (Render) |
| **Streamlit Cloud** | app del repo | https://metgo-3d-quillota-60gb.streamlit.app | Portal público Cloud |
| **Supabase** | 1 proyecto datos | Dashboard Supabase | Postgres (usuarios, meteo, faenas) — **no** Auth IdP |
| **Cloudflare Pages** | Quillota / Copiapó / Mantos / SPATI / Paine | `*.pages.dev` | SPAs Vue (**principal**) |
| **Netlify** | Quillota (legado) | https://metgo3d.netlify.app | Mirror / legado; preferir Pages |
| **GitHub Actions** | repo monorepo | Actions | Cron ETL + alertas SPATI |
| **Zoho Mail** | buzón `@metgo3d.com` | Zoho | SMTP verify / alertas |
| **Stripe** | cuenta billing | Dashboard Stripe | Cobro (opcional; mock sin key) |
| **Open-Meteo** | cuenta API | open-meteo.com | Key opcional anti-429 |
| **WordPress** | marketing | www (propio) | Solo enlaces; **sin** claves METGO |
| **cron-job.org** | opcional | — | Alternativa a GitHub cron |

---

## 1. Render — `metgo-api` (todas las claves críticas)

**Dónde:** [Render Dashboard](https://dashboard.render.com) → servicio **`metgo-api`** → **Environment**.  
Tras cambiar secretos: **Manual Deploy → Clear build cache & deploy**.

### 1.1 Seguridad e identity (P0)

| Variable | Obligatoria | Cómo obtenerla / valor | Notas |
|----------|-------------|------------------------|--------|
| `METGO_JWT_SECRET` | **Sí** | `openssl rand -hex 32` (o Generate en Render) | Firma JWT. **No** reutilizar como PII. |
| `METGO_PII_KEK` | **Sí** | Otro `openssl rand -hex 32` | Cifra RUT/nombres. Rotar invalida PII antigua. |
| `METGO_IDENTITY_STORE` | **Sí** | `supabase` | `memory` solo tests |
| `METGO_EMAIL_DEV` | **Sí** | `0` | `1` = token verify en JSON (inseguro) |
| `METGO_ALLOW_SELF_REGISTER` | **Sí** | `0` | Registro comercial = `register-v2` |
| `METGO_API_AUTH_REQUIRED` | **Sí** | `1` | Endpoints protegidos |
| `METGO_ENV` | Recomendado | `production` | O confiar en `RENDER=true` |
| `METGO_SPATI_PUBLIC_URL` | **Sí** (SPATI) | `https://metgo-spati.pages.dev` | Links verify-email / checkout return |
| `METGO_PUBLIC_APP_URL` | Opcional | URL Quillota | Links verify si no hay SPATI |
| `METGO_CORS_ORIGINS` | **Sí** | Lista CSV de orígenes HTTPS | Ver §1.8 |
| `CRON_SECRET` | **Sí** | `openssl rand -hex 24` | Token crons; **igual** en GitHub |

### 1.2 Supabase (en Render, no en el front)

| Variable | Obligatoria | Dónde sacarla | Notas |
|----------|-------------|---------------|--------|
| `SUPABASE_URL` | **Sí** | Project Settings → API → Project URL | Ej. `https://xxxx.supabase.co` |
| `SUPABASE_KEY` | **Sí** | Project Settings → API → **`service_role`** | **Nunca** en SPA / Netlify / CF Pages |

### 1.3 Passwords legacy por “proyecto / sitio” (JWT clásico)

Usuarios fijos en código; la **clave** sale del env. Útiles como break-glass mientras identity Supabase no cubre el 100 %.

| Variable | Usuario típico | Proyecto / SPA |
|----------|----------------|----------------|
| `METGO_PASSWORD_ADMIN` | `admin` | Todos (ops / break-glass) |
| `METGO_PASSWORD_USER` | `user` | Quillota |
| `METGO_PASSWORD_METGO` | `metgo` | Quillota |
| `METGO_PASSWORD_AGRONOMO` | `agronomo` | Quillota |
| `METGO_PASSWORD_OPERADOR` | `operador` | Quillota |
| `METGO_PASSWORD_LECTOR` | `lector` | Quillota |
| `METGO_PASSWORD_COPIAPO` | `copiapo` | **Copiapó** |
| `METGO_PASSWORD_MANTOS` | `mantos` | **Mantos Blancos** |
| `METGO_PASSWORD_PAINE` | `paine` | **Paine** |

URLs públicas SPA (verify-email register-v2):

| Variable | Default |
|----------|---------|
| `METGO_SPATI_PUBLIC_URL` | `https://metgo-spati.pages.dev` |
| `METGO_QUILLOTA_PUBLIC_URL` / `METGO_VUE_URL` | `https://metgo-quillota.pages.dev` |
| `METGO_COPIAPO_PUBLIC_URL` | `https://metgo-copiapo.pages.dev` |
| `METGO_MANTOS_PUBLIC_URL` | `https://metgo-mantos.pages.dev` |
| `METGO_PAINE_PUBLIC_URL` | `https://metgo-paine.pages.dev` |

Generar claves fuertes distintas por rol. Tras rotar → redeploy.

### 1.4 SMTP (verify-email + notificaciones)

| Variable | Ejemplo | Notas |
|----------|---------|--------|
| `METGO_SMTP_HOST` | `smtp.zoho.com` | |
| `METGO_SMTP_PORT` | `587` | |
| `METGO_SMTP_TLS` | `1` | |
| `METGO_SMTP_USER` | `miguel.lucero@metgo3d.com` | |
| `METGO_SMTP_PASSWORD` | App Password Zoho | No la clave de login web si hay 2FA |
| `METGO_SMTP_FROM` | mismo correo o `noreply@…` | |
| `METGO_NOTIFY_EMAIL` | destino ops | Default código: `miguel.lucero@metgo3d.com` |
| `METGO_WEBHOOK_URL` | Discord/Slack/Make | Alternativa sin SMTP |

**Zoho Forever Free** suele **no** exponer SMTP a apps externas → Mail Lite+ o ZeptoMail/Resend.  
Sin SMTP: verify queda en **logs** Render (`mode=log`); outbox en `datos_runtime/notificaciones_outbox.jsonl`.

### 1.5 Stripe (opcional)

| Variable | Valor | Notas |
|----------|-------|--------|
| `STRIPE_SECRET_KEY` | `sk_test_…` o `sk_live_…` | Sin esto → **checkout mock** (aplica plan al instante) |
| `STRIPE_PRICE_STARTER` | Price ID | Plan starter |
| `STRIPE_PRICE_PRO` | Price ID | Plan pro |
| `STRIPE_PRICE_ENTERPRISE` | Price ID | Si existe en catálogo |
| `STRIPE_WEBHOOK_SECRET` | `whsec_…` | Endpoint: `POST /api/billing/webhook` |

### 1.6 Demo / preview SPATI

La **demo fija** (`demo@ventora.demo`) está **retirada**. No publicar claves en docs ni en SPA.

| Variable | Default | Notas |
|----------|---------|--------|
| `METGO_SEED_DEMO_PREVIEW` | `0` | Solo `1` recrea demo (no usar en prod) |
| `METGO_DEMO_EMAIL` | — | Solo si se re-habilita seed |
| `METGO_DEMO_PASSWORD` | — | Solo si se re-habilita seed; no documentar valor |
| `METGO_DEMO_FAENA` | `quebrada_blanca` | Solo con seed |
| `METGO_ALLOW_PREVIEW` | `0` / `1` | Permite preview-hora / DELETE demo sin cron |

### 1.7 Datos oficiales / E12 (P1–P2)

| Variable | Uso |
|----------|-----|
| `METGO_OPENMETEO_API_KEY` | Reduce 429 Open-Meteo |
| `METGO_OPENMETEO_TIMEOUT` | Default `8` (Blueprint) |
| `METGO_OPENMETEO_RETRIES` | Default `2` |
| `METGO_OPENMETEO_COOLDOWN` | Default `120` |
| `METGO_SINCA_CSV_DIR` | Carpeta CSV prod en disco Render |
| `METGO_SINCA_CSV_URL` | URL con `{slug}` |
| `METGO_SINCA_IDS` | JSON `{"copiapo_centro":"ID",…}` |
| `METGO_SINCA_USE_EJEMPLOS` | `0` en prod con CSV propio |
| `METGO_AGROMET_IDS` / `METGO_AGROMET_CSV_DIR` / `METGO_AGROMET_USE_EJEMPLOS` | Agromet |
| `METGO_DMC_IDS` / `METGO_DMC_CSV_DIR` / `METGO_DMC_USE_EJEMPLOS` | DMC |
| `METGO_DMC_USAR_CANDIDATOS` | `1` tras validar código 330007 |
| `METGO_OP_UMBRALES_JSON` | Override umbrales ops por env |

Sin dirs CSV → fallback `docs/ejemplos/*_csv/` (E12.1).

### 1.8 CORS (orígenes SPA)

Valor Blueprint de referencia (`render.yaml`):

```text
https://metgo3d.netlify.app,
https://metgo-quillota.pages.dev,
https://metgo-copiapo.pages.dev,
https://metgo-mantos.pages.dev,
https://metgo-paine.pages.dev,
https://metgo-spati.pages.dev,
https://metgo-3d-quillota-60gb.streamlit.app,
https://metgo-paine.netlify.app,
https://metgo-copiapo.netlify.app,
https://metgo-mantos.netlify.app
```

Añadir dominios custom cuando existan.

### 1.9 Otras (Blueprint / ops)

| Variable | Uso |
|----------|-----|
| `METGO_API_HOST` | `0.0.0.0` |
| `METGO_STREAMLIT_CLOUD_URL` | URL Streamlit para API/portal |
| `METGO_STREAMLIT_RENDER_URL` | Render Streamlit |
| `METGO_ML_LEGACY_SCAN` | `0` |
| `METGO_ML_AUTO_TRAIN` | `1` |
| `METGO_MQTT_*` | IoT opcional (ver `.env.example`) |
| `METGO_ETL_*` | ETL nocturno |
| `METGO_METRICS_PUBLIC` | Prometheus |
| `METGO_CONSENT_VERSION` | Versión consentimientos |
| `PYTHON_VERSION` | `3.11.9` |

---

## 2. Render — `metgo-streamlit`

| Variable | Valor típico | Notas |
|----------|--------------|--------|
| `METGO_VUE_URL` | `https://metgo-quillota.pages.dev` (Netlify legado opcional) | Enlaces del portal |
| `METGO_CORS_ORIGINS` | Vue + streamlit | |
| `METGO_PASSWORD_*` | Mismos que API si el portal autentica | Opcional |
| `PYTHON_VERSION` | `3.11.9` | |

---

## 3. Streamlit Cloud

**Dónde:** App → **Settings → Secrets** (TOML).

| Secret | Uso |
|--------|-----|
| `METGO_VUE_URL` | `"https://metgo-quillota.pages.dev"` |
| `METGO_PASSWORD_ADMIN` (y roles) | Si el portal exige login |
| (opcional) `SUPABASE_*` | Solo si algún script Cloud lee DB directo — preferir API |

No sustituye a `metgo-api`. App: `https://metgo-3d-quillota-60gb.streamlit.app`.

---

## 4. Supabase (un proyecto)

| Clave en dashboard | Qué hacer con ella |
|--------------------|--------------------|
| Project URL | → `SUPABASE_URL` en **Render API** |
| `anon` `public` | Solo frontends con Realtime (ej. Paine); RLS obligatorio |
| `service_role` `secret` | → `SUPABASE_KEY` **solo** Render API |
| DB password | Solo migraciones CLI / Studio; no en SPA |

**Auth de producto = JWT Flask**, no Supabase Auth.  
Grants/migraciones: ver `GUIA_ARRANQUE_OPS_P0.md` bloque B y `supabase/migrations/`.

---

## 5. Cloudflare Pages — por proyecto SPA

Cada proyecto Pages → **Settings → Environment variables** (Production / Preview).

| Proyecto | Sitio código | URL | Variables |
|----------|--------------|-----|-----------|
| Quillota | `frontend/vue` | `metgo-quillota.pages.dev` | `VITE_METGO_API=https://metgo-api.onrender.com/api` · `VITE_ALLOW_SELF_REGISTER=0` · opcional `VITE_METGO_STREAMLIT_RENDER_URL` |
| Copiapó | `frontend/copiapo` | `metgo-copiapo.pages.dev` | `VITE_METGO_API=…` |
| Mantos | `frontend/mantos_blancos` | `metgo-mantos.pages.dev` | `VITE_METGO_API=…` |
| SPATI / VENTORA | `frontend/spati` | `metgo-spati.pages.dev` | `VITE_METGO_API=…` (default en `site.config.js` si no hay env) |
| Paine | repo `metgo-paine` | `metgo-paine.pages.dev` | `/` landing pública · `/app` JWT · `VITE_METGO_API` · `METGO_PASSWORD_PAINE` |

**Prohibido en Pages:** `METGO_JWT_SECRET`, `METGO_PII_KEK`, `SUPABASE_KEY` service_role, `METGO_SMTP_*`, `STRIPE_SECRET_KEY`, `CRON_SECRET`.

Tras cambiar `VITE_*` → **nuevo deploy** (se inyectan en build).

---

## 6. Netlify (legado)

| Sitio | Variable | Valor |
|-------|----------|--------|
| Quillota (mirror) | `VITE_METGO_API` | `https://metgo-api.onrender.com/api` |
| | `VITE_ALLOW_SELF_REGISTER` | `0` |

**URL principal Quillota:** https://metgo-quillota.pages.dev (Cloudflare Pages). Netlify `metgo3d.netlify.app` queda como legado.

---

## 7. GitHub Actions (monorepo)

**Dónde:** GitHub → `METGO_3D_Quillota_60GB` → **Settings → Secrets and variables → Actions**.

| Secret | Debe coincidir con | Workflows |
|--------|--------------------|-----------|
| `CRON_SECRET` | Render `CRON_SECRET` | `spati-alertas-cron.yml`, `etl-meteo-cron.yml` |

CI (`ci.yml` / `metgo-ci.yml`) no necesita secretos de prod para tests unitarios habituales.

---

## 8. Zoho Mail (proveedor externo)

| Paso | Acción |
|------|--------|
| 1 | Plan con SMTP (Mail Lite+) |
| 2 | Activar IMAP/SMTP en la cuenta |
| 3 | Si 2FA → **App Password** |
| 4 | Pegar en Render `METGO_SMTP_*` |

Usuario de referencia ops: `miguel.lucero@metgo3d.com` (ver `.env.example`).

---

## 9. Stripe (proveedor externo)

| En Stripe Dashboard | En Render |
|---------------------|-----------|
| Secret key | `STRIPE_SECRET_KEY` |
| Products → Prices | `STRIPE_PRICE_STARTER` / `_PRO` / … |
| Webhook → `https://metgo-api.onrender.com/api/billing/webhook` | `STRIPE_WEBHOOK_SECRET` |

Sin cuenta Stripe el producto **sigue operable** con checkout mock.

---

## 10. Open-Meteo

| Variable | Dónde | Efecto |
|----------|-------|--------|
| `METGO_OPENMETEO_API_KEY` | Render API | Menos 429; sin key hay cooldown + fallback |

---

## 11. WordPress

Sin variables METGO. Solo botones/enlaces a:

- `https://metgo-spati.pages.dev/f/{faena}/login`
- `https://metgo-spati.pages.dev/f/{faena}/registro`
- SPAs Quillota / Copiapó / Mantos / Paine según campaña

---

## 12. Matriz “proyecto de producto → claves que le afectan”

| Producto | Front | Auth usuarios | Claves en ese front | Claves en API que lo habilitan |
|----------|-------|---------------|---------------------|--------------------------------|
| Quillota agrícola | Vue / **CF Pages** (`metgo-quillota.pages.dev`) | JWT legacy + identity | `VITE_METGO_API` | `METGO_PASSWORD_*`, JWT, Supabase, CORS |
| Copiapó aire | CF Pages | JWT `copiapo` / identity | `VITE_METGO_API` | `METGO_PASSWORD_COPIAPO`, SINCA IDs |
| Mantos faena | CF Pages | JWT `mantos` / identity | `VITE_METGO_API` | `METGO_PASSWORD_MANTOS`, umbrales |
| SPATI / VENTORA | CF Pages | Identity Supabase + demo | `VITE_METGO_API` | PII, SMTP, Stripe, `METGO_SPATI_PUBLIC_URL`, demo |
| Paine | CF Pages (repo aparte) | JWT `paine` | `VITE_METGO_API` (+ anon Supabase) | `METGO_PASSWORD_PAINE` |
| Streamlit portal | Cloud / Render | Passwords opcionales | Secrets Cloud | `METGO_VUE_URL` |
| WordPress | CMS | — | — | — |

---

## 13. Cómo generar secretos (sin compartirlos)

```bash
openssl rand -hex 32   # JWT, PII_KEK
openssl rand -hex 24   # CRON_SECRET
```

PowerShell:

```powershell
-join ((1..48) | ForEach-Object { '{0:x2}' -f (Get-Random -Max 256) })
```

---

## 14. Diagnóstico — qué falta (comando)

```powershell
$h = Invoke-RestMethod "https://metgo-api.onrender.com/api/health" -TimeoutSec 90
$h.s5_ops
$h.e12_ops
$h.supabase_error
```

| Campo `s5_ops` | Significado |
|----------------|-------------|
| `pii_kek_configurado` | `METGO_PII_KEK` presente |
| `smtp_configurado` | `METGO_SMTP_HOST`+`USER`+`PASSWORD` |
| `stripe_configurado` | `STRIPE_SECRET_KEY` |
| `email_dev` | Debe ser `false` en prod |
| `pendiente` | Lista de variables que el health marca faltantes |
| `identity_store` | Debe ser `supabase` |

Referencia al corte 2026-08-03 (prod):

- `pii_kek_configurado`: **true**
- `email_dev`: **false**
- `pendiente`: `METGO_SMTP_HOST`, `STRIPE_SECRET_KEY`
- `e12_ops`: CSV ejemplos; faltan IDs oficiales prod

---

## 15. Checklist de revisión (imprimible)

```text
RENDER metgo-api
[ ] METGO_JWT_SECRET
[ ] METGO_PII_KEK (≠ JWT)
[ ] SUPABASE_URL + SUPABASE_KEY (service_role)
[ ] CRON_SECRET
[ ] METGO_CORS_ORIGINS (todas las SPAs)
[ ] METGO_EMAIL_DEV=0
[ ] METGO_IDENTITY_STORE=supabase
[ ] METGO_API_AUTH_REQUIRED=1
[ ] METGO_SPATI_PUBLIC_URL
[ ] METGO_PASSWORD_ADMIN (+ COPIAPO/MANTOS/PAINE)
[ ] METGO_SMTP_* (o decisión: solo logs)
[ ] STRIPE_* (o decisión: mock OK)
[ ] METGO_OPENMETEO_API_KEY (P2)
[ ] METGO_SINCA_* / AGROMET / DMC (P2)

GITHUB
[ ] Actions secret CRON_SECRET = Render

CLOUDFLARE / NETLIFY (cada SPA)
[ ] VITE_METGO_API = https://metgo-api.onrender.com/api
[ ] Sin service_role ni JWT secret

STREAMLIT CLOUD
[ ] METGO_VUE_URL (opcional passwords)

SUPABASE
[ ] Grants identity + faena_reglas
[ ] service_role solo en Render

ZOHO / STRIPE
[ ] App password SMTP / keys Stripe según decisión comercial
```

---

## Fase

**Ops P0–P2** · inventario de claves · sin cambio de contrato OpenAPI.
