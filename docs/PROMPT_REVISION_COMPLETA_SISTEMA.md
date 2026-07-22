# PROMPT â€” RevisiÃ³n completa del sistema METGO 3D (flujo OpenMeteo â†’ Supabase)

> Copiar y pegar este prompt completo en Cursor (modo Agente) para ejecutar la revisiÃ³n.
> Requiere: Python del proyecto, `.env` con `SUPABASE_URL`/`SUPABASE_KEY` (opcional pero recomendado).

---

## CONTEXTO

Eres un ingeniero senior full-stack del proyecto **METGO 3D** (`d:\METGO_3D_Quillota_60GB`).
La arquitectura de datos es: **Frontend Vue â†’ API Flask (Render) â†’ OpenMeteo â†’ validaciÃ³n â†’ Supabase â†’ cÃ¡lculos y vistas desde Supabase**, con actualizaciÃ³n programada a las **00 y 12 UTC** (GitHub Actions `.github/workflows/etl-meteo-cron.yml` â†’ `GET /api/cron/sync?token=CRON_SECRET`).

Cadena de resiliencia implementada (en este orden):

1. **OpenMeteo en vivo** con reintentos/backoff (`datos_reales_openmeteo.py`, `_get_json`, env `METGO_OPENMETEO_TIMEOUT`/`METGO_OPENMETEO_RETRIES`).
2. **CachÃ© disco TTL 15 min** + **"Ãºltimo dato bueno" â‰¤48 h** (`backend/08_Gestion_Datos/cache_openmeteo.py`: `get_meteo_cached`, `get_json_cached`).
3. **Supabase** (`backend/08_Gestion_Datos/supabase_db/meteo_repository.py`):
   - `meteo_registros` (histÃ³rico observado) â€” `guardar_registros`/`leer_registros`
   - `meteo_pronostico` (pronÃ³stico diario) â€” `guardar_pronostico`/`leer_pronostico`
   - `meteo_series` (series JSON: viento horario, precip 3h) â€” `guardar_serie`/`leer_serie`
   - SQL: `backend/08_Gestion_Datos/supabase_db/meteo_pronostico.sql`
4. **Nunca datos sintÃ©ticos** en producciÃ³n: `_persistir_pronostico` filtra `fuente` con "sintetico"; todo dato servido desde cachÃ©/BD lleva `desde_cache: true`.

## TAREA

Ejecuta una revisiÃ³n completa de extremo a extremo y reporta resultados. **No modifiques cÃ³digo salvo que encuentres un bug; en ese caso corrÃ­gelo y documenta el cambio.**

### Paso 1 â€” Script de humo (funciones de servicio reales)

