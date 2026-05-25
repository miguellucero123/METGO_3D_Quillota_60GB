# Site-web METGO

Capa de **exposición pública**: resumen meteorológico abierto (OpenMeteo) sin login de operador.

## Estructura

| Carpeta | Uso |
|---------|-----|
| `streamlit/` | `dashboard_web_publico.py` — panel público |
| `streamlit/ngrok_tunnel.py` | Túnel ngrok (opcional; no es el dashboard) |
| `static/` | Assets para landing o marketing (futuro) |

El panel con **login de operadores** está en `frontend/dashboards/`.

## Arranque local

```bash
# Desde la raíz del repositorio
streamlit run site-web/streamlit/dashboard_web_publico.py --server.port 8505
```

O doble clic / terminal:

```bash
backend\10_Deployment_Produccion\scripts\iniciar_site_web.bat
```

## Datos

El dashboard público usa los mismos servicios OpenMeteo que la API (`backend/05_APIs_Externas/api_rest/services.py`), sin JWT.

Para acceso completo (agrícola, alertas, ML): use **Vue** + API en `frontend/vue`.

## Túnel público (ngrok)

```bash
python backend/10_Deployment_Produccion/scripts/ejecutar_con_ngrok.py
# o
python site-web/streamlit/ngrok_tunnel.py
```
