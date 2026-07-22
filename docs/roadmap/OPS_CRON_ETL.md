# Ops — Cron ETL (OpenMeteo → Supabase)

Flujo: **scheduler → API Render `/api/cron/sync` → OpenMeteo → Supabase**.  
No apuntar el cron a `api.open-meteo.org` directamente.

## Requisitos

| Dónde | Variable | Notas |
|-------|----------|--------|
| Render (`metgo-api`) | `CRON_SECRET` | Obligatorio |
| GitHub Actions | secret `CRON_SECRET` | Mismo valor que Render |
| cron-job.org | `?token=...` en la URL | Mismo valor |

## Opción A — GitHub Actions (recomendada)

Workflow: `.github/workflows/etl-meteo-cron.yml`

1. Despierta `/api/health` (hasta 12 intentos).
2. Llama `/api/cron/sync?token=...` con reintentos ante 502/503.
3. Horarios: 00:00 y 12:00 UTC; domingo 03:00 UTC con Archive.

Verificar: Actions → *ETL Meteo* → Run workflow, o  
`https://metgo-api.onrender.com/api/datos/etl/status` → `ultimo` reciente.

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
| 200 + `errores: []` | OK | Revisar `etl/status` |

## Verificación

```bash
curl.exe -s "https://metgo-api.onrender.com/api/health"
curl.exe -s "https://metgo-api.onrender.com/api/datos/etl/status"
```
