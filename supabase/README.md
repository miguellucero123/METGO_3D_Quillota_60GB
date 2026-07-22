# Supabase CLI — migraciones METGO

Proyecto linkeado: `ylivhjigvxqzpzchllte` (`supabase/.temp/project-ref`).

Fuente canónica del SQL: `backend/08_Gestion_Datos/supabase_db/meteo_pronostico.sql`  
Migración CLI: `supabase/migrations/20260722011000_meteo_tablas_y_helada_cultivo.sql`

## Aplicar al remoto (recomendado)

```powershell
cd d:\METGO_3D_Quillota_60GB

# Si no estás logueado:
supabase login

# Confirmar link (ya existe project-ref):
supabase link --project-ref ylivhjigvxqzpzchllte

# Empujar migraciones pendientes al proyecto cloud:
supabase db push
```

## Alternativa: ejecutar un archivo SQL puntual

```powershell
supabase db query --linked -f backend/08_Gestion_Datos/supabase_db/meteo_pronostico.sql
```

(o, según versión CLI: `supabase db execute --file ...` / `psql` con la connection string del dashboard).

## Verificar

```powershell
supabase db query --linked "select table_name from information_schema.tables where table_schema='public' and table_name in ('meteo_registros','meteo_pronostico','meteo_series','meteo_helada_pronostico') order by 1;"
```

## Notas

- El SQL es **idempotente** (`IF NOT EXISTS` / `ADD COLUMN IF NOT EXISTS`).
- Tras el push, el ETL/API hace upsert en `meteo_helada_pronostico` (una fila por estación+fecha+cultivo).
- No commitear secrets; `.temp` ya está en `supabase/.gitignore`.
