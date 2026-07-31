# Usuario preview 1 hora (VENTORA)

Acceso temporal solo a **Ahora** + **Panel técnico**.

## Demo fija (recomendada)

| Campo | Valor |
|-------|--------|
| Usuario | `demo@ventora.demo` |
| Clave | `DemoVentora1!` |
| Faena | `quebrada_blanca` |
| Tabs | Ahora, Panel técnico |
| Login | https://metgo-spati.pages.dev/login?faena=quebrada_blanca |

Si el login da 401, ver `docs/roadmap/FIX_LOGIN_DEMO_SUPABASE.md` (faltaban GRANTs en Supabase).

Se crea en SQL (`20260731020000_preview_grants_demo_fijo.sql`) y/o al arrancar la API (`METGO_SEED_DEMO_PREVIEW=1`) o con:

```http
POST /api/auth/preview-demo
X-Cron-Token: <CRON_SECRET>
{ "faena": "quebrada_blanca", "horas": 24 }
```

Override opcional: `METGO_DEMO_PASSWORD`, `METGO_DEMO_EMAIL`, `METGO_DEMO_FAENA`.
No se elimina en `purge-preview`.

## Crear temporal (clave aleatoria)

```http
POST /api/auth/preview-hora
Content-Type: application/json
X-Cron-Token: <CRON_SECRET>

{ "faena": "quebrada_blanca", "horas": 1, "label": "demo_cliente" }
```

Respuesta `201` con `email` / `password` únicos.

## Expiración y borrado (solo temporales)

- Tras `expires_at`, el login responde **403** `subscription_expired`.
- Purga: `POST /api/cron/identity/purge-preview`

## Fase

**2.x / S1 identidad** · plan `preview` + demo fija.
