-- E8 — Mantos Blancos (Antofagasta): sitio minero + puntos de faena +
-- tabla de ventanas operacionales (semáforo por actividad para tronadura,
-- transporte e izaje según viento / ráfaga / visibilidad / precipitación).

insert into public.sitios (slug, nombre, region, dominio, estado, primary_color, center_lat, center_lon, modules) values
  (
    'mantos_blancos',
    'METGO Mantos Blancos',
    'Antofagasta · faena minera',
    'mineria',
    'activo',
    '#fb923c',
    -23.43,
    -70.06,
    '["meteo","aire","operaciones"]'::jsonb
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
  ('mb_rajo',        'Rajo',            'mantos_blancos', -23.4300, -70.0600),
  ('mb_campamento',  'Campamento',      'mantos_blancos', -23.4200, -70.0500),
  ('mb_chancado',    'Chancado',        'mantos_blancos', -23.4400, -70.0700),
  ('mb_ruta_acceso', 'Ruta de acceso',  'mantos_blancos', -23.5000, -70.2000)
on conflict (id) do update set
  nombre = excluded.nombre,
  sitio = excluded.sitio,
  lat = excluded.lat,
  lon = excluded.lon;

-- Ventanas operacionales por punto de faena (semáforo por actividad).
create table if not exists public.operaciones_ventanas (
    id bigint generated always as identity primary key,
    estacion_id text not null references public.estaciones (id),
    fecha_hora timestamptz not null,
    viento_sostenido double precision,   -- m/s
    viento_racha double precision,        -- m/s
    viento_direccion double precision,    -- °
    visibilidad double precision,         -- km
    precipitacion double precision,       -- mm/h
    uv_index double precision,
    nivel_tronadura text,                 -- verde | amarillo | rojo
    nivel_transporte text,
    nivel_izaje text,
    nivel_global text,
    fuente text not null default 'openmeteo_forecast',
    tipo_dato text not null default 'pronostico',
    created_at timestamptz not null default now(),
    unique (estacion_id, fecha_hora, fuente)
);

create index if not exists operaciones_ventanas_estacion_fecha_idx
    on public.operaciones_ventanas (estacion_id, fecha_hora desc);

create index if not exists operaciones_ventanas_global_idx
    on public.operaciones_ventanas (nivel_global, fecha_hora desc);

comment on table public.operaciones_ventanas is 'Ventanas operacionales de faena (E8 Mantos Blancos): semáforo por actividad';
comment on column public.operaciones_ventanas.nivel_global is 'peor semáforo entre actividades: verde|amarillo|rojo';

grant select on public.operaciones_ventanas to anon, authenticated;
