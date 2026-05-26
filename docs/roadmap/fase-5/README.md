# Fase 5 — Conexiones Vue ↔ API (módulos 01–11)

Consolida la capa `api_rest/integracion/` con pantallas Vue operativas.

## Vue

| Ruta | Conexiones API |
|------|----------------|
| `/integracion` | Hub: estado %, ETL, ML registry, reportes, deploy, tests |
| `/estado` | `GET /api/integracion/estado` (público) |
| `/meteo/historico` | `POST /api/datos/etl/sync`, `GET /api/datos/meteo/store` |
| `/agricola` | `/agricola/{id}`, `/riego`, `/economico`, `/cultivos` |
| `/monitoreo` | `/alertas`, `/alertas/historial` |
| `/alertas/config` | `/alertas/config`, `/notificaciones/*` |
| `/iot` | `/iot/*`, `/iot/drones`, `/iot/satelital` |
| `/ml` | `/ml/*`, `/ml/registry/sync` |

## Bloques 4A–4B cubiertos (MVP)

| ID | Estado |
|----|--------|
| 4A.1 ETL histórico | Botón sync + store SQLite |
| 4A.2 Agrícola completo | Riego, cultivos, económico vía API |
| 4A.3 Alertas unificadas | Historial + config + notificaciones |
| 4A.4 IoT | Lecturas + drones + satelital |
| 4B.1 MLOps | Registro + sanity + Vue `/ml` |
| 4B.2 Reportes | Listado en `/integracion` |
| 4B.3 Notificaciones | Config + prueba en alertas |
| 4B.4 Streamlit | Cobertura % en `/integracion` |

## Pendiente producción

Ver [Fase 6 — ETL nocturno](../fase-6/README.md) (implementado).

Seguimiento:

- Email/SMS real (SMTP / Twilio)
- MQTT IoT real
- Re-entrenamiento ML asíncrono
