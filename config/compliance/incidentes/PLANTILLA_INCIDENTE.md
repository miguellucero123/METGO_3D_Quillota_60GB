# Plantilla de incidente de seguridad / brecha (Ley 21.719)

**ID:** INC-YYYYMMDD-XX  
**Fecha detección (UTC):**  
**Detectado por:** (Sentry / usuario / Render / Supabase / otro)  
**Clasificación preliminar:** baja / media / grave  

## 1. Qué pasó
- Sistemas afectados:
- Datos personales involucrados (sí/no, categorías):
- Volumen estimado:

## 2. Contención (< 4 h técnico)
- [ ] Rotar `METGO_JWT_SECRET`
- [ ] Rotar `SUPABASE` service_role / `SUPABASE_KEY`
- [ ] Rotar `CRON_SECRET` (GitHub + Render)
- [ ] Rotar `METGO_PII_KEK` (dejar anterior en `METGO_PII_KEK_PREV`)
- [ ] Revisar `audit_auth` últimas 72 h
- [ ] Deshabilitar registro público si aplica

## 3. Notificación legal (DPD)
- [ ] ¿Vulneración grave? (criterio legal)
- [ ] Agencia notificada dentro de **72 h** (fecha/hora):
- [ ] Titulares avisados (sí/no/motivo):

## 4. Evidencia
- Logs adjuntos / IDs:
- Commits / deploys relacionados:

## 5. Post-mortem
- Causa raíz:
- Acciones correctivas:
- Fecha cierre:
