# API REST METGO

API HTTP (Flask) que expone datos OpenMeteo y lógica de alertas/recomendaciones para el frontend Vue.

## Inicio

```bash
cd METGO_3D_Quillota_60GB
pip install -r requirements.txt
python 10_Deployment_Produccion/scripts/iniciar_api_rest.py
```

Por defecto: **http://127.0.0.1:8080** (cambiable con `METGO_API_PORT`, p. ej. `9090`)

Variables de entorno:

| Variable | Default | Descripción |
|----------|---------|-------------|
| `METGO_API_PORT` | `8080` | Puerto (`9090` u otro si 8080 está ocupado) |
| `METGO_API_HOST` | `127.0.0.1` | Host |
| `METGO_API_DEBUG` | `0` | `1` = modo debug Flask |
| `METGO_CORS_ORIGINS` | `*` | Orígenes CORS separados por coma |
| `METGO_JWT_SECRET` | (dev) | Secreto para firmar tokens |
| `METGO_JWT_EXPIRATION_SECONDS` | `3600` | Duración del token |
| `METGO_API_AUTH_REQUIRED` | `1` | `0` desactiva JWT (solo desarrollo) |
| `METGO_PASSWORD_*` | — | Mismas credenciales que Streamlit |

## Autenticación JWT

### Login

```http
POST /api/auth/login
Content-Type: application/json

{"username": "admin", "password": "tu_password"}
```

Respuesta:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": { "username": "admin", "role": "admin" }
}
```

### Rutas protegidas

Enviar header: `Authorization: Bearer <access_token>`

Rutas públicas: `GET /api/health`, `POST /api/auth/login`, `GET /api/public/estaciones`, `GET /api/public/meteo/{id}`

### Otros endpoints auth

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/auth/me` | Usuario actual (requiere token) |
| POST | `/api/auth/refresh` | Nuevo token (requiere token válido) |

Credenciales compartidas con Streamlit: `metgo_auth.py` + variables `METGO_PASSWORD_ADMIN`, `METGO_PASSWORD_USER`, `METGO_PASSWORD_METGO`.

## Endpoints públicos de solo lectura (sin JWT)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/public/estaciones` | Estaciones principales |
| GET | `/api/public/meteo/{id}` | Resumen meteorológico (mismo JSON que `/api/meteo/{id}`) |

Uso previsto: `site-web`, widgets externos o landing. Sin datos agrícolas ni alertas.

## Endpoints de datos (requieren JWT)

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/api/health` | No | Estado y conectividad OpenMeteo |
| GET | `/api/estaciones` | JWT | Lista de estaciones |
| GET | `/api/meteo/{id}` | JWT | Resumen actual |
| GET | `/api/meteo/{id}/pronostico?dias=7` | JWT | Pronóstico diario |
| GET | `/api/meteo/{id}/historico?dias=30` | JWT | Histórico diario |
| GET | `/api/alertas?estacion=quillota` | JWT | Alertas por umbrales |
| GET | `/api/agricola/{id}` | JWT | Recomendaciones agrícolas |

### IDs de estación (slug)

`quillota`, `los_nogales`, `hijuelas`, `limache`, `olmue`

### Ejemplo resumen meteo

```json
{
  "estacion_id": "quillota",
  "estacion": "Quillota",
  "temperatura": 16.2,
  "temperatura_max": 22.1,
  "temperatura_min": 8.5,
  "humedad": 72.0,
  "viento": 14.0,
  "precipitacion": 0.0,
  "presion": 1013.2,
  "fuente": "openmeteo_real",
  "actualizado": "2026-05-23T12:00:00"
}
```

## Frontend Vue

Terminal 1 — API:

```bash
python 10_Deployment_Produccion/scripts/iniciar_api_rest.py
```

Terminal 2 — Vue (proxy `/api` → puerto 8080):

```bash
cd 04_Dashboards_Unificados/frontend_vue
npm install
npm run dev
```

## Ubicación del código

- `05_APIs_Externas/api_rest/auth_routes.py` — JWT login y decorador
- `07_Sistema_Monitoreo/scripts/metgo_auth.py` (wrapper `metgo_auth.py` en raíz) — credenciales Streamlit + API
