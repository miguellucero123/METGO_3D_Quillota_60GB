# METGO — qué va en el vault cifrado (bundle)

> Plantilla pública (OK en Git). Copia ideas a `METGO_BOOTSTRAP.local.md`.
> Empaquetar: `python scripts/ops/vault_crypto.py pack`
> Restaurar:  `python scripts/ops/vault_crypto.py unpack`

## Contenido del `.enc` (v2)

| Ruta | Para qué |
|------|----------|
| `local/METGO_VAULT.local.env` | Secretos / URLs |
| `local/METGO_BOOTSTRAP.local.md` | Checklist del PC |
| `.env` (raíz, si existe) | Copia de trabajo local |
| `docs/` | Roadmap, ops, manuales (oculto en GitHub) |
| `site-web/` | Estático legado |
| `templates/` | Plantilla sitios |
| `loadtests/` | k6 |
| `.devcontainer/` | Dev container |
| `docker-compose.dev.yml` | Compose opcional |
| `test_supabase.py` | Script one-off |

**No** incluye: `CORFO/`, `node_modules/`, `dist/`, modelos `.h5`, dumps scratch.

## Flujo otro PC

1. Clone del repo GitHub (código público del monorepo).
2. Copiar `METGO_VAULT.local.enc` → `local/`.
3. `pip install cryptography`
4. `python scripts/ops/vault_crypto.py unpack`
5. Passphrase por canal aparte.
6. `copy local\METGO_VAULT.local.env .env` si hace falta.
7. Arrancar API / Vue / Ventora.

## Seguridad

- Passphrase ≥ 12 caracteres; no la guardes en el mismo USB que el `.enc`.
- Nunca subas `.enc` ni `.local.env` a GitHub.
