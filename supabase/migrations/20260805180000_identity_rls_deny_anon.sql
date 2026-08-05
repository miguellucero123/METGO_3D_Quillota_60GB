-- Identity RLS: deny anon/authenticated; solo service_role (API Render).
-- Fase DT-auth-sec / seguridad P1

ALTER TABLE IF EXISTS public.orgs ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.usuarios_app ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.consentimientos ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.suscripciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.audit_auth ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.entitlements ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.faena_reglas ENABLE ROW LEVEL SECURITY;

-- Revocar acceso amplio a roles de cliente (por si existía GRANT previo)
REVOKE ALL ON TABLE public.orgs FROM anon, authenticated;
REVOKE ALL ON TABLE public.usuarios_app FROM anon, authenticated;
REVOKE ALL ON TABLE public.consentimientos FROM anon, authenticated;
REVOKE ALL ON TABLE public.suscripciones FROM anon, authenticated;
REVOKE ALL ON TABLE public.audit_auth FROM anon, authenticated;

-- service_role bypasa RLS en Supabase; grants explícitos por claridad
GRANT ALL ON TABLE public.orgs TO service_role;
GRANT ALL ON TABLE public.usuarios_app TO service_role;
GRANT ALL ON TABLE public.consentimientos TO service_role;
GRANT ALL ON TABLE public.suscripciones TO service_role;
GRANT ALL ON TABLE public.audit_auth TO service_role;

-- Políticas deny-by-default: sin policy de SELECT/INSERT para anon/authenticated
-- (RLS enabled + sin policy = denegado). No crear policies públicas.
