# TAREA 1.1 — OpenAPI 3 + Swagger UI

**Fase:** 1.1 | **Prioridad:** alta

## Objetivo

`GET /api/docs` → Swagger UI interactivo. Terceros prueban login y meteo sin leer código.

## Implementación en repo

- `backend/05_APIs_Externas/api_rest/openapi.yaml`
- `backend/05_APIs_Externas/api_rest/docs_routes.py` → registra `/api/docs`, `/api/openapi.json`
- `docs/manuales/API_REFERENCE.md`

## Verificación

```bash
curl -s http://127.0.0.1:8080/api/health
# Navegador: http://127.0.0.1:8080/api/docs
```

## Criterio de aceptación

- UI Swagger carga y lista endpoints principales.
- Spec incluye auth, estaciones, meteo, alertas, catálogo, visor.
