# E12 — Datos oficiales + ML por dominio

## E12.1 (2026-08-01) — CSV ejemplos usable sin env

Sin `METGO_SINCA_CSV_DIR` / `METGO_*_CSV_DIR`, la API usa por defecto:

| Fuente | Ruta fallback | Desactivar |
|--------|---------------|------------|
| SINCA / AWS faena | `docs/ejemplos/sinca_csv/` | `METGO_SINCA_USE_EJEMPLOS=0` |
| DMC | `docs/ejemplos/dmc_csv/` | `METGO_DMC_USE_EJEMPLOS=0` |
| Agromet | `docs/ejemplos/agromet_csv/` | `METGO_AGROMET_USE_EJEMPLOS=0` |

Incluye CSV demo: `escondida_rajo`, `quebrada_blanca_rajo`, Copiapó/Paipote/TA, `mb_rajo`, DMC/Agromet Quillota.

Health: `(Invoke-RestMethod …/api/health).e12_ops`

```powershell
python -m pytest tests/test_mineria_multi_faena.py -q -k e12
# Sync local (usa ejemplos):
# POST /api/cron/sync → sincronizar_sinca
```

## Ya hecho (E12 MVP previo)

- Catálogo SINCA + sesgo CAMS, Agromet/DMC pipeline, ML dominio (PM10/helada/viento), CB SINCA

## Pendiente ops (prod)

- [ ] `METGO_SINCA_IDS` reales Atacama + CSV diario en disco Render (`METGO_SINCA_CSV_DIR` = `env`)
- [ ] `METGO_AGROMET_IDS` / `METGO_DMC_IDS` (o `METGO_DMC_USAR_CANDIDATOS=1` tras confirmar 330007)
- [ ] Reentrenar helada/PM10 con histórico oficial largo

## Fase

**E12.1** · datos oficiales (fallback ejemplos + health)