Crea `_smoke_revision.py` en la raÃ­z del repo con el contenido de abajo, ejecÃºtalo con `python _smoke_revision.py`, captura la salida completa y **elimÃ­nalo al terminar**.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke test: replica el setup de rutas de la app y prueba funciones reales + fallbacks."""
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import metgo_paths  # noqa: E402

sys.path.insert(0, str(metgo_paths.MODULE_PATHS["05_api_rest"]))
metgo_paths.setup_paths("01_meteo", "05_apis", "08_datos")
sys.path.insert(0, str(ROOT / "backend" / "05_APIs_Externas" / "api_rest"))

RESULTADOS = {}

def check(nombre, fn):
    try:
        out = fn()
        RESULTADOS[nombre] = {"ok": bool(out), "detalle": out}
        print(f"[OK ] {nombre}")
    except Exception as e:
        RESULTADOS[nombre] = {"ok": False, "error": f"{type(e).__name__}: {e}"}
        print(f"[ERR] {nombre}: {e}")

from api_rest import services  # noqa: E402
import cache_openmeteo as cache  # noqa: E402

# 1. Datos en vivo (o cachÃ©/BD si OpenMeteo falla; mirar 'desde_cache')
check("resumen_meteo", lambda: (
    lambda r: {k: r.get(k) for k in ("fecha", "temperatura", "fuente", "tipo_dato", "desde_cache")} if r else None
)(services.resumen_meteo("quillota")))

check("pronostico_meteo(7)", lambda: (
    lambda p: {"dias": len(p or []), "primera_fecha": p[0]["fecha"] if p else None,
               "desde_cache": p[0].get("desde_cache") if p else None}
)(services.pronostico_meteo("quillota", 7)))

check("historico_meteo(14)", lambda: (
    lambda h: {"dias": len(h or []), "ultima_fecha": h[-1]["fecha"] if h else None}
)(services.historico_meteo("quillota", 14)))

check("viento_horario(7)", lambda: (
    lambda v: {"puntos": len((v or {}).get("direcciones") or []), "fuente": (v or {}).get("fuente")}
)(services.viento_horario_meteo("quillota", 7)))

check("precip_3h(7)", lambda: (
    lambda p: {"ventanas": len((p or {}).get("fechas") or []), "fuente": (p or {}).get("fuente_datos")}
)(services.precipitacion_horaria_3h_meteo("quillota", 7)))

check("precip_calibrada(7)", lambda: bool(services.pronostico_precipitacion_calibrado("quillota", 7)))
check("heladas(7)", lambda: bool(services.pronostico_heladas("quillota", 7)))

# 2. Fallback de cachÃ©: fetcher que SIEMPRE falla debe servir 'Ãºltimo dato bueno'
def _fallback_cache():
    df = cache.get_meteo_cached("Quillota", "pronostico", 7, lambda *a: None)
    if df is None or df.empty:
        return {"lastgood": False, "nota": "sin dato bueno previo (correr 2 veces)"}
    return {"lastgood": True, "desde_cache": "desde_cache" in df.columns}
check("fallback_cache_lastgood", _fallback_cache)
check("cache_stats", cache.cache_stats)

# 3. Fallback Supabase (requiere .env con SUPABASE_URL/KEY; si no, reporta inactivo)
def _supabase():
    from api_rest.integracion import meteo_store
    stats = meteo_store.estadisticas_store()
    pron = meteo_store.leer_pronostico("quillota", 7)
    serie = meteo_store.leer_serie("quillota", "precip_3h_7")
    return {"store": stats, "pronostico_filas": len(pron), "serie_precip3h": bool(serie)}
check("supabase_store", _supabase)

# 4. API completa vÃ­a test_client (rutas reales con JWT)
def _api():
    import os
    os.environ.setdefault("METGO_PASSWORD_ADMIN", "admin123")
    from api_rest.app import create_app
    c = create_app().test_client()
    r = c.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    tok = r.get_json()["access_token"]
    H = {"Authorization": f"Bearer {tok}"}
    rutas = [
        "/api/health",
        "/api/meteo/quillota?tipo=pronostico",
        "/api/meteo/quillota/pronostico?dias=7",
        "/api/meteo/quillota/historico?dias=14",
        "/api/meteo/quillota/viento-horario?dias=7",
        "/api/meteo/quillota/precipitacion-calibrada?dias=7&intervalo=3h",
        "/api/meteo/quillota/heladas?dias=7",
        "/api/datos/etl/status",
    ]
    return {ruta: c.get(ruta, headers=H).status_code for ruta in rutas}
check("api_endpoints", _api)

print("\n===== RESUMEN =====")
print(json.dumps(RESULTADOS, indent=2, ensure_ascii=False, default=str))
fallos = [k for k, v in RESULTADOS.items() if not v.get("ok")]
print(f"\nTotal: {len(RESULTADOS)} checks, fallos: {len(fallos)} {fallos}")
sys.exit(1 if fallos else 0)
```

**Importante:** ejecutar el script **dos veces**. La primera puebla cachÃ© y Supabase; la segunda valida `fallback_cache_lastgood: true`.

### Paso 2 â€” Tests del repositorio

```powershell
python -m pytest tests/test_pronostico_fechas.py -q
```

Si hay mÃ¡s tests que toquen meteo/ETL (`Grep "pronostico|etl|meteo" tests/`), correrlos tambiÃ©n.

### Paso 3 â€” ProducciÃ³n (Render + Supabase + cron)

```powershell
curl.exe -s "https://metgo-api.onrender.com/api/health"          # esperar "openmeteo": true|false y "version" == commit actual
curl.exe -s "https://metgo-api.onrender.com/api/public/meteo/quillota"
curl.exe -s "https://metgo-api.onrender.com/api/datos/etl/status" # "ultimo" debe tener timestamp de las 00 o 12 UTC
```

Checklist manual:

- [ ] Tablas `meteo_pronostico` y `meteo_series` creadas en Supabase (SQL `backend/08_Gestion_Datos/supabase_db/meteo_pronostico.sql`).
- [ ] Render: env `SUPABASE_URL`, `SUPABASE_KEY`, `CRON_SECRET` configuradas; redeploy con el Ãºltimo commit de `main`.
- [x] GitHub: secret `CRON_SECRET` (mismo valor que Render); workflow `ETL Meteo (00 y 12 UTC)` con wake + retry 503.
- [ ] Correr el workflow una vez con "Run workflow" (workflow_dispatch) y verificar HTTP 200.
- [ ] Si usas cron-job.org: job wake `/api/health` 2–3 min antes del sync (`docs/roadmap/OPS_CRON_ETL.md`).

### Paso 4 â€” Reporte final

Entregar en espaÃ±ol:

1. Tabla de checks del script de humo (ok/fallo + detalle).
2. Resultado de pytest.
3. Estado de producciÃ³n (health, versiÃ³n desplegada, ETL status).
4. Lista de bugs encontrados y corregidos (archivo:lÃ­nea).
5. Pendientes de ops que no se pueden automatizar (envs Render, SQL Supabase, secret GitHub).

## CRITERIOS DE Ã‰XITO

- Todos los endpoints meteo devuelven 200 con datos reales (`fuente` contiene "openmeteo" o "supabase"; nunca "sintetico").
- Con OpenMeteo caÃ­do (simulado), el sistema sirve datos con `desde_cache: true` en lugar de 404/503.
- `meteo_pronostico` y `meteo_series` en Supabase se actualizan tras cada llamada fresca y tras el cron 00/12 UTC.
- CI verde.

