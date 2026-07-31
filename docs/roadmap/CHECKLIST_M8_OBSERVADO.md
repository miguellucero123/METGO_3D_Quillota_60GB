# M8 — Observado real (SINCA/AWS CSV) + estaciones SPATI

Sin portal MMA: CSV en `METGO_SINCA_CSV_DIR/{slug}.csv` + FK `estaciones`.

## 1. Supabase

- [x] Migración `20260728230000_estaciones_faenas_spati.sql` (84 IDs)
- [x] Aplicada en prod (2026-07-31): `escondida_rajo`, `quebrada_blanca_rajo`, etc. (`ON CONFLICT` upsert)
- [ ] Opcional: `POST /api/cron/faena/sync-estaciones` (re-upsert desde catálogo)

Smoke local:

```powershell
python -m pytest tests/test_mineria_multi_faena.py -q -k m8
```

## 2. CSV observado (AWS / SINCA export)

Plantilla: [`docs/ejemplos/plantilla_sinca_observado.csv`](../ejemplos/plantilla_sinca_observado.csv)

Ejemplos listos para copiar a Render:

- [`docs/ejemplos/sinca_csv/escondida_rajo.csv`](../ejemplos/sinca_csv/escondida_rajo.csv)
- [`docs/ejemplos/sinca_csv/quebrada_blanca_rajo.csv`](../ejemplos/sinca_csv/quebrada_blanca_rajo.csv)

```text
METGO_SINCA_CSV_DIR=/ruta/sinca
# archivos: paipote.csv, mb_rajo.csv, escondida_rajo.csv, …
```

Columnas: `fecha,pm25,pm10,so2,no2,o3`

En Render: montar carpeta o subir CSV y apuntar `METGO_SINCA_CSV_DIR` (ops manual).

## 3. Cron

```http
GET  /api/cron/sync?token=CRON_SECRET
POST /api/cron/faena/sync-estaciones?token=…
POST /api/cron/faena/estaciones-area?token=…
```

`sincronizar_sinca` escribe `aire_registros` (observado) y marca `faena_estaciones_area.fuente=observado`.

## 4. Criterio de cierre

- [x] `escondida_rajo` (y otras faenas) en `public.estaciones`
- [ ] CSV sync → `observado-status` / MVO `ok|parcial` vía **cron SINCA** (no solo demo M7) — requiere `METGO_SINCA_CSV_DIR` en Render
- [x] Documentado en este checklist + ejemplos CSV

## 5. Smoke

```powershell
python -m pytest tests/test_mineria_multi_faena.py -q -k m8
# Prod (tras CSV en Render)
Invoke-RestMethod -Method POST "https://metgo-api.onrender.com/api/cron/faena/sync-estaciones?token=$env:CRON_SECRET"
```

## Fase

**M8** · minería multi-faena · estaciones OK · CSV Render pendiente.
