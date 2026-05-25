# Qué va en la raíz del repositorio (GitHub)

La raíz debe verse **limpia** en GitHub. Solo quedan archivos exigidos por despliegue o entrada del proyecto.

## En la raíz (visible en GitHub)

| Archivo / carpeta | Motivo |
|-------------------|--------|
| `README.md` | Presentación del proyecto |
| `LICENSE` | Licencia |
| `requirements.txt` | Dependencias Python (Render, Streamlit Cloud) |
| `pytest.ini` | Tests |
| `render.yaml` | Blueprint Render |
| `netlify.toml` | Despliegue Vue en Netlify |
| `streamlit_app.py` | **Main file** Streamlit Cloud |
| `sistema_auth_dashboard_principal_metgo.py` | Entrada legacy Streamlit Cloud |
| `metgo_paths.py` | Marcador de raíz + rutas (`metgo/paths.py`) |
| `metgo_auth.py` | Wrapper JWT (implementación en `backend/07_...`) |
| `pages/` | Páginas multipágina Streamlit (convención del framework) |
| `backend/` | Lógica, API, ML, despliegue |
| `frontend/` | Vue, dashboards Streamlit |
| `docs/` | Manuales |
| `site-web/` | Sitio público |
| `tests/` | Pruebas |
| `metgo/` | Biblioteca compartida (tema, portal, visor, Vue embed) |
| `scripts/` | Utilidades (`compat/`, `git/`) |
| `.streamlit/` | Config tema Streamlit |
| `.github/` | CI |

## Ya no en la raíz

| Antes | Ahora |
|-------|--------|
| `metgo_streamlit_*.py`, `metgo_vue_embed.py`, `metgo_dashboard_loader.py` | `metgo/` |
| `datos_reales_openmeteo.py`, `dashboard_*.py`, `mobile_config.py` | `scripts/compat/` |
| `SUBIR_*.bat` (contenido) | `scripts/git/` (acceso con `SUBIR_GITHUB_MANUAL.bat` en raíz) |

## Accesos rápidos

- Subir a GitHub: `SUBIR_GITHUB_MANUAL.bat` o `docs/manuales/SUBIR_GITHUB_MANUAL.md`
- Arranque local: `backend/10_Deployment_Produccion/scripts/iniciar_metgo_desarrollo.bat`
