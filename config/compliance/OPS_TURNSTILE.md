# Ops — activar Cloudflare Turnstile (anti-bot registro)

El código ya verifica tokens (`security_hardening.verify_turnstile`) y las SPA muestran el widget si hay `site_key`.

## 1. Crear widget

1. https://dash.cloudflare.com → **Turnstile** → Add widget.  
2. Dominios: `localhost`, `127.0.0.1`, `metgo-quillota.pages.dev`, `metgo-spati.pages.dev`, `ventora-izaje-mar.pages.dev`, `metgo-copiapo.pages.dev`, `metgo-mantos.pages.dev`, `metgo3d.com` (y custom domains si hay).  
3. Mode: Managed.  
4. Copia **Site Key** y **Secret Key**.

Token API para automatizar necesita permiso **Account.Turnstile:Edit** (el token Pages-only no basta).

## 2. Render (API)

```
METGO_TURNSTILE_SECRET=<secret>
METGO_TURNSTILE_SITE_KEY=<site_key>
METGO_TURNSTILE_REQUIRED=1
```

Redeploy. Health debe mostrar `turnstile_configured: true`.

## 3. Frontend (opcional)

`VITE_TURNSTILE_SITE_KEY` en build Pages **o** dejar vacío y usar la key pública del endpoint de config de seguridad (ya leída en `RegistroView`).

## 4. Probar

Registro en SPA → widget visible → submit sin token debe fallar si `required=1`.
