-- E8 follow-up: columnas UV / SO₂ / exposición en operaciones_ventanas.

alter table public.operaciones_ventanas
    add column if not exists nivel_exposicion_uv text,
    add column if not exists uv_index double precision,
    add column if not exists so2 double precision;

comment on column public.operaciones_ventanas.nivel_exposicion_uv is 'verde|amarillo|rojo — índice UV turno a cielo abierto';
comment on column public.operaciones_ventanas.so2 is 'µg/m³ SO2 (CAMS) al momento del sync';
