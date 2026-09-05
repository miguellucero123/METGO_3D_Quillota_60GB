# Estaciones oficiales — Quillota / valle Aconcagua (E12)

**Actualizado:** 2026-09-04 (inventario parte 1)  
**Inventario nacional:** [`INVENTARIO_ESTACIONES_PARTE1.md`](INVENTARIO_ESTACIONES_PARTE1.md) · [`env_ids_recomendados.json`](env_ids_recomendados.json)

Portales:
- DMC: https://climatologia.meteochile.gob.cl/ (ficha `/application/informacion/fichaDeEstacion/{codigo}`)
- Agromet agregado: https://agrometeorologia.cl/

## Tabla Quillota

| Slug METGO | DMC código | Agromet / otra | Estado | Notas |
|------------|------------|----------------|--------|-------|
| quillota | **`320124`** | — | confirmado | Quillota, Liceo Agrícola · lat -32.90722 lon -71.27139 |
| quillota_fdf | `320100` (ficha también 320096) | FDF vía DMC | confirmado P1 | Fundación Desarrollo Frutícola |
| la_cruz | — | INIA activa, código interno pendiente | pendiente_codigo | Listado agrometeorologia.cl |
| limache | — | — | gap | Histórico boletín; no en listado vivo |
| olmue | — | — | gap | Idem Limache |
| hijuelas | — | — | sin_estacion | Cubrir vía Quillota/La Cruz |
| los_nogales | — | — | sin_estacion | Idem |

## Activación Render (Quillota P0)

```text
METGO_DMC_USAR_CANDIDATOS=1
METGO_DMC_IDS={"quillota":"320124"}
# Opcional secundaria:
# METGO_DMC_IDS={"quillota":"320124","quillota_fdf":"320100"}
METGO_DMC_CSV_DIR=/data/dmc
```

CSV: `{slug}.csv` · fixtures: `tests/fixtures/dmc/`

## Checklist ops

- [x] Código DMC Quillota confirmado (`320124`)  
- [ ] Export CSV diario / token catastro DMC si se automatiza  
- [ ] Códigos INIA La Cruz (contacto / inspección XHR portal)  
- [ ] Cron `sincronizar_oficiales` con CSV poblado  
- [ ] `GET /api/public/datos/oficiales/estado` → `estaciones_con_codigo >= 1`

Código: `backend/05_APIs_Externas/api_rest/oficiales_service.py`
