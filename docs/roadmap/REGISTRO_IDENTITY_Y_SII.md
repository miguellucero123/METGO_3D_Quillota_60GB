# Registro identity + facturación electrónica SII

> Corte: 2026-08-04 · Extiende S1 (VENTORA) a todos los SPA y deja scaffold SII.

## 1. Registro comercial (mismo flujo VENTORA)

API: `POST /api/auth/validate-registro` → `POST /api/auth/register-v2` → `GET /api/auth/verify-email`

| SPA | Sitio fijo | Rutas |
|-----|------------|-------|
| SPATI / VENTORA | `spati` (+ faena) | `/registro`, `/f/:faena/registro`, `/verificar` |
| Quillota | `quillota` | `/registro`, `/verificar` |
| Copiapó | `copiapo` | `/registro`, `/verificar` |
| Mantos Blancos | `mantos_blancos` | `/registro`, `/verificar` |
| Paine | `paine` | Repo externo — mismo patrón |

### Piloto 15 días y cobro

- Plan `trial` en catálogo: **15 días**, precio **$0**.
- Al registrarse: suscripción `trialing` con `current_period_end = now + 15d`.
- **Cobro (Starter/Pro):** se aplica cuando el usuario (logueado) hace checkout en `/cuenta` o equivalente — no al crear la cuenta.
- Al vencer el trial sin plan pago: acceso pasa a expirado/cancelado (gate `/auth/access`).

### Unicidad RUT (anti multi-cuenta)

- Un mismo **RUT empresa** no puede abrir otra org en el mismo `sitio` (+ `faena` en SPATI) aunque cambie el email.
- Implementado con `orgs.rut_hash` (HMAC), no con `rut_enc` (AES no determinístico).
- Mensaje API: `code: rut_already_registered` → debe iniciar sesión o pedir invitación.

### ¿Verificar con cédula de identidad?

**Sí, se puede**, pero no es un “subir foto y listo” casero. Opciones reales en Chile:

| Nivel | Mecanismo | Esfuerzo | Confianza |
|-------|-----------|----------|-----------|
| A (hecho) | RUT único + consentimientos + email verify | Bajo | Media (anti abuso básico) |
| B | ClaveÚnica (Estado) OAuth para persona natural | Medio–alto | Alta |
| C | Proveedor KYC (TOC, Veridas, Jumio, etc.): foto cédula + selfie/liveness | Medio + costo por check | Alta |
| D | Revisión manual ops (subir PDF/cédula, admin aprueba) | Bajo código / alto ops | Media |

Recomendación METGO:

1. Mantener **RUT empresa** único (ya).
2. Para **persona natural** (representante): ClaveÚnica o KYC proveedor **antes** de activar plan pago / emitir DTE.
3. No almacenar imagen de cédula en claro sin base legal + retención; si se guarda, cifrada y con consentimiento explícito (Ley 19.628).

Verify URL por env (Render):

| Variable | Default |
|----------|---------|
| `METGO_SPATI_PUBLIC_URL` | `https://metgo-spati.pages.dev` |
| `METGO_QUILLOTA_PUBLIC_URL` / `METGO_VUE_URL` | `https://metgo-quillota.pages.dev` |
| `METGO_COPIAPO_PUBLIC_URL` | `https://metgo-copiapo.pages.dev` |
| `METGO_MANTOS_PUBLIC_URL` | `https://metgo-mantos.pages.dev` |
| `METGO_PAINE_PUBLIC_URL` | `https://metgo-paine.pages.dev` |

Cuentas `METGO_PASSWORD_*` = break-glass ops, no onboarding de clientes.

**Ops pendiente:** SMTP (`METGO_SMTP_HOST`…) para que el correo de verificación salga de verdad.

## 2. SII (boletas / facturas)

Scaffold: [`scripts/sii/README.md`](../../scripts/sii/README.md)

- Stripe/mock = cobro.
- SII = DTE 33/39 tras pago (cola futura desde webhook billing).

No hay emisión real hasta certificado + CAF + certificación SII.
