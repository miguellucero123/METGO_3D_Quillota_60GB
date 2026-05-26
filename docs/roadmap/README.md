# Roadmap de implementación METGO 3D

Estructura para ejecutar el [prompt MVP](../PROMPT_MVP_METGO.md) y el rol en **`AGENTS.md`**.

## Carpetas

| Carpeta | Contenido |
|---------|-----------|
| [`fase-1/`](fase-1/) | Consolidar MVP (semanas 1–6) — **prioridad alta** |
| [`fase-2/`](fase-2/) | Producto ampliado (semanas 7–12) |
| [`fase-3/`](fase-3/) | Escala y datos propios (meses 3–6) — **integrada (MVP)** |
| [`fase-4/`](fase-4/) | **Integrar módulos backend 01–12** con Vue + API |
| [`fase-5/`](fase-5/) | **Conexiones Vue ↔ API** (hub `/integracion`) |
| [`fase-6/`](fase-6/) | **ETL nocturno** (cron + métricas) |
| [`fase-7/`](fase-7/) | **MQTT IoT** + **cola ML** (sin SMTP) |
| [`fase-8/`](fase-8/) | **Workers** MQTT/ML + **entrenamiento real** |
| [`fase-9/`](fase-9/) | **Notificaciones** webhook + outbox + SMTP opcional |
| [`fase-10/`](fase-10/) | **Prometheus**, MQTT TLS, ML profundo |
| [`PROMPT_ESCALAMIENTO_MVP.md`](../PROMPT_ESCALAMIENTO_MVP.md) | **Prompt maestro escalamiento** post-fases 1–10 |
| [`BACKEND_MODULOS_01-12_AUDITORIA.md`](BACKEND_MODULOS_01-12_AUDITORIA.md) | **Auditoría exhaustiva** por carpeta |
| [`deuda-tecnica/`](deuda-tecnica/) | Tareas transversales (DT-1 … DT-3) |

## Estado de integración en código

| Tarea | Estado | Ubicación en repo |
|-------|--------|-------------------|
| 1.1 OpenAPI + Swagger | Integrado | `api_rest/openapi.yaml`, `api_rest/docs_routes.py` |
| 1.2 CI GitHub Actions | Integrado | `.github/workflows/ci.yml` |
| 1.3 Health dashboard | Integrado | `api_rest/health.py`, `frontend/vue/.../EstadoView.vue` |
| 1.4 Caché OpenMeteo | Integrado | `backend/08_Gestion_Datos/cache_openmeteo.py` |
| 1.5 UX puertos | Integrado | `PuertosView.vue`, `QUE_VER_EN_NUBE.md` |
| 2.x – 3.x | Integrado (MVP) | Ver `fase-2/README.md`, `fase-3/README.md` |
| 4.x Integración 01–12 | Integrado (MVP) | `api_rest/integracion/`, `fase-4/README.md` |
| 5.x Conexiones Vue | Integrado | `IntegracionView.vue`, `fase-5/README.md` |
| 6.x ETL nocturno | Integrado | `run_etl_meteo_nightly.py`, `fase-6/README.md` |
| 7.x MQTT + cola ML | Integrado | `mqtt_bridge.py`, `ml_training_queue.py`, `fase-7/README.md` |
| 8.x Workers + train | Integrado | `ml_train_runner.py`, `run_mqtt_listener.py`, `fase-8/README.md` |
| 9.x Notificaciones | Integrado | `notificaciones.py`, `fase-9/README.md` |
| 10.x Métricas / TLS / ML deep | Integrado | `prometheus_metrics.py`, `fase-10/README.md` |

## Cómo trabajar una tarea

1. Abrir la ficha `fase-N/XX-nombre.md`.
2. Seguir **criterio de aceptación** y **verificación**.
3. Responder con el formato de `AGENTS.md` (análisis, archivos, implementación, verificación, fase).
