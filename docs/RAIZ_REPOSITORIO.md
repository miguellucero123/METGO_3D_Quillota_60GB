# Qué va en la raíz del repositorio (GitHub)

La raíz debe verse **limpia** en GitHub. Solo quedan archivos exigidos por despliegue o entrada del proyecto.

## En la raíz (visible en GitHub)

| Archivo / carpeta | Motivo |
|-------------------|--------|
| `README.md` · `LICENSE` · `AGENTS.md` | Presentación / licencia / agentes |
| `requirements.txt` · `pytest.ini` | Python + tests |
| `render.yaml` · `netlify.toml` · `wsgi_api.py` | Deploy API / Netlify |
| `streamlit_app.py` | **Main file** Streamlit Cloud |
| `sistema_auth_dashboard_principal_metgo.py` | Alias legacy → delega en `streamlit_app.py` |
| `metgo_paths.py` · `metgo_auth.py` | Raíz + JWT wrapper |
| `pages/` · `.streamlit/` | Multipágina Streamlit + tema |
| `backend/` · `frontend/` · `ventora-izaje-mar/` | Producto |
| `metgo/` · `docs/` · `scripts/` · `tests/` · `e2e/` · `supabase/` | Lib, docs, ops, CI e2e, SQL |
| `.github/` · `.gitleaks.toml` · `.env.example` | CI / seguridad / plantilla env |
| `local/*.example*` | Plantillas vault (sin secretos) |

## Ocultos (`.gitignore` — siguen en tu PC)

| Ruta | Motivo |
|------|--------|
| `loadtests/` | k6 interno |
| `templates/` | plantilla de sitio, no producto live |
| `site-web/` | estático legado (WP / Pages lo reemplazan) |
| `.devcontainer/` | solo VS Code/Cursor opcional |
| `docker-compose.dev.yml` | compose local opcional |
| `/package.json` · `/package-lock.json` | residuo npm en raíz |
| `/test_supabase.py` | script one-off |
| `scratch/` · `*.rar` · `*.zip` · logs | basura local |
| `local/METGO_VAULT.local.*` (no example) | secretos |

## Accesos rápidos

- Arranque local: `backend/10_Deployment_Produccion/scripts/iniciar_metgo_desarrollo.bat`
- Otro PC / vault: `docs/ops/BOOTSTRAP_OTRO_PC.md`
- Publicar: `docs/manuales/PUBLICAR_GITHUB.md`
