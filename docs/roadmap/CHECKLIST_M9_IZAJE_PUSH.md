# M9 — Umbrales izaje por faena + alertas push

Umbrales SPATI editables por sitio + cron de transiciones → webhook/email/outbox (Fase 9).

## Endpoints

```http
GET  /api/public/spati/{sitio}/umbrales
PUT  /api/public/spati/{sitio}/umbrales?token=CRON_SECRET
POST /api/cron/spati/alertas?token=CRON_SECRET&sitio=escondida
POST /api/cron/spati/alertas?forzar=1   # todos los sitios
```

## Env Render

| Variable | Uso |
|----------|-----|
| `CRON_SECRET` | Cron alertas |
| `METGO_NOTIFY_EMAIL` / `METGO_SPATI_ALERT_EMAIL` | Destino email |
| `METGO_WEBHOOK_URL` / `METGO_SPATI_ALERT_WEBHOOK` | Push webhook |
| `METGO_SPATI_UMBRALES_JSON` | Override global JSON opcional |

Ejemplo override:

```json
{"escondida":{"rojo_min_kmh":40,"verde_max_kmh":28}}
```

## Supabase

Migración `20260728240000_spati_umbrales_alertas.sql`:
- `spati_sitios_grua.umbrales_json` / `alertas_destino`
- `spati_alert_state`

```powershell
npx supabase db push --yes
```

## Cron sugerido (cada 15–30 min)

```text
POST https://metgo-api.onrender.com/api/cron/spati/alertas?token=…
```

Notifica solo si el nivel **sube** y ≥ `nivel_minimo` (default 2 = naranja).

## UI

SPATI → `/umbrales` lee umbrales del API por sitio.

## Criterio de cierre

- [x] Umbrales parametrizables por sitio
- [x] Cron alertas + outbox/email/webhook
- [x] Tests M9
- [x] Cron programado (GitHub Actions `spati-alertas-cron.yml` cada 20 min)
- [ ] Destinos por faena en Supabase (`alertas_destino`)
- [ ] Secret `CRON_SECRET` verificado en GitHub Actions (mismo que Render)

## Fase

**M9** · minería / izaje.
