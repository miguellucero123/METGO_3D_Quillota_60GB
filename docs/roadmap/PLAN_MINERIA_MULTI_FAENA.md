# Plan minería multi-faena — METGO

> **Estado:** 2026-07-28 · **M1–M7 en prod** · **M8 en código**.  
> Checklist deploy: [`CHECKLIST_M7_DEPLOY.md`](CHECKLIST_M7_DEPLOY.md) · M8: [`CHECKLIST_M8_OBSERVADO.md`](CHECKLIST_M8_OBSERVADO.md).

## Visión

Cada minera = una configuración: izaje + aire + meteo + nieve + **CSV/PDF** + estaciones área + modelo vs observado.

## Fases

| Fase | Entrega | Estado |
|------|---------|--------|
| M1–M5 | Catálogo → MVO | ✅ |
| **M6** | Documentos CSV + PDF | ✅ |
| **M7** | Demo observado + status + deploy | ✅ prod |
| **M8** | Observado SINCA/CSV + `estaciones` SPATI (FK) | ✅ código |
| **M9** | Umbrales izaje por faena + alertas push | ✅ código |
| **M10** | Dashboard unificado ops multi-faena (Vue) | ✅ código (MVP) |

## M10 (resumen)

Board operativo para admin / `multi_faena` / ≥2 faenas:

```http
GET /api/auth/ops-board
GET /api/auth/ops-board?refresh=1
```

SPA: `/ops` · enlace desde hub y sidebar.

- Filas: nivel global, izaje/caminos/botaderos, ráfaga, MVO lite.
- Preferencia **lastgood**; `refresh=1` regenera live (tope `METGO_OPS_BOARD_LIVE`).

## M9 (resumen)

```http
GET  /api/public/spati/{sitio}/umbrales
POST /api/cron/spati/alertas?sitio=escondida
```

Checklist: [`CHECKLIST_M9_IZAJE_PUSH.md`](CHECKLIST_M9_IZAJE_PUSH.md)
## M8 (resumen)

```http
POST /api/cron/faena/sync-estaciones
GET  /api/cron/sync   # sincronizar_sinca + estaciones_publicas
```

CSV: `METGO_SINCA_CSV_DIR/{slug}.csv` (slugs rajo: `paipote`, `mb_rajo`, `escondida_rajo`, …).

## Documentos

```http
GET …/informe?formato=csv|pdf
GET …/modelo-vs-observado?formato=csv
GET …/observado-status
POST …/cron/faena/demo-observado?faena=paipote
```

## Verificación

```powershell
python -m pytest tests/test_mineria_multi_faena.py -q
# Demo (API local sin CRON_SECRET o con token)
Invoke-RestMethod -Method POST "http://127.0.0.1:8080/api/cron/faena/demo-observado?faena=paipote"
Invoke-RestMethod "http://127.0.0.1:8080/api/public/operaciones/faena/paipote/observado-status"
```
