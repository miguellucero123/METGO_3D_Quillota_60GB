-- E7/E8: permisos alineados con meteo_* (service_role escribe; anon/auth leen).
-- Sin esto la API con SUPABASE_KEY=service_role recibe 42501 permission denied.

grant usage on schema public to anon, authenticated, service_role;

grant select, insert, update, delete on public.sitios to service_role;
grant select, insert, update, delete on public.estaciones to service_role;
grant select, insert, update, delete on public.aire_registros to service_role;
grant select, insert, update, delete on public.aire_dispersion to service_role;
grant select, insert, update, delete on public.operaciones_ventanas to service_role;

grant select on public.sitios to anon, authenticated;
grant select on public.estaciones to anon, authenticated;
grant select on public.aire_registros to anon, authenticated;
grant select on public.aire_dispersion to anon, authenticated;
grant select on public.operaciones_ventanas to anon, authenticated;

grant usage, select on all sequences in schema public to service_role;

-- Lectura pública vía PostgREST (sin policies la tabla queda inaccesible a anon si RLS está ON).
alter table public.sitios enable row level security;
alter table public.estaciones enable row level security;
alter table public.aire_registros enable row level security;
alter table public.aire_dispersion enable row level security;
alter table public.operaciones_ventanas enable row level security;

drop policy if exists sitios_select_public on public.sitios;
create policy sitios_select_public on public.sitios for select to anon, authenticated using (true);

drop policy if exists estaciones_select_public on public.estaciones;
create policy estaciones_select_public on public.estaciones for select to anon, authenticated using (true);

drop policy if exists aire_registros_select_public on public.aire_registros;
create policy aire_registros_select_public on public.aire_registros for select to anon, authenticated using (true);

drop policy if exists aire_dispersion_select_public on public.aire_dispersion;
create policy aire_dispersion_select_public on public.aire_dispersion for select to anon, authenticated using (true);

drop policy if exists operaciones_ventanas_select_public on public.operaciones_ventanas;
create policy operaciones_ventanas_select_public on public.operaciones_ventanas for select to anon, authenticated using (true);
