# Requisitos pendientes (acciones humanas / negocio)

Actualizado: 2026-09-05 · Plan continuidad: `config/PLAN_CONTINUIDAD_IMPLEMENTACION.md`

## Obligatorio para cerrar fase compliance Oct

| # | Requisito | Estado código | Acción tuya |
|---|-----------|---------------|-------------|
| R4 A5–A6 | MFA Zoho + WP | Checklist listo | Completar en `SESION_R4_R7_HOY.md` (A1–A4 ya ON) |
| R7 | Drill backup documental | Runbook + acta plantilla | Ver Backups Supabase + acta en vault |
| R8/R9 UI | Export / olvido | **Hecho en Cuenta** (SPA) | Probar en `/cuenta` tras deploy Pages |
| R12 MFA | Inventario endpoints | CSV existe | Marcar `mfa` → `totp` en A1–A4 |

## Condicional (activar cuando aplique)

| Requisito | Cómo |
|-----------|------|
| Turnstile | Widget CF → `METGO_TURNSTILE_SECRET` + site key en Render; FE ya cableado |
| Stripe | Solo al primer cobro |
| Auto-registro público | Solo con Turnstile + `METGO_ALLOW_SELF_REGISTER=1` |
| Inventario parte 2 | Limache/Olmué, INIA La Cruz, coords SINCA, Spence — integrar como p1 |
| CSV/ETL DMC·SINCA | `METGO_*_CSV_DIR` + cron sincronizar; IDs ya en Render |
| Agromet IDs | Cuando existan códigos INIA → `METGO_AGROMET_IDS` |

## Ya cerrado en repo / prod

R1, R2 runbook, R3 decisión, R4 A1–A4 (GitHub/CF/Render/Supabase), R5, R6, R8 API, R9 API, R10 legales, RAT v0, DPD, Encargado B2B, R12 plantilla, derechos UI, E12 multi-fuente + inventario p1 + IDs DMC/SINCA en Render, CI verde (`7e56277`).

## Verificación rápida

```powershell
python scripts/ops/check_prod_health_flags.py
gh run list --limit 3
```
