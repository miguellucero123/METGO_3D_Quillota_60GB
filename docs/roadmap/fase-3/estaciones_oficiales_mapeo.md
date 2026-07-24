# Mapeo estaciones METGO ↔ fuentes históricas

> Etapa E / **E12**. Fuente programática inmediata: **OpenMeteo Archive** (ERA5).
> Observación oficial: Agromet / DMC / SINCA vía env + CSV (sin inventar series).

| Slug METGO | Nombre OpenMeteo | Lat | Lon | Fuente inmediata | Fuente oficial |
|------------|------------------|-----|-----|------------------|----------------|
| `quillota` | Quillota | -32.8833 | -71.25 | `openmeteo_archive` | DMC candidato `330007` · Agromet (código portal) |
| `los_nogales` | Los Nogales | -32.9333 | -71.2167 | `openmeteo_archive` | Agromet cercana (pendiente) |
| `hijuelas` | Hijuelas | -32.8000 | -71.1333 | `openmeteo_archive` | Agromet (pendiente) |
| `limache` | Limache | -33.0167 | -71.2667 | `openmeteo_archive` | DMC / Agromet (pendiente) |
| `olmue` | Olmue | -33.0000 | -71.2167 | `openmeteo_archive` | DMC / Agromet (pendiente) |

## Activación E12 (env)

```bash
# DMC Quillota — confirma código en meteochile, luego:
export METGO_DMC_IDS='{"quillota":"330007"}'
# o candidatos documentados:
export METGO_DMC_USAR_CANDIDATOS=1
export METGO_DMC_CSV_DIR=/data/dmc   # quillota.csv

# Agromet INIA — código del portal agromet.inia.cl:
export METGO_AGROMET_IDS='{"quillota":"CODIGO_PORTAL"}'
export METGO_AGROMET_CSV_DIR=/data/agromet

# SINCA Copiapó:
export METGO_SINCA_IDS='{"copiapo_centro":"ID_PORTAL","paipote":"…"}'
export METGO_SINCA_CSV_DIR=/data/sinca
```

CSV meteo: `fecha,temperatura_max,temperatura_min,humedad,precipitacion,viento,presion`  
CSV SINCA: `fecha,pm25,pm10,so2,no2,o3`

Endpoints: `GET /api/public/datos/oficiales/estado` · cron escribe `oficiales` + `sinca`.

## Persistencia

- ETL Archive: `backend/08_Gestion_Datos/scripts/etl_archive_openmeteo.py`
- Oficiales: `api_rest.oficiales_service.sincronizar_oficiales` → `meteo_registros` (`fuente=agromet|dmc`)
- SINCA: `api_rest.sinca_service` → `aire_registros` (`fuente=sinca`, `tipo_dato=observado`)

## Notas

- ERA5 (~9 km) no sustituye observación in situ.
- Código DMC `330007` es **candidato documentado**; no activar en prod sin confirmar portal.
- Implementación: `backend/05_APIs_Externas/api_rest/oficiales_service.py`
