-- M7: lecturas IoT (observado) para modelo-vs-observado y demo faena.
-- Persistencia compartida API Render ↔ demo local (antes solo JSON local).

create table if not exists public.datos_iot (
    id uuid primary key default gen_random_uuid(),
    sensor_id text not null,
    tipo text not null,
    estacion_id text,
    valor double precision,
    unidad text,
    fuente text not null default 'iot_api',
    timestamp timestamptz not null default now(),
    created_at timestamptz not null default now()
);

create index if not exists datos_iot_estacion_ts_idx
    on public.datos_iot (estacion_id, timestamp desc);

create index if not exists datos_iot_fuente_ts_idx
    on public.datos_iot (fuente, timestamp desc);

comment on table public.datos_iot is
    'Lecturas IoT (M7). fuente=iot_api|m7_demo|iot_simulado';

grant select, insert, update, delete on public.datos_iot to service_role;
grant select on public.datos_iot to anon, authenticated;

alter table public.datos_iot enable row level security;

drop policy if exists datos_iot_select_public on public.datos_iot;
create policy datos_iot_select_public
    on public.datos_iot
    for select
    to anon, authenticated
    using (true);
