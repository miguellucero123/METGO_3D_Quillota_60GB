-- METGO — ml_registry (MLOps). Idempotente.
-- Origen: backend/08_Gestion_Datos/supabase_db/ml_registry.sql

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
