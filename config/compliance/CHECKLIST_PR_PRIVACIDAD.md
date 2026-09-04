# Checklist PR — privacidad por diseño (Ley 21.719)

Antes de merge, el autor marca:

- [ ] ¿El cambio recolecta o muestra **datos personales** (email, nombre, RUT, teléfono, IP)?
- [ ] Si sí: ¿está cifrado en reposo (`pii_crypto`) y **no** se loguea en claro?
- [ ] ¿Hay consentimiento / base legal documentada o enlace a política?
- [ ] ¿Se actualizó OpenAPI / contrato API si hay campos nuevos?
- [ ] ¿El olvido (`delete_user_data`) y/o export siguen siendo posibles?
- [ ] ¿Secrets solo en Render/GitHub Secrets (nada `VITE_` con secretos)?
- [ ] ¿Si toca Supabase: migración RLS + grants service_role revisados?
- [ ] ¿Actualizar fila en RAT (`config/compliance/RAT_METGO_v0.csv`)?

Si todo “No aplica”, escribir en la descripción del PR: `Privacidad: N/A — sin PII`.
