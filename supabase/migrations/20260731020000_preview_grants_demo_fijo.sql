-- Grants identity + plan preview (seed demo fija OBSOLETO — retirado 2026-08)
-- Aplicar en Supabase → SQL Editor → Run (proyecto ylivhjigvxqzpzchllte)
-- Corrige: PostgREST 403 permission denied on usuarios_app
-- Demo: ver 20260804160000_remove_demo_ventora.sql

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
-- 3) Seed demo fijo — retirado (no recrear demo@ventora.demo)
-- ---------------------------------------------------------------------------

-- Regla mínima izaje para quebrada_blanca (si aún no existe)
INSERT INTO public.faena_reglas (faena, sistema, enabled, plan_minimo, config)
VALUES
  ('quebrada_blanca', 'izaje', true, 'trial', '{"tabs":["panel","ahora"]}'::jsonb),
  ('quebrada_blanca', 'ambiente', true, 'pro', '{"tabs":["ambiente"]}'::jsonb),
  ('quebrada_blanca', 'dron', true, 'pro', '{"tabs":["dron"]}'::jsonb),
  ('quebrada_blanca', 'ops', true, 'pro', '{"tabs":["umbrales"]}'::jsonb)
ON CONFLICT (faena, sistema) DO NOTHING;
