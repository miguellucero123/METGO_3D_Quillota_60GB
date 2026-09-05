# Ops — Open-Meteo + E12 observados

## Open-Meteo (no martillar)

```text
METGO_OPENMETEO_FETCH_MODE=ciclo
METGO_OPENMETEO_CACHE_TTL=3600
METGO_OPENMETEO_TIMEOUT=8
METGO_OPENMETEO_RETRIES=2
METGO_OPENMETEO_COOLDOWN=120
METGO_CACHE_LASTGOOD_MAX_AGE=172800
```

```powershell
python scripts/ops/check_prod_health_flags.py
```

## E12 DMC / SINCA (Render) — inventario 2026-09-04

Quillota DMC confirmado **`320124`** (no usar 330007).

```text
METGO_DMC_USAR_CANDIDATOS=1
METGO_DMC_IDS={"quillota":"320124","copiapo_centro":"270009","chuquicamata":"220901"}
METGO_SINCA_IDS={"copiapo_centro":"223","paipote":"196","tierra_amarilla":"224"}
# METGO_DMC_CSV_DIR=/opt/render/project/src/data/dmc
# METGO_SINCA_CSV_DIR=/opt/render/project/src/data/sinca
```

JSON completo: `config/meteo/env_ids_recomendados.json`  
Inventario: `config/meteo/INVENTARIO_ESTACIONES_PARTE1.md`

1. Pegar env en Render → redeploy  
2. CSV `{slug}.csv` o export DMC/SINCA  
3. Cron ETL `sincronizar_oficiales` + `sincronizar_sinca`  
4. `GET /api/public/datos/oficiales/estado` y health `e12_ops`
