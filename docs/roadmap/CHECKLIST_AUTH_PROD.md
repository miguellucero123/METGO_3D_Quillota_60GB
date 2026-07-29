# Checklist auth producción (DT-auth)

Endurecimiento JWT Flask — sin nuevo proyecto Supabase ni SSO WordPress.

## Render (`metgo-api`)

| Variable | Valor |
|----------|--------|
| `METGO_ENV` | `production` (opcional si ya existe `RENDER=true`) |
| `METGO_JWT_SECRET` | secreto largo aleatorio (**obligatorio**; sin fallback) |
| `METGO_ALLOW_SELF_REGISTER` | `0` |
| `METGO_API_AUTH_REQUIRED` | `1` |
| `METGO_PASSWORD_ADMIN` | fuerte, rotada |
| `METGO_PASSWORD_AGRONOMO` | opcional |
| `METGO_PASSWORD_OPERADOR` | opcional |
| `METGO_PASSWORD_LECTOR` | opcional |
| `METGO_PASSWORD_COPIAPO` | fuerte |
| `METGO_PASSWORD_MANTOS` | fuerte (también SPATI) |
| `METGO_PASSWORD_PAINE` | fuerte |
| `METGO_CORS_ORIGINS` | URLs `*.pages.dev` + dominios propios |

Tras cambiar env: **Manual Deploy → Clear build cache & deploy**.

## Cloudflare Pages (SPAs)

- Redeploy Quillota / Copiapó / Mantos / SPATI / Paine tras quitar demos de `/login`.
- Quillota: **no** definir `VITE_ALLOW_SELF_REGISTER=1` en producción.
- Paine: repo `metgo-paine` — commit + deploy aparte.

## Smoke

```powershell
# Debe fallar con password demo si ya rotó METGO_PASSWORD_ADMIN
Invoke-RestMethod -Method POST https://metgo-api.onrender.com/api/auth/login `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"admin123"}'

# Debe OK con el password de Render
Invoke-RestMethod -Method POST https://metgo-api.onrender.com/api/auth/login `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"SU_PASSWORD_RENDER"}'
```

UI: `/login` sin texto de usuario/password demo.

## WordPress / Supabase

- **No** crear otro proyecto Supabase para usuarios.
- WordPress = marketing/CMS que **enlaza** a las SPAs (sin SSO por ahora).

## Local

Demos y tabla de usuarios: [`docs/DESARROLLO_LOCAL.md`](../DESARROLLO_LOCAL.md).

## Fase

DT-auth / ops prod.
