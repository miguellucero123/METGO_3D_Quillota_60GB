-- M4 multi-faena: estaciones meteorológicas por área (rajo/campamento/chancado/botadero).
-- Lectura pública; escritura service_role. Seed Mantos + Paipote; SPATI vía sync API.

create table if not exists public.faena_estaciones_area (
    id text primary key,
    faena_id text not null,
    nombre text not null,
    rol text not null
        check (rol in ('rajo', 'campamento', 'chancado', 'botadero', 'ruta', 'otro')),
    lat double precision not null,
    lon double precision not null,
    altitud_m double precision,
    fuente text not null default 'modelo'
        check (fuente in ('modelo', 'observado', 'seed')),
    activa boolean not null default true,
    synced_at timestamptz not null default now(),
    created_at timestamptz not null default now(),
    unique (faena_id, rol)
);

create index if not exists faena_estaciones_area_faena_idx
    on public.faena_estaciones_area (faena_id);

create index if not exists faena_estaciones_area_fuente_idx
    on public.faena_estaciones_area (fuente);

comment on table public.faena_estaciones_area is
    'Puntos meteo por área de faena (M4). fuente=modelo|observado|seed';
comment on column public.faena_estaciones_area.rol is
    'rajo|campamento|chancado|botadero|ruta|otro';

grant select, insert, update, delete on public.faena_estaciones_area to service_role;
grant select on public.faena_estaciones_area to anon, authenticated;

alter table public.faena_estaciones_area enable row level security;

drop policy if exists faena_estaciones_area_select_public on public.faena_estaciones_area;
create policy faena_estaciones_area_select_public
    on public.faena_estaciones_area
    for select
    to anon, authenticated
    using (true);

-- Seed Mantos Blancos (alineado a public.estaciones mb_*)
insert into public.faena_estaciones_area (id, faena_id, nombre, rol, lat, lon, fuente) values
  ('mb_rajo',        'mantos_blancos', 'Rajo',           'rajo',       -23.4300, -70.0600, 'seed'),
  ('mb_campamento',  'mantos_blancos', 'Campamento',     'campamento', -23.4200, -70.0500, 'seed'),
  ('mb_chancado',    'mantos_blancos', 'Chancado',       'chancado',   -23.4400, -70.0700, 'seed'),
  ('mb_ruta_acceso', 'mantos_blancos', 'Ruta de acceso', 'ruta',       -23.5000, -70.2000, 'seed')
on conflict (id) do update set
  faena_id = excluded.faena_id,
  nombre = excluded.nombre,
  rol = excluded.rol,
  lat = excluded.lat,
  lon = excluded.lon,
  fuente = excluded.fuente,
  synced_at = now();

-- Seed Paipote (ancla + puntos proxy área)
insert into public.faena_estaciones_area (id, faena_id, nombre, rol, lat, lon, fuente) values
  ('paipote',            'paipote', 'Paipote (rajo/pluma)', 'rajo',       -27.4064, -70.2853, 'seed'),
  ('paipote_campamento', 'paipote', 'Campamento',          'campamento', -27.3864, -70.3053, 'seed'),
  ('paipote_chancado',   'paipote', 'Chancado',            'chancado',   -27.4214, -70.2653, 'seed'),
  ('paipote_botadero',   'paipote', 'Botadero',            'botadero',   -27.3964, -70.2603, 'seed')
on conflict (id) do update set
  faena_id = excluded.faena_id,
  nombre = excluded.nombre,
  rol = excluded.rol,
  lat = excluded.lat,
  lon = excluded.lon,
  fuente = excluded.fuente,
  synced_at = now();
