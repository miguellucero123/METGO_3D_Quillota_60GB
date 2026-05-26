# Fase 7 — MQTT IoT y cola ML (sin correo SMTP)

## Objetivo

Conectar el módulo **03 IoT** con ingesta tipo MQTT sin depender de un broker en la API, y ofrecer una **cola ligera** para re-sincronizar el registro MLOps (módulo **06**) de forma asíncrona vía cron o botón admin.

**Correo SMTP (Zoho):** diferido — ver `.env.example` y Fase 6.

## Componentes

| Componente | Ubicación |
|------------|-----------|
| Adaptador MQTT | `api_rest/integracion/mqtt_bridge.py` |
| Cola ML | `api_rest/integracion/ml_training_queue.py` |
| Rutas API | `api_rest/fase7_routes.py` |
| Inbox JSON | `backend/08_Gestion_Datos/datos_runtime/mqtt_inbox/` |
| Cola JSON | `backend/08_Gestion_Datos/datos_runtime/ml_training_queue.json` |

## API

| Método | Ruta | Auth |
|--------|------|------|
| GET | `/api/iot/mqtt/status` | Público |
| POST | `/api/iot/mqtt/ingestar` | JWT |
| POST | `/api/iot/mqtt/inbox/procesar` | admin / operador |
| GET | `/api/ml/train/status` | JWT |
| POST | `/api/ml/train/queue` | JWT |
| POST | `/api/ml/train/run-next` | admin |

## Variables de entorno

Ver `.env.example` — `METGO_MQTT_*` (opcional; MVP funciona sin broker).

## Verificación

```powershell
Set-Location d:\METGO_3D_Quillota_60GB
python -m pytest tests/test_fase7.py -q
```

Reiniciar API tras cambios Python. En Vue: `/iot` (panel MQTT) y `/ml` (cola entrenamiento).

## Siguiente incremento

- **Fase 8** (integrada): workers MQTT/ML + entrenamiento Quillota — ver [`fase-8/README.md`](../fase-8/README.md).
- **Pendiente:** SMTP Zoho / ZeptoMail.
