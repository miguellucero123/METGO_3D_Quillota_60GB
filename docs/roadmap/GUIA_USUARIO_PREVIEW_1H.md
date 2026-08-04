# Usuario preview 1 hora (VENTORA)

Acceso temporal solo a **Ahora** + **Panel técnico**.

## Demo fija — retirada

La cuenta fija `demo@ventora.demo` **ya no se usa** en producción (clave de demostración eliminada).

- Seed al arrancar: **apagado** salvo `METGO_SEED_DEMO_PREVIEW=1` (solo entornos controlados).
- Eliminar en API: `DELETE /api/auth/preview-demo` (auth cron/admin).
- SQL: `supabase/migrations/20260804160000_remove_demo_ventora.sql`

Para demos a clientes, crear un **preview temporal** (clave aleatoria):

## Crear temporal (clave aleatoria)

```http
POST /api/auth/preview-hora
Content-Type: application/json
X-Cron-Token: <CRON_SECRET>

{ "faena": "quebrada_blanca", "horas": 1, "label": "demo_cliente" }
```

Respuesta `201` con `email` / `password` únicos.

## Expiración y borrado (solo temporales)

`POST /api/cron/identity/purge-preview` elimina orgs preview vencidas.

Override ops (no publicar): `METGO_DEMO_EMAIL`, `METGO_DEMO_PASSWORD`, `METGO_DEMO_FAENA` solo si se re-habilita el seed.
