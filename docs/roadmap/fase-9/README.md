# Fase 9 — Notificaciones multicanal (sin obligar SMTP Zoho)

## Objetivo

Enviar alertas y pruebas por **webhook** y/o **email**, con **outbox local** cuando SMTP no está configurado. Las alertas `warning`/`critical` del módulo 01 se notifican al registrarse en historial.

## Canales

| Canal | Cuándo |
|-------|--------|
| Webhook | `webhook_url` en config o `METGO_WEBHOOK_URL` |
| SMTP | `METGO_SMTP_*` en `.env` |
| Outbox | Siempre como respaldo (`notificaciones_outbox.jsonl`) |

## API

| Método | Ruta | Auth |
|--------|------|------|
| GET | `/api/notificaciones/status` | JWT |
| GET | `/api/notificaciones/outbox` | JWT |
| POST | `/api/notificaciones/outbox/retry` | admin |
| POST | `/api/notificaciones/probar` | JWT (existente) |

## Script cron (cuando active SMTP)

```powershell
python backend\08_Gestion_Datos\scripts\run_notificaciones_outbox_retry.py
```

## Vue

`/alertas/config` — estado de canales, outbox, reintentar, alertas automáticas.

## Verificación

```powershell
python -m pytest tests/test_fase9.py tests/test_notificaciones.py -q
```

## Siguiente incremento

- **Fase 10** (integrada): métricas, MQTT TLS, ML profundo — ver [`fase-10/README.md`](../fase-10/README.md).
- **Escalamiento:** [`PROMPT_ESCALAMIENTO_MVP.md`](../../PROMPT_ESCALAMIENTO_MVP.md).
