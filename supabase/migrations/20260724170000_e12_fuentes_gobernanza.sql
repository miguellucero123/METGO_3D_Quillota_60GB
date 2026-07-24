-- E12 — Gobernanza de fuentes de datos (licencia, frescura, cobertura por sitio).

create table if not exists public.fuentes (
    id text primary key,
    sitio text,
    proveedor text not null,
    nombre text not null,
    tipo_dato text not null default 'modelo',
    licencia text,
    url text,
    frescura_sla_h integer,
    cobertura text,
    estado text not null default 'activo',
    notas text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint fuentes_sitio_fk
        foreign key (sitio) references public.sitios (slug) on delete set null,
    constraint fuentes_tipo_dato_chk
        check (tipo_dato in ('observado', 'pronostico', 'modelo', 'reanalisis', 'mixto')),
    constraint fuentes_estado_chk
        check (estado in ('activo', 'pendiente', 'degradado', 'retirado'))
);

create index if not exists fuentes_sitio_idx on public.fuentes (sitio);
create index if not exists fuentes_estado_idx on public.fuentes (estado);

comment on table public.fuentes is
    'Catálogo de fuentes E12: licencia, SLA de frescura y cobertura por sitio';
comment on column public.fuentes.frescura_sla_h is
    'Máximo de horas aceptable entre actualizaciones (SLO de frescura)';

grant select, insert, update, delete on public.fuentes to service_role;
grant select on public.fuentes to authenticated;
grant select on public.fuentes to anon;

alter table public.fuentes enable row level security;

drop policy if exists fuentes_select_public on public.fuentes;
create policy fuentes_select_public
    on public.fuentes
    for select
    to anon, authenticated
    using (true);

insert into public.fuentes (
    id, sitio, proveedor, nombre, tipo_dato, licencia, url,
    frescura_sla_h, cobertura, estado, notas
) values
(
    'openmeteo_forecast_quillota',
    'quillota',
    'openmeteo',
    'Open-Meteo Forecast',
    'pronostico',
    'CC-BY 4.0 (Open-Meteo)',
    'https://open-meteo.com/',
    6,
    'Valle de Aconcagua (5 estaciones)',
    'activo',
    'Fuente operativa principal Quillota'
),
(
    'openmeteo_archive_quillota',
    'quillota',
    'openmeteo',
    'Open-Meteo Archive (ERA5)',
    'reanalisis',
    'CC-BY 4.0 (Open-Meteo / ECMWF)',
    'https://open-meteo.com/en/docs/historical-weather-api',
    24,
    'Reanálisis ~9 km',
    'activo',
    'Históricos largos hasta integrar Agromet/DMC'
),
(
    'agromet_quillota',
    'quillota',
    'agromet_inia',
    'Agromet INIA',
    'observado',
    'Uso sujeto a registro INIA',
    'https://agromet.inia.cl/',
    3,
    'Estaciones físicas valle (códigos pendientes)',
    'pendiente',
    'E12: completar códigos en fuentes_oficiales_chile.py'
),
(
    'dmc_quillota',
    'quillota',
    'dmc',
    'DMC Chile',
    'observado',
    'Datos oficiales DMC',
    'https://www.meteochile.gob.cl/',
    3,
    'Red sinóptica (códigos pendientes)',
    'pendiente',
    'E12 stub'
),
(
    'openmeteo_cams_copiapo',
    'copiapo',
    'openmeteo_cams',
    'Open-Meteo Air Quality (CAMS)',
    'modelo',
    'CC-BY 4.0 (Open-Meteo / CAMS)',
    'https://open-meteo.com/en/docs/air-quality-api',
    3,
    'Airshed Copiapó / Tierra Amarilla',
    'activo',
    'Fuente operativa E7 hasta SINCA observado'
),
(
    'sinca_mma_copiapo',
    'copiapo',
    'sinca_mma',
    'SINCA MMA Chile',
    'observado',
    'Datos públicos MMA (portal SINCA)',
    'https://sinca.mma.gob.cl',
    24,
    'Copiapó, Paipote, Tierra Amarilla',
    'pendiente',
    'Validación de sesgo vs CAMS (E12). Completar sinca_id + CSV/scraper.'
),
(
    'openmeteo_cams_mantos',
    'mantos_blancos',
    'openmeteo_cams',
    'Open-Meteo Air Quality (CAMS)',
    'modelo',
    'CC-BY 4.0 (Open-Meteo / CAMS)',
    'https://open-meteo.com/en/docs/air-quality-api',
    3,
    'Puntos de faena Mantos Blancos',
    'activo',
    'Apoyo a ventanas operacionales E8'
),
(
    'openmeteo_forecast_paine',
    'paine',
    'openmeteo',
    'Open-Meteo Forecast',
    'pronostico',
    'CC-BY 4.0 (Open-Meteo)',
    'https://open-meteo.com/',
    6,
    'Torres del Paine',
    'activo',
    'Criósfera / meteo Paine'
)
on conflict (id) do update set
    nombre = excluded.nombre,
    tipo_dato = excluded.tipo_dato,
    licencia = excluded.licencia,
    url = excluded.url,
    frescura_sla_h = excluded.frescura_sla_h,
    cobertura = excluded.cobertura,
    estado = excluded.estado,
    notas = excluded.notas,
    updated_at = now();
