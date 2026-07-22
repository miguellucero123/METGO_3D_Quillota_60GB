# Checklist operativo — Etapa E (Archive + Supabase)

Código listo en repo. Falta ejecución en infra.

## 1. SQL en Supabase — HECHO (2026-07-22)

Tablas accesibles con la key del `.env` (sin *permission denied*).
Tras sync corto: `meteo_registros` ~1348 filas, `meteo_pronostico` ~35.
Tras Archive 1 año: `meteo_registros` ~1830+ filas.

Re-ejecutar `meteo_pronostico.sql` solo si hace falta re-aplicar GRANTs/columnas.

### 1b. `ml_registry` (MLOps) — SQL en repo (2026-07-22)

- Archivo: `backend/08_Gestion_Datos/supabase_db/ml_registry.sql`
- Migración: `supabase/migrations/20260722144600_ml_registry.sql`
- Si la tabla ya existe en el dashboard, el SQL es idempotente (seguro re-ejecutar).
- Tras restart de la API en Render (o `POST /api/ml/registry/sync` con JWT) debe quedar **1 fila** (`id=1`).
- Verificado 2026-07-22: `ml_registry` count=1, `total=43` / `servibles=43`.


## 2. Secrets

| Dónde | Variables |
|-------|-----------|
| Render (API) | `SUPABASE_URL`, `SUPABASE_KEY` (service_role preferible) |
| GitHub Actions | mismos + URL API / token si el cron llama al endpoint sync |

## 3. Sync Archive (histórico largo)

- Endpoint sync (`fase4_routes` / ETL): body con `"incluir_archive": true` y `anios_archive` (p. ej. 2–5).
- Cron: `.github/workflows/etl-meteo-cron.yml` — activar `incluir_archive` en el payload si aún está en `false`.
- Tras el primer sync Archive, `/api/meteo/{id}/historico?dias=365` debe responder desde store (sin OpenMeteo en caliente si `dias>92`).

### 3b. Archive 5 años — HECHO (2026-07-22, sync local)

- Rango: `2021-07-21` … `2026-07-21` (1827 días × 5 estaciones).
- Persistidos: **9135** registros (`quillota`, `los_nogales`, `hijuelas`, `limache`, `olmue`).
- `errores: []`.
- Verificación: `python scratch/verificar_supabase_tablas.py` → `meteo_registros` ~9135+.

## 4. Verificación rápida

```bash
curl -s "https://metgo-api.onrender.com/api/health"
# Tras auth JWT:
# GET /api/meteo/quillota/historico?dias=365
```

## 5. Agromet / DMC

Fuera de alcance inmediato: documentado como siguiente fuente oficial tras Archive.
