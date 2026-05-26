# Fase 6 — ETL nocturno y operación datos (producción MVP)

## Objetivo

Ejecutar sincronización meteorológica sin depender solo del botón Vue o de una llamada REST manual.

## Componentes

| Componente | Ubicación |
|------------|-----------|
| Lógica ETL | `api_rest/integracion/etl_sync.py` (`sincronizar_estaciones`, métricas JSON) |
| Métricas últimas corridas | `backend/08_Gestion_Datos/datos_runtime/etl_meteo_metrics.json` |
| Script línea de comando | `backend/08_Gestion_Datos/scripts/run_etl_meteo_nightly.py` |
| Programador Windows | `backend/10_Deployment_Produccion/scripts/etl_meteo_nightly.bat` |
| API smoke (público) | `GET /api/datos/etl/status` |
| API sync (JWT) | `POST /api/datos/etl/sync` |

## Variables de entorno

Ver `.env.example` — `METGO_ETL_DIAS_SYNC`, `METGO_ETL_SKIP_CSV`.

## Programación

**Windows (Programador de tareas):** ejecutar el `.bat` diariamente (usuario con Python en PATH y `cd` estable al repo).

**Linux (cron):**

```cron
15 3 * * * cd /ruta/METGO_3D_Quillota_60GB && /usr/bin/python3 backend/08_Gestion_Datos/scripts/run_etl_meteo_nightly.py >> logs/etl_meteo.log 2>&1
```

## Siguiente incremento

- **Fase 7** (integrada): MQTT REST/inbox + cola ML — ver [`fase-7/README.md`](../fase-7/README.md).
- **Pendiente:** SMTP Zoho (`METGO_SMTP_*`) cuando suban plan o usen ZeptoMail.
