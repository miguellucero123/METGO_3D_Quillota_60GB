# Ops — Open-Meteo + E12 observados (Quillota)

## Open-Meteo (no martillar)

```text
METGO_OPENMETEO_FETCH_MODE=ciclo
METGO_OPENMETEO_CACHE_TTL=3600
METGO_OPENMETEO_TIMEOUT=8
METGO_OPENMETEO_RETRIES=2
METGO_OPENMETEO_COOLDOWN=120
METGO_CACHE_LASTGOOD_MAX_AGE=172800
```

Descargas productivas: cron ETL 00/12 UTC. Health no debe forzar ping en cada hit.

Verificación:

```powershell
python scripts/ops/check_prod_health_flags.py
```

Esperado con store/caché sano: `status=ok` aunque `openmeteo_live` sea false momentáneamente.

## E12 DMC / Agromet (Render)

1. Confirmar código DMC Quillota en meteochile (`330007` candidato).  
2. En Render Environment:

```text
METGO_DMC_USAR_CANDIDATOS=1
METGO_DMC_IDS={"quillota":"330007"}
# Cuando tengas código INIA:
# METGO_AGROMET_IDS={"quillota":"..."}
# METGO_DMC_CSV_DIR=/opt/render/project/src/data/dmc
# METGO_AGROMET_CSV_DIR=/opt/render/project/src/data/agromet
```

3. Colocar CSV `{slug}.csv` o conectar export.  
4. Disparar sync (cron ETL ya llama `sincronizar_oficiales` o endpoint internos con `CRON_SECRET`).  
5. `GET /api/public/datos/oficiales/estado`

Detalle estaciones: `config/meteo/ESTACIONES_OFICIALES_QUILLOTA.md`  
Política: `config/meteo/POLITICA_FUENTES.md`
