# Site-web METGO

Capa de **exposición pública**: dashboards Streamlit abiertos y assets estáticos para web externa.

## Estructura

| Carpeta | Uso |
|---------|-----|
| `streamlit/` | `dashboard_web_publico.py` y futuros dashboards públicos |
| `static/` | Imágenes, CSS o landing estática |

## Ejecución local

```bash
streamlit run site-web/streamlit/dashboard_web_publico.py
```

El panel con login de operadores permanece en `frontend/dashboards/`.
