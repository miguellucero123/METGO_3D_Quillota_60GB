-- E7 — Copiapó dispersión de contaminantes:
-- amplía la malla del airshed a 7 puntos (≈15 km) y agrega la tabla horaria
-- de meteorología de dispersión (inversión térmica, capa límite, viento,
-- nubosidad baja / niebla costera) para 24/48/72 h, 7 días y proyección 16-30 d.

insert into public.estaciones (id, nombre, sitio, lat, lon) values
  ('chamonate',        'Chamonate',        'copiapo', -27.2610, -70.4470),
  ('la_chimba',        'La Chimba',        'copiapo', -27.3300, -70.3100),
  ('punta_del_cobre',  'Punta del Cobre',  'copiapo', -27.4400, -70.2100),
  ('nantoco',          'Nantoco',          'copiapo', -27.5600, -70.2400)
on conflict (id) do update set
  nombre = excluded.nombre,
  sitio = excluded.sitio,
  lat = excluded.lat,
  lon = excluded.lon;

-- Meteorología de dispersión por estación (horaria / diaria / proyección).
create table if not exists public.aire_dispersion (
    id bigint generated always as identity primary key,
    estacion_id text not null references public.estaciones (id),
    fecha_hora timestamptz not null,
    horizonte text not null default 'horaria',      -- horaria | diaria | proyeccion
    temp_2m double precision,
    temp_925hpa double precision,
    temp_850hpa double precision,
    gradiente_termico double precision,             -- °C (temp_925hpa - temp_2m); >0 = inversión
    inversion boolean,
    inversion_intensidad double precision,          -- °C
    altura_capa_limite double precision,            -- m (boundary layer height, si disponible)
    viento_velocidad double precision,              -- m/s
    viento_direccion double precision,              -- °
    viento_racha double precision,                  -- m/s
    viento_categoria text,                          -- calma|flojo|leve|moderado|favorable|fuerte
    nubosidad_baja double precision,                -- %
    visibilidad double precision,                   -- km
    niebla boolean,
    tipo_nubosidad text,                            -- niebla|neblina|estratos|despejado
    humedad_relativa double precision,              -- %
    indice_dispersion double precision,             -- 0-100 (mayor = mejor dispersión)
    potencial_dispersion text,                      -- muy_baja|baja|moderada|buena|muy_buena
    alerta_dispersion boolean,                      -- true si acumulación probable
    confianza text not null default 'alta',         -- alta|media|baja (proyección climatológica = baja)
    fuente text not null default 'openmeteo_forecast',
    tipo_dato text not null default 'pronostico',   -- pronostico|proyeccion
    created_at timestamptz not null default now(),
    unique (estacion_id, fecha_hora, horizonte, fuente)
);

create index if not exists aire_dispersion_estacion_fecha_idx
    on public.aire_dispersion (estacion_id, horizonte, fecha_hora desc);

create index if not exists aire_dispersion_alerta_idx
    on public.aire_dispersion (alerta_dispersion, fecha_hora desc)
    where alerta_dispersion is true;

comment on table public.aire_dispersion is 'Meteorología de dispersión de contaminantes (E7 Copiapó): inversión, capa límite, viento, niebla costera';
comment on column public.aire_dispersion.horizonte is 'horaria (72 h) | diaria (7 d) | proyeccion (16-30 d, climatología)';
comment on column public.aire_dispersion.gradiente_termico is '°C entre 925 hPa y 2 m; positivo indica inversión térmica';
comment on column public.aire_dispersion.potencial_dispersion is 'muy_baja|baja|moderada|buena|muy_buena según índice de ventilación';

grant select on public.aire_dispersion to anon, authenticated;
