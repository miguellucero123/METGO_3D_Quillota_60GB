# Paso a paso — tareas pendientes (ops + smoke)

> **Corte:** 2026-08-05 · API prod `version=d3f8c2e`  
> **Para quién:** acceso a Render, Supabase, GitHub y correo real.  
> **Objetivo:** cerrar lo que aún es **humano** (mail verify, destinos umbrales, Stripe opcional, datos oficiales).  
> Claves: [`INVENTARIO_CLAVES_PLATAFORMAS.md`](INVENTARIO_CLAVES_PLATAFORMAS.md) · Plan mejoras: [`PLAN_TRABAJO_MEJORAS.md`](PLAN_TRABAJO_MEJORAS.md) · Checklist corto: [`PASOS_PENDIENTES_OPS.md`](PASOS_PENDIENTES_OPS.md)

API: `https://metgo-api.onrender.com/api` · SPATI: `https://metgo-spati.pages.dev`

---

## Checkpoint actual

| Ítem | Estado | Evidencia |
|------|--------|-----------|
| Health / SMTP | ✅ | `s5_ops.smtp_configurado=true`; `pendiente` solo `STRIPE_SECRET_KEY` |
| Supabase `rut_hash` + remove demo | ✅ | `db push` + login `demo@ventora.demo` → 401 |
| Crons SPATI alertas + ETL sync | ✅ | Actions schedule OK; SPATI por sitio (no `forzar=1` global) |
| Outbox flush cron | ✅ | `POST /api/cron/notificaciones/outbox-retry` + paso en workflow M9 |
| Landings + `/registro` + `/cuenta` + banner piloto | ✅ | Pages Quillota/Copiapó/Mantos/Paine/SPATI |
| Invite org (B3) | ✅ | API + UI en `/cuenta` |
| Smoke endpoints automatizado | ✅ | `python scripts/smoke_ops_p1.py` (públicos OK 2026-08-05) |
| **P1-7 Destinos umbrales en prod** | 🔶 | UI lista; falta guardar (UI o smoke con `CRON_SECRET`/JWT) |
| **Smoke registro → clic mail** | 🔶 | SMTP OK; falta E2E con correo real |
| Stripe cobro real | ⬜ opcional | Checkout mock válido sin keys |
| CSV/IDs SINCA·Agromet·DMC | ⬜ P2 | `e12_ops.pendiente` aún lista IDs/CSV prod |

### Qué hacer ahora (orden)

1. **Umbrales** — guardar email en Escondida (UI o smoke con secret).  
2. **Verify-email** — un registro real + abrir link del mail → login → `/app`.  
3. (Opcional) Stripe / IDs oficiales cuando haya datos comerciales.

---

## Ya hecho — no repetir (referencia)

### Diagnóstico (Paso 0) ✅

```powershell
$h = Invoke-RestMethod "https://metgo-api.onrender.com/api/health"
$h.s5_ops
# Esperado 2026-08-05:
#   smtp_configurado = True
#   pendiente = ["STRIPE_SECRET_KEY"]   # opcional
#   email_dev = False, pii_kek_configurado = True
```

### Supabase (Paso 1) ✅

Migraciones aplicadas: `20260804150000_orgs_rut_hash_unique.sql`, `20260804160000_remove_demo_ventora.sql`.

### Render SMTP + URLs (Paso 2–3) ✅

`METGO_SMTP_*`, `METGO_EMAIL_DEV=0`, `METGO_PII_KEK`, `METGO_*_PUBLIC_URL`, seed demo off. Redeploy Live.

### Producto código (ex Paso 6 parcial) ✅

- `/cuenta` + checkout mock + invitar: Quillota, Copiapó, Mantos, SPATI.  
- Banner “quedan X días” si `trialing`.  
- Registro SPATI: `/f/{faena}/registro` fija la faena (esperado).

---

## Pendiente A — Destinos alerta SPATI (P1-7) · ~5–10 min

### Opción A1 — UI

1. https://metgo-spati.pages.dev/f/escondida/login (Ctrl+F5).  
2. Login JWT (break-glass o cuenta registrada).  
3. https://metgo-spati.pages.dev/f/escondida/umbrales  
4. **Emails:** p. ej. `miguel.lucero@metgo3d.com` · **Nivel mínimo:** 2 · **Guardar destinos**.  
5. (Opcional) repetir en `/f/quebrada_blanca/umbrales`.

### Opción A2 — Smoke (sin UI)

```powershell
cd D:\METGO_3D_Quillota_60GB
$env:CRON_SECRET = "<mismo valor que Render metgo-api>"
python scripts\smoke_ops_p1.py --faena escondida --alerta-email "miguel.lucero@metgo3d.com"
# Debe marcar OK: PUT umbrales + POST /cron/spati/alertas
```

O con usuario:

```powershell
$env:METGO_SMOKE_USER = "admin"   # o email identity
$env:METGO_SMOKE_PASS = "<METGO_PASSWORD_ADMIN u otra>"
$env:METGO_SMOKE_SITIO = "spati"
$env:METGO_SMOKE_FAENA = "escondida"
python scripts\smoke_ops_p1.py
```

**Hecho cuando:** en Supabase `spati_sitios_grua.alertas_destino` del slug `escondida` tiene el email (o el smoke PUT da OK).

---

## Pendiente B — Smoke registro → mail → panel · ~15 min

El script **no puede hacer clic** en el correo. Automatiza hasta `validate-registro` / `register-v2`.

