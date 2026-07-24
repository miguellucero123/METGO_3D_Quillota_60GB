# DT-1 — Eliminar rutas hardcodeadas

> **Estado (2026-07-24):** casi cerrado en runtime.  
> Launchers `ejecutar_sistema_organizado.py` / `_final` / `_reorganizado` usan `metgo.paths` + checklist F.

```bash
rg "04_Dashboards" -g "*.py"
```

**Hecho:**
- SPA `frontend/vue/` en docs
- `metgo.paths.streamlit_dashboard_path` / `frontend_vue_dir`
- Launchers Streamlit 8501–8513 sin `04_Dashboards_Unificados`

**Pendiente (bajo):**
- Scripts históricos `reorganizar_proyecto_v2/v3.py` (migración one-shot; no runtime)
- Criterio estricto: 0 menciones en `.py` productivos fuera de `paths.py` y scripts de migración
