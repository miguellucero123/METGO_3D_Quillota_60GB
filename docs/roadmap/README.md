# Roadmap de implementación METGO 3D

Estructura para ejecutar el [prompt MVP](../PROMPT_MVP_METGO.md) y el rol en **`AGENTS.md`**.

## Carpetas

| Carpeta | Contenido |
|---------|-----------|
| [`fase-1/`](fase-1/) | Consolidar MVP (semanas 1–6) — **prioridad alta** |
| [`fase-2/`](fase-2/) | Producto ampliado (semanas 7–12) |
| [`fase-3/`](fase-3/) | Escala y datos propios (meses 3–6) |
| [`deuda-tecnica/`](deuda-tecnica/) | Tareas transversales (DT-1 … DT-3) |

## Estado de integración en código

| Tarea | Estado | Ubicación en repo |
|-------|--------|-------------------|
| 1.1 OpenAPI + Swagger | Integrado | `api_rest/openapi.yaml`, `api_rest/docs_routes.py` |
| 1.2 CI GitHub Actions | Integrado | `.github/workflows/ci.yml` |
| 1.3 Health dashboard | Integrado | `api_rest/health.py`, `frontend/vue/.../EstadoView.vue` |
| 1.4 Caché OpenMeteo | Integrado | `backend/08_Gestion_Datos/cache_openmeteo.py` |
| 1.5 UX puertos | Integrado | `PuertosView.vue`, `QUE_VER_EN_NUBE.md` |
| 2.x – 3.x | Pendiente | Ver fichas en cada fase |

## Cómo trabajar una tarea

1. Abrir la ficha `fase-N/XX-nombre.md`.
2. Seguir **criterio de aceptación** y **verificación**.
3. Responder con el formato de `AGENTS.md` (análisis, archivos, implementación, verificación, fase).
