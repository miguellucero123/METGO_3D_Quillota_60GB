# Decisión R3 — SELECT `anon` en tablas meteo / aire / spati

**Fecha:** 2026-09-04  
**Estado:** **Aceptado con riesgo residual** (revisar ante primer contrato B2B sensible)  
**Owner decisión:** DPD interino + técnico

## Contexto

Varias tablas técnicas tienen políticas `SELECT` para roles `anon` / `authenticated` (migraciones E7/E8/E9 y hardening advisor). Contienen series ambientales/operativas **sin PII** (estaciones, contaminantes, NWP, ventanas). Identity (`usuarios_app`, consentimientos, etc.) ya es **deny** a clientes (R1/RLS).

## Decisión

**Mantener SELECT público (`anon`) en series técnicas no-PII** mientras:

1. No haya datos de operadores/personas en esas tablas.  
2. El valor de producto (landing, demos Pages, mapas) dependa de lecturas sin JWT.  
3. Escrituras sigan solo por `service_role` / API.

**No** abrir identity ni tablas con PII a `anon`.

## Riesgos aceptados

| Riesgo | Mitigación |
|--------|------------|
| Scraping de series operativas | Rate limit API; volumen acotado; sin secretos en filas |
| Cliente B2B exige exclusividad | Contrato Encargado + migración a JWT-only por tenant |
| Mezcla accidental de PII en tablas públicas | Checklist PR + review migraciones |

## Trigger de revisión (cerrar anon)

Reabrir esta decisión si ocurre cualquiera:

- Primer cliente industrial exige datos no públicos.  
- Se detecta columna o join con identificadores personales.  
- Abuso de cuota Supabase por scrapers.

**Acción técnica entonces:** revocar policies `*_select_public` → solo `service_role` + API JWT; actualizar RAT T8.

## Artefactos

- RAT: `RAT_METGO_v0.csv` fila T8  
- Plantilla Encargado: `CONTRATO_ENCARGADO_B2B.md`
