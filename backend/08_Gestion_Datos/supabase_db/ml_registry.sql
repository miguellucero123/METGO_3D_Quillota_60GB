-- =============================================================================
-- METGO — Tabla ml_registry (MLOps catálogo en Supabase)
--
-- Usada por: api_rest/ml_registry_core.py (upsert id=1, columna datos jsonb)
-- Fallback local si falla: datos_runtime/ml_registry.json
--
-- Vías de aplicación:
--   A) SQL Editor → New query → Run (pegar este archivo)
--   B) supabase db push
--      (migración: supabase/migrations/20260722144600_ml_registry.sql)
--
-- Idempotente: CREATE IF NOT EXISTS + DROP POLICY IF EXISTS
-- =============================================================================

create table if not exists public.ml_registry (
    id integer primary key,
    datos jsonb not null default '{}'::jsonb,
    actualizado_en timestamptz default now()
);

grant select, insert, update, delete on public.ml_registry to service_role;
grant select on public.ml_registry to anon, authenticated;

alter table public.ml_registry enable row level security;

drop policy if exists ml_registry_lectura on public.ml_registry;
create policy ml_registry_lectura on public.ml_registry for select using (true);

-- Verificación opcional:
-- select id, jsonb_typeof(datos) as tipo, actualizado_en from public.ml_registry;
