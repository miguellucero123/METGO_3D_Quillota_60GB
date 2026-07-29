-- M9: umbrales izaje por faena/cliente + estado de alertas SPATI.

alter table public.spati_sitios_grua
  add column if not exists umbrales_json jsonb not null default '{}'::jsonb;

alter table public.spati_sitios_grua
  add column if not exists alertas_destino jsonb not null default '{}'::jsonb;

comment on column public.spati_sitios_grua.umbrales_json is
  'Override umbrales SPATI (km/h): verde_max, amarillo_min, naranja_min, rojo_min, flag_critico';
comment on column public.spati_sitios_grua.alertas_destino is
  'Destinos alertas: {emails:[], webhook_url, nivel_minimo}';

create table if not exists public.spati_alert_state (
  sitio_slug text primary key references public.spati_sitios_grua (slug) on delete cascade,
  ultimo_nivel smallint not null default 0 check (ultimo_nivel between 0 and 3),
  ultimo_notificado_en timestamptz,
  ultimo_valid_time timestamptz,
  updated_at timestamptz not null default now()
);

grant select, insert, update, delete on public.spati_alert_state to service_role;
grant select on public.spati_alert_state to anon, authenticated;

alter table public.spati_alert_state enable row level security;

drop policy if exists spati_alert_state_select_public on public.spati_alert_state;
create policy spati_alert_state_select_public
  on public.spati_alert_state for select to anon, authenticated using (true);
