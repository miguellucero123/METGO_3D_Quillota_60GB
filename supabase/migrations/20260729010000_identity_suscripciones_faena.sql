-- Identity comercial multi-producto + faena (S1)
-- Proyecto: mismo Supabase (sin Auth IdP). PII cifrada en app (columnas *_enc).

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------------
-- Orgs / usuarios
-- ---------------------------------------------------------------------------
create table if not exists public.orgs (
  id uuid primary key default gen_random_uuid(),
  sitio text not null,
  faena text,
  razon_social_enc text not null,
  rut_enc text not null,
  giro text,
  created_at timestamptz not null default now(),
  unique (sitio, faena, rut_enc)
);

create index if not exists orgs_sitio_faena_idx on public.orgs (sitio, faena);

create table if not exists public.usuarios_app (
  id uuid primary key default gen_random_uuid(),
  email_norm text not null,
  password_hash text not null,
  nombres_enc text not null,
  apellidos_enc text not null,
  telefono_enc text,
  org_id uuid not null references public.orgs (id) on delete cascade,
  sitio text not null,
  faena text,
  role text not null default 'operador'
    check (role in ('admin', 'agronomo', 'operador', 'lectura')),
  email_verified_at timestamptz,
  status text not null default 'pending'
    check (status in ('pending', 'active', 'suspended')),
  created_at timestamptz not null default now(),
  unique (email_norm, sitio, faena)
);

create index if not exists usuarios_app_sitio_faena_idx
  on public.usuarios_app (sitio, faena);

create table if not exists public.consentimientos (
  id uuid primary key default gen_random_uuid(),
  usuario_id uuid not null references public.usuarios_app (id) on delete cascade,
  tipo text not null
    check (tipo in ('almacenamiento_datos', 'tos', 'privacy', 'veracidad', 'marketing')),
  version text not null,
  accepted_at timestamptz not null default now(),
  ip_hash text,
  unique (usuario_id, tipo, version)
);

create table if not exists public.suscripciones (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references public.orgs (id) on delete cascade,
  sitio text not null,
  faena text,
  plan_code text not null
    check (plan_code in ('trial', 'starter', 'pro', 'enterprise')),
  status text not null default 'trialing'
    check (status in ('trialing', 'active', 'past_due', 'canceled')),
  stripe_customer_id text,
  stripe_subscription_id text,
  current_period_end timestamptz,
  seats int not null default 1,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (org_id)
);

create table if not exists public.entitlements (
  id uuid primary key default gen_random_uuid(),
  suscripcion_id uuid not null references public.suscripciones (id) on delete cascade,
  feature_key text not null,
  enabled boolean not null default true,
  unique (suscripcion_id, feature_key)
);

-- Reglas por minera: qué sistemas anexar y plan mínimo
create table if not exists public.faena_reglas (
  faena text not null,
  sistema text not null
    check (sistema in ('izaje', 'ambiente', 'dron', 'ops', 'aire')),
  enabled boolean not null default true,
  plan_minimo text not null default 'trial'
    check (plan_minimo in ('trial', 'starter', 'pro', 'enterprise')),
  config jsonb not null default '{}'::jsonb,
  primary key (faena, sistema)
);

create table if not exists public.audit_auth (
  id bigserial primary key,
  usuario_id uuid,
  sitio text,
  faena text,
  evento text not null,
  ip_hash text,
  ua_hash text,
  at timestamptz not null default now()
);

-- Seeds: reglas SPATI alta montaña (todas con izaje; dron/umbrales por plan)
insert into public.faena_reglas (faena, sistema, enabled, plan_minimo, config)
values
  ('escondida', 'izaje', true, 'trial', '{"tabs":["panel"]}'),
  ('escondida', 'ambiente', true, 'trial', '{"tabs":["ambiente"]}'),
  ('escondida', 'dron', true, 'starter', '{"tabs":["dron"]}'),
  ('escondida', 'ops', true, 'pro', '{"tabs":["umbrales"]}'),
  ('los_bronces', 'izaje', true, 'trial', '{"tabs":["panel"]}'),
  ('los_bronces', 'ambiente', true, 'trial', '{"tabs":["ambiente"]}'),
  ('los_bronces', 'dron', true, 'starter', '{"tabs":["dron"]}'),
  ('los_bronces', 'ops', true, 'pro', '{"tabs":["umbrales"]}'),
  ('collahuasi', 'izaje', true, 'trial', '{"tabs":["panel"]}'),
  ('collahuasi', 'ambiente', true, 'trial', '{"tabs":["ambiente"]}'),
  ('collahuasi', 'dron', true, 'starter', '{"tabs":["dron"]}'),
  ('collahuasi', 'ops', true, 'pro', '{"tabs":["umbrales"]}'),
  ('andina', 'izaje', true, 'trial', '{"tabs":["panel"]}'),
  ('andina', 'ambiente', true, 'trial', '{"tabs":["ambiente"]}'),
  ('andina', 'dron', true, 'starter', '{"tabs":["dron"]}'),
  ('andina', 'ops', true, 'pro', '{"tabs":["umbrales"]}'),
  ('el_teniente', 'izaje', true, 'trial', '{"tabs":["panel"]}'),
  ('el_teniente', 'ambiente', true, 'trial', '{"tabs":["ambiente"]}'),
  ('el_teniente', 'dron', true, 'starter', '{"tabs":["dron"]}'),
  ('el_teniente', 'ops', true, 'pro', '{"tabs":["umbrales"]}')
on conflict (faena, sistema) do nothing;

comment on table public.usuarios_app is
  'Identidad METGO comercial; PII en *_enc (AES-GCM app). Login vía API Flask JWT.';
comment on table public.faena_reglas is
  'Por minera: sistemas anexables y plan mínimo (enlace /f/{faena}).';
