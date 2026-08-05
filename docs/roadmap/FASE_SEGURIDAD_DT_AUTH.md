# Fase seguridad — DT-auth-sec (acceso, BD, consentimientos, anti-abuso)

> Corte: 2026-08-05 · Complementa [`CHECKLIST_AUTH_PROD.md`](CHECKLIST_AUTH_PROD.md) y [`ADR_KYC_IDENTIDAD.md`](ADR_KYC_IDENTIDAD.md).

## Objetivo

Reducir abuso de registro/login, blindar tablas identity y endurecer headers/endpoints públicos.

## Estado

| Control | Estado | Notas |
|---------|--------|--------|
| Rate limit login/register/validate/reenviar | ✅ código | In-memory; `METGO_RATE_LIMIT_ENABLED=1` |
| Cloudflare Turnstile | ✅ código (opcional) | Widget en SPATI, Mantos, Copiapó, Quillota; activo si secret + site key |
| Verify-email obligatorio | ✅ código | `METGO_REQUIRE_EMAIL_VERIFY=1` |
| Headers API (nosniff, frame, referrer) | ✅ | `app.after_request` |
| CSP + headers SPAs CF Pages | ✅ | `frontend/*/public/_headers` |
| RLS identity (deny anon) | ✅ migración | `20260805180000_identity_rls_deny_anon.sql` — **aplicar en Supabase** |
| ETL retry-queue con CRON | ✅ | Ya no es público sin token |
| KYC manual (ADR A) | ✅ código | `orgs.kyc_status` + `POST /api/auth/ops/kyc`; gate `METGO_KYC_GATE_PAID` |
| Sesión idle | ✅ código | `METGO_SESSION_IDLE_S` (0=off); Redis multi-worker ⬜ |
| KEK rotación soft | ✅ código | `METGO_PII_KEK_PREV` para decrypt dual; **no rota `rut_hash`** |

## Variables Render (nuevas)

| Variable | Uso |
|----------|-----|
| `METGO_RATE_LIMIT_ENABLED` | `1` (default) |
| `METGO_TURNSTILE_SECRET` | Secret del widget Cloudflare Turnstile |
| `METGO_TURNSTILE_SITE_KEY` | Site key (también en Pages `VITE_TURNSTILE_SITE_KEY`) |
| `METGO_TURNSTILE_REQUIRED` | `1` fuerza captcha; vacío = auto en `production`/`RENDER` |
| `METGO_REQUIRE_EMAIL_VERIFY` | `1` (default) |
| `METGO_KYC_GATE_PAID` | `1` bloquea planes de pago sin KYC verified (default off) |
| `METGO_SESSION_IDLE_S` | Segundos idle → 401 `session_replaced` (0=off) |
| `METGO_PII_KEK_PREV` | KEK anterior durante rotación (solo decrypt) |

## Pasos ops (humano)

1. **Supabase:** `supabase db push` (RLS + `orgs_kyc_status`).
2. **Cloudflare Turnstile:** crear widget → pegar secret/site key en Render + Pages.
3. **Redeploy API** Render + SPAs Pages.
4. Smoke: registro sin captcha (si required) → 400 `captcha_failed`; flood login → 429.
5. Verify-email E2E (mail real).
6. KYC: marcar verified vía `/api/auth/ops/kyc`; activar gate solo al cobrar.

## Tests

```powershell
# Desde la raíz del repo (pytest.ini ya agrega backend/05_APIs_Externas al path)
pytest tests/test_security_hardening.py tests/test_identity_s1.py tests/test_kyc_p2.py -q
```


## Fase

**DT-auth-sec** ✅ · **P2 KYC/sesión/KEK** ✅ código (Redis ⬜) · **Ops** 🔶
