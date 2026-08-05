# Paso a paso — tareas pendientes (ops + smoke)

> **Para quién:** quien tenga acceso a Render, Supabase y GitHub.  
> **Objetivo:** dejar registro usable (verify-email), RUT único, demo retirada, y smoke en las SPAs.  
> Detalle de claves: [`INVENTARIO_CLAVES_PLATAFORMAS.md`](INVENTARIO_CLAVES_PLATAFORMAS.md)

## Checkpoint 2026-08-05 (tarde)

| Hecho | Estado |
|-------|--------|
| Paso 0 health | ✅ `smtp_configurado=True` (queda Stripe opcional) |
| Paso 1 Supabase `db push` | ✅ rut_hash + remove demo + grants |
| Paine landing/auth | ✅ push + Pages |
| Mantos/Copiapó landing click/scroll | ✅ redeploy Pages 2026-08-05 |
| Cron SPATI alertas | ✅ por sitio (no `forzar=1` global); schedule OK |
| Demo VENTORA | ✅ login `demo@ventora.demo` → 401 |
| Vista `/cuenta` + banner piloto | ✅ Quillota, Copiapó, Mantos (+ SPATI banner) |
| Smoke registro → mail verify | 🔶 **manual** (correo real en `/registro`) |

**Siguiente humano:** smoke en https://metgo-paine.pages.dev/registro (o Quillota) con correo real → inbox → login → `/app`. Luego deploy CF de Quillota/Copiapó/Mantos/SPATI si aún no se publicó este commit.

Orden: **1 diagnóstico → 2 Supabase → 3 Render → 4 redeploy → 5 smoke → 6 P1**.

---

## Paso 0 — Diagnóstico (5 min)

PowerShell:

```powershell
$h = Invoke-RestMethod "https://metgo-api.onrender.com/api/health"
$h.s5_ops
$h.e12_ops
$h.supabase_error
```

Anota qué sale en `s5_ops.pendiente` (típicamente `METGO_SMTP_HOST`, `STRIPE_SECRET_KEY`).

---

## Paso 1 — Supabase SQL (15 min)

