# Mapeo estaciones METGO ↔ fuentes históricas

> Etapa E — históricos largos. Fuente programática inmediata: **OpenMeteo Archive** (reanálisis ERA5 por coordenadas). Fuentes de estación física (Agromet, DMC): pendiente registro y ETL dedicado.

| Slug METGO | Nombre OpenMeteo | Lat | Lon | Fuente inmediata | Fuente oficial futura |
|------------|------------------|-----|-----|------------------|------------------------|
| `quillota` | Quillota | -32.8833 | -71.25 | `openmeteo_archive` | Agromet / DMC Quillota (pendiente registro) |
| `los_nogales` | Los Nogales | -32.9333 | -71.2167 | `openmeteo_archive` | Agromet cercana (pendiente mapeo código) |
| `hijuelas` | Hijuelas | -32.8000 | -71.1333 | `openmeteo_archive` | Agromet Hijuelas/La Cruz (pendiente registro) |
| `limache` | Limache | -33.0167 | -71.2667 | `openmeteo_archive` | DMC / Agromet (pendiente registro) |
| `olmue` | Olmue | -33.0000 | -71.2167 | `openmeteo_archive` | DMC / Agromet (pendiente registro) |

## Persistencia

- ETL CLI: `backend/08_Gestion_Datos/scripts/etl_archive_openmeteo.py`
- API: `POST /api/datos/etl/sync` con `{ "incluir_archive": true, "anios_archive": 5 }`
- Columna `fuente` en `meteo_registros`: `openmeteo_archive`

## Notas

- Las coordenadas coinciden con `OpenMeteoData.estaciones` en `datos_reales_openmeteo.py`.
- ERA5 es reanálisis de cuadrícula (~9 km); no sustituye observación in situ hasta integrar Agromet/DMC.
