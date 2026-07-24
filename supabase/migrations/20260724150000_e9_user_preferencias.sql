-- E9 — Multi-tenant: preferencias/favoritos por usuario + sitio.
-- Escritura vía API (service_role). Lectura autenticada futura vía RLS.

create table if not exists public.user_preferencias (
    usuario text not null,
    sitio text not null,
    prefs jsonb not null default '{}'::jsonb,
    favorites jsonb not null default '[]'::jsonb,
    updated_at timestamptz not null default now(),
    created_at timestamptz not null default now(),
    primary key (usuario, sitio)
);

create index if not exists user_preferencias_sitio_idx
    on public.user_preferencias (sitio);

comment on table public.user_preferencias is 'Preferencias y favoritos por usuario+sitio (E9 multi-tenant)';
comment on column public.user_preferencias.sitio is 'Slug producto: quillota|paine|copiapo|mantos_blancos|demo';

grant select, insert, update, delete on public.user_preferencias to service_role;
grant select on public.user_preferencias to authenticated;

alter table public.user_preferencias enable row level security;

-- Lectura para rol authenticated (API Flask usa service_role y filtra en código).
drop policy if exists user_preferencias_select_own on public.user_preferencias;
create policy user_preferencias_select_authenticated
    on public.user_preferencias
    for select
    to authenticated
    using (true);
-- Trigger updated_at
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists user_preferencias_set_updated_at on public.user_preferencias;
create trigger user_preferencias_set_updated_at
    before update on public.user_preferencias
    for each row execute function public.set_updated_at();
