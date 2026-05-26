# Fase 3 — Integrada (MVP)

| ID | Tarea | Estado |
|----|-------|--------|
| 3.1 | Ingesta IoT (`/api/iot/*`, JSON runtime) | Hecho |
| 3.2 | MLOps (`/api/ml/*`, registro + sanity-check módulo 06) | Hecho |
| 3.3 | Multi-tenant JWT (`tenant` claim, filtro estaciones) | Hecho |
| 3.4 | Observabilidad (logs JSON, `X-Request-ID`, health extendido) | Hecho |
| 3.5 | Streamlit dedicado por dashboard | Pendiente (negocio) |

## Vue

- `/iot` — lecturas y sensores
- `/ml` — catálogo, registro servible/no servible, sincronizar, predicción

## API nueva

- `GET /api/iot/sensores`, `GET /api/iot/lecturas`, `POST /api/iot/simular`
- `GET /api/ml/modelos` (`?solo_servibles=1`), `GET /api/ml/resumen`, `GET /api/ml/prediccion/<variable>`
- `GET /api/ml/registry`, `POST /api/ml/registry/sync` — registro en `backend/08_Gestion_Datos/datos_runtime/ml_registry.json`
- `GET /api/tenants`, `GET /api/tenants/me`

## Variables

- `METGO_SENTRY_DSN` (opcional, futuro SDK)
- `METGO_TENANT_DEFAULT`
