# Referencia API METGO 3D

## Documentación interactiva

| Entorno | URL |
|---------|-----|
| Local | http://127.0.0.1:8080/api/docs |
| Producción | https://metgo-api.onrender.com/api/docs |

Spec OpenAPI: `/api/openapi.json`  
Archivo fuente: `backend/05_APIs_Externas/api_rest/openapi.yaml`

## Autenticación

```http
POST /api/auth/login
Content-Type: application/json

{"username": "admin", "password": "admin123"}
```

Respuesta: `access_token` (JWT). Enviar en rutas protegidas:

```http
Authorization: Bearer <token>
```

## Endpoints principales (MVP)

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/api/health` | No | Estado, versión, uptime, caché, OpenMeteo |
| GET | `/api/docs` | No | Swagger UI |
| POST | `/api/auth/login` | No | JWT |
| GET | `/api/estaciones` | Sí | Estaciones |
| GET | `/api/meteo/{id}` | Sí | Resumen meteo |
| GET | `/api/alertas` | Sí | Alertas |
| GET | `/api/catalogo` | Sí | Catálogo módulos (alias `/api/modulos`) |
| GET | `/api/servicios/streamlit/{id}/visor` | Sí | URL visor iframe |

## Health (ejemplo)

```json
{
  "status": "ok",
  "version": "a1b2c3d",
  "uptime_s": 3600,
  "latencia_openmeteo_ms": 420,
  "openmeteo": true,
  "cache_hits": 12,
  "cache_misses": 3,
  "timestamp": "2026-05-23T12:00:00"
}
```

Más detalle: [`docs/roadmap/fase-1/`](../roadmap/fase-1/).
