# Guía de arranque ops P0/P1 — METGO producción

Documento **paso a paso** para cerrar lo pendiente sin adivinar variables ni URLs.  
Corte: 2026-07-30 · Servicio API: `https://metgo-api.onrender.com` · SPATI: `https://metgo-spati.pages.dev`

Relacionado: [`CUADRO_FASES_METGO.md`](CUADRO_FASES_METGO.md) · [`CHECKLIST_AUTH_PROD.md`](CHECKLIST_AUTH_PROD.md) · [`CHECKLIST_M8_OBSERVADO.md`](CHECKLIST_M8_OBSERVADO.md) · [`CHECKLIST_M9_IZAJE_PUSH.md`](CHECKLIST_M9_IZAJE_PUSH.md)

---

## Orden recomendado (1 sesión ~1–2 h)

| # | Bloque | Tiempo | Resultado esperado |
|---|--------|--------|--------------------|
| **A** | Diagnóstico actual | 5 min | Sabes qué falta en `health.s5_ops` |
| **B** | Supabase GRANT | 10 min | Health sin error `faena_reglas` |
| **C** | Render env P0 | 20–40 min | PII + SMTP (+ Stripe opcional) |
| **D** | Redeploy + smoke | 10 min | Registro / verify / health OK |
| **E** | GitHub `CRON_SECRET` (P1) | 10 min | Cron M9 deja de fallar por secret |
| **F** | Destinos alerta UI (P1) | 10 min | Emails por faena guardados |
| **G** | M8 CSV (P1, si hay datos) | 30+ min | Observado real (no solo demo) |

---

## A — Diagnóstico (antes de tocar nada)

En PowerShell:

```powershell
$h = Invoke-RestMethod "https://metgo-api.onrender.com/api/health"
$h.status
$h.supabase_error
$h.s5_ops
$h.openmeteo
$h.openmeteo_cooldown_s
```

Interpretación:

| Campo | Si ves… | Acción |
|-------|---------|--------|
| `supabase_error` con `faena_reglas` / `42501` | GRANT faltante | Bloque **B** |
| `s5_ops.pii_kek_configurado = false` | Sin cifrado PII prod | Bloque **C** → `METGO_PII_KEK` |
| `s5_ops.smtp_configurado = false` | Verify-email solo en logs | Bloque **C** → SMTP |
| `s5_ops.stripe_configurado = false` | Checkout mock (válido staging) | Opcional Stripe |
| `s5_ops.email_dev = true` | Token verify en JSON (inseguro) | `METGO_EMAIL_DEV=0` |
| `openmeteo = false` + cooldown | Rate limit | P2: API key Open-Meteo |

---

## B — Supabase: GRANT `faena_reglas` (P0)

