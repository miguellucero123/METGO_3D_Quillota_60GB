-- E7 — Copiapó calidad del aire: sitio + estaciones + tabla aire_registros.

insert into public.sitios (slug, nombre, region, dominio, estado, primary_color, center_lat, center_lon, modules) values
  (
    'copiapo',
    'METGO Copiapó',
    'Copiapó · Región de Atacama',
    'aire',
    'activo',
    '#fbbf24',
    -27.3668,
    -70.3323,
    '["meteo","aire","alertas_salud"]'::jsonb
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

insert into public.estaciones (id, nombre, sitio, lat, lon) values
  ('copiapo_centro', 'Copiapo Centro', 'copiapo', -27.3668, -70.3323),
  ('paipote', 'Paipote', 'copiapo', -27.4064, -70.2853),
  ('tierra_amarilla', 'Tierra Amarilla', 'copiapo', -27.4667, -70.2667)
on conflict (id) do update set
  nombre = excluded.nombre,
  sitio = excluded.sitio,
  lat = excluded.lat,
  lon = excluded.lon;

-- Registros de calidad del aire (ETL CAMS cada 1–3 h + SINCA diario futuro)
create table if not exists public.aire_registros (
    id bigint generated always as identity primary key,
    estacion_id text not null references public.estaciones (id),
    fecha_hora timestamptz not null,
    pm25 double precision,
    pm10 double precision,
    so2 double precision,
    no2 double precision,
    o3 double precision,
    co double precision,
    dust double precision,
    icap double precision,
    categoria text,
    fuente text not null default 'openmeteo_cams',
    tipo_dato text not null default 'modelo',
    created_at timestamptz not null default now(),
    unique (estacion_id, fecha_hora, fuente)
);

create index if not exists aire_registros_estacion_fecha_idx
    on public.aire_registros (estacion_id, fecha_hora desc);

comment on table public.aire_registros is 'Calidad del aire por estación (CAMS/SINCA), E7 Copiapó';
comment on column public.aire_registros.categoria is 'bueno|regular|alerta|preemergencia|emergencia';
comment on column public.aire_registros.tipo_dato is 'observado|pronostico|modelo';

grant select on public.aire_registros to anon, authenticated;
