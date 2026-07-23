-- Catálogo multi-sitio METGO (espejo del catálogo en código).
-- No sustituye estacion_id text en meteo_*; es referencia para UI/ETL futuros.

create table if not exists public.estaciones (
    id text primary key,
    nombre text not null,
    sitio text not null default 'quillota',
    lat double precision not null,
    lon double precision not null,
    activa boolean not null default true,
    circuito text,
    altitud integer,
    created_at timestamptz not null default now()
);

create index if not exists estaciones_sitio_idx on public.estaciones (sitio);

comment on table public.estaciones is 'Catálogo multi-sitio METGO (quillota|paine|…)';
comment on column public.estaciones.sitio is 'Slug de producto/sitio; default quillota';

-- Seed Quillota (Valle de Aconcagua)
insert into public.estaciones (id, nombre, sitio, lat, lon) values
  ('quillota', 'Quillota', 'quillota', -32.8833, -71.25),
  ('los_nogales', 'Los Nogales', 'quillota', -32.9333, -71.2167),
  ('hijuelas', 'Hijuelas', 'quillota', -32.8000, -71.1333),
  ('limache', 'Limache', 'quillota', -33.0167, -71.2667),
  ('olmue', 'Olmue', 'quillota', -33.0000, -71.2167)
on conflict (id) do update set
  nombre = excluded.nombre,
  sitio = excluded.sitio,
  lat = excluded.lat,
  lon = excluded.lon;

-- Seed Torres del Paine (METGO Glaciares)
insert into public.estaciones (id, nombre, sitio, lat, lon, circuito, altitud) values
  ('base_torres', 'Base Torres', 'paine', -50.9417, -72.9667, 'W', 900),
  ('glaciar_grey', 'Glaciar Grey', 'paine', -51.0, -73.23, 'W', 50),
  ('valle_frances', 'Valle del Frances', 'paine', -50.9667, -73.0833, 'W', 300),
  ('paine_grande', 'Paine Grande', 'paine', -50.9500, -73.1167, 'O', 50),
  ('campamento_italiano', 'Campamento Italiano', 'paine', -50.9583, -73.0667, 'W', 120),
  ('los_cuernos', 'Los Cuernos', 'paine', -50.9750, -73.0500, 'O', 200)
on conflict (id) do update set
  nombre = excluded.nombre,
  sitio = excluded.sitio,
  lat = excluded.lat,
  lon = excluded.lon,
  circuito = excluded.circuito,
  altitud = excluded.altitud;

insert into public.estaciones (id, nombre, sitio, lat, lon) values
  ('demo_norte', 'Demo Norte', 'demo', -33.30, -71.40),
  ('demo_sur', 'Demo Sur', 'demo', -33.34, -71.44)
on conflict (id) do update set
  nombre = excluded.nombre,
  sitio = excluded.sitio,
  lat = excluded.lat,
  lon = excluded.lon;

grant select on public.estaciones to anon, authenticated;
