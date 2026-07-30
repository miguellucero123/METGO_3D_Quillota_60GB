# Checklist auth producción (DT-auth + identity S1–S3)

Endurecimiento JWT Flask + registro comercial multi-faena — sin nuevo proyecto Supabase Auth ni SSO WordPress.

## Render (`metgo-api`)

| Variable | Valor |
|----------|--------|
| `METGO_ENV` | `production` (o confiar en `RENDER=true`) |
| `METGO_JWT_SECRET` | secreto largo aleatorio (**obligatorio**) |
| `METGO_PII_KEK` | secreto distinto al JWT para cifrar PII (**obligatorio** en prod) |
| `METGO_IDENTITY_STORE` | `supabase` (omitir solo en tests `memory`) |
| `METGO_ALLOW_SELF_REGISTER` | `0` (legacy JSON; usar `register-v2`) |
| `METGO_EMAIL_DEV` | `0` en prod (no devolver `verify_token` en JSON) |
| `METGO_API_AUTH_REQUIRED` | `1` |
| `METGO_SPATI_PUBLIC_URL` | `https://metgo-spati.pages.dev` |
| `METGO_PASSWORD_ADMIN` | fuerte, rotada (break-glass) |
| `METGO_PASSWORD_COPIAPO` / `_MANTOS` / `_PAINE` | opcionales hasta migrar 100% a `usuarios_app` |
| `METGO_CORS_ORIGINS` | `*.pages.dev` + dominios propios (incluye `metgo-spati.pages.dev`) |

### SMTP (verify-email)

| Variable | Valor |
|----------|--------|
| `METGO_SMTP_HOST` | smtp.ejemplo.com |
| `METGO_SMTP_PORT` | `587` |
| `METGO_SMTP_USER` / `METGO_SMTP_PASSWORD` | credenciales |
| `METGO_SMTP_FROM` | `noreply@metgo.cl` |
| `METGO_SMTP_TLS` | `1` |

Sin SMTP → el API solo registra el enlace en logs (`mode=log`).

### Stripe (opcional S3)

| Variable | Valor |
|----------|--------|
| `STRIPE_SECRET_KEY` | `sk_live_…` o `sk_test_…` |
| `STRIPE_PRICE_STARTER` / `_PRO` | Price IDs |
| `STRIPE_WEBHOOK_SECRET` | firma webhook → `POST /api/billing/webhook` |

Sin Stripe → checkout **mock** aplica el plan al instante (útil en staging).

Tras cambiar env: **Manual Deploy → Clear build cache & deploy**.

## Cloudflare Pages (SPAs)

- SPATI: hub `/` y faenas `/f/{faena}/registro|login|cuenta`.
- Redeploy tras cambios de auth/UI.
- Quillota: **no** `VITE_ALLOW_SELF_REGISTER=1` en prod.

## Smoke

```powershell
# Legacy demo (debe fallar si rotó passwords)
Invoke-RestMethod -Method POST https://metgo-api.onrender.com/api/auth/login `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"admin123"}'

# Planes públicos
Invoke-RestMethod "https://metgo-api.onrender.com/api/public/planes?sitio=spati&faena=escondida"

# Reglas faena
Invoke-RestMethod "https://metgo-api.onrender.com/api/public/faenas/escondida/reglas"

# S5 readiness (booleans, sin secretos)
(Invoke-RestMethod "https://metgo-api.onrender.com/api/health").s5_ops

# M10 board (JWT admin / multi_faena)
# Invoke-RestMethod https://metgo-api.onrender.com/api/auth/ops-board -Headers @{Authorization="Bearer …"}
```

UI SPATI: https://metgo-spati.pages.dev/ops (board) · `/f/escondida/registro` — sin demos en pantalla.

## WordPress / Supabase

- **No** segundo proyecto Supabase para Auth.
- Supabase = datos (`usuarios_app`, `suscripciones`, `faena_reglas`).
- WordPress = marketing que **enlaza** a cada `/f/{faena}/`.

## Local

Demos: [`docs/DESARROLLO_LOCAL.md`](../DESARROLLO_LOCAL.md).  
Plan: [`PLAN_REGISTRO_SUSCRIPCION_MULTISITIO.md`](PLAN_REGISTRO_SUSCRIPCION_MULTISITIO.md).

## Fase

DT-auth-sub / S4 entitlements UI (S3 SMTP/Stripe keys en Render cuando haya credenciales reales).
