# Supabase CLI — migraciones METGO

Proyecto linkeado (producción API): `ylivhjigvxqzpzchllte` → https://ylivhjigvxqzpzchllte.supabase.co  
(`supabase/.temp/project-ref`). No usar refs de otros proyectos Free a los que el CLI no tenga acceso.

Fuente canónica del SQL: `backend/08_Gestion_Datos/supabase_db/meteo_pronostico.sql`
Migración CLI: `supabase/migrations/20260722011000_meteo_tablas_y_helada_cultivo.sql`

## Advisor Center (Security / Performance)

Migración: [`migrations/20260831140000_supabase_advisor_hardening.sql`](migrations/20260831140000_supabase_advisor_hardening.sql)

| Aviso | Qué hacer |
|-------|-----------|
| RLS Enabled No Policy (identity) | Políticas `*_deny_clients` (deny anon; API usa `service_role`) |
| Multiple Permissive Policies (meteo_*) | Una sola `*_select_public` |
| Function Search Path Mutable | `set_updated_at` con `SET search_path = public` |
| Unindexed FK `usuarios_app` | Índice `usuarios_app_org_id_idx` |
| Disk IO / Slow Queries | Evitar `count=exact` en health/ETL; ciclos 00/12 UTC |

Tras `db push`: Advisors → **Rerun linter** y Query Performance → **Reset report**.

## Carretera Austral (módulo Paine `/carretera`)

Migración: [`migrations/20260728120000_carretera_austral.sql`](migrations/20260728120000_carretera_austral.sql)

Tablas `ca_localidades` / `ca_tramos` — lectura pública (anon), escritura `service_role`, Realtime en `ca_tramos`.

SPA: repo `metgo-paine` → ruta `/carretera` (Leaflet/OSM; seed local si faltan `VITE_SUPABASE_*`).

## Aplicar al remoto (recomendado)

```powershell
cd d:\METGO_3D_Quillota_60GB

# Si no estás logueado:
supabase login

# Confirmar link (ya existe project-ref):
supabase link --project-ref ylivhjigvxqzpzchllte

# Empujar migraciones pendientes al proyecto cloud:
supabase db push --linked --yes
```

## Estado remoto (2026-07-24)

Aplicadas (E7/E8 multi-sitio):

| Migración | Contenido |
|-----------|-----------|
| `…23120000_estaciones_multisitio` | tabla `estaciones` + seed Quillota/Paine |
| `…23140000_sitios_multisitio` | tabla `sitios` + demo |
| `…23150000_copiapo_aire` | Copiapó + `aire_registros` |
| `…24100000_copiapo_dispersion` | 7 puntos + `aire_dispersion` |
| `…24120000_mantos_blancos_operaciones` | faena + `operaciones_ventanas` |
| `…24130000_operaciones_uv_so2` | columnas UV/SO₂ |
| `…24140000_e7_e8_grants_rls` | GRANTs `service_role` + RLS lectura |
| `…28120000_carretera_austral` | `ca_localidades` + `ca_tramos` (módulo Paine) |
| `…28180000_faena_estaciones_area` | M4 puntos rajo/campamento/chancado/botadero por faena |
| `…28220000_datos_iot` | M7 lecturas IoT compartidas (`datos_iot`) |
| `…28221000_estaciones_escondida` | Estaciones aire Escondida (FK `aire_registros`) |
| `…28230000_estaciones_faenas_spati` | M8: 84 IDs faena/SPATI → `estaciones` |
| `…28240000_spati_umbrales_alertas` | M9: `umbrales_json` + `spati_alert_state` |

Verificación:

```powershell
python scratch/verificar_supabase_e7_e8.py
```

Esperado: **8/8 accesibles** (`sitios`, `estaciones`, `aire_registros`, `aire_dispersion`, `operaciones_ventanas`, meteo_*, `ml_registry`).

## Alternativa: ejecutar un archivo SQL puntual

```powershell
supabase db query --linked -f backend/08_Gestion_Datos/supabase_db/meteo_pronostico.sql
```

(o, según versión CLI: `supabase db execute --file ...` / `psql` con la connection string del dashboard).

## Verificar

```powershell
supabase db query --linked "select table_name from information_schema.tables where table_schema='public' and table_name in ('meteo_registros','meteo_pronostico','meteo_series','meteo_helada_pronostico','sitios','estaciones','aire_registros','aire_dispersion','operaciones_ventanas') order by 1;"
```

## Notas

- El SQL es **idempotente** (`IF NOT EXISTS` / `ADD COLUMN IF NOT EXISTS`).
- Tras el push, el ETL/API hace upsert en `meteo_helada_pronostico` (una fila por estación+fecha+cultivo).
- El cron `/api/cron/sync` también escribe `aire_registros`, `aire_dispersion` y `operaciones_ventanas` (E7/E8).
- No commitear secrets; `.temp` ya está en `supabase/.gitignore`.
- Docker Desktop no es obligatorio para `db push` al remoto (solo para desarrollo local).
