# Requisitos pendientes (acciones humanas / negocio)

Actualizado: 2026-09-04 · CI verde tras gitleaks fix.

## Obligatorio para cerrar fase compliance Oct

| # | Requisito | Estado código | Acción tuya |
|---|-----------|---------------|-------------|
| R4 | MFA admin | Checklist + sesión | Activar 2FA GitHub, CF, Render, Supabase — `SESION_R4_R7_HOY.md` |
| R7 | Drill backup | Runbook + acta plantilla | Ver Backups en Supabase + guardar acta en vault |
| R8/R9 UI | Export / olvido | **Hecho en Cuenta** (SPA) | Probar en `/cuenta` tras deploy Pages |

## Condicional (activar cuando aplique)

| Requisito | Cómo |
|-----------|------|
| Turnstile | Crear widget CF (permiso Turnstile:Edit) → `METGO_TURNSTILE_SECRET` + `METGO_TURNSTILE_SITE_KEY` en Render; site key también vía `/api/.../security` config. FE ya cableado. |
| Stripe | Solo al primer cobro |
| Auto-registro público | Solo con Turnstile + `METGO_ALLOW_SELF_REGISTER=1` |
| SINCA/Agromet/DMC | IDs reales en Render (`e12_ops.pendiente`) |

## Ya cerrado en repo / prod

R1, R2 runbook, R3 decisión, R5, R6, R8 API, R9 API, R10 legales, RAT v0, DPD, Encargado B2B, R12 inventario, CI gitleaks.

## Verificación rápida

```powershell
python scripts/ops/check_prod_health_flags.py
gh run list --limit 3
```
