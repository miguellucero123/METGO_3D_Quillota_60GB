# PROMPT — Revisión completa del sistema METGO 3D (flujo OpenMeteo → Supabase)

> Copiar y pegar este prompt en Cursor (modo Agente) para ejecutar la revisión.  
> Requiere: Python del proyecto, `.env` con `SUPABASE_URL`/`SUPABASE_KEY` (opcional pero recomendado).  
> **Actualizado 2026-07-24:** encoding UTF-8 restaurado; tablas meteo marcadas hechas según PLAN_CALIDAD / CHECKLIST_E.

---

## CONTEXTO

Eres un ingeniero senior full-stack del proyecto **METGO 3D** (`d:\METGO_3D_Quillota_60GB`).
Arquitectura de datos: **Frontend Vue → API Flask (Render) → OpenMeteo → validación → Supabase → cálculos y vistas**, con ETL a las **00 y 12 UTC** (GitHub Actions `.github/workflows/etl-meteo-cron.yml` → `GET /api/cron/sync?token=CRON_SECRET`).

Cadena de resiliencia (orden):

1. **OpenMeteo en vivo** con reintentos/backoff (`datos_reales_openmeteo.py`; env `METGO_OPENMETEO_TIMEOUT` / `METGO_OPENMETEO_RETRIES`).
2. **Caché disco TTL 15 min** + último dato bueno ≤48 h (`backend/08_Gestion_Datos/cache_openmeteo.py`).
3. **Supabase** (`meteo_store` / `meteo_repository`):
   - `meteo_registros` — histórico observado
   - `meteo_pronostico` — pronóstico diario
   - `meteo_series` — series JSON (viento horario, precip 3h)
4. **Nunca datos sintéticos** en producción; datos de caché/BD llevan `desde_cache: true`.

SPA: `frontend/vue/` (no `04_Dashboards_Unificados`). Rutas: `metgo.paths` / `metgo_paths`.

## TAREA

Ejecuta una revisión extremo a extremo y reporta resultados. **No modifiques código salvo bug; si lo corriges, documenta el cambio.**

### Paso 1 — Script de humo

Crear `_smoke_revision.py` en la raíz, ejecutar `python _smoke_revision.py`, capturar salida y **eliminarlo al terminar**. El script debe:

- Importar `create_app` / servicios meteo
- Llamar resumen Quillota + health
- Imprimir `fuente`, `desde_cache`, códigos HTTP
- No inventar datos

### Paso 2 — Tests del repositorio

```powershell
python -m pytest tests/ -q --tb=line
```

### Paso 3 — Producción (Render + Supabase + cron)

```powershell
curl.exe -s "https://metgo-api.onrender.com/api/health"
curl.exe -s "https://metgo-api.onrender.com/api/public/meteo/quillota"
curl.exe -s "https://metgo-api.onrender.com/api/datos/etl/status"
```

Checklist manual:

- [x] Tablas `meteo_registros`, `meteo_pronostico` y `meteo_series` en Supabase (PLAN_CALIDAD / CHECKLIST_E)
- [ ] Render: confirmar `SUPABASE_URL`, `SUPABASE_KEY`, `CRON_SECRET` reales; redeploy desde **`master`**
- [x] GitHub: secret `CRON_SECRET` + workflow ETL 00/12 UTC (wake + retry 503)
- [ ] Correr workflow una vez (workflow_dispatch) y verificar HTTP 200
- [ ] cron-job.org: wake `/api/health` 2–3 min antes del sync (`docs/roadmap/OPS_CRON_ETL.md`)

### Paso 4 — Reporte final

Entregar en español:

1. Tabla de checks del script de humo (ok/fallo + detalle).
2. Resultado de pytest.
3. Estado de producción (health, versión, ETL status).
4. Bugs encontrados y corregidos (archivo:línea).
5. Pendientes de ops no automatizables (envs Render, SQL, secrets).

## CRITERIOS DE ÉXITO

- Endpoints meteo 200 con datos reales (`fuente` openmeteo/supabase; nunca sintético).
- Con OpenMeteo caído (simulado), servir `desde_cache: true` en lugar de 404/503 vacío.
- `meteo_pronostico` / `meteo_series` se actualizan tras sync fresco y cron 00/12 UTC.
- CI verde.
