# METGO Frontend Vue.js

Frontend moderno del sistema METGO (Quillota) con **Vue 3**, **Vite**, **Vue Router** y **Pinia**.

## Inicio rápido

```bash
# 1) API (otra terminal, desde la raíz del repo)
python 10_Deployment_Produccion/scripts/iniciar_api_rest.py

# 2) Vue
cd 04_Dashboards_Unificados/frontend_vue
npm install
npm run dev
```

Abrir en **Chrome o Edge** (pestaña normal): http://127.0.0.1:5173

### Error «Unsafe attempt to load URL… chrome-error»

Suele aparecer si:
- El servidor Vue **no está corriendo** (`npm run dev`) y se abre el preview embebido de Cursor.
- Se usa el **Simple Browser** de Cursor en lugar del navegador externo.

**Solución:** ejecutar `npm run dev`, luego abrir http://127.0.0.1:5173 en Chrome/Edge (no en el panel iframe de Cursor).

## Estructura

```text
src/
├── views/          # Páginas por módulo (meteo, agrícola, monitoreo)
├── components/     # UI reutilizable
├── stores/         # Estado global (Pinia)
├── api/            # Cliente HTTP hacia backend Python
└── router/         # Rutas Vue
```

## Integración con Python

1. Iniciar API REST (terminal 1):

```bash
python 10_Deployment_Produccion/scripts/iniciar_api_rest.py
```

2. Iniciar Vue (terminal 2):

```bash
npm run dev
```

El proxy de Vite redirige `/api` → `http://localhost:8080`.

| Vista | Endpoint |
|-------|----------|
| DashboardView | `GET /api/meteo/{id}` |
| MeteoView | `+ /api/meteo/{id}/pronostico` |
| MonitoreoView | `GET /api/alertas` |
| AgricolaView | `GET /api/agricola/{id}` |

Documentación API: `docs/manuales/API_REST.md`

## Despliegue en Netlify

1. Conectar el repo en [Netlify](https://www.netlify.com) (el `netlify.toml` de la **raíz del repo** ya define `base = frontend/vue`).
2. Variable **Production**: `VITE_METGO_API=https://su-api-publica.com/api`
3. Tras el deploy, en Streamlit Cloud Secrets: `METGO_VUE_URL = "https://su-sitio.netlify.app"`

Guía completa: [`../../docs/manuales/DESPLIEGUE_VUE_NETLIFY.md`](../../docs/manuales/DESPLIEGUE_VUE_NETLIFY.md)
