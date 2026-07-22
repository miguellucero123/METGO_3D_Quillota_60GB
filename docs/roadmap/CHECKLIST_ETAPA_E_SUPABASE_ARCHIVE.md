# Checklist operativo — Etapa E (Archive + Supabase)

Código listo en repo. Falta ejecución en infra.

## 1. SQL en Supabase (actualizar tablas existentes)

1. Abrir [Supabase](https://supabase.com) → proyecto METGO → **SQL Editor**.
2. Pegar y ejecutar todo: `backend/08_Gestion_Datos/supabase_db/meteo_pronostico.sql`
   - Es **idempotente**: no borra datos; hace `CREATE IF NOT EXISTS` + `ADD COLUMN IF NOT EXISTS`.
   - Actualiza `meteo_registros` (ya creada) y crea/alinea `meteo_pronostico` + `meteo_series`.
3. Confirmar las 3 tablas en Table Editor y que no haya *permission denied*.
4. Re-ejecutar el script es seguro si hace falta re-aplicar GRANTs/RLS.

## 2. Secrets

| Dónde | Variables |
|-------|-----------|
| Render (API) | `SUPABASE_URL`, `SUPABASE_KEY` (service_role preferible) |
| GitHub Actions | mismos + URL API / token si el cron llama al endpoint sync |

## 3. Sync Archive (histórico largo)

- Endpoint sync (`fase4_routes` / ETL): body con `"incluir_archive": true` y `anios_archive` (p. ej. 2–5).
- Cron: `.github/workflows/etl-meteo-cron.yml` — activar `incluir_archive` en el payload si aún está en `false`.
- Tras el primer sync Archive, `/api/meteo/{id}/historico?dias=365` debe responder desde store (sin OpenMeteo en caliente si `dias>92`).

## 4. Verificación rápida

```bash
curl -s "https://metgo-api.onrender.com/api/health"
# Tras auth JWT:
# GET /api/meteo/quillota/historico?dias=365
```

## 5. Agromet / DMC

Fuera de alcance inmediato: documentado como siguiente fuente oficial tras Archive.
