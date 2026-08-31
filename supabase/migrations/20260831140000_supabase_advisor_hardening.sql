-- Advisor Center / Security + Performance (metgo3d Free)
-- - Identity: políticas explícitas deny (RLS ON sin policy → Info "RLS Enabled No Policy")
-- - Meteo: una sola policy SELECT (evita "Multiple Permissive Policies")
-- - set_updated_at: search_path fijo
-- - usuarios_app.org_id: índice FK

-- ---------------------------------------------------------------------------
-- 1) Identity: deny explícito anon/authenticated (service_role bypasa RLS)
-- ---------------------------------------------------------------------------
do $$
declare
  t text;
begin
  foreach t in array array[
    'orgs',
    'usuarios_app',
    'consentimientos',
    'suscripciones',
    'audit_auth',
    'entitlements'
  ]
  loop
    if to_regclass('public.' || t) is null then
      continue;
    end if;
    execute format('alter table public.%I enable row level security', t);
    execute format('drop policy if exists %I_deny_clients on public.%I', t, t);
    execute format(
      'create policy %I_deny_clients on public.%I for all to anon, authenticated using (false) with check (false)',
      t, t
    );
  end loop;
end $$;

revoke all on table public.orgs from anon, authenticated;
revoke all on table public.usuarios_app from anon, authenticated;
revoke all on table public.consentimientos from anon, authenticated;
revoke all on table public.suscripciones from anon, authenticated;
revoke all on table public.audit_auth from anon, authenticated;
revoke all on table public.entitlements from anon, authenticated;

grant all on table public.orgs to service_role;
grant all on table public.usuarios_app to service_role;
grant all on table public.consentimientos to service_role;
grant all on table public.suscripciones to service_role;
grant all on table public.audit_auth to service_role;
grant all on table public.entitlements to service_role;

-- ---------------------------------------------------------------------------
-- 2) FK index (Advisor: Unindexed foreign keys)
-- ---------------------------------------------------------------------------
create index if not exists usuarios_app_org_id_idx
  on public.usuarios_app (org_id);

create index if not exists consentimientos_usuario_id_idx
  on public.consentimientos (usuario_id);

-- ---------------------------------------------------------------------------
-- 3) Una sola policy SELECT en series meteo (quita duplicados lectura + select_public)
-- ---------------------------------------------------------------------------
do $$
declare
  t text;
begin
  foreach t in array array[
    'meteo_registros',
    'meteo_pronostico',
    'meteo_series'
  ]
  loop
    if to_regclass('public.' || t) is null then
      continue;
    end if;
    execute format('drop policy if exists %I_lectura on public.%I', t, t);
    execute format('drop policy if exists %I_select_public on public.%I', t, t);
    execute format('alter table public.%I enable row level security', t);
    execute format(
      'create policy %I_select_public on public.%I for select to anon, authenticated using (true)',
      t, t
    );
    execute format('grant select on public.%I to anon, authenticated', t);
    execute format('grant all on public.%I to service_role', t);
  end loop;
end $$;

-- ---------------------------------------------------------------------------
-- 4) Function Search Path Mutable
-- ---------------------------------------------------------------------------
create or replace function public.set_updated_at()
returns trigger
language plpgsql
set search_path = public
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

comment on function public.set_updated_at() is
  'Trigger updated_at; search_path fijo (Supabase Security Advisor).';
