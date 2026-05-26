# Fase 4 — Integrar backend 01–12 con Vue + API

Basado en [`BACKEND_MODULOS_01-12_AUDITORIA.md`](../BACKEND_MODULOS_01-12_AUDITORIA.md).

## Bloques

| Bloque | Fichas | Prioridad |
|--------|--------|-----------|
| **4A** Datos y negocio | 01-historico-bd, 02-agricola-completo, 03-alertas-unificadas, 04-iot-real | Alta |
| **4B** ML y operación | 01-mlops, 02-reportes-api, 03-notificaciones, 04-deprecar-streamlit | Media |
| **4C** Limpieza | DT-1, DT-2, DT-3, README módulos | Continua |

## Estado

**Integración Fase 4 (MVP) implementada** — capa `api_rest/integracion/`.

| Componente | Ruta / archivo |
|------------|----------------|
| Estado integración | `GET /api/integracion/estado` (público) |
| Agrícola avanzado 02 | `GET /api/agricola/{id}/avanzado` |
| Histórico local 08 | `meteo_store.py` + sync en `historico_meteo` |
| Alertas 01+07 | `alertas_store.py` + `GET /api/alertas/historial` |
| IoT 03 | `iot_bridge.py` en `POST /api/iot/simular` |
| ML ampliado 06 | Catálogo `modelos_ml` + quillota |
| Reportes 07 | `GET /api/reportes/ultimos` |
| Vue | `/estado` muestra % por módulo |

## Fase 5 (conexiones Vue)

Ver [`fase-5/README.md`](../fase-5/README.md) — hub `/integracion` y vistas enlazadas a endpoints 4A–4B.

## Próximo sprint (producción)

1. Job ETL nocturno (cron) 08.  
2. Email/SMS real alertas 07.  
3. Cola entrenamiento ML 06.  
4. MQTT IoT 03.
