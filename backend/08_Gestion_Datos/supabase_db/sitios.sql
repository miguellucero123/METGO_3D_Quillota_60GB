-- Catálogo de sitios METGO (multi-producto). Espejo de estaciones_catalogo.SITIOS_META.

create table if not exists public.sitios (
    slug text primary key,
    nombre text not null,
    region text,
    dominio text not null default 'meteo',
    estado text not null default 'activo',
    primary_color text,
    center_lat double precision,
    center_lon double precision,
    modules jsonb not null default '[]'::jsonb,
    created_at timestamptz not null default now()
);

comment on table public.sitios is 'Productos/sitios METGO (quillota|paine|demo|…)';
comment on column public.sitios.dominio is 'agro|criosfera|aire|mineria|template|…';
comment on column public.sitios.estado is 'activo|plantilla|archivado';

insert into public.sitios (slug, nombre, region, dominio, estado, primary_color, center_lat, center_lon, modules) values
  (
    'quillota',
    'METGO Quillota',
    'Valle de Aconcagua',
    'agro',
    'activo',
    '#00ffaa',
    -32.8833,
    -71.25,
    '["meteo","agricola","iot","ml"]'::jsonb
  ),
  (
    'paine',
    'METGO Paine',
    'Torres del Paine',
    'criosfera',
    'activo',
    '#22d3ee',
    -50.96,
    -73.05,
    '["meteo","lugares"]'::jsonb
  ),
  (
    'demo',
    'METGO Demo',
    'Valle Demo (ficticio)',
    'template',
    'plantilla',
    '#a78bfa',
    -33.32,
    -71.42,
    '["meteo","lugares"]'::jsonb
  )
on conflict (slug) do update set
  nombre = excluded.nombre,
  region = excluded.region,
  dominio = excluded.dominio,
  estado = excluded.estado,
  primary_color = excluded.primary_color,
  center_lat = excluded.center_lat,
  center_lon = excluded.center_lon,
  modules = excluded.modules;

-- Estaciones del sitio plantilla demo (E6)
insert into public.estaciones (id, nombre, sitio, lat, lon) values
  ('demo_norte', 'Demo Norte', 'demo', -33.30, -71.40),
  ('demo_sur', 'Demo Sur', 'demo', -33.34, -71.44)
on conflict (id) do update set
  nombre = excluded.nombre,
  sitio = excluded.sitio,
  lat = excluded.lat,
  lon = excluded.lon;

grant select on public.sitios to anon, authenticated;
