# Checklist operativo — Etapa E (Archive + Supabase)

Código listo en repo. Falta ejecución en infra.

## 1. SQL en Supabase — HECHO (2026-07-22)

Tablas accesibles con la key del `.env` (sin *permission denied*).
Tras sync corto: `meteo_registros` ~1348 filas, `meteo_pronostico` ~35.

Re-ejecutar `meteo_pronostico.sql` solo si hace falta re-aplicar GRANTs/columnas.


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
