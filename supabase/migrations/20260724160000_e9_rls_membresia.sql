-- E9 — Membresía usuario↔ sitio + RLS: escrituras solo service_role.
-- La API Flask autentica con JWT propio y escribe con service_role;
-- anon/authenticated quedan en solo lectura de series públicas.

create table if not exists public.user_sitio_membresia (
    usuario text not null,
    sitio text not null,
    role text not null default 'lectura',
    created_at timestamptz not null default now(),
    primary key (usuario, sitio),
    constraint user_sitio_membresia_sitio_fk
        foreign key (sitio) references public.sitios (slug) on delete cascade
);

create index if not exists user_sitio_membresia_sitio_idx
    on public.user_sitio_membresia (sitio);

comment on table public.user_sitio_membresia is
    'Membresía multi-tenant E9 (espejo documental; runtime demo también en sitios_auth.USER_SITIO)';

grant select, insert, update, delete on public.user_sitio_membresia to service_role;
grant select on public.user_sitio_membresia to authenticated;

alter table public.user_sitio_membresia enable row level security;

drop policy if exists user_sitio_membresia_select_authenticated on public.user_sitio_membresia;
create policy user_sitio_membresia_select_authenticated
    on public.user_sitio_membresia
    for select
    to authenticated
    using (true);

-- Seeds demo (alineados con metgo_auth / sitios_auth)
insert into public.user_sitio_membresia (usuario, sitio, role) values
    ('metgo', 'quillota', 'agronomo'),
    ('agronomo', 'quillota', 'agronomo'),
    ('operador', 'quillota', 'operador'),
    ('lector', 'quillota', 'lectura'),
    ('copiapo', 'copiapo', 'lectura'),
    ('mantos', 'mantos_blancos', 'operador'),
    ('paine', 'paine', 'lectura')
on conflict (usuario, sitio) do update set role = excluded.role;

-- Preferencias: sin escritura desde anon/authenticated (solo service_role)
revoke insert, update, delete on public.user_preferencias from anon, authenticated;
grant select on public.user_preferencias to authenticated;

-- Series de negocio: RLS + SELECT público; escritura solo service_role
do $$
declare
  t text;
begin
  foreach t in array array[
    'aire_registros',
    'aire_dispersion',
    'operaciones_ventanas',
    'meteo_registros',
    'meteo_pronostico',
    'meteo_series'
  ]
  loop
    if to_regclass('public.' || t) is not null then
      execute format('alter table public.%I enable row level security', t);
      execute format('drop policy if exists %I_select_public on public.%I', t, t);
      execute format(
        'create policy %I_select_public on public.%I for select to anon, authenticated using (true)',
        t, t
      );
      execute format('grant select on public.%I to anon, authenticated', t);
      execute format('grant all on public.%I to service_role', t);
    end if;
  end loop;
end $$;
