# HTML estático (archivado)

Estos archivos **ya no se usan en producción**. Fueron reemplazados por dashboards Streamlit dinámicos con tema METGO unificado.

| HTML (archivado) | Reemplazo dinámico |
|------------------|-------------------|
| `dashboard_metgo_3d.html` | `dashboard_metgo_3d.py` (puerto 8513) |
| `dashboard_global_html.html` | `dashboard_global_html.py` o `dashboard_global_metricas.py` (8507) |
| `dashboard_html_completo.html` | `dashboard_html_completo.py` o `dashboard_completo_metgo.py` |
| `dashboard_sistema_unificado.html` | `dashboard_sistema_unificado.py` (8512) |

Ejecutar:

```bash
streamlit run frontend/dashboards/dashboard_sistema_unificado.py --server.port 8512
```

Ver `../DISENO_UNIFICADO.md`.
