# Plan: Registro, identidad confidencial y suscripción multi-producto

**Fase:** DT-auth-sub / producto 2.x · **S1 en curso**  
**Estado:** implementación iniciada  
**Relacionado:** [`CHECKLIST_AUTH_PROD.md`](CHECKLIST_AUTH_PROD.md) · [`PLAN_MINERIA_MULTI_FAENA.md`](PLAN_MINERIA_MULTI_FAENA.md) · E9 `sitios_auth.py`

---

## 1. Objetivo

Permitir que **cada producto METGO** (industria distinta) y, en minería, **cada faena** (Escondida, Los Bronces, …) tengan:

1. **Registro propio** con PII + org + **consentimiento explícito** de almacenamiento.
2. **Validación de veracidad/formato** (RUT, email, teléfono, nombres) antes de persistir.
3. **Suscripción** con precios **escalonados** por plan (+ reglas por faena).
4. **GET de acceso por pestaña** para que el router no abra módulos sin entitlement.
5. Datos confidenciales **cifrados** (Argon2id/scrypt + AES-GCM); API unificada, negocio aislado.

WordPress = marketing (enlaces). Cloudflare Pages = SPA. Supabase = datos (no Auth IdP en esta fase).

---

## 2. Tres capas de aislamiento

```text
Producto (industria)     sitio JWT: quillota | paine | copiapo | mantos_blancos | spati
  └─ Faena / cliente     claim faena: escondida | los_bronces | …  (solo minería/SPATI)
       └─ Plan pago      trial | starter | pro | enterprise
```

| Capa | Ejemplo | Enlace | Qué aísla |
|------|---------|--------|-----------|
| Producto | Copiapó aire | `metgo-copiapo.pages.dev` | Industria y facturación de producto |
| Faena | Escondida | `metgo-spati.pages.dev/f/escondida` | Org, reglas, umbrales, suscripción de esa mina |
| Módulo/pestaña | Dron / Umbrales | path `/f/escondida/dron` | Entitlement del plan + `faena_reglas` |

**Minería (decisión clave):** el código puede ser multi-faena, pero **comercialmente cada mina es un tenant**:

- URL propia bajo `/f/{faena}/…` (y más adelante subdominio `escondida.metgo.cl`).
- Registro y pago asociados a esa `faena`.
- Reglas anexables por tipo de sistema (`izaje`, `ambiente`, `dron`, `ops`) en `faena_reglas`.
- Un usuario de Escondida **no** entra a Los Bronces sin membresía adicional.

---

## 3. Consentimiento y veracidad

En aceptación del registro (obligatorio, no pre-chequeado):

| Consentimiento | `tipo` | Efecto |
|----------------|--------|--------|
| Guardar información personal/org | `almacenamiento_datos` | Sin esto → 400, no hay insert |
| Términos de uso | `tos` | Obligatoriod |
| Política de privacidad | `privacy` | Obligatorio |
| Declaración de veracidad | `veracidad` | Usuario declara que los datos son correctos |

Versiones en `METGO_CONSENT_VERSION` (default `2026-07-29`). Auditoría en `consentimientos` (sin PII en claro: `ip_hash`).

**Verificación de datos (no solo “obligatorio”):**

- Endpoint dry-run `POST /api/auth/validate-registro`.
- Reglas: email RFC, RUT/CI chileno (DV), teléfono CL `+56…`, nombres 2–80 chars, razón social, contraseña ≥ 10 con complejidad.
- Listas de bloqueo: emails temporales conocidos, RUTs inválidos, strings placeholder (`test`, `asdf`).
- Resultado: `{ ok, errors: { campo: [...] }, warnings: [] }` — el front no envía register si `ok=false`.

---

## 4. Modelo de datos

