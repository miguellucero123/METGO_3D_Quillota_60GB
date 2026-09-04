# Sesión operativa — R4 MFA + R7 Backup (hoy)

**Fecha guía:** 2026-09-04  
**Orden:** MFA primero (~20–30 min) → verificación backup / acta documental (~15 min).  
**No** pegues capturas con secretos en el chat ni en Git.

---

## Parte A — MFA (R4) · hazlo ahora en el navegador

Marca cada casilla cuando veas “two-factor / MFA enabled”.

### A1. GitHub (obligatorio)
1. Abre https://github.com/settings/security  
2. **Enable** two-factor authentication (app TOTP o llave).  
3. Guarda recovery codes en Bitwarden / lugar seguro (fuera del repo).  
- [x] GitHub MFA ON · 2026-09-04 (recovery codes en gestor personal, no en Git)

### A2. Cloudflare (obligatorio)
1. https://dash.cloudflare.com/profile/authentication  
2. Activa **Two-factor authentication**.  
- [x] Cloudflare MFA ON · 2026-09-04 (TOTP app)

### A3. Render (obligatorio)
1. https://dashboard.render.com → Account Settings → **Security**  
2. Enable two-factor.  
- [ ] Render MFA ON

### A4. Supabase (obligatorio)
1. https://supabase.com/dashboard/account/security (o Account → MFA)  
2. Enable MFA para tu usuario owner.  
- [ ] Supabase MFA ON

### A5. Zoho Mail (recomendado — SMTP ya en prod)
1. https://accounts.zoho.com → Security → MFA / App passwords.  
2. Confirma que el SMTP de Render sigue usando app password (no rotar a ciegas).  
- [ ] Zoho MFA ON

### A6. WordPress metgo3d.com (recomendado)
1. wp-admin → plugin 2FA del host o Jetpack/Wordfence según lo instalado.  
- [ ] WP MFA ON o documentado “pendiente host”

Cuando termines A1–A4, responde en el chat: **`MFA listo: GitHub, CF, Render, Supabase`** (o indica cuáles faltan) para actualizar `INVENTARIO_ENDPOINTS_R12.csv`.

---

## Parte B — Backup R7 · verificación + drill documental (seguro)

> **Hoy no restauramos producción.** Primer drill = comprobar backups + rellenar acta. Restore real a staging = siguiente ventana.

### B1. Abrir Backups
1. https://supabase.com/dashboard → proyecto METGO (`ylivhjig…`).  
2. **Project Settings → Database → Backups** (o Database → Backups según UI).  
3. Anota:
   - Plan del proyecto (Free / Pro / …)  
   - ¿Hay backup diario / PITR? sí/no  
   - Fecha/hora del último backup  

### B2. Baseline rápido (sin dump)
En PowerShell (solo lectura vía health; no toca DB):

```powershell
python scripts/ops/check_prod_health_flags.py
```

Anota `version`, `supabase_ok=True`, `meteo_store_registros` si aparece en health completo:

```powershell
(Invoke-RestMethod https://metgo-api.onrender.com/api/health).meteo_store_registros
```

### B3. Rellenar acta (vault / Drive — no Git)

Copia desde `config/compliance/ACTA_DRILL_BACKUP.template.md` a tu vault, completa y guarda.

Escenario de hoy: **`simulacion_documental`**.

### B4. Criterio R7 parcial (hoy)
- [ ] Backups vistos en dashboard  
- [ ] Acta firmada/guardada en vault  
- [ ] Riesgo Free-sin-PITR documentado si aplica  

R7 **completo** = más adelante un restore a proyecto staging.

---

## Parte C — Después de esta sesión

1. Actualizar inventario R12 (`mfa` → `totp`).  
2. Marcar R4/R7 en `PLAN_LEY_21719_METGO.md`.  
3. Calendario: próximo drill restore staging en ~90 días o al primer cliente B2B.
