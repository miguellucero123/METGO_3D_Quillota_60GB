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
| KYC / KMS / sesión Redis | ⬜ P2 | ADR KYC; KEK rotación |

## Variables Render (nuevas)

| Variable | Uso |
|----------|-----|
| `METGO_RATE_LIMIT_ENABLED` | `1` (default) |
| `METGO_TURNSTILE_SECRET` | Secret del widget Cloudflare Turnstile |
| `METGO_TURNSTILE_SITE_KEY` | Site key (también en Pages `VITE_TURNSTILE_SITE_KEY`) |
| `METGO_TURNSTILE_REQUIRED` | `1` fuerza captcha; vacío = auto en `production`/`RENDER` |
| `METGO_REQUIRE_EMAIL_VERIFY` | `1` (default) |

## Pasos ops (humano)

1. **Supabase:** `supabase db push` (o aplicar migración RLS).
2. **Cloudflare Turnstile:** crear widget → pegar secret/site key en Render + Pages.
3. **Redeploy API** Render + SPAs Pages.
4. Smoke: registro sin captcha (si required) → 400 `captcha_failed`; flood login → 429.
5. Verify-email E2E (mail real).

## Tests

```powershell
# Desde la raíz del repo (pytest.ini ya agrega backend/05_APIs_Externas al path)
pytest tests/test_security_hardening.py tests/test_identity_s1.py -q
```


## Fase

**DT-auth-sec / Ops P0–P1**
