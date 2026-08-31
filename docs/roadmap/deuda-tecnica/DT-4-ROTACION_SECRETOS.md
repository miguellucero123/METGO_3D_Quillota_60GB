# DT-4 — Rotación de secretos (ops)

Tras exposición posible en git (historial o hardcodes), rotar en estos paneles. No guardar valores nuevos en el repo.

## Render (API `metgo-api`)

| Variable | Acción |
|----------|--------|
| `METGO_JWT_SECRET` / `JWT_SECRET_KEY` | Generar nuevo (`secrets.token_urlsafe(48)`), redesplegar |
| `METGO_PASSWORD_*` (admin, sitios) | Cambiar break-glass ops |
| `CRON_SECRET` | Regenerar si se usó en scripts |
| `METGO_SMTP_PASSWORD` | Rotar en proveedor SMTP |
| `STRIPE_SECRET_KEY` / webhook | Rotar en Stripe Dashboard si estuvo en algún commit |
| `METGO_TURNSTILE_SECRET` | Rotar en Cloudflare Turnstile |
| `METGO_PII_KEK` | Rotar si existe (implica re-cifrado PII) |

## WordPress (`metgo3d.com`)

| Variable local | Acción |
|----------------|--------|
| `WP_APP_PASSWORD` en `.env` | Revocar Application Password en WP y crear una nueva; nunca commit |

## Postgres / Redis

Si se usaron passwords tipo `metgo3d_2024_secure` / `metgo_secure_2025` en algún entorno real: cambiar password y actualizar env del host.

## Cloudflare Pages

Revisar tokens de deploy/API; rotar si alguna vez estuvieron en el repo (auditoría no los encontró trackeados).

## Comprobar que `.env` raíz no esté en historial

```powershell
git log --all --full-history -- .env
```

Si aparece algún commit con secretos reales, proceder a purga de historial (`git filter-repo`) y **force-push solo con OK explícito**.

## Tras rotar

1. Redeploy API en Render
2. Probar login break-glass y un flujo JWT
3. Actualizar `.env` local del desarrollador (fuera de git) y el vault:
   `local/METGO_VAULT.local.env` → `python scripts/ops/vault_crypto.py pack`
   Guía otro PC: [`docs/ops/BOOTSTRAP_OTRO_PC.md`](../../ops/BOOTSTRAP_OTRO_PC.md)
