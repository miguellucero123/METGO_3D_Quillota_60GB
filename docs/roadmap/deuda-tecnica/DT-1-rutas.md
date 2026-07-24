# DT-1 — Eliminar rutas hardcodeadas

> **Estado (2026-07-24):** parcial — runtime API/Vue vía `metgo.paths` / `metgo_paths`.  
> Residual: scripts legacy en `backend/10_Deployment_Produccion/scripts/ejecutar_sistema_*.py` y docs antiguos.

```bash
rg "04_Dashboards" -g "*.py" -g "*.md"
```

Reemplazar por `metgo.paths.*` salvo en `metgo/paths.py` (y menciones históricas en docs).

**Hecho:**
- SPA en `frontend/vue/` (docs `ESTRUCTURA_PROYECTO_METGO.md` + `API_REST.md` actualizados)
- Capas: `docs/CAPAS_OPERACION.md`

**Pendiente:**
- Scripts launcher `ejecutar_sistema_organizado.py` (y siblings) → usar `metgo.paths`
- Criterio estricto: 0 ocurrencias legacy en `.py` de producción fuera de `paths.py`
