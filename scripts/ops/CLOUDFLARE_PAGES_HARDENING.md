# Cloudflare Pages — hardening METGO (seguridad)

> Corte: 2026-09-03 · Repo monorepo + Pages Git-connected  
> **Fase:** DT-seguridad / ops Cloudflare  
> **Fuente de verdad:** GitHub (`config/cloudflare/pages_security.json`)  
> **Automatización:** `.github/workflows/cloudflare-pages-security.yml` + `scripts/ops/cloudflare_pages_harden.py`

## Automatización (recomendado)

1. En Cloudflare → My Profile → **API Tokens** → Create Token  
   - Plantilla o custom: **Account → Cloudflare Pages → Edit**  
   - **Account Settings → Read** (opcional pero útil)
2. Copia **Account ID** (Workers & Pages → Overview, barra derecha).
3. En GitHub → Settings → Secrets and variables → Actions, crea:
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`
4. Actions → **Cloudflare Pages security** → Run workflow  
   o haz push a `config/cloudflare/pages_security.json`.

Comportamiento:

| Evento | Acción |
|--------|--------|
| `workflow_dispatch` / push a la policy | **Aplica** `preview_deployment_setting=none` + `production_branch` |
| Cron semanal | Solo **`--check`** (falla si hay drift) |

Local (opcional):

```powershell
$env:CLOUDFLARE_API_TOKEN="..."
$env:CLOUDFLARE_ACCOUNT_ID="..."
python scripts/ops/cloudflare_pages_harden.py --dry-run
python scripts/ops/cloudflare_pages_harden.py
```

GitHub también refuerza deps con `.github/dependabot.yml`.

## 0. Qué es riesgo real vs ruido

| Afirmación | Realidad METGO |
|------------|----------------|
| “Cualquiera con `*.pages.dev` tiene acceso total” | **Parcial.** Ve la SPA (landing, JS). Datos API requieren JWT/`METGO_API_AUTH_REQUIRED`. No es “acceso total” a Supabase ni al vault. |
| Sin WAF en `pages.dev` | **Cierto** para la zona Pages managed. WAF/reglas de zona requieren **dominio custom** en Cloudflare DNS. |
| Previews públicos | **Cierto** si `preview_deployment_setting = all`. Cada push de rama genera URL pública con el mismo shell. |
| Access Zero Trust | Útil para **previews** y sitios **internos**. No sustituye el login JWT de producto para clientes. |

**Sitios actuales (producción Pages):**

| Proyecto | Carpeta | URL típica | Público / producto |
|----------|---------|------------|--------------------|
| metgo-quillota | `frontend/vue` | `metgo-quillota.pages.dev` | Producto + landing |
| metgo-spati | `frontend/spati` | `metgo-spati.pages.dev` | Producto faena |
| ventora-izaje-mar | `ventora-izaje-mar` | `ventora-izaje-mar.pages.dev` | Producto izaje |
| metgo-copiapo | `frontend/copiapo` | `metgo-copiapo.pages.dev` | Producto aire |
| metgo-mantos | `frontend/mantos_blancos` | `metgo-mantos.pages.dev` | Producto faena |
| (paine) | repo aparte | `metgo-paine.pages.dev` | Outdoor |

Marketing corporativo: `metgo3d.com` (WordPress) — zona DNS aparte si ya está en Cloudflare.

---

## 1. Prioridad inmediata (hacer hoy, 15–30 min)

### 1.1 Previews: `none` o `custom` (solo PR)

En cada proyecto Pages:

1. [Workers & Pages](https://dash.cloudflare.com/?to=/:account/workers-and-pages) → proyecto → **Settings** → **Builds & deployments**.
2. **Preview deployments** → **None** (máxima seguridad) o **Custom branches** / solo PRs.
3. Repetir en: quillota, spati, ventora, copiapo, mantos, paine.

Evita URLs `*.pages.dev` por cada push a ramas experimentales.

### 1.2 Secrets en Pages

Solo variables **públicas** del build Vite:

- `VITE_METGO_API=https://metgo-api.onrender.com/api`
- `VITE_TURNSTILE_SITE_KEY=...` (si hay captcha)

