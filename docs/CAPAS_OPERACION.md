# Operación por capas (backend · frontend · site-web)

Guía rápida para arrancar METGO con el layout v4.

## Orden recomendado (desarrollo)

1. **API** — `python backend/10_Deployment_Produccion/scripts/iniciar_api_rest.py` → `:8080`
2. **Vue** — `cd frontend/vue && npm run dev` → `:5173`
3. **Streamlit operador** (opcional) — `streamlit run streamlit_app.py` → `:8501`
4. **Público** (opcional) — `iniciar_site_web.bat` → `:8505`

O todo en uno (API + Vue): `iniciar_metgo_desarrollo.bat`.

## Responsabilidades

| Capa | Quién la usa | Autenticación |
|------|----------------|---------------|
| `backend/` | Servicios, scripts, ML | JWT en API |
| `frontend/vue` | Operadores / agrónomos | Login Vue → API |
| `frontend/dashboards` | Análisis profundo | Streamlit auth |
| `site-web/` | Visitantes / demo pública | Sin login |

## Rutas en código

```python
import metgo_paths

metgo_paths.setup_all_paths()
metgo_paths.streamlit_dashboard_path("sistema_auth_dashboard_principal_metgo.py")
metgo_paths.site_web_streamlit_path("dashboard_web_publico.py")
metgo_paths.frontend_vue_dir()
```

## Variables de entorno

- Raíz: `.env.example` (API, JWT, CORS)
- Vue dev: `frontend/vue/.env.development`
- Vue build: `frontend/vue/.env.production`
- Alinear `VITE_API_PORT` con `METGO_API_PORT`

## API pública (sin JWT)

- `GET /api/public/estaciones`
- `GET /api/public/meteo/<estacion_id>` — ej. `quillota`, `limache`

## Scripts legacy

Los `ejecutar_sistema_*.py` están **deprecated**. Usar `METGO_ALLOW_DEPRECATED=1` solo si debe ejecutarlos.

## CI

GitHub Actions: `.github/workflows/metgo-ci.yml` — `pytest tests/test_metgo_smoke.py`