1. Abrí [Supabase Dashboard](https://supabase.com/dashboard) → proyecto METGO.
2. **SQL Editor** → New query.
3. Ejecutá **en este orden** (Run cada uno):

### 1.A — RUT único

Archivo: `supabase/migrations/20260804150000_orgs_rut_hash_unique.sql`

```sql
alter table public.orgs
  add column if not exists rut_hash text;

create unique index if not exists orgs_sitio_faena_rut_hash_uidx
  on public.orgs (sitio, coalesce(faena, ''), rut_hash)
  where rut_hash is not null;
```

### 1.B — Borrar demo VENTORA

Archivo: `supabase/migrations/20260804160000_remove_demo_ventora.sql`  
(pegar el archivo completo del repo y Run).

### Verificar SQL

```sql
SELECT email_norm FROM public.usuarios_app WHERE email_norm = 'demo@ventora.demo';
-- 0 filas

SELECT column_name FROM information_schema.columns
WHERE table_name = 'orgs' AND column_name = 'rut_hash';
-- 1 fila
```

---

## Paso 2 — Render: variables (20–40 min)

Render → servicio **`metgo-api`** → **Environment**.

### 2.A — SMTP (obligatorio para verify-email)

| Variable | Valor típico (Zoho) |
|----------|---------------------|
| `METGO_SMTP_HOST` | `smtp.zoho.com` |
| `METGO_SMTP_PORT` | `587` |
| `METGO_SMTP_TLS` | `1` |
| `METGO_SMTP_USER` | tu correo `@metgo3d.com` |
| `METGO_SMTP_PASSWORD` | **App Password** Zoho (no la clave web si hay 2FA) |
| `METGO_SMTP_FROM` | mismo correo o `noreply@…` |

Si Zoho Free no deja SMTP externo → Mail Lite+ / Resend / ZeptoMail.

### 2.B — URLs de verify (links del mail)

| Variable | Valor |
|----------|--------|
| `METGO_SPATI_PUBLIC_URL` | `https://metgo-spati.pages.dev` |
| `METGO_QUILLOTA_PUBLIC_URL` | `https://metgo-quillota.pages.dev` |
| `METGO_COPIAPO_PUBLIC_URL` | `https://metgo-copiapo.pages.dev` |
| `METGO_MANTOS_PUBLIC_URL` | `https://metgo-mantos.pages.dev` |
| `METGO_PAINE_PUBLIC_URL` | `https://metgo-paine.pages.dev` |

### 2.C — Confirmar (ya deberían existir)

| Variable | Esperado |
|----------|----------|
| `METGO_PII_KEK` | presente (≠ JWT) |
| `METGO_EMAIL_DEV` | `0` |
| `METGO_IDENTITY_STORE` | `supabase` |
| `METGO_SEED_DEMO_PREVIEW` | **no** poner `1` (o `0`) |
| `METGO_PASSWORD_PAINE` / `_MANTOS` / `_COPIAPO` / `_ADMIN` | break-glass (fuertes, no demos) |

### 2.D — Opcional

- Stripe: `STRIPE_SECRET_KEY` + Price IDs (si no, checkout mock OK).

---

## Paso 3 — Redeploy API (5–10 min)

1. Render → `metgo-api` → **Manual Deploy** → clear build cache (recomendado).
2. Esperá “Live”.
3. Verificá:

```powershell
$h = Invoke-RestMethod "https://metgo-api.onrender.com/api/health"
$h.s5_ops.smtp_configurado   # debe ser True
$h.s5_ops.pendiente          # sin METGO_SMTP_HOST
```

Demo retirada:

```powershell
try {
  Invoke-RestMethod https://metgo-api.onrender.com/api/auth/login `
    -Method POST -ContentType "application/json" `
    -Body '{"username":"demo@ventora.demo","password":"x","sitio":"spati","faena":"quebrada_blanca"}'
} catch { $_.Exception.Response.StatusCode.value__ }
# esperado: 401
```

---

## Paso 4 — Smoke registro / login (20 min)

Por cada SPA (Ctrl+F5):

| SPA | Landing | Registro | Login panel |
|-----|---------|----------|-------------|
| Paine | https://metgo-paine.pages.dev/ | `/registro` | `/app` solo con JWT |
| Quillota | https://metgo-quillota.pages.dev/ | `/registro` | `/app` |
| Copiapó | https://metgo-copiapo.pages.dev/ | `/registro` | `/app` |
| Mantos | https://metgo-mantos.pages.dev/ | `/registro` | `/app` |
| SPATI | https://metgo-spati.pages.dev/ | registro faena | panel faena |

Checklist por sitio:

1. Abrí `/` → landing (no el panel).
2. `/login` → **formulario** (si salta al panel: borrar Local Storage `metgo_*` / `metgo_paine_*`).
3. `/registro` → completar RUT + consentimientos → mensaje OK.
4. Abrí el correo → link `/verificar?token=…`.
5. Login → entra a `/app` (o panel del sitio).
6. Segundo registro con **mismo RUT** → debe rechazar (`rut_already_registered`).

Break-glass (ops): usuario `paine` / `mantos` / … con `METGO_PASSWORD_*` en Render.

---

## Paso 5 — P1 alertas (15–20 min, después del P0)

1. Render: copiá el valor de `CRON_SECRET`.
2. GitHub monorepo → **Settings → Secrets and variables → Actions** → secret `CRON_SECRET` = **mismo valor**.
3. SPATI → `/f/{faena}/umbrales` → guardar email/webhook de alerta.
4. Probar (opcional):

```powershell
# reemplazar TOKEN
Invoke-RestMethod "https://metgo-api.onrender.com/api/cron/sync?token=TOKEN" -Method POST
```

---

## Paso 6 — Producto (cuando ops P0 esté verde)

Orden de código (otra sesión):

1. Vista **Cuenta / planes / checkout** en Quillota, Copiapó, Mantos (como SPATI).
2. Banner “quedan X días de piloto”.
3. Decidir KYC (ClaveÚnica / proveedor / manual).
4. SII: certificado `.p12` + CAF (contabilidad) antes de boletas reales.

---

## Criterio de “listo para clientes”

- [ ] `health.s5_ops.smtp_configurado = true`
- [ ] Verify-email llega y abre el SPA correcto
- [ ] `rut_hash` aplicado; mismo RUT no abre otra org
- [ ] `demo@ventora.demo` → 401
- [ ] Paine `/` = landing; `/app` exige login
- [ ] Smoke registro OK en al menos 2 SPAs + SPATI

---

## Fase

**Ops P0** (pasos 1–4) → **Ops P1** (paso 5) → **Producto 2.x** (paso 6).
