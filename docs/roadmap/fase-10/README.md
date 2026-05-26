# Fase 10 — Observabilidad Prometheus, MQTT TLS, ML profundo

## Objetivo

Exponer métricas para monitoreo externo, soportar **MQTT sobre TLS** y permitir **entrenamiento profundo** vía subprocess (scripts módulo 06) sin bloquear la API.

## Componentes

| Componente | Ubicación |
|------------|-----------|
| Métricas | `integracion/prometheus_metrics.py` |
| ML profundo | `integracion/ml_train_deep.py`, `run_ml_train_deep.py` |
| MQTT TLS | `mqtt_bridge.py`, `mqtt_listener_core.py` |
| Rutas | `fase10_routes.py` |

## API

| Método | Ruta | Auth |
|--------|------|------|
| GET | `/api/metrics` | Público (si `METGO_METRICS_PUBLIC=1`) |
| GET | `/api/metrics/json` | JWT |
| GET | `/api/ml/train/deep/status` | JWT |
| POST | `/api/ml/train/deep` | admin |

## Verificación

```powershell
python -m pytest tests/test_fase10.py -q
curl http://127.0.0.1:8080/api/metrics
```

## Documento de escalamiento

Ver **`docs/PROMPT_ESCALAMIENTO_MVP.md`** — prompt maestro post-fases 1–10.
