# Runbook R2 — Rotación de secrets (service_role y afines)

**Objetivo:** que un secret filtrado deje de servir en &lt; 4 h.  
**Nunca** pegar valores reales en Git, tickets públicos ni capturas.

## Inventario crítico (Render / GitHub)

| Secret | Dónde | Impacto si filtra |
|--------|-------|-------------------|
| `SUPABASE_KEY` / service_role / `sb_secret_` | Render | Acceso total DB |
| `METGO_JWT_SECRET` | Render | Forjar sesiones |
| `METGO_PII_KEK` (+ `METGO_PII_KEK_PREV`) | Render | Leer/rotar PII cifrado |
| `CRON_SECRET` | Render + GitHub Actions | Disparar crons |
| `METGO_SMTP_PASSWORD` | Render | Enviar correo como METGO |
| `CLOUDFLARE_API_TOKEN` | GitHub Secrets | Mutar Pages |
| `METGO_TURNSTILE_SECRET` | Render | Bypass anti-bot |
| `STRIPE_SECRET_KEY` / webhook | Render | Cobros |

## Rotación estándar (service_role)

1. Supabase → **Settings → API** → generar nueva service_role (o rotar según UI).  
2. Pegar en Render → Environment → `SUPABASE_KEY` (y alias si existe).  
3. Redeploy / restart servicio API.  
4. Verificar `GET /api/health` → `supabase_client_ok: true`.  
5. Revocar/invalidar clave antigua en Supabase.  
6. Registrar en vault: fecha, quién, motivo (sin valor).

## Rotación JWT

1. Generar secreto largo (≥ 32 bytes random).  
2. Actualizar `METGO_JWT_SECRET` en Render.  
3. Restart → **todas las sesiones caducan** (esperado).  
4. Avisar equipo interno.

## Rotación PII KEK

1. Generar nuevo KEK.  
2. Poner actual en `METGO_PII_KEK_PREV` y nuevo en `METGO_PII_KEK`.  
3. Redeploy; validar health `pii_kek_configurado`.  
4. Planificar re-cifrado batch si el código lo soporta; si no, dual-read con PREV hasta migrar.

## Cloudflare / GitHub

1. Cloudflare → Create Token nuevo (Pages Edit + Account Read).  
2. GitHub → Secrets → `CLOUDFLARE_API_TOKEN`.  
3. Correr workflow Pages security.  
4. Revocar token viejo.

## Criterio R2 continuo

- [ ] Secrets solo en Render/GitHub (no Pages env con secretos, no `VITE_*` secretos)  
- [ ] Tras cualquier sospecha de leak: rotar en ventana 4 h  
- [ ] Al menos 1 revisión trimestral del inventario
