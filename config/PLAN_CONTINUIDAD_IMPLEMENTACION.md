# Plan de continuidad — implementación METGO

**Actualizado:** 2026-09-05  
**Ramas:** `main` / `master` alineadas · API prod `version≈7e56277`  
**Docs ancla:** `config/compliance/PLAN_LEY_21719_METGO.md` · `config/meteo/INVENTARIO_ESTACIONES_PARTE1.md` · `config/compliance/SESION_R4_R7_HOY.md`

---

## 1. Objetivo

Cerrar compliance operativo (Ley 21.719) y dejar la capa multi-fuente E12 (DMC / SINCA / OpenMeteo) usable en producción con datos observados reales, sin mezclar NWP con OBSERVADO.

---

## 2. Resuelto (no rehacer)

### 2.1 Compliance / Ley 21.719

| Ítem | Evidencia |
|------|-----------|
| R1 ANON en prod | API + `client.py` |
| R2 rotación credenciales | `ROTACION_CREDENCIALES_R2.md` |
| R3 decisión SELECT anon | `DECISION_R3_ANON_SELECT.md` |
| R4 MFA A1–A4 | GitHub, Cloudflare, Render, Supabase ON · `SESION_R4_R7_HOY.md` |
| R5 Pages harden | secrets CF + workflow |
| R6 retención audit | cron + `compliance_retention` |
| R8/R9 API + UI | export/olvido en API y `CuentaView` (SPA) |
| R10 legales WP | `/privacidad/` `/terminos/` + enlaces registro |
| R12 inventario endpoints | `INVENTARIO_ENDPOINTS_R12.csv` |
| RAT v0 + DPD | `RAT_METGO_v0.csv` · `DPD_INTERINO.md` |
| Encargado B2B + derechos | plantillas + procedimiento |
| Runbook brechas 72 h | `RUNBOOK_BRECHAS_72H.md` |
| CI gitleaks / SINCA stub | verde tras `7e56277` |

### 2.2 Multi-fuente meteo (E12)

| Ítem | Evidencia |
|------|-----------|
| Health OM endurecido | `degraded` solo sin live/last-good/store; `fuente_activa` |
| Política fuentes | `config/meteo/POLITICA_FUENTES.md` |
| Ops OpenMeteo | `config/meteo/OPS_OPENMETEO_E12.md` |
| Inventario parte 1 | Quillota DMC **320124**; SINCA Copiapó/Paipote/TA |
| Catálogos + JSON env | `env_ids_recomendados.json` · oficiales/sinca actualizados |
| Render env IDs | `METGO_DMC_USAR_CANDIDATOS=1` · `METGO_DMC_IDS` · `METGO_SINCA_IDS` pegados |
| Badge fuente (Quillota) | `FuenteBadge` en SPA |

### 2.3 Reglas de producto ya asumidas

- No mezclar NWP con OBSERVADO en UI/API.
- Collahuasi / QB / Spence: sin estación pública &lt;50 km → convenio o modelo **etiquetado**.
- Recovery MFA / secretos: vault offline, **nunca** Git.

---

## 3. Pendiente — orden de implementación

### Fase A — Cierre compliance Oct (humano, ~30–45 min)

| # | Paso | Criterio de hecho | Archivo / URL |
|---|------|-------------------|---------------|
| A1 | MFA Zoho (A5) | 2FA ON; SMTP Render sigue con app password | Zoho Security |
| A2 | MFA WordPress (A6) | 2FA ON o nota “pendiente host” | wp-admin metgo3d.com |
| A3 | Drill backup R7 documental | Backups vistos + acta en vault (no Git) | Supabase → Backups · `ACTA_DRILL_BACKUP.template.md` |
| A4 | Actualizar R12 MFA | campos `mfa` → `totp` donde corresponda | `INVENTARIO_ENDPOINTS_R12.csv` |
| A5 | Probar derechos UI | export + olvido en `/cuenta` post-deploy | SPA Quillota (y hermanas) |

**R7 completo** (restore a staging) = ventana futura (~90 días o primer B2B), no bloquea A3.