Marcar como **Encrypted / secret** cualquier valor que no deba verse en el log de build. **Nunca** poner JWT, `SUPABASE_KEY` service role, SMTP ni Stripe en Pages.

### 1.3 Confirmar API endurecida (ya en código)

- Render: `METGO_API_AUTH_REQUIRED=1`, `METGO_ENV=production`, CORS solo orígenes conocidos.
- Rate limit / Turnstile cuando abran registro público.

---

## 2. Dominios personalizados + WAF (escala comercial)

Objetivo: `quillota.metgo3d.com`, `spati.metgo3d.com`, etc. (o paths bajo un solo host más adelante).

Por cada proyecto Pages:

1. **Custom domains** → Add → `quillota.metgo3d.com` (ejemplo).
2. DNS del dominio `metgo3d.com` debe estar en Cloudflare (zona activa).
3. Tras verificar SSL: **Disable** acceso a `*.pages.dev` si la UI lo ofrece (Custom domains → disable pages.dev).
4. En la zona `metgo3d.com`: Security → WAF / Rate limiting / Bot Fight (plan Free tiene capa básica).

Luego actualizar:

- `METGO_CORS_ORIGINS` en **Render** (y `.env` local).
- `METGO_*_PUBLIC_URL` en env.
- CSP `connect-src` en `public/_headers` (ya incluye `https://*.metgo3d.com` en el monorepo).

---

## 3. Cloudflare Access (Zero Trust) — cuándo sí

| Caso | Recomendación |
|------|----------------|
| Previews de desarrollo | Access “Previews only” o política email `@metgo3d.com` |
| Demo interna antes de piloto | Access en producción `*.pages.dev` **o** subdominio `staging.*` |
| Producto con login JWT para clientes | **No** sustituir JWT por Access; Access opcional delante de staging |

Pasos:

1. Zero Trust → Access → Applications → Add self-hosted.
2. Application domain = hostname Pages o preview.
3. Policy: Allow emails `miguel.lucero@metgo3d.com` (+ segundo fundador).
4. Alternativa rápida: en Worker/Pages Settings → **Enable Cloudflare Access** (one-click) si aparece.

Free: hasta ~50 usuarios Access.

---

## 4. Web Analytics

Workers & Pages → proyecto → Analytics → Enable **Web Analytics** (gratuito, sin cookies pesadas). Útil en landings públicas.

---

## 5. Arquitectura a medio plazo (no bloquear MVP)

1. **Un dominio + rutas** (`app.metgo3d.com/quillota|spati|…`) — requiere router monorepo o reverse proxy; más trabajo de front.
2. **Migrar Pages → Workers + assets** — solo si necesitan Functions/bindings (D1, R2, KV) en el edge.
3. Mantener monorepo (ya está bien).

---

## 6. Checklist de verificación

- [ ] Previews = None o solo PR en los 6 proyectos Pages  
- [ ] Ningún secret de backend en variables Pages  
- [ ] Dominio custom al menos en 1 sitio piloto + CORS actualizado  
- [ ] (Opcional) Access en previews / staging  
- [ ] Web Analytics en landings  
- [ ] `pages.dev` deshabilitado cuando el custom domain esté estable  
- [ ] Render CORS incluye solo dominios oficiales  

---

## 7. Enlaces dashboard

- [Workers & Pages](https://dash.cloudflare.com/?to=/:account/workers-and-pages)  
- [Zero Trust / Access](https://one.dash.cloudflare.com/)  
- [Docs: preview deployments](https://developers.cloudflare.com/pages/configuration/preview-deployments/)  
- [Docs: custom domains](https://developers.cloudflare.com/pages/configuration/custom-domains/)  
- [Docs: Access + Workers](https://developers.cloudflare.com/workers/configuration/cloudflare-access/)  

Deploy CLI (opcional, no necesario con Git): `scripts/deploy_cloudflare_all.ps1`
