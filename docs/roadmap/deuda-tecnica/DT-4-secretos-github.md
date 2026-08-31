# DT-4 — Secretos fuera de GitHub

**Estado:** En curso · **Prioridad:** alta · **Fase:** DT-x / seguridad

## Objetivo

Ningún `.env`, `secrets.toml`, clave API/JWT/DB ni hash de credenciales debe quedar trackeado o visible en GitHub.

## Qué NUNCA commitear

| Patrón | Dónde vive en su lugar |
|--------|------------------------|
| `.env`, `.env.local`, `.env.development`, `.env.production` | Máquina local / Render / Cloudflare |
| `secrets.toml` | `.streamlit/secrets.toml` local o secrets del host |
| `api_keys*.json` (reales) | Copiar desde `api_keys_meteorologicas.json.example` |
| `credentials.json`, `*.pem`, service accounts | Secret manager / fuera del repo |
| `WP_APP_PASSWORD`, Stripe, SMTP | `.env` local o panel Render |
| `CORFO/` | Ya en `.gitignore` |

## Plantillas OK en git

- `*.env.example`, `*.env.*.example`
- `.streamlit/secrets.toml.example`
- `api_keys_meteorologicas.json.example`

## Verificación (PowerShell)

```powershell
# No debe listar .env reales ni secrets.toml ni metgo.env
git ls-files | Select-String -Pattern '\.env(?!\.example)|secrets\.toml$|usuarios\.json|metgo\.env|api_keys_meteorologicas\.json$'

# Escaneo de patrones peligrosos (ignorar examples y docs)
git grep -I -E "SECRET_KEY=.+[a-zA-Z0-9]{12,}|password=.+[a-zA-Z0-9_]{8,}|sk_live|postgres://[^:]+:[^@]+@" -- ":!*.example" ":!docs/**"
```

## Historial

`git rm --cached` solo limpia commits futuros. Para borrar del historial remoto hace falta `git filter-repo` + force-push (ver `DT-4-ROTACION_SECRETOS.md`). No hacer force-push a `main`/`master` sin OK explícito.

## Criterio de cierre

- [x] `.gitignore` refuerza `.env.*`, `secrets.toml`, credentials, `api_keys`, obsoletos
- [x] Archivos sensibles sacados del índice
- [x] Placeholders en deploy/monitoreo/auth (sin claves hardcodeadas de prod)
- [ ] Force-push de historial limpio (ops, con OK)
- [ ] Rotación en Render / WP (checklist ops)
