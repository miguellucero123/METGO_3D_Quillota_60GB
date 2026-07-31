-- Grants identity + plan preview + seed demo fija VENTORA
-- Aplicar en Supabase → SQL Editor → Run (proyecto ylivhjigvxqzpzchllte)
-- Corrige: PostgREST 403 permission denied on usuarios_app

-- ---------------------------------------------------------------------------
-- 1) Permisos service_role (API Flask)
-- ---------------------------------------------------------------------------
GRANT SELECT ON TABLE public.faena_reglas TO service_role, authenticated, anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.usuarios_app TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.orgs TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.suscripciones TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.entitlements TO service_role;
GRANT SELECT, INSERT ON TABLE public.consentimientos TO service_role;
GRANT SELECT, INSERT ON TABLE public.audit_auth TO service_role;
GRANT SELECT, INSERT, UPDATE ON TABLE public.spati_sitios_grua TO service_role;

ALTER TABLE IF EXISTS public.faena_reglas ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS faena_reglas_select_public ON public.faena_reglas;
CREATE POLICY faena_reglas_select_public ON public.faena_reglas
  FOR SELECT TO anon, authenticated, service_role
  USING (true);

-- ---------------------------------------------------------------------------
-- 2) Permitir plan_code = preview
-- ---------------------------------------------------------------------------
ALTER TABLE public.suscripciones DROP CONSTRAINT IF EXISTS suscripciones_plan_code_check;
ALTER TABLE public.suscripciones
  ADD CONSTRAINT suscripciones_plan_code_check
  CHECK (plan_code IN ('trial', 'starter', 'pro', 'enterprise', 'preview'));

-- ---------------------------------------------------------------------------
-- 3) Seed demo fijo: demo@ventora.demo / DemoVentora1!
--    (hash scrypt N=16384; solo Ahora + Panel)
-- ---------------------------------------------------------------------------
INSERT INTO public.orgs (id, sitio, faena, razon_social_enc, rut_enc, giro)
VALUES (
  'a0000000-0000-4000-8000-000000000001',
  'spati',
  'quebrada_blanca',
  'v1.rY_iUCAKpZ_s2sNKB5DLPrz8YuBaHbu40RfEMh4BM-qkEBe5ogG5BQ==',
  'v1.AAH8Lo_4vwAC1nvbKbZiTPwgUQNW59f7_i0ndaMHqx9QrSL1V7Hc-Q==',
  'demo'
)
ON CONFLICT (id) DO UPDATE SET
  faena = EXCLUDED.faena,
  giro = EXCLUDED.giro;

INSERT INTO public.usuarios_app (
  id, email_norm, password_hash, nombres_enc, apellidos_enc,
  org_id, sitio, faena, role, email_verified_at, status
)
VALUES (
  'a0000000-0000-4000-8000-000000000002',
  'demo@ventora.demo',
  'scrypt$16384$rdCuYh2OHhIMNzZfH-HW-PuPvYJM0v_R0lhOozTl_41XDWfL62Livc66qYft9IZV',
  'v1.0EruYly0kcdU9Y1gZy-I2ATCaFiY1YAS5MTiJYdMdyk=',
  'v1.mejpBrkKr5gUjgkQcrJF03ypFi3wvtfVRq_sIVSwZ2H0asU=',
  'a0000000-0000-4000-8000-000000000001',
  'spati',
  'quebrada_blanca',
  'operador',
  now(),
  'active'
)
ON CONFLICT (email_norm, sitio, faena) DO UPDATE SET
  password_hash = EXCLUDED.password_hash,
  org_id = EXCLUDED.org_id,
  status = 'active',
  email_verified_at = now(),
  role = 'operador';

INSERT INTO public.suscripciones (
  id, org_id, sitio, faena, plan_code, status, current_period_end, seats, metadata
)
VALUES (
  'a0000000-0000-4000-8000-000000000003',
  'a0000000-0000-4000-8000-000000000001',
  'spati',
  'quebrada_blanca',
  'preview',
  'trialing',
  now() + interval '30 days',
  1,
  '{"preview": true, "fixed_demo": true, "auto_delete": false}'::jsonb
)
ON CONFLICT (org_id) DO UPDATE SET
  plan_code = 'preview',
  status = 'trialing',
  current_period_end = now() + interval '30 days',
  faena = EXCLUDED.faena,
  metadata = EXCLUDED.metadata;

INSERT INTO public.entitlements (suscripcion_id, feature_key, enabled)
VALUES
  ('a0000000-0000-4000-8000-000000000003', 'panel', true),
  ('a0000000-0000-4000-8000-000000000003', 'ahora', true)
ON CONFLICT (suscripcion_id, feature_key) DO UPDATE SET enabled = true;

-- Regla mínima izaje para quebrada_blanca (si aún no existe)
INSERT INTO public.faena_reglas (faena, sistema, enabled, plan_minimo, config)
VALUES
  ('quebrada_blanca', 'izaje', true, 'trial', '{"tabs":["panel","ahora"]}'::jsonb),
  ('quebrada_blanca', 'ambiente', true, 'pro', '{"tabs":["ambiente"]}'::jsonb),
  ('quebrada_blanca', 'dron', true, 'pro', '{"tabs":["dron"]}'::jsonb),
  ('quebrada_blanca', 'ops', true, 'pro', '{"tabs":["umbrales"]}'::jsonb)
ON CONFLICT (faena, sistema) DO NOTHING;