### Dónde
1. Abrir [Supabase Dashboard](https://supabase.com/dashboard) → proyecto METGO (`ylivhjigvxqzpzchllte` si es el de prod).
2. **SQL Editor** → New query.
3. Pegar y **Run** el contenido de:

`supabase/migrations/20260729190000_grants_faena_reglas_service_role.sql`

### SQL (copia directa)

```sql
GRANT SELECT ON TABLE public.faena_reglas TO service_role, authenticated, anon;
GRANT SELECT, INSERT, UPDATE ON TABLE public.usuarios_app TO service_role;
GRANT SELECT, INSERT, UPDATE ON TABLE public.orgs TO service_role;
GRANT SELECT, INSERT, UPDATE ON TABLE public.suscripciones TO service_role;
GRANT SELECT, INSERT ON TABLE public.consentimientos TO service_role;
GRANT SELECT, INSERT, UPDATE ON TABLE public.spati_sitios_grua TO service_role;

ALTER TABLE IF EXISTS public.faena_reglas ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS faena_reglas_select_public ON public.faena_reglas;
CREATE POLICY faena_reglas_select_public ON public.faena_reglas
  FOR SELECT TO anon, authenticated, service_role
  USING (true);
```

### Verificar

```powershell
(Invoke-RestMethod "https://metgo-api.onrender.com/api/health").supabase_error
# Ideal: null / vacío
Invoke-RestMethod "https://metgo-api.onrender.com/api/public/faenas/escondida/reglas"
```

Si la tabla `faena_reglas` no existe, primero hay que aplicar migraciones identity (db push). En ese caso avisar y se revisa el orden de migraciones.

---

## C — Render: variables P0 (`metgo-api`)

### Dónde
Render Dashboard → servicio **`metgo-api`** → **Environment** → Add / Edit.

### C.1 Obligatorio (seguridad / identity)

| Variable | Cómo generarla / valor | Notas |
|----------|------------------------|--------|
| `METGO_JWT_SECRET` | Ya debería existir; si no: `openssl rand -hex 32` | No compartir |
| `METGO_PII_KEK` | **Distinto** al JWT: `openssl rand -hex 32` | Cifra RUT/nombres; no rotar a la ligera (rompe lectura de PII vieja) |
| `METGO_IDENTITY_STORE` | `supabase` | |
| `METGO_EMAIL_DEV` | `0` | En prod no devolver `verify_token` en la respuesta |
| `METGO_ALLOW_SELF_REGISTER` | `0` | Registro vía `register-v2` |
| `METGO_API_AUTH_REQUIRED` | `1` | |
| `METGO_SPATI_PUBLIC_URL` | `https://metgo-spati.pages.dev` | Links de verify-email |
| `SUPABASE_URL` | URL del proyecto | Ya suele estar |
| `SUPABASE_KEY` | **service_role** (no anon) | Ya suele estar; sin esto identity falla |

Generar secretos (Git Bash / WSL / OpenSSL):

```bash
openssl rand -hex 32
```

PowerShell:

```powershell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }) -as [byte[]])
```

### C.2 SMTP (verify-email real)

El código usa Zoho-compatible (ver `.env.example`):

| Variable | Ejemplo |
|----------|---------|
| `METGO_SMTP_HOST` | `smtp.zoho.com` |
| `METGO_SMTP_PORT` | `587` |
| `METGO_SMTP_TLS` | `1` |
| `METGO_SMTP_USER` | `tu@metgo3d.com` |
| `METGO_SMTP_PASSWORD` | app password (si 2FA) |
| `METGO_SMTP_FROM` | mismo o `noreply@…` |
| `METGO_NOTIFY_EMAIL` | destino ops (opcional alertas) |

**Nota Zoho:** plan Forever Free a menudo **no** permite SMTP externo; hace falta Mail Lite o superior + IMAP/SMTP activado.

Sin SMTP el sistema sigue vivo: el enlace de verificación solo aparece en **logs** de Render (`mode=log`).

### C.3 Stripe (opcional ahora)

| Variable | Valor |
|----------|--------|
| `STRIPE_SECRET_KEY` | `sk_test_…` (staging) o `sk_live_…` |
| `STRIPE_PRICE_STARTER` | Price ID del plan starter |
| `STRIPE_PRICE_PRO` | Price ID del plan pro |
| `STRIPE_WEBHOOK_SECRET` | `whsec_…` → endpoint `https://metgo-api.onrender.com/api/billing/webhook` |

**Sin Stripe:** el checkout mock **aplica el plan al instante** (útil mientras no hay billing real). Puedes saltar C.3 y seguir.

### C.4 Tras guardar env

En Render: **Manual Deploy** → **Clear build cache & deploy** (recomendado tras cambiar secrets).

Espera a que el health vuelva 200 (~1–3 min en free tier / cold start).

---

## D — Smoke de cierre P0

```powershell
# 1) Readiness S5
(Invoke-RestMethod "https://metgo-api.onrender.com/api/health").s5_ops
# Esperado: pii_kek_configurado=true, email_dev=false
# smtp_configurado=true si configuraste SMTP

# 2) Login demo débil (debe FALLAR si rotaste passwords)
try {
  Invoke-RestMethod -Method POST "https://metgo-api.onrender.com/api/auth/login" `
    -ContentType "application/json" `
    -Body '{"username":"admin","password":"admin123"}'
} catch { $_.Exception.Response.StatusCode.value__ }  # ideal 401

# 3) Planes + reglas
Invoke-RestMethod "https://metgo-api.onrender.com/api/public/planes?sitio=spati&faena=escondida"
Invoke-RestMethod "https://metgo-api.onrender.com/api/public/faenas/escondida/reglas"

# 4) UI
# Abrir: https://metgo-spati.pages.dev/f/escondida/registro
# Completar registro → correo de verify (si SMTP) o mirar logs Render
```

Criterio P0 cerrado:

- [ ] `supabase_error` vacío o sin `faena_reglas`
- [ ] `s5_ops.pii_kek_configurado = true`
- [ ] `s5_ops.email_dev = false`
- [ ] Registro UI no muestra demos; verify funciona (mail o log consciente)

---

## E — GitHub Actions: `CRON_SECRET` (P1 / M9)

### Por qué
El workflow `.github/workflows/spati-alertas-cron.yml` llama cada 20 min a:

`POST https://metgo-api.onrender.com/api/cron/spati/alertas?token=…&forzar=1`

Si el secret no existe o no coincide con Render → el job falla.

### Pasos
1. Render → `metgo-api` → Environment → copiar valor de `CRON_SECRET` (o crearlo: `openssl rand -hex 24`).
2. GitHub → repo `METGO_3D_Quillota_60GB` → **Settings** → **Secrets and variables** → **Actions**.
3. New repository secret:
   - Name: `CRON_SECRET`
   - Value: **exactamente el mismo** que en Render.
4. Actions → workflow **SPATI alertas izaje (M9)** → **Run workflow** (manual).
5. Debe terminar en verde; el JSON de respuesta puede decir `notificado: false` si no hubo subida de nivel (eso es OK).

Mismo secret usan ETL: `.github/workflows/etl-meteo-cron.yml`.

---

## F — Destinos de alerta por faena (P1 / M9 UI)

1. Login en https://metgo-spati.pages.dev (usuario con acceso a la faena).
2. Ir a `/f/escondida/umbrales` (o tu faena).
3. Sección **Destinos de alerta (M9)**:
   - Emails (coma): `ops@…, hse@…`
   - Webhook opcional
   - Nivel mínimo: 2 = naranja
4. **Guardar destinos** (requiere JWT Bearer).
5. Persiste en archivo runtime + `spati_sitios_grua.alertas_destino` si Supabase tiene la fila.

Alternativa API (con token cron o Bearer):

```powershell
# Con CRON_SECRET
Invoke-RestMethod -Method PUT `
  "https://metgo-api.onrender.com/api/public/spati/escondida/umbrales?token=$env:CRON_SECRET" `
  -ContentType "application/json" `
  -Body '{"alertas":{"emails":["ops@escondida.cl"],"nivel_minimo":2}}'
```

---

## G — M8 observado real (P1, cuando tengas CSV)

1. En máquina / Render disk: carpeta CSV, ej. `/var/data/sinca` o path Windows.
2. Archivos: `escondida_rajo.csv`, `paipote.csv`, … columnas `fecha,pm25,pm10,so2,no2,o3`  
   Plantilla: `docs/ejemplos/plantilla_sinca_observado.csv`
3. Render env: `METGO_SINCA_CSV_DIR=/ruta/absoluta`
4. Supabase: `npx supabase db push --yes` (estaciones SPATI) si aún no.
5. Sync:

```powershell
Invoke-RestMethod -Method POST `
  "https://metgo-api.onrender.com/api/cron/faena/sync-estaciones?token=$env:CRON_SECRET"
# Luego sync general / SINCA según OPS_CRON_ETL.md
Invoke-RestMethod `
  "https://metgo-api.onrender.com/api/public/operaciones/faena/escondida/observado-status"
```

Hasta entonces el demo M7 (`demo-observado`) sigue siendo válido para demos.

---

## P2 — Open-Meteo (cuando haya presupuesto / cuenta)

| Variable | Uso |
|----------|-----|
| `METGO_OPENMETEO_API_KEY` | Reduce 429; paquete ambiental / NWP más estables |

Sin key el sistema ya degrada (lastgood / synthetic) y no debería tumbar la UI con 503.

---

## Checklist de sesión (imprimible)

```text
[ ] A  health.s5_ops leído
[ ] B  GRANT faena_reglas ejecutado
[ ] C1 METGO_PII_KEK + METGO_EMAIL_DEV=0
[ ] C2 SMTP (o decisión consciente: solo logs)
[ ] C3 Stripe (o mock OK)
[ ] D  Redeploy + smoke
[ ] E  CRON_SECRET en GitHub = Render
[ ] F  Destinos en /umbrales
[ ] G  M8 CSV (si aplica)
```

---

## Si te trabas

| Síntoma | Revisar |
|---------|---------|
| Health 503 / cold | Esperar wake; reintentar health |
| Registro 500 | Logs Render + `METGO_PII_KEK` + Supabase `usuarios_app` grants |
| Verify sin mail | SMTP o logs `email_notify` |
| Cron Actions rojo | Secret `CRON_SECRET` ausente / distinto |
| Board `/ops` 403 | Usuario con 1 faena trial; usar admin o multi_faena |
| PDF viejo | Esperar deploy API `xhtml2pdf` en Render |

## Fase

**Ops P0/P1** · guía de arranque · DT-auth-sub / M8–M9.
