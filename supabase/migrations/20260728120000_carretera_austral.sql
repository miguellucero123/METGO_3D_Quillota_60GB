-- Carretera Austral (módulo Paine) — localidades + tramos pavimento/ripio.
-- Lectura pública (anon); escritura service_role. Realtime en ca_tramos.

create table if not exists public.ca_localidades (
    id uuid primary key default gen_random_uuid(),
    nombre text unique not null,
    lat numeric not null,
    lng numeric not null,
    created_at timestamptz not null default now()
);

create table if not exists public.ca_tramos (
    id uuid primary key default gen_random_uuid(),
    origen text not null,
    destino text not null,
    distancia_km numeric not null,
    tipo_camino text not null check (tipo_camino in ('pavimento', 'ripio', 'mixto')),
    pct_pavimento numeric not null default 0
        check (pct_pavimento >= 0 and pct_pavimento <= 100),
    velocidad_kmh numeric not null,
    tiempo_hrs numeric not null,
    lat_origen numeric not null,
    lng_origen numeric not null,
    lat_destino numeric not null,
    lng_destino numeric not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists ca_tramos_tipo_idx on public.ca_tramos (tipo_camino);
create index if not exists ca_tramos_origen_idx on public.ca_tramos (origen);
create index if not exists ca_tramos_destino_idx on public.ca_tramos (destino);

comment on table public.ca_localidades is
    'Localidades Carretera Austral (módulo METGO Paine)';
comment on table public.ca_tramos is
    'Tramos Carretera Austral con tipo de camino y coords para mapa';

grant select, insert, update, delete on public.ca_localidades to service_role;
grant select on public.ca_localidades to authenticated;
grant select on public.ca_localidades to anon;

grant select, insert, update, delete on public.ca_tramos to service_role;
grant select on public.ca_tramos to authenticated;
grant select on public.ca_tramos to anon;

alter table public.ca_localidades enable row level security;
alter table public.ca_tramos enable row level security;

drop policy if exists ca_localidades_select_public on public.ca_localidades;
create policy ca_localidades_select_public
    on public.ca_localidades
    for select
    to anon, authenticated
    using (true);

drop policy if exists ca_tramos_select_public on public.ca_tramos;
create policy ca_tramos_select_public
    on public.ca_tramos
    for select
    to anon, authenticated
    using (true);

-- Realtime (idempotente si la tabla ya está en la publication)
do $$
begin
  if not exists (
    select 1 from pg_publication_tables
    where pubname = 'supabase_realtime'
      and schemaname = 'public'
      and tablename = 'ca_tramos'
  ) then
    alter publication supabase_realtime add table public.ca_tramos;
  end if;
exception
  when undefined_object then
    raise notice 'Publication supabase_realtime no existe; omitir Realtime';
end $$;

insert into public.ca_localidades (nombre, lat, lng) values
('Puerto Montt', -41.4719, -72.9396),
('Hornopirén', -41.9689, -72.4466),
('Caleta Gonzalo', -42.5185, -72.6355),
('Chaitén', -42.9167, -72.7167),
('Villa Santa Lucía', -43.4092, -72.3983),
('Futaleufú', -43.1850, -71.8667),
('Palena', -43.6167, -71.8000),
('La Junta', -43.9667, -72.4000),
('Raúl Marín Balmaceda', -44.0500, -72.5500),
('Puyuhuapi', -44.3167, -72.5667),
('Lago Verde', -44.2333, -72.0000),
('Puerto Cisnes', -44.7333, -72.7000),
('Coyhaique', -45.5712, -72.0685),
('Puerto Aysén', -45.4000, -72.7000),
('Balmaceda', -45.9140, -71.7160),
('Puerto Ibáñez', -46.3000, -71.9333),
('Villa Cerro Castillo', -46.0833, -72.1833),
('Murta', -46.4667, -72.6667),
('Puerto Río Tranquilo', -46.6167, -72.6833),
('Puerto Guadal', -46.4167, -72.6500),
('Chile Chico', -46.5333, -71.7333),
('Puerto Bertrand', -46.9833, -72.8333),
('Cochrane', -47.2500, -72.5667),
('Caleta Tortel', -47.7833, -73.5333),
('Villa O''Higgins', -48.4667, -72.5667)
on conflict (nombre) do update set
  lat = excluded.lat,
  lng = excluded.lng;

-- Seed tramos (solo si vacío)
insert into public.ca_tramos (
  origen, destino, distancia_km, tipo_camino, pct_pavimento,
  velocidad_kmh, tiempo_hrs,
  lat_origen, lng_origen, lat_destino, lng_destino
)
select * from (values
  ('Puerto Montt', 'Hornopirén', 106::numeric, 'pavimento', 100::numeric, 50::numeric, 2.12::numeric, -41.4719, -72.9396, -41.9689, -72.4466),
  ('Caleta Gonzalo', 'Chaitén', 56, 'ripio', 0, 38, 1.47, -42.5185, -72.6355, -42.9167, -72.7167),
  ('Chaitén', 'Villa Santa Lucía', 75, 'pavimento', 100, 50, 1.50, -42.9167, -72.7167, -43.4092, -72.3983),
  ('Villa Santa Lucía', 'Futaleufú', 76, 'mixto', 20, 46, 1.65, -43.4092, -72.3983, -43.1850, -71.8667),
  ('Villa Santa Lucía', 'Palena', 71, 'mixto', 20, 46, 1.54, -43.4092, -72.3983, -43.6167, -71.8000),
  ('Villa Santa Lucía', 'La Junta', 69, 'pavimento', 100, 50, 1.38, -43.4092, -72.3983, -43.9667, -72.4000),
  ('La Junta', 'Raúl Marín Balmaceda', 74, 'ripio', 0, 38, 1.95, -43.9667, -72.4000, -44.0500, -72.5500),
  ('La Junta', 'Puyuhuapi', 45, 'pavimento', 100, 50, 0.90, -43.9667, -72.4000, -44.3167, -72.5667),
  ('La Junta', 'Lago Verde', 72, 'ripio', 0, 38, 1.89, -43.9667, -72.4000, -44.2333, -72.0000),
  ('Puyuhuapi', 'Puerto Cisnes', 87, 'mixto', 90, 49.5, 1.76, -44.3167, -72.5667, -44.7333, -72.7000),
  ('Puyuhuapi', 'Coyhaique', 233, 'mixto', 90, 49.5, 4.71, -44.3167, -72.5667, -45.5712, -72.0685),
  ('Puyuhuapi', 'Puerto Aysén', 205, 'mixto', 90, 49.5, 4.14, -44.3167, -72.5667, -45.4000, -72.7000),
  ('Puerto Aysén', 'Coyhaique', 64, 'pavimento', 100, 50, 1.28, -45.4000, -72.7000, -45.5712, -72.0685),
  ('Coyhaique', 'Balmaceda', 56, 'pavimento', 100, 50, 1.12, -45.5712, -72.0685, -45.9140, -71.7160),
  ('Coyhaique', 'Puerto Ibáñez', 115, 'pavimento', 100, 50, 2.30, -45.5712, -72.0685, -46.3000, -71.9333),
  ('Coyhaique', 'Villa Cerro Castillo', 96, 'pavimento', 100, 50, 1.92, -45.5712, -72.0685, -46.0833, -72.1833),
  ('Villa Cerro Castillo', 'Murta', 100, 'mixto', 10, 45, 2.22, -46.0833, -72.1833, -46.4667, -72.6667),
  ('Murta', 'Puerto Río Tranquilo', 23, 'ripio', 0, 38, 0.61, -46.4667, -72.6667, -46.6167, -72.6833),
  ('Puerto Río Tranquilo', 'Puerto Guadal', 59, 'ripio', 0, 38, 1.55, -46.6167, -72.6833, -46.4167, -72.6500),
  ('Puerto Guadal', 'Chile Chico', 105, 'mixto', 5, 42.5, 2.47, -46.4167, -72.6500, -46.5333, -71.7333),
  ('Puerto Río Tranquilo', 'Puerto Bertrand', 67, 'ripio', 0, 38, 1.76, -46.6167, -72.6833, -46.9833, -72.8333),
  ('Puerto Bertrand', 'Cochrane', 48, 'ripio', 0, 38, 1.26, -46.9833, -72.8333, -47.2500, -72.5667),
  ('Cochrane', 'Caleta Tortel', 126, 'ripio', 0, 38, 3.32, -47.2500, -72.5667, -47.7833, -73.5333),
  ('Caleta Tortel', 'Villa O''Higgins', 151, 'ripio', 0, 38, 3.97, -47.7833, -73.5333, -48.4667, -72.5667),
  ('Cochrane', 'Villa O''Higgins', 231, 'ripio', 0, 38, 6.08, -47.2500, -72.5667, -48.4667, -72.5667)
) as v(
  origen, destino, distancia_km, tipo_camino, pct_pavimento,
  velocidad_kmh, tiempo_hrs,
  lat_origen, lng_origen, lat_destino, lng_destino
)
where not exists (select 1 from public.ca_tramos limit 1);
