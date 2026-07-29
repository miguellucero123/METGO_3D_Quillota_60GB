# Plan minería multi-faena — METGO

> **Estado:** 2026-07-28 · **M1–M7 en código y prod**.  
> Checklist deploy: [`CHECKLIST_M7_DEPLOY.md`](CHECKLIST_M7_DEPLOY.md) · smoke Render PASS · Paipote/Mantos `listo_produccion=true`.

## Visión

Cada minera = una configuración: izaje + aire + meteo + nieve + **CSV/PDF** + estaciones área + modelo vs observado.

## Fases

| Fase | Entrega | Estado |
|------|---------|--------|
| M1–M5 | Catálogo → MVO | ✅ |
| **M6** | Documentos CSV + PDF | ✅ |
| **M7** | Demo observado + status + deploy | ✅ prod |
| **M8** | Observado real SINCA/AWS + estaciones SPATI en `estaciones` | pendiente |

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
