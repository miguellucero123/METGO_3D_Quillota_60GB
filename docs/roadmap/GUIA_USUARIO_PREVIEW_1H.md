# Usuario preview 1 hora (VENTORA)

Acceso temporal solo a **Ahora** + **Panel técnico**. Caduca a la hora y se puede purgar.

## Crear

```http
POST /api/auth/preview-hora
Content-Type: application/json
X-Cron-Token: <CRON_SECRET>
# o Authorization: Bearer <jwt_admin>
# o METGO_ALLOW_PREVIEW=1 en local

{ "faena": "quebrada_blanca", "horas": 1, "label": "demo_cliente" }
```

Respuesta `201`:

```json
{
  "email": "preview.quebrada_blanca....@ventora.demo",
  "password": "Vp!……",
  "faena": "quebrada_blanca",
  "tabs": ["ahora", "panel"],
  "expires_at": "…",
  "login_url": "https://metgo-spati.pages.dev/login?faena=quebrada_blanca"
}
```

## Login SPA

1. Abrir `login_url` (o `/login`).
2. Usuario = `email`, contraseña = `password`.
3. Entra a `/f/{faena}/ahora`. No ve Ambiente, Dron, Umbrales ni Informes.

## Expiración y borrado

- Tras `expires_at`, el login responde **403** `subscription_expired`.
- Purga orgs vencidas:

```http
POST /api/cron/identity/purge-preview
X-Cron-Token: <CRON_SECRET>
```

Programar en Render Cron (p. ej. cada hora).

## Fase

**2.x / S1 identidad** · plan `preview` oculto del catálogo comercial.
