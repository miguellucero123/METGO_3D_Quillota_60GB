# Runbook brechas — 72 horas (METGO)

Ver plan: `PLAN_LEY_21719_METGO.md` §4.

## Contactos
| Rol | Quién | Canal |
|-----|-------|-------|
| DPD interino | Miguel Lucero | miguel.lucero@metgo3d.com |
| Técnico seguridad | Co-fundador (completar nombre) | email / WhatsApp |

## Minutos 0–60
1. Confirmar incidente (no falso positivo).  
2. Contener: rotar secretos listados en `incidentes/PLANTILLA_INCIDENTE.md`.  
3. Abrir ticket con la plantilla (copiar a Drive/vault; no subir PII a Git).

## Horas 1–24
4. Clasificar gravedad con DPD.  
5. Si **grave**: preparar notificación a la Agencia (plazo **72 h** desde conocimiento).  
6. Comunicar a titulares afectados si procede.

## Post
7. Post-mortem en 7 días.  
8. Actualizar RAT / controles (R1–R12).

## Comandos útiles (ops)
```powershell
# Health API
curl https://metgo-api.onrender.com/api/health

# Dry-run retención audit
curl "https://metgo-api.onrender.com/api/cron/compliance/purge-audit?token=$env:CRON_SECRET&dry_run=1"
```
