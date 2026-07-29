-- Permisos PostgREST service_role / authenticated lectura para identity & spati.
-- Aplicar en Supabase SQL editor si health reporta "permission denied".

GRANT SELECT ON TABLE public.faena_reglas TO service_role, authenticated, anon;
GRANT SELECT, INSERT, UPDATE ON TABLE public.usuarios_app TO service_role;
GRANT SELECT, INSERT, UPDATE ON TABLE public.orgs TO service_role;
GRANT SELECT, INSERT, UPDATE ON TABLE public.suscripciones TO service_role;
GRANT SELECT, INSERT ON TABLE public.consentimientos TO service_role;
GRANT SELECT, INSERT, UPDATE ON TABLE public.spati_sitios_grua TO service_role;

-- Opcional: vistas / RL S existentes no deben bloquear service_role
ALTER TABLE IF EXISTS public.faena_reglas ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS faena_reglas_select_public ON public.faena_reglas;
CREATE POLICY faena_reglas_select_public ON public.faena_reglas
  FOR SELECT TO anon, authenticated, service_role
  USING (true);
