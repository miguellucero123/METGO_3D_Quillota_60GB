# Runbook R7 — Backup / restore Supabase (PITR) + drill

**Objetivo:** demostrar continuidad ante pérdida o corrupción de datos (Ley 21.719 / evidencia auditoría).  
**Owner técnico:** co-fundador seguridad · **DPD:** Miguel Lucero  
**Frecuencia:** al menos **1 drill semestral** (acta en vault; no subir dumps a Git).

## 1. Qué respaldamos

| Capa | Qué | Dónde vive | Mecanismo |
|------|-----|------------|-----------|
| Identity / producto | `usuarios_app`, orgs, consentimientos, audit_auth, suscripciones | Supabase Postgres | Backups automáticos + **PITR** (plan Pro+) |
| Series técnicas | meteo, aire, spati (no PII) | Mismo proyecto / tablas | Mismo backup |
| Secrets | JWT, PII KEK, service_role, CRON, SMTP | Render + GitHub Secrets | Rotación R2 (no backup de valores en Git) |
| Código / migraciones | esquema | Git `supabase/migrations/` | Repo |

## 2. Verificación diaria (2 min)

1. Supabase Dashboard → **Project Settings → Database → Backups**.  
2. Confirmar última copia &lt; 24 h y PITR habilitado (si el plan lo incluye).  
3. Anotar en ops board o calendario: “backup OK YYYY-MM-DD”.

Si el plan es Free sin PITR: documentar riesgo residual y prioridad de upgrade antes de clientes con PII contractual.

## 3. Restore de emergencia (pasos)

> No ejecutar en producción sin ventana acordada. Preferir **proyecto staging** clonado.

1. Declarar incidente (`incidentes/PLANTILLA_INCIDENTE.md`).  
2. Pausar escrituras críticas si es posible (mantenimiento API / `METGO_API_AUTH_REQUIRED`).  
3. En Supabase: **Backups → Restore** (punto en el tiempo o snapshot).  
4. Validar:  
   - `GET /api/health` → `supabase_client_ok`, `pii_kek_configurado`  
   - Login de cuenta de prueba  
   - Conteo filas clave (usuarios activos, orgs) vs nota pre-drill  
5. Rotar `SUPABASE` service_role **solo si** hubo exposición durante el incidente (ver R2).  
6. Post-mortem &lt; 7 días.

## 4. Drill semestral (plantilla de acta)

Copiar a Drive/vault (no Git con datos reales):

```
ACTA DRILL BACKUP METGO — fecha:
Participantes:
Proyecto Supabase (ref):
Plan backup / PITR: sí/no
Escenario: restore a staging | restore read-only | simulación documental
Inicio / fin (UTC):
RTO observado (minutos):
RPO observado (minutos de datos perdidos aceptados):
Checks health / login / export / olvido: OK/FAIL
Incidentes durante drill:
Acciones abiertas:
Firma DPD / técnico:
```

## 5. Criterio de “R7 cumplido”

- [ ] Runbook leído por DPD + técnico  
- [ ] Al menos **un** drill con acta fechada en vault  
- [ ] RTO/RPO anotados (objetivo orientativo: RTO &lt; 4 h, RPO &lt; 24 h en MVP)

## Referencias

- Dashboard: https://supabase.com/dashboard  
- Rotación secrets: `ROTACION_SECRETS_R2.md`  
- Brechas: `RUNBOOK_BRECHAS_72H.md`
