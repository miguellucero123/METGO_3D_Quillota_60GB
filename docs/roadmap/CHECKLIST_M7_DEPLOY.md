# M7 — Deploy + observado real (checklist)

Ciclo minería multi-faena: documentos **CSV/PDF** + sesgo modelo vs observado en producción.

## 1. API Render (`metgo-api`)

- [x] Redeploy con código M1–M7 _(smoke 2026-07-28 PASS)_
- [x] Env: `SUPABASE_URL` / `SUPABASE_KEY` (service_role)
- [ ] Env: `CRON_SECRET` verificado en Render (para cron remoto)
- [ ] opcional: `METGO_SINCA_IDS`, `METGO_SINCA_CSV_DIR` o `METGO_SINCA_CSV_URL`
- [ ] CORS incluye orígenes SPATI / Mantos / Paine (`*.pages.dev`)
- [x] Smoke:
  ```http
  GET /api/public/operaciones/faenas
  GET /api/public/operaciones/faena/escondida/informe?formato=csv
  GET /api/public/operaciones/faena/escondida/informe?formato=pdf
  GET /api/public/operaciones/faena/paipote/observado-status
  ```

## 2. Demo observado (staging / sin portal SINCA)

```http
POST /api/cron/faena/demo-observado?token=CRON_SECRET&faena=paipote&dias=7
POST /api/cron/faena/demo-observado?token=CRON_SECRET   # Paipote+Mantos+Escondida
```

Escribe `aire_registros` (sinca/observado + cams/modelo) + IoT demo.  
Validar: `GET …/modelo-vs-observado` → `estado=ok` o `parcial`.

Plantilla: [`docs/ejemplos/plantilla_sinca_observado.csv`](../ejemplos/plantilla_sinca_observado.csv)

## 3. Observado real (producción)

1. Exportar CSV diario SINCA / AWS faena (`fecha,pm25,pm10,so2,no2,o3`)
2. Subir a disco/URL y configurar `METGO_SINCA_*`
3. Cron: `GET /api/cron/sync?token=…` (ya llama `sincronizar_sinca`)
4. Marcar AWS: `faena_estaciones_area.fuente='observado'`
5. IoT: `POST /api/iot/lecturas` con `estacion_id` del rajo

## 4. SPA

| App | Acción |
|-----|--------|
| SPATI | Deploy CF Pages · `/ambiente` CSV/PDF/MVO |
| Mantos | Deploy CF Pages · `/ambiente` |
| Sync estaciones | `POST /api/cron/faena/estaciones-area` (ya 84 puntos) |

## 5. Criterio de cierre M7

- [x] Informe CSV y PDF descargables en prod
- [x] Al menos una faena con `observado-status.listo_produccion=true` _(Paipote; demo aire + tabla `datos_iot`)_
- [x] Documentado en `PLAN_MINERIA_MULTI_FAENA.md`
- [x] Migración `20260728220000_datos_iot.sql` aplicada en Supabase

## 6. Smoke automatizado

```powershell
# Local (API en :8080)
python scripts/smoke_mineria_m7.py --faena paipote --demo

# Producción Render
python scripts/smoke_mineria_m7.py --base https://metgo-api.onrender.com --faena paipote --demo --token $env:CRON_SECRET
```

Checks: `faenas`, informe CSV/PDF, `observado-status`, `estaciones-area`, umbrales; opcional `demo-observado`.
