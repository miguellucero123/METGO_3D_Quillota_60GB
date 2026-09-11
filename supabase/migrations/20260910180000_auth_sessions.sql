-- Sesión única JWT (jti) persistente entre cold starts de Render.
-- Solo service_role (API); anon denegado.

create table if not exists public.auth_sessions (
  user_key text primary key,
  jti text not null,
  updated_at timestamptz not null default now()
);

create index if not exists auth_sessions_updated_at_idx
  on public.auth_sessions (updated_at desc);

alter table public.auth_sessions enable row level security;

revoke all on table public.auth_sessions from anon, authenticated;
grant select, insert, update, delete on table public.auth_sessions to service_role;

comment on table public.auth_sessions is
  'Último jti JWT por usuario (email/username). Invalidar sesión previa en otro dispositivo.';
