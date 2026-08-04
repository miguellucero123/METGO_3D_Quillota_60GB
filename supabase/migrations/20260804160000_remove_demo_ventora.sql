-- Retirar cuenta demo fija SPATI/VENTORA (demo@ventora.demo)
-- Aplicar en Supabase → SQL Editor → Run
-- Tras esto: login con la clave de demostración debe fallar.

-- Entitlements de la suscripción demo
DELETE FROM public.entitlements
WHERE suscripcion_id IN (
  SELECT id FROM public.suscripciones
  WHERE org_id = 'a0000000-0000-4000-8000-000000000001'
     OR org_id IN (
       SELECT org_id FROM public.usuarios_app
       WHERE email_norm = 'demo@ventora.demo' AND sitio = 'spati'
     )
);

DELETE FROM public.suscripciones
WHERE org_id = 'a0000000-0000-4000-8000-000000000001'
   OR org_id IN (
     SELECT org_id FROM public.usuarios_app
     WHERE email_norm = 'demo@ventora.demo' AND sitio = 'spati'
   );

DELETE FROM public.usuarios_app
WHERE email_norm = 'demo@ventora.demo'
   OR id = 'a0000000-0000-4000-8000-000000000002'
   OR org_id = 'a0000000-0000-4000-8000-000000000001';

DELETE FROM public.orgs
WHERE id = 'a0000000-0000-4000-8000-000000000001'
   OR (sitio = 'spati' AND giro = 'demo' AND id::text LIKE 'a0000000-%');
