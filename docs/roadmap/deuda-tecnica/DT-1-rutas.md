# DT-1 — Eliminar rutas hardcodeadas

```bash
grep -r "04_Dashboards" --include="*.py"
grep -r "frontend/dashboards" --include="*.py"
```

Reemplazar por `metgo.paths.*` salvo en `metgo/paths.py`.

**Criterio:** 0 ocurrencias legacy fuera de paths.
