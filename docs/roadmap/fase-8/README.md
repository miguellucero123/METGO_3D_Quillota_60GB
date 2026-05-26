# Fase 8 — Workers MQTT/ML y entrenamiento real (sin SMTP)

## Objetivo

Ejecutar **MQTT** y **cola ML** en procesos separados de Gunicorn/Flask, y permitir **entrenamiento ligero** de modelos Quillota con datos SQLite o sintéticos.

**Correo:** sigue diferido (Fase 6–7).

## Componentes

| Componente | Ubicación |
|------------|-----------|
| Entrenamiento Quillota | `integracion/ml_train_runner.py` |
| Listener MQTT | `integracion/mqtt_listener_core.py` |
| Heartbeats workers | `integracion/workers_status.py` |
| Rutas API | `fase8_routes.py` |
| Script MQTT | `08_Gestion_Datos/scripts/run_mqtt_listener.py` |
| Script cola ML | `08_Gestion_Datos/scripts/run_ml_training_worker.py` |
| `.bat` Windows | `10_Deployment_Produccion/scripts/mqtt_listener.bat`, `ml_training_worker.bat` |

## API nueva

| Método | Ruta | Auth |
|--------|------|------|
| GET | `/api/workers/status` | Público |
| POST | `/api/ml/train/run` | admin — entrenar ahora |
| POST | `/api/ml/train/process-queue` | admin — vaciar cola (max 10) |

Cola Fase 7 ampliada: `POST /api/ml/train/queue` acepta `"modo": "sync"` \| `"train"`.

## Workers (cron / Task Scheduler)

```powershell
# MQTT inbox (sin broker)
python backend\08_Gestion_Datos\scripts\run_mqtt_listener.py --once

# Listener continuo (con broker + paho-mqtt)
backend\10_Deployment_Produccion\scripts\mqtt_listener.bat

# Procesar cola ML encolada desde Vue
backend\10_Deployment_Produccion\scripts\ml_training_worker.bat
```

## Verificación

```powershell
Set-Location d:\METGO_3D_Quillota_60GB
python -m pytest tests/test_fase8.py -q
```

Reiniciar API. Vue: `/ml` (entrenar ahora, workers), `/integracion` (fase 8).

## Siguiente incremento

- **Fase 9** (integrada): notificaciones multicanal — ver [`fase-9/README.md`](../fase-9/README.md).
- **Fase 10 sugerida:** MQTT TLS, Prometheus, entrenamiento profundo.
