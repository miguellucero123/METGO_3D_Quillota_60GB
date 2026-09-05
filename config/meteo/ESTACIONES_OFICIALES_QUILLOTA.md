# Estaciones oficiales — Quillota / valle Aconcagua (E12)

**Objetivo:** mapear slugs METGO ↔ códigos DMC (MeteoChile) / Agromet (INIA).  
**Estado:** borrador operativo 2026-09-04. Confirmar en portales antes de producción.

Portales:
- DMC: https://www.meteochile.gob.cl/
- Agromet: https://agromet.inia.cl/

## Tabla Quillota

| Slug METGO | DMC código | Agromet código | Estado | Notas |
|------------|------------|----------------|--------|-------|
| quillota | `330007` (candidato) | *pendiente portal* | dmc_candidato | Activar con `METGO_DMC_USAR_CANDIDATOS=1` o `METGO_DMC_IDS` |
| limache | *pendiente* | *pendiente* | pendiente_registro | Revisar red sinóptica / Agromet Limache |
| olmue | *pendiente* | *pendiente* | pendiente_registro | |
| hijuelas | *pendiente* | *pendiente* | pendiente_registro | |
| los_nogales | *pendiente* | *pendiente* | pendiente_registro | |

## Activación Render (ejemplo)

```text
METGO_DMC_USAR_CANDIDATOS=1
METGO_DMC_IDS={"quillota":"330007"}
METGO_AGROMET_IDS={"quillota":"CODIGO_INIA"}
METGO_DMC_CSV_DIR=/data/dmc
METGO_AGROMET_CSV_DIR=/data/agromet
```

CSV esperado por slug: `{slug}.csv` con columnas `fecha,temperatura_max,temperatura_min,...`  
Fixtures de desarrollo: `tests/fixtures/dmc/`, `tests/fixtures/agromet/`.

## Checklist ops

- [ ] Confirmar `330007` vigente en MeteoChile para Quillota  
- [ ] Obtener códigos Agromet Quillota / La Cruz  
- [ ] Export diario CSV o API → directorio en Render / worker ETL  
- [ ] `GET /api/public/datos/oficiales/estado` → `dmc.estaciones_con_codigo >= 1`  
- [ ] Cron ETL incluye `sincronizar_oficiales`

Código: `backend/05_APIs_Externas/api_rest/oficiales_service.py`
