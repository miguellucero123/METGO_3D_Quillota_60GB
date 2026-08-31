# Cuadro de fases METGO — estado y pendientes

> **Corte:** 2026-08-05 · Documento vivo.  
> Plan de mejoras: [`PLAN_TRABAJO_MEJORAS.md`](PLAN_TRABAJO_MEJORAS.md)  
> Relacionado: [`README.md`](README.md) · [`CHECKLIST_E12.md`](CHECKLIST_E12.md) · [`PLAN_MAESTRO_METGO_MULTISITIO.md`](PLAN_MAESTRO_METGO_MULTISITIO.md)

## Resumen

| Estado | Cantidad | Significado |
|--------|----------|-------------|
| **Hecho** | 1–10, S0–S4, M1–M7, M10, E11, landings, `/cuenta`, invite API/UI | Código + usable |
| **Parcial** | S5, M9, M8 CSV, E12.1 | Código listo; falta smoke mail + destinos UI + keys prod |
| **Ops manual** | Stripe, OpenMeteo key, IDs SINCA / Agromet / DMC | No se cierra solo con commits |
| **Pendiente** | KYC ADR, SII DTE, retrain prod | Producto / contabilidad |

---

## 1. Escalamiento MVP (fases 1–10)

| Fase | Entrega | Estado | Falta |
|------|---------|--------|-------|
| 1.x | OpenAPI, CI, health, caché | ✅ Hecho | — |
| 2–3 | Producto + escala | ✅ Hecho | — |
| 4–5 | Integración 01–12 + hub Vue | ✅ Hecho | — |
| 6 | ETL nocturno | ✅ Hecho | — |
| 7–8 | MQTT + workers ML | ✅ Hecho | — |
| 9 | Notificaciones | ✅ Hecho | SMTP real opcional en Render |
| 10 | Prometheus / TLS / ML deep | ✅ Hecho | — |

---

## 2. Auth / suscripción multi-sitio (S0–S5)

| Fase | Entrega | Estado | Falta |
|------|---------|--------|-------|
| S0 | Diseño consentimiento + precios | ✅ | — |
| S1 | Identidad + access + UI faena | ✅ | — |
| S2 | Billing mock + cuenta + verify | ✅ | — |
| S3 | Cutover prod (código) | 🔶 Ops | SMTP, Stripe, `METGO_PII_KEK`, retirar demos |
| S4 | Entitlements UI | ✅ | — |
| S4.1 | Hub por membresía | ✅ | — |
| S5 | Ops prod + M10 | 🔶 Parcial | Credenciales Render; **M10 código OK** |

Checklist: [`CHECKLIST_AUTH_PROD.md`](CHECKLIST_AUTH_PROD.md)

---

## 3. Minería SPATI (M1–M10)

| Fase | Entrega | Estado | Falta |
|------|---------|--------|-------|
| M1–M5 | Catálogo → paquete → MVO | ✅ | — |
| M6 | CSV + PDF ejecutivo A4 | ✅ | — |
| M7 | Demo observado + deploy | ✅ prod | — |
| M8 | SINCA/CSV + estaciones FK | 🔶 Parcial | Estaciones en Supabase OK; falta `METGO_SINCA_CSV_DIR` + sync en Render |
| M9 | Umbrales + alertas + destinos UI | 🔶 Parcial | `CRON_SECRET` en GitHub; destinos en Supabase prod |
| M10 | Board `/ops` multi-faena | ✅ MVP | Pulido opcional |

---

## 4. Infra / plataforma (huecos abiertos)

| Ítem | Estado | Falta |
|------|--------|-------|
| `GRANT` identity (`usuarios_app`, etc.) | ✅ Hecho | Seed demo + grants 2026-07-31 |
| Open-Meteo API key | 🔶 Parcial | `METGO_OPENMETEO_API_KEY` (evitar 429) |
| **E11** PWA / a11y / i18n | ✅ Slice 1–2 | PWA, i18n, Lighthouse a11y CI ≥90 |
| **E12** datos oficiales + ML | 🔶 E12.1 | Fallback CSV ejemplos + `e12_ops` en health; keys prod pendientes |

---

## 5. Prioridad de lo que falta (acción humana)

### P0 — esta semana
1. **Render:** `METGO_SMTP_*`, `STRIPE_*` (o aceptar mock), `METGO_PII_KEK`, `METGO_EMAIL_DEV=0`
2. ~~Supabase GRANT~~ — OK si `health.supabase_error` vacío (ya verificado)

**Lista única de pasos:** [`PASOS_PENDIENTES_OPS.md`](PASOS_PENDIENTES_OPS.md) · detalle: [`GUIA_ARRANQUE_OPS_P0.md`](GUIA_ARRANQUE_OPS_P0.md)

### P1 — cierre M8/M9 ops
3. CSV en `METGO_SINCA_CSV_DIR` (ejemplos en `docs/ejemplos/sinca_csv/`) + `POST …/sync` SINCA
4. Secret **`CRON_SECRET`** en GitHub Actions (= Render) para workflow `spati-alertas-cron.yml`
5. Guardar destinos de alerta desde UI `/umbrales` (persiste en Supabase si hay fila)

### P2 — calidad
6. `METGO_OPENMETEO_API_KEY`
7. E12 resto: IDs SINCA/Agromet/DMC en Render + retrain (ver [`CHECKLIST_E12.md`](CHECKLIST_E12.md))

---

## 6. Ya no hace falta “seguir codeando” para

- Board ops M10 (`/ops`)
- Entitlements / hub membresía
- PDF informe ejecutivo
- Edición `alertas_destino` por faena
- Cron YAML de alertas izaje (falta solo el secret)
- Estaciones SPATI en Supabase (M8 filas)
- E11: PWA + i18n ES/EN + Lighthouse a11y CI
- E12.1: sync SINCA/DMC/Agromet desde CSV de ejemplo del repo

El siguiente valor: **ops producción** (SMTP, CSV diario real, IDs oficiales) + retrain ML con observado.

## Fase documento

**Cuadro de estado** · DT-auth-sub / minería · ops P0.
