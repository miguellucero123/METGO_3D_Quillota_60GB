# Procedimiento — derechos de titulares (Ley 21.719)

**DPD interino:** Miguel Lucero · miguel.lucero@metgo3d.com  
**Canales:** producto autenticado · correo DPD · (futuro) formulario WP

## Derechos y cómo ejercerlos

| Derecho | Canal preferente | Plazo interno |
|---------|------------------|---------------|
| Acceso / portabilidad | SPA → **Cuenta** → “Descargar mis datos” (`GET /api/auth/me/export`) | Inmediato |
| Cancelación / olvido | SPA → **Cuenta** → escribir `ELIMINAR` (`DELETE /api/auth/me/delete`) | Inmediato técnico |
| Rectificación | Correo DPD o soporte (edición de perfil si existe) | ≤ 15 días hábiles |
| Oposición / limitación | Correo DPD | ≤ 15 días hábiles |
| Revocación consentimiento marketing | Correo DPD (no hay newsletter automatizado aún) | ≤ 5 días |

Políticas públicas: https://metgo3d.com/privacidad/ · https://metgo3d.com/terminos/

## Flujo interno (correo)

1. Registrar solicitud (fecha, canal, email del titular) en vault — **sin** pegar PII extra en Git.  
2. Verificar identidad (mismo email de cuenta o documento razonable).  
3. Ejecutar vía API autenticada o script ops con service_role solo si el titular no puede entrar.  
4. Responder al titular con resultado.  
5. Si es brecha, derivar a `RUNBOOK_BRECHAS_72H.md`.

## Evidencia

- `audit_auth` (accesos)  
- Flags de consentimiento en registro  
- Acta si hubo intervención manual
