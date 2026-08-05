# ADR — KYC / verificación de identidad (METGO)

- **Estado:** propuesto  
- **Fecha:** 2026-08-05  
- **Contexto:** Registro actual = RUT + consentimientos + email verify. Antes de cobro real / DTE SII hace falta decidir el nivel de identidad del representante.

## Opciones

| Opción | Descripción | Pros | Contras |
|--------|-------------|------|---------|
| **A — Manual** | Ops revisa RUT/razón social (planilla o ticket) y marca `org.kyc_status=verified` | Rápido de implementar; sin proveedor | No escala; subjetivo |
| **B — Proveedor** | Integrar verificador (p. ej. TocToc / Regcheq / similar) vía API | Automatizable; audit trail | Costo por verificación; PII extra |
| **C — ClaveÚnica** | Login/vinculación con ClaveÚnica (estado chileno) | Alta confianza legal | Integración compleja; alcance ciudadano ≠ empresa |

## Decisión recomendada (piloto)

1. **Corto plazo (piloto 15 días / Starter mock):** **A — Manual**  
   - Campo `orgs.kyc_status` ∈ `pending|verified|rejected` (migración futura).  
   - Gate opcional: bloquear upgrade a plan pago si `kyc_status != verified` (feature flag).  
2. **Cuando haya cobro Stripe real:** evaluar **B** si el volumen > ~20 orgs/mes; si no, mantener A.  
3. **ClaveÚnica (C):** solo si un cliente enterprise o requisito legal lo exige; no bloquear MVP.

## Consecuencias

- No implementar C ni B en esta iteración.  
- Documentar checklist ops de revisión manual en `PASO_A_PASO_OPS_PENDIENTES.md` cuando se active el gate.  
- SII (boleta/factura) exige KYC al menos nivel A antes de emisión.

## Relacionado

- [`PLAN_PENDIENTES_POST_LANDINGS_IDENTITY.md`](PLAN_PENDIENTES_POST_LANDINGS_IDENTITY.md) B6/B7  
- [`REGISTRO_IDENTITY_Y_SII.md`](REGISTRO_IDENTITY_Y_SII.md)
