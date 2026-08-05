# Pasos pendientes METGO (ops producción)

> **Corte:** 2026-08-01 · El desarrollo de fases **1–10, E11 y E12.1** está en código.  
> Lo que sigue es **configuración humana** (Render / GitHub / datos oficiales).  
> Guía detallada: [`GUIA_ARRANQUE_OPS_P0.md`](GUIA_ARRANQUE_OPS_P0.md)  
> **Inventario de claves por plataforma:** [`INVENTARIO_CLAVES_PLATAFORMAS.md`](INVENTARIO_CLAVES_PLATAFORMAS.md)  
> **Registro identity + SII:** [`REGISTRO_IDENTITY_Y_SII.md`](REGISTRO_IDENTITY_Y_SII.md)  
> **Plan condiciones/tareas pendientes:** [`PLAN_PENDIENTES_POST_LANDINGS_IDENTITY.md`](PLAN_PENDIENTES_POST_LANDINGS_IDENTITY.md)  
> **Paso a paso operativo (esta sesión):** [`PASO_A_PASO_OPS_PENDIENTES.md`](PASO_A_PASO_OPS_PENDIENTES.md)

API: `https://metgo-api.onrender.com` · SPA: `https://metgo-spati.pages.dev`

---

## Estado de fases (código)

| Bloque | Estado |
|--------|--------|
| Escalamiento MVP **1–10** | ✅ Hecho |
| Auth S0–S4.1 | ✅ Hecho |
| Minería M1–M7, M10 | ✅ Hecho |
| M8 estaciones Supabase | ✅ Hecho (CSV prod pendiente) |
| M9 código + cron YAML | ✅ Hecho (secret GitHub pendiente) |
| E11 PWA / a11y / i18n / Lighthouse | ✅ Hecho |
| E12.1 CSV ejemplos + `e12_ops` | ✅ Hecho |
| E12 resto (IDs oficiales + retrain) | 🔶 Ops / continuo |

**No hay una “fase 13” de código** pendiente para cerrar el MVP. El valor ahora es ops.

---

## Diagnóstico rápido (repetir cuando cambien env)

```powershell
$h = Invoke-RestMethod "https://metgo-api.onrender.com/api/health"
$h.s5_ops
$h.e12_ops
$h.supabase_error
```

Referencia típica actual:

| Señal | Lectura |
|-------|---------|
| `supabase_error` vacío | Grants OK |
| `s5_ops.pendiente` = SMTP, Stripe, PII_KEK | Falta Render P0 |
| `email_dev` = true | Poner `METGO_EMAIL_DEV=0` |
| `e12_ops.sinca_csv_origen` = ejemplos | Demo OK; falta CSV/IDs prod |

---

## Checklist de lo que **tú** debes realizar

### P0 — Seguridad y correo (esta semana)

- [x] **1.** `METGO_PII_KEK` en Render (**ya OK** en health 2026-08-03)
- [x] **2.** `METGO_EMAIL_DEV=0` (**ya OK**)
- [x] **3.** Configurar SMTP: `METGO_SMTP_*` (**health `smtp_configurado=true` 2026-08-05**)
- [ ] **4.** (Opcional) Stripe: `STRIPE_SECRET_KEY` + Price IDs; si no, el checkout mock sigue válido
- [x] **5.** Redeploy API + verificar `s5_ops.pendiente` sin SMTP (Stripe opcional OK)

### P1 — Alertas y observado

- [x] **6.** `CRON_SECRET` en GitHub Actions (= Render); workflow SPATI por sitio OK
- [ ] **7.** En SPA `/f/{faena}/umbrales`, guardar destinos email/webhook
- [ ] **8.** (Cuando haya datos reales) carpeta CSV en Render + `METGO_SINCA_CSV_DIR`
- [ ] **9.** Probar sync: `POST /api/cron/sync?token=CRON_SECRET`

### P2 — Calidad / datos oficiales

- [ ] **10.** `METGO_OPENMETEO_API_KEY` (menos 429)
- [ ] **11.** IDs oficiales: `METGO_SINCA_IDS`, `METGO_AGROMET_IDS`, `METGO_DMC_IDS`  
      (o `METGO_DMC_USAR_CANDIDATOS=1` tras confirmar código 330007)
- [ ] **12.** (Más adelante) reentrenar helada/PM10 con histórico oficial largo

### Ya no hace falta (código listo)

- [x] Fases 1–10 API/Vue/ETL/MQTT/ML/notificaciones/métricas  
- [x] Landing VENTORA, Ahora, Informes, sesión única, demo 1 h  
- [x] Grants identity (service_role)
- [x] Retiro demo fija `demo@ventora.demo` (seed off + SQL remove)  
- [x] PWA + i18n + Lighthouse CI  
- [x] Fallback CSV ejemplos E12.1  

---

## Orden sugerido en una sesión (~1–2 h)

1. P0 pasos 1–5 (Render)  
2. Redeploy + smoke health  
3. P1 paso 6 (GitHub secret)  
4. P1 paso 7 (umbrales en UI)  
5. Dejar P1–8/9 y P2 para cuando tengáis CSV/IDs reales  

Demo fija SPATI/VENTORA: **retirada** (`demo@ventora.demo` eliminada; seed off).  
Acceso temporal: `POST /api/auth/preview-hora` · SQL remove: `20260804160000_remove_demo_ventora.sql`.

## Fase documento

**Ops P0–P2** · sin nueva fase de código MVP.
