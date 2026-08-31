# Ops — Cron ETL (OpenMeteo → Supabase)

Flujo: **scheduler → API Render `/api/cron/sync` → OpenMeteo → Supabase**.  
No apuntar el cron a `api.open-meteo.org` directamente.

## Ciclos 00 y 12 UTC (pronósticos + mapas)

Todas las **descargas de variables Open-Meteo** usadas para pronósticos y generación de mapas
se alinean a los ciclos **00 UTC** y **12 UTC**:

| Hora UTC | Qué descarga |
|----------|----------------|
| **00:00 / 12:00** | Sync completo: histórico corto, pronóstico 7 d, heladas, aire (CAMS), dispersión/mapas, operaciones, catálogos, oficiales/SINCA |
| **06:00 / 18:00** | Solo ventilación Paipote (N/R/M). Para forzar sync completo: `?full=1` |
| **Dom 03:00** | Sync + Archive ERA5 |

Entre ciclos, la API sirve **caché / last-good** del ciclo vigente (`METGO_OPENMETEO_FETCH_MODE=ciclo`, default).  
Para volver al refresco por TTL horario: `METGO_OPENMETEO_FETCH_MODE=ttl`.

Módulo: `api_rest/integracion/openmeteo_ciclo.py`. La respuesta de `/api/cron/sync` incluye `ciclo_utc` y `modo`.

## Health check Render (alerta “expiró tras 5 segundos”)

Causa habitual en **plan free**: cold start + `/api/health` llamando OpenMeteo (timeout 2–5 s) → Render marca la instancia caída.

**Mitigación en código:** `healthCheckPath: /api/health/live` (liveness sin I/O externo).  
`/api/health` sigue siendo el diagnóstico completo (ops / cron wake).

En Dashboard Render → `metgo-api` → Settings → Health Check Path → `/api/health/live` (si no usas Blueprint sync).

---

## Requisitos

| Dónde | Variable | Notas |
|-------|----------|--------|
| Render (`metgo-api`) | `CRON_SECRET` | Obligatorio |
| GitHub Actions | secret `CRON_SECRET` | Mismo valor que Render |
| cron-job.org | `?token=...` en la URL | Mismo valor |
| Render (opcional) | `METGO_OPENMETEO_FETCH_MODE` | `ciclo` (default) o `ttl` |

## Opción A — GitHub Actions (recomendada)

Workflow: `.github/workflows/etl-meteo-cron.yml`

1. Despierta `/api/health` (hasta 30 intentos).
2. Llama `/api/cron/sync?token=...` con reintentos ante 502/503.
3. Horarios: **00:00 y 12:00 UTC** (ciclo completo); 06/18 ventilación; domingo 03:00 Archive.

Verificar: Actions → *ETL Meteo* → Run workflow, o  
`https://metgo-api.onrender.com/api/datos/etl/status` → `ultimo.ciclo_utc` reciente.

## Opción B — cron-job.org (evitar 503 cold start)

Crear **dos** jobs (misma zona horaria; preferir UTC):

### 1) Wake (2–3 min antes)

- URL: `https://metgo-api.onrender.com/api/health`
- Horario: `23:57` y `11:57` UTC
- Timeout: ≥ 90 s

### 2) Sync

- URL: `https://metgo-api.onrender.com/api/cron/sync?token=TU_CRON_SECRET`
- Horario: `00:00` y `12:00` UTC
- Timeout: ≥ 10 min
- Reintentos en fallo: sí (1–2), si el plan lo permite

Si usas A y B a la vez, el sync se ejecuta dos veces (aceptable). Para simplificar, deja solo una opción.

## Errores típicos

| HTTP | Causa | Qué hacer |
|------|--------|-----------|
| 401 | Token vacío o distinto a Render | Igualar `CRON_SECRET` |
| 503 / 502 | Render free dormido | Job wake + timeout largo / usar Actions |
| 200 + `errores: []` | OK | Revisar `etl/status` y `ciclo_utc` |

## Verificación

```bash
curl.exe -s "https://metgo-api.onrender.com/api/health"
curl.exe -s "https://metgo-api.onrender.com/api/datos/etl/status"
```