```text
orgs
  id, sitio, faena (nullable), razon_social_enc, rut_enc, giro, created_at

usuarios_app
  id, email_norm, password_hash,
  nombres_enc, apellidos_enc, telefono_enc,
  org_id, sitio, faena, role,
  email_verified_at, status (pending|active|suspended), created_at

consentimientos
  usuario_id, tipo, version, accepted_at, ip_hash

suscripciones
  id, org_id, sitio, faena, plan_code, status,
  stripe_customer_id, stripe_subscription_id,
  current_period_end, seats, metadata jsonb

entitlements
  suscripcion_id, feature_key, enabled

faena_reglas          # anexar sistemas por mina
  faena, sistema (izaje|ambiente|dron|ops|aire), enabled,
  config jsonb, plan_minimo (trial|starter|pro|enterprise)

audit_auth
  id, usuario_id, sitio, faena, evento, ip_hash, ua_hash, at

planes_catalogo (código + opcional tabla)
  sitio, plan_code, precio_mensual_clp, seat_incluidos, features[]
```

PII `*_enc`: AES-256-GCM. Email normalizado en claro solo para login único.

---

## 5. Precios escalonados (MVP catálogo)

Por **producto** (y en SPATI también por faena vía multiplicador / plan mínimo):

| Plan | CLP/mes (ref.) | Seats | Features típicas |
|------|----------------|-------|------------------|
| `trial` | 0 (14 días) | 1 | panel + ambiente lectura |
| `starter` | 149 000 | 3 | + dron calibración |
| `pro` | 399 000 | 10 | + umbrales editables + alertas push |
| `enterprise` | a convenir | ilimitado | + multi-faena org + SLA |

`GET /api/public/planes?sitio=spati&faena=escondida` devuelve precios efectivos.

Pago: Stripe Checkout (mock si no hay `STRIPE_SECRET_KEY`). Webhooks en S2.

---

## 6. Endpoints (contrato)

| Método | Ruta | Uso |
|--------|------|-----|
| POST | `/api/auth/validate-registro` | Dry-run validación + veracidad |
| POST | `/api/auth/register-v2` | Alta org+user+consentimientos (cifrado) |
| GET | `/api/auth/verify-email` | Token email |
| GET | `/api/auth/access` | **¿Puede abrir pestañas?** JWT + plan + faena_reglas |
| GET | `/api/auth/me` | Ampliar: org_id, faena, sub_status, plan_code |
| GET | `/api/public/planes` | Catálogo precios escalonados |
| GET | `/api/public/faenas/{faena}/reglas` | Reglas/sistemas de esa mina |
| POST | `/api/billing/checkout` | Sesión Stripe / mock |
| POST | `/api/billing/webhook` | Stripe events (S2) |

`GET /api/auth/access` ejemplo:

```json
{
  "allowed": true,
  "sitio": "spati",
  "faena": "escondida",
  "plan_code": "starter",
  "sub_status": "active",
  "tabs": { "panel": true, "dron": true, "umbrales": false, "ambiente": true },
  "sistemas": { "izaje": true, "dron": true, "ambiente": true, "ops": false }
}
```

El `beforeEach` del router SPA llama esto al entrar a cada pestaña protegida.

---

## 7. Enlaces por minera (SPATI)

| Faena | Path | Registro | Login |
|-------|------|----------|-------|
| Escondida | `/f/escondida/` | `/f/escondida/registro` | `/f/escondida/login` |
| Los Bronces | `/f/los_bronces/` | … | … |
| … | `/f/{slug}/` | … | … |

WordPress / portal: un botón por mina → ese path.  
Hub opcional `/` lista faenas (público) sin datos operativos.

---

## 8. Fases

### S0 — Diseño ✅ documentado

- Consentimientos, validación, precios, faena-enlace.

### S1 — Identidad + access + UI SPATI faena *(en curso)*

- [x] Plan actualizado (este doc).
- [x] Migración SQL.
- [x] `pii_crypto`, validators, store, register-v2, validate, access, planes.
- [x] OpenAPI + tests memoria.
- [x] SPATI: rutas `/f/:faena/*`, RegistroView, guard access.

### S2 — Billing real Stripe + `/cuenta`

### S3 — Cutover (quitar env demos), `sitio=spati`, hardening

---

## 9. Archivos

Ver implementación bajo `api_rest/identity/`, `supabase/migrations/*_identity_suscripciones.sql`, `frontend/spati/src/...`.

## 10. Fase roadmap

**DT-auth-sub / S1** · minería: extensión M-faena-tenant (post M9).