### B1 — Dry-run (sin crear usuario)

```powershell
python scripts\smoke_ops_p1.py --validate-registro --sitio paine
# OK = payload válido contra API
```

### B2 — Registro real + verify (humano)

| Paso | URL |
|------|-----|
| Registro | https://metgo-paine.pages.dev/registro (o Quillota `/registro`) |
| Mail | Abrir link `/verificar?token=…` |
| Login | `/login` → `/app` |

Checklist:

1. `/` = landing (no panel).  
2. Registro: RUT chileno válido + 4 consentimientos + password ≥10.  
3. Mail llega (Zoho; revisar spam).  
4. Tras verify, login entra a `/app`.  
5. Segundo registro mismo RUT → `rut_already_registered`.

Script opcional (crea org real):

```powershell
$env:SMOKE_DO_REGISTER = "1"
$env:METGO_SMOKE_EMAIL = "tu_correo_real@..."
python scripts\smoke_ops_p1.py --register --sitio paine
# Luego: clic en el mail; después login con ese email
```

SPATI: registro por faena, ej. https://metgo-spati.pages.dev/f/escondida/registro (la faena en la URL es correcta).

---

## Pendiente C — Stripe (opcional)

Solo si cobro real. Render → `metgo-api` → Environment:

- `STRIPE_SECRET_KEY`
- `STRIPE_PRICE_STARTER` / `STRIPE_PRICE_PRO`
- Redeploy → `/cuenta` → “Elegir” debe ir a Checkout Stripe.

Sin esto, el mock aplica el plan al instante (OK para piloto).

---

## Pendiente D — P2 datos oficiales (cuando haya IDs/CSV)

No bloquea registro ni alertas M9.

| Variable / acción | Notas |
|-------------------|--------|
| `METGO_OPENMETEO_API_KEY` | Menos 429 |
| `METGO_SINCA_IDS`, `METGO_AGROMET_IDS`, `METGO_DMC_IDS` | Health `e12_ops.pendiente` |
| `METGO_SINCA_CSV_DIR` + `METGO_SINCA_USE_EJEMPLOS=0` | CSV prod en Render |
| Retrain helada/PM10 | Más adelante |

---

## Smoke automático — referencia rápida

```powershell
cd D:\METGO_3D_Quillota_60GB

# Solo GET públicos (sin secretos) — ya OK en prod
python scripts\smoke_ops_p1.py --public-only

# Completo con CRON o JWT (umbrales + cron)
# ver variables arriba en Pendiente A
python scripts\smoke_ops_p1.py --faena escondida
```

Contratos reales (no usar paths viejos del borrador):

| Acción | Método / path |
|--------|----------------|
| Health | `GET /api/health` |
| Planes | `GET /api/public/planes?sitio=` |
| Umbrales | `GET/PUT /api/public/spati/{faena}/umbrales` |
| Login | `POST /api/auth/login` → JWT en `access_token` |
| Me / cuenta | `GET /api/auth/me`, `GET /api/auth/cuenta` |
| Validate / register | `POST /api/auth/validate-registro`, `POST /api/auth/register-v2` |
| Cron alertas | `POST /api/cron/spati/alertas` + `X-Cron-Token` |
| ETL sync | `GET` o `POST /api/cron/sync` + token |

ETL ya corre en GitHub (`etl-meteo-cron.yml`). Comprobar manual opcional:

```powershell
Invoke-RestMethod "https://metgo-api.onrender.com/api/cron/sync?token=TOKEN" -Method Get
```

---

## Seguridad (DT-auth-sec + P2)

Detalle: [`FASE_SEGURIDAD_DT_AUTH.md`](FASE_SEGURIDAD_DT_AUTH.md) · KYC: [`ADR_KYC_IDENTIDAD.md`](ADR_KYC_IDENTIDAD.md).

| Control | Estado |
|---------|--------|
| Rate limit login/register/reenviar | ✅ código — deploy API |
| Turnstile registro (4 SPAs) | ✅ código — keys Render + Pages |
| CSP + `_headers` Pages | ✅ código — redeploy SPAs |
| RLS identity deny anon | ✅ aplicado CLI 2026-08-05 |
| ETL retry-queue + CRON | ✅ código |
| KYC manual + gate pago | ✅ migración aplicada; gate off hasta cobrar |
| Sesión idle / KEK_PREV | ✅ código — Redis multi-worker ⬜ |

---

## Criterio “listo para clientes”

| Criterio | Estado |
|----------|--------|
| `smtp_configurado = true` | ✅ |
| Verify-email E2E (mail → SPA → login) | 🔶 |
| `rut_hash` + rechazo mismo RUT | ✅ código/SQL; 🔶 probar E2E en smoke B |
| `demo@ventora.demo` → 401 | ✅ |
| Paine `/` landing; `/app` con JWT | ✅ |
| Destinos umbrales guardados en prod | 🔶 |
| Smoke registro en ≥2 SPAs + SPATI | 🔶 |
| Rate limit + Turnstile en prod | 🔶 keys + deploy |
| KYC ops checklist | ✅ ADR; 🔶 primer caso real |
| Stripe | ⬜ opcional |

---

## Fase

**Ops P0** ✅ (salvo verify E2E) → **DT-auth-sec + P2 KYC** ✅ código / 🔶 ops → **Ops P1** 🔶 (umbrales) → **Producto 2.x** (SII) → **Redis** cuando haya >1 worker.