### Fase B — Datos observados reales (código + ops)

| # | Paso | Criterio de hecho | Notas |
|---|------|-------------------|-------|
| B1 | Inventario **parte 2** (usuario aporta) | Doc + JSON actualizados | Limache/Olmué, INIA La Cruz, coords SINCA, Sierra Gorda→Spence |
| B2 | Integrar parte 2 al repo | catálogos + `.env.example` + ops | Mismo patrón que parte 1 |
| B3 | CSV / directorios DMC·SINCA | archivos `{slug}.csv` o `METGO_*_CSV_DIR` en Render | Hoy IDs solos no alimentan series |
| B4 | ETL / cron `sincronizar_oficiales` + `sincronizar_sinca` | jobs verdes; store con registros | Ver `OPS_OPENMETEO_E12.md` |
| B5 | Verificar API | `GET /api/public/datos/oficiales/estado` + health `e12_ops` | Distinguir OM vs DMC/SINCA |
| B6 | Agromet IDs (cuando existan) | `METGO_AGROMET_IDS` deja de estar “pendiente” | Depende de códigos INIA |

### Fase C — Condicional / negocio (cuando aplique)

| # | Paso | Cuándo |
|---|------|--------|
| C1 | Turnstile keys en Render | Antes de auto-registro público |
| C2 | Stripe | Primer cobro |
| C3 | Piloto comercial / TRL | Cliente o demo formal |
| C4 | Convenios datos faena | Collahuasi / Spence / Mantos in-site |
| C5 | NWP distinto de OpenMeteo | Solo si OM insuficiente; etiquetar siempre |

### Fase D — Auth VENTORA (usuarios / registro / sesión)

Plan detallado: [`config/ventora/PLAN_AUTH_USUARIOS_VENTORA.md`](ventora/PLAN_AUTH_USUARIOS_VENTORA.md)

| # | Paso | Prioridad |
|---|------|-----------|
| D0 | SMTP + `METGO_VENTORA_PUBLIC_URL` + quitar mock login FE | P0 ops |
| D1 | Sesión única persistente (Supabase `auth_sessions`) | P0 |
| D2 | Registro universal / trial+pago (sin faena obligatoria) | P0–P1 |
| D3 | Email verify + modal “cuenta activada” | P0 |

---

## 4. Próxima sesión recomendada (checklist corto)

1. **Si hay 20 min humanos:** A1–A3 (Zoho/WP MFA + acta R7).  
2. **Si hay datos parte 2:** pegar inventario → B1–B2.  
3. **Si el foco es producto meteo:** B3–B5 (CSV + ETL + verificación estado).  
4. Verificar prod:

```powershell
python scripts/ops/check_prod_health_flags.py
gh run list --limit 3
```

---

## 5. Fuera de alcance ahora

- Mover `streamlit_app.py` / promesas de puertos 8501–8513 en Netlify.  
- Commit de `.env` / recovery codes / capturas con secretos.  
- Mezclar forecast OpenMeteo como si fuera estación observada.  
- Restore destructivo de producción (solo staging, con acta).

---

## 6. Mapa de archivos clave

| Tema | Ruta |
|------|------|
| Plan Ley 21.719 | `config/compliance/PLAN_LEY_21719_METGO.md` |
| Pendientes humanos | `config/compliance/REQUISITOS_PENDIENTES.md` |
| Sesión MFA/R7 | `config/compliance/SESION_R4_R7_HOY.md` |
| Inventario estaciones | `config/meteo/INVENTARIO_ESTACIONES_PARTE1.md` |
| Env IDs | `config/meteo/env_ids_recomendados.json` |
| Ops E12 | `config/meteo/OPS_OPENMETEO_E12.md` |
| Política fuentes | `config/meteo/POLITICA_FUENTES.md` |

---

## 7. Fase roadmap

- **Compliance:** Oct 2026 (R4 parcial cerrado; R7 documental pendiente).  
- **Meteo E12:** producto ampliado / ops — inventario p1 hecho; p2 + CSV/ETL siguientes.  
- **Negocio:** fase 2–3 según piloto.
