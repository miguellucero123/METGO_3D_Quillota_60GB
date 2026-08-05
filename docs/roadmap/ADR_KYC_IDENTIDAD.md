# ADR — KYC / verificación de identidad (METGO)

- **Estado:** aceptado (piloto = manual A) · implementado 2026-08-05  
- **Fecha:** 2026-08-05  
- **Contexto:** Registro actual = RUT + consentimientos + email verify. Antes de cobro real / DTE SII hace falta decidir el nivel de identidad del representante.

## Opciones

| Opción | Descripción | Pros | Contras |
|--------|-------------|------|---------|
| **A — Manual** | Ops revisa RUT/razón social (planilla o ticket) y marca `org.kyc_status=verified` | Rápido de implementar; sin proveedor | No escala; subjetivo |
| **B — Proveedor** | Integrar verificador (p. ej. TocToc / Regcheq / similar) vía API | Automatizable; audit trail | Costo por verificación; PII extra |
| **C — ClaveÚnica** | Login/vinculación con ClaveÚnica (estado chileno) | Alta confianza legal | Integración compleja; alcance ciudadano ≠ empresa |

## Decisión (piloto)

1. **Corto plazo (piloto 15 días / Starter mock):** **A — Manual** ✅  
   - Campo `orgs.kyc_status` ∈ `pending|verified|rejected` (migración `20260805200000_orgs_kyc_status.sql`).  
   - Gate opcional: `METGO_KYC_GATE_PAID=1` bloquea checkout/webhook a starter/pro/enterprise si no `verified`.  
   - Ops: `POST /api/auth/ops/kyc` + admin JWT o `CRON_SECRET`.  
2. **Cuando haya cobro Stripe real:** evaluar **B** si el volumen > ~20 orgs/mes; si no, mantener A.  
3. **ClaveÚnica (C):** solo si un cliente enterprise o requisito legal lo exige; no bloquear MVP.

## Checklist ops (revisión manual)

1. Recibir registro (email + RUT + razón social en cuenta / soporte).  
2. Contrastar RUT/razón (SII público / ficha cliente).  
3. `POST /api/auth/ops/kyc` con `{ "org_id", "kyc_status": "verified", "notes": "…" }` + `X-Cron-Token`.  
4. Si rechazo: `kyc_status=rejected` + nota; el trial sigue; no cobro.  
5. Activar gate en Render solo cuando se cobre de verdad: `METGO_KYC_GATE_PAID=1`.

## Consecuencias

- B/C no en esta iteración.  
- SII (boleta/factura) exige KYC al menos nivel A antes de emisión.

## Relacionado

- [`PLAN_PENDIENTES_POST_LANDINGS_IDENTITY.md`](PLAN_PENDIENTES_POST_LANDINGS_IDENTITY.md) B6/B7  
- [`REGISTRO_IDENTITY_Y_SII.md`](REGISTRO_IDENTITY_Y_SII.md)  
- [`FASE_SEGURIDAD_DT_AUTH.md`](FASE_SEGURIDAD_DT_AUTH.md)
