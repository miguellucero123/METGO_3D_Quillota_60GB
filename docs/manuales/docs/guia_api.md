# 🔌 Guía de API - METGO 3D

## 🌾 Sistema Meteorológico Agrícola Quillota

### 📋 Tabla de Contenidos

1. [Introducción a la API](#introducción-a-la-api)
2. [Autenticación](#autenticación)
3. [Endpoints Principales](#endpoints-principales)
4. [API Meteorológica](#api-meteorológica)
5. [API Agrícola](#api-agrícola)
6. [API de Alertas](#api-de-alertas)
7. [API IoT](#api-iot)
8. [API de Machine Learning](#api-de-machine-learning)
9. [API de Visualización](#api-de-visualización)
10. [API de Reportes](#api-de-reportes)
11. [API de Configuración](#api-de-configuración)
12. [API de Monitoreo](#api-de-monitoreo)
13. [Códigos de Error](#códigos-de-error)
14. [Ejemplos de Uso](#ejemplos-de-uso)
15. [SDKs y Clientes](#sdks-y-clientes)

---

## 🚀 Introducción a la API

**METGO 3D** proporciona una API RESTful completa para acceder a todos los servicios del sistema meteorológico agrícola. La API está diseñada para ser:

- **RESTful**: Sigue los principios REST
- **JSON**: Todas las respuestas en formato JSON
- **Documentada**: Documentación completa con ejemplos
- **Versionada**: Soporte para versiones de API
- **Rate Limited**: Límites de velocidad para proteger el sistema
- **Autenticada**: Sistema de autenticación JWT

### Base URL

```
http://localhost:5000/api/v1
```

### Versiones de API

- **v1**: Versión actual (estable)
- **v2**: Versión en desarrollo (beta)

### Formato de Respuesta

Todas las respuestas siguen el formato estándar:

```json
{
  "success": true,
  "data": {},
  "message": "Operación exitosa",
  "timestamp": "2025-01-02T12:00:00Z",
  "version": "2.0"
}
```

### Rate Limiting

- **Límite**: 1000 requests por hora por IP
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

---

## 🔐 Autenticación

### JWT Token

La API utiliza JWT (JSON Web Tokens) para autenticación.

#### Obtener Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "usuario",
  "password": "contraseña"
}
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "token": "YOUR_JWT_TOKEN_HERE",
    "expires_in": 3600,
    "token_type": "Bearer"
  }
}
```

#### Usar Token

```http
GET /api/v1/meteorologia/datos
Authorization: Bearer YOUR_JWT_TOKEN_HERE
```

#### Renovar Token

```http
POST /api/v1/auth/refresh
Authorization: Bearer <token_actual>
```

#### Cerrar Sesión

```http
POST /api/v1/auth/logout
Authorization: Bearer <token>
```

---

## 🏠 Endpoints Principales

### Health Check

```http
GET /api/v1/health
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "2.0",
    "timestamp": "2025-01-02T12:00:00Z",
    "services": {
      "database": "healthy",
      "apis": "healthy",
      "ml_models": "healthy"
    }
  }
}
```

### Información del Sistema

```http
GET /api/v1/info
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "name": "METGO 3D",
    "version": "2.0",
    "description": "Sistema Meteorológico Agrícola Quillota",
    "author": "Equipo METGO 3D",
    "license": "MIT",
    "repository": "https://github.com/tu-usuario/metgo3d",
    "documentation": "https://metgo3d.readthedocs.io"
  }
}
```

### Estadísticas del Sistema

```http
GET /api/v1/stats
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "total_requests": 15420,
    "active_users": 25,
    "data_points": 1250000,
    "alerts_active": 3,
    "uptime": "99.9%",
    "last_update": "2025-01-02T12:00:00Z"
  }
}
```

---

## 🌤️ API Meteorológica

### Base URL: `/api/v1/meteorologia`

#### Obtener Datos Meteorológicos

```http
GET /api/v1/meteorologia/datos
```

**Parámetros de consulta**:
- `fecha_inicio` (opcional): Fecha de inicio (ISO 8601)
- `fecha_fin` (opcional): Fecha de fin (ISO 8601)
- `variables` (opcional): Variables específicas (comma-separated)
- `limit` (opcional): Límite de registros (default: 100)
- `offset` (opcional): Offset para paginación (default: 0)

**Ejemplo**:
```http
GET /api/v1/meteorologia/datos?fecha_inicio=2025-01-01T00:00:00Z&variables=temperatura,humedad&limit=50
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "datos": [
      {
        "timestamp": "2025-01-02T12:00:00Z",
        "temperatura": 22.5,
        "humedad": 65.2,
        "precipitacion": 0.0,
        "viento_velocidad": 3.2,
        "viento_direccion": 180,
        "presion": 1013.25,
        "radiacion_solar": 450.0,
        "punto_rocio": 15.8
      }
    ],
    "total": 1250,
    "limit": 50,
    "offset": 0
  }
}
```

#### Obtener Datos Actuales

```http
GET /api/v1/meteorologia/actual
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "timestamp": "2025-01-02T12:00:00Z",
    "temperatura": 22.5,
    "humedad": 65.2,
    "precipitacion": 0.0,
    "viento_velocidad": 3.2,
    "viento_direccion": 180,
    "presion": 1013.25,
    "radiacion_solar": 450.0,
    "punto_rocio": 15.8,
    "calidad": 0.95
  }
}
```

#### Obtener Pronóstico

```http
GET /api/v1/meteorologia/pronostico
```

**Parámetros de consulta**:
- `horizonte` (opcional): Horas de pronóstico (default: 24)

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "pronostico": [
      {
        "timestamp": "2025-01-02T13:00:00Z",
        "temperatura": 23.1,
        "humedad": 63.8,
        "precipitacion": 0.0,
        "confianza": 0.87
      }
    ],
    "horizonte": 24,
    "modelo": "lstm",
    "generado": "2025-01-02T12:00:00Z"
  }
}
```

#### Obtener Estadísticas

```http
GET /api/v1/meteorologia/estadisticas
```

**Parámetros de consulta**:
- `periodo` (opcional): Período (diario, semanal, mensual, anual)

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "periodo": "diario",
    "estadisticas": {
      "temperatura": {
        "min": 15.2,
        "max": 28.5,
        "promedio": 21.8,
        "mediana": 22.1,
        "desviacion_estandar": 3.2
      },
      "humedad": {
        "min": 45.0,
        "max": 95.0,
        "promedio": 68.5,
        "mediana": 67.0,
        "desviacion_estandar": 12.3
      }
    }
  }
}
```

---

## 🌾 API Agrícola

### Base URL: `/api/v1/agricola`

#### Obtener Índices Agrícolas

```http
GET /api/v1/agricola/indices
```

**Parámetros de consulta**:
- `fecha_inicio` (opcional): Fecha de inicio
- `fecha_fin` (opcional): Fecha de fin
- `indices` (opcional): Índices específicos

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "indices": [
      {
        "timestamp": "2025-01-02T12:00:00Z",
        "grados_dia": 15.2,
        "confort_termico": 0.75,
        "necesidad_riego": 0.3,
        "riesgo_heladas": 0.1,
        "riesgo_hongos": 0.2
      }
    ]
  }
}
```

#### Obtener Recomendaciones Agrícolas

```http
GET /api/v1/agricola/recomendaciones
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "recomendaciones": [
      {
        "tipo": "riego",
        "nivel": "info",
        "mensaje": "Condiciones óptimas para riego",
        "timestamp": "2025-01-02T12:00:00Z",
        "validez_hasta": "2025-01-02T18:00:00Z"
      }
    ]
  }
}
```

#### Obtener Alertas Agrícolas

```http
GET /api/v1/agricola/alertas
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "alertas": [
      {
        "id": "alerta_001",
        "tipo": "heladas",
        "nivel": "warning",
        "mensaje": "Riesgo de heladas en las próximas 6 horas",
        "timestamp": "2025-01-02T12:00:00Z",
        "activa": true
      }
    ]
  }
}
```

---

## 🚨 API de Alertas

### Base URL: `/api/v1/alertas`

#### Obtener Alertas Activas

```http
GET /api/v1/alertas/activas
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "alertas": [
      {
        "id": "alerta_001",
        "nivel": "warning",
        "mensaje": "Temperatura alta detectada",
        "timestamp": "2025-01-02T12:00:00Z",
        "servicio": "meteorologia",
        "metrica": "temperatura",
        "valor": 35.2,
        "umbral": 35.0,
        "resuelta": false
      }
    ],
    "total": 3
  }
}
```

#### Obtener Historial de Alertas

```http
GET /api/v1/alertas/historial
```

**Parámetros de consulta**:
- `fecha_inicio` (opcional): Fecha de inicio
- `fecha_fin` (opcional): Fecha de fin
- `nivel` (opcional): Nivel de alerta
- `limit` (opcional): Límite de registros

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "alertas": [
      {
        "id": "alerta_001",
        "nivel": "warning",
        "mensaje": "Temperatura alta detectada",
        "timestamp": "2025-01-02T12:00:00Z",
        "resuelta": true,
        "resuelta_en": "2025-01-02T12:30:00Z"
      }
    ],
    "total": 150,
    "limit": 50,
    "offset": 0
  }
}
```

#### Crear Alerta Manual

```http
POST /api/v1/alertas
Content-Type: application/json

{
  "nivel": "info",
  "mensaje": "Alerta manual creada",
  "servicio": "manual",
  "metrica": "custom",
  "valor": 0,
  "umbral": 0
}
```

#### Resolver Alerta

```http
PUT /api/v1/alertas/{alerta_id}/resolver
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "id": "alerta_001",
    "resuelta": true,
    "resuelta_en": "2025-01-02T12:30:00Z"
  }
}
```

---

## 📡 API IoT

### Base URL: `/api/v1/iot`

#### Obtener Datos de Sensores

```http
GET /api/v1/iot/sensores
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "sensores": [
      {
        "sensor_id": "sensor_001",
        "tipo": "temperatura",
        "ubicacion": {
          "latitud": -32.8833,
          "longitud": -71.2333,
          "altitud": 127
        },
        "estado": "activo",
        "bateria": 85.0,
        "senal": 90.0,
        "ultima_lectura": "2025-01-02T12:00:00Z"
      }
    ]
  }
}
```
#### Obtener Lecturas de Sensores

```http
GET /api/v1/iot/lecturas
```

**Parámetros de consulta**:
- `sensor_id` (opcional): ID del sensor
- `fecha_inicio` (opcional): Fecha de inicio
- `fecha_fin` (opcional): Fecha de fin
- `limit` (opcional): Límite de registros

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "lecturas": [
      {
        "sensor_id": "sensor_001",
        "tipo": "temperatura",
        "timestamp": "2025-01-02T12:00:00Z",
        "valor": 22.5,
        "unidad": "°C",
        "bateria": 85.0,
        "senal": 90.0
      }
    ],
    "total": 1000,
    "limit": 50,
    "offset": 0
  }
}
```

#### Obtener Estado de Gateway

```http
GET /api/v1/iot/gateways
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "gateways": [
      {
        "gateway_id": "gateway_001",
        "estado": "activo",
        "total_sensores": 10,
        "ultima_comunicacion": "2025-01-02T12:00:00Z",
        "ubicacion": {
          "latitud": -32.8833,
          "longitud": -71.2333
        }
      }
    ]
  }
}
```

---

## 🤖 API de Machine Learning

### Base URL: `/api/v1/ml`

#### Obtener Modelos Disponibles

```http
GET /api/v1/ml/modelos
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "modelos": [
      {
        "nombre": "lstm_temperatura",
        "tipo": "lstm",
        "variable": "temperatura",
        "version": "1.0",
        "entrenado": true,
        "precision": 0.87,
        "ultima_actualizacion": "2025-01-02T12:00:00Z"
      }
    ]
  }
}
```

#### Obtener Predicciones

```http
GET /api/v1/ml/predicciones
```

**Parámetros de consulta**:
- `modelo` (opcional): Nombre del modelo
- `variable` (opcional): Variable a predecir
- `horizonte` (opcional): Horas de predicción

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "predicciones": [
      {
        "timestamp": "2025-01-02T13:00:00Z",
        "modelo": "lstm_temperatura",
        "variable": "temperatura",
        "prediccion": 23.1,
        "confianza": 0.87,
        "horizonte": 1
      }
    ]
  }
}
```

#### Entrenar Modelo

```http
POST /api/v1/ml/entrenar
Content-Type: application/json

{
  "modelo": "lstm_temperatura",
  "datos_entrenamiento": "2024-01-01T00:00:00Z",
  "datos_validacion": "2024-12-31T23:59:59Z",
  "parametros": {
    "epochs": 100,
    "batch_size": 32,
    "learning_rate": 0.001
  }
}
```

#### Evaluar Modelo

```http
GET /api/v1/ml/evaluacion/{modelo}
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "modelo": "lstm_temperatura",
    "metricas": {
      "mae": 1.2,
      "mse": 2.1,
      "rmse": 1.45,
      "r2": 0.87
    },
    "fecha_evaluacion": "2025-01-02T12:00:00Z"
  }
}
```

---

## 📊 API de Visualización

### Base URL: `/api/v1/visualizacion`

#### Obtener Gráficos Disponibles

```http
GET /api/v1/visualizacion/graficos
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "graficos": [
      {
        "id": "temperatura_tiempo",
        "nombre": "Temperatura en el Tiempo",
        "tipo": "line",
        "variables": ["temperatura"],
        "descripcion": "Gráfico de temperatura vs tiempo"
      }
    ]
  }
}
```

#### Generar Gráfico

```http
POST /api/v1/visualizacion/generar
Content-Type: application/json

{
  "grafico_id": "temperatura_tiempo",
  "fecha_inicio": "2025-01-01T00:00:00Z",
  "fecha_fin": "2025-01-02T00:00:00Z",
  "formato": "png"
}
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "grafico_id": "temp_001",
    "url": "/api/v1/visualizacion/graficos/temp_001.png",
    "formato": "png",
    "tamaño": 1024
  }
}
```

#### Obtener Dashboard HTML

```http
GET /api/v1/visualizacion/dashboard
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "dashboard_id": "dashboard_001",
    "url": "/api/v1/visualizacion/dashboards/dashboard_001.html",
    "tipo": "interactivo",
    "componentes": ["graficos", "metricas", "alertas"]
  }
}
```

---

## 📋 API de Reportes

### Base URL: `/api/v1/reportes`

#### Obtener Reportes Disponibles

```http
GET /api/v1/reportes
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "reportes": [
      {
        "id": "reporte_001",
        "nombre": "Reporte Diario",
        "tipo": "diario",
        "formato": "pdf",
        "generado": "2025-01-02T12:00:00Z"
      }
    ]
  }
}
```

#### Generar Reporte

```http
POST /api/v1/reportes/generar
Content-Type: application/json

{
  "tipo": "diario",
  "fecha": "2025-01-02",
  "formato": "pdf",
  "incluir_graficos": true
}
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "reporte_id": "reporte_001",
    "url": "/api/v1/reportes/descargar/reporte_001.pdf",
    "formato": "pdf",
    "tamaño": 2048
  }
}
```

#### Descargar Reporte

```http
GET /api/v1/reportes/descargar/{reporte_id}
```

---

## ⚙️ API de Configuración

### Base URL: `/api/v1/configuracion`

#### Obtener Configuración

```http
GET /api/v1/configuracion
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "sistema": {
      "nombre": "METGO 3D",
      "version": "2.0",
      "entorno": "produccion"
    },
    "quillota": {
      "coordenadas": {
        "latitud": -32.8833,
        "longitud": -71.2333,
        "altitud": 127
      }
    },
    "meteorologia": {
      "variables": ["temperatura", "humedad", "precipitacion"]
    }
  }
}
```

#### Actualizar Configuración

```http
PUT /api/v1/configuracion
Content-Type: application/json

{
  "meteorologia": {
    "variables": ["temperatura", "humedad", "precipitacion", "viento"]
  }
}
```

#### Obtener Umbrales de Alertas

```http
GET /api/v1/configuracion/umbrales
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "temperatura": {
      "warning": 35.0,
      "critical": 40.0
    },
    "humedad": {
      "warning": 90.0,
      "critical": 95.0
    }
  }
}
```

#### Actualizar Umbrales

```http
PUT /api/v1/configuracion/umbrales
Content-Type: application/json

{
  "temperatura": {
    "warning": 30.0,
    "critical": 35.0
  }
}
```

---

## 📈 API de Monitoreo

### Base URL: `/api/v1/monitoreo`

#### Obtener Métricas del Sistema

```http
GET /api/v1/monitoreo/metricas
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "metricas": [
      {
        "nombre": "cpu_uso",
        "valor": 45.2,
        "unidad": "%",
        "timestamp": "2025-01-02T12:00:00Z"
      }
    ]
  }
}
```

#### Obtener Estado de Servicios

```http
GET /api/v1/monitoreo/servicios
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "servicios": [
      {
        "nombre": "api_principal",
        "estado": "healthy",
        "uptime": 99.9,
        "latencia": 0.05,
        "errores": 0
      }
    ]
  }
}
```

#### Obtener Estadísticas de Monitoreo

```http
GET /api/v1/monitoreo/estadisticas
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "total_metricas": 1250,
    "alertas_activas": 3,
    "servicios_monitoreados": 13,
    "uptime_promedio": 99.9
  }
}
```

---

## ❌ Códigos de Error

### Códigos HTTP

- **200**: OK - Operación exitosa
- **201**: Created - Recurso creado exitosamente
- **400**: Bad Request - Solicitud inválida
- **401**: Unauthorized - No autenticado
- **403**: Forbidden - Sin permisos
- **404**: Not Found - Recurso no encontrado
- **429**: Too Many Requests - Límite de velocidad excedido
- **500**: Internal Server Error - Error interno del servidor
- **503**: Service Unavailable - Servicio no disponible

### Formato de Error

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Parámetros de entrada inválidos",
    "details": {
      "field": "fecha_inicio",
      "reason": "Formato de fecha inválido"
    }
  },
  "timestamp": "2025-01-02T12:00:00Z"
}
```

### Códigos de Error Específicos

- **VALIDATION_ERROR**: Error de validación de parámetros
- **AUTHENTICATION_ERROR**: Error de autenticación
- **AUTHORIZATION_ERROR**: Error de autorización
- **RESOURCE_NOT_FOUND**: Recurso no encontrado
- **RATE_LIMIT_EXCEEDED**: Límite de velocidad excedido
- **INTERNAL_ERROR**: Error interno del servidor
- **SERVICE_UNAVAILABLE**: Servicio no disponible

---

## 💡 Ejemplos de Uso

### Python

```python
import requests
import json

# Configuración
BASE_URL = "http://localhost:5000/api/v1"
TOKEN = "tu-jwt-token"

# Headers
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Obtener datos meteorológicos
response = requests.get(
    f"{BASE_URL}/meteorologia/datos",
    headers=headers,
    params={
        "fecha_inicio": "2025-01-01T00:00:00Z",
        "variables": "temperatura,humedad",
        "limit": 10
    }
)

if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### JavaScript

```javascript
const BASE_URL = "http://localhost:5000/api/v1";
const TOKEN = "tu-jwt-token";

// Configuración
const config = {
    headers: {
        "Authorization": `Bearer ${TOKEN}`,
        "Content-Type": "application/json"
    }
};

// Obtener datos meteorológicos
async function obtenerDatosMeteorologicos() {
    try {
        const response = await fetch(
            `${BASE_URL}/meteorologia/datos?limit=10`,
            config
        );
        
        if (response.ok) {
            const data = await response.json();
            console.log(data);
        } else {
            console.error(`Error: ${response.status}`);
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

// Llamar función
obtenerDatosMeteorologicos();
```

### cURL

```bash
# Obtener token
TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"usuario","password":"contraseña"}' \
  | jq -r '.data.token')

# Obtener datos meteorológicos
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/v1/meteorologia/datos?limit=10"

# Obtener alertas activas
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/v1/alertas/activas"

# Generar reporte
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tipo":"diario","formato":"pdf"}' \
  "http://localhost:5000/api/v1/reportes/generar"
```

---

## 🔧 SDKs y Clientes

### Python SDK

```python
# Instalar SDK
pip install metgo3d-sdk

# Usar SDK
from metgo3d import METGO3DClient

client = METGO3DClient(
    base_url="http://localhost:5000/api/v1",
    token="tu-jwt-token"
)

# Obtener datos meteorológicos
datos = client.meteorologia.obtener_datos(
    fecha_inicio="2025-01-01T00:00:00Z",
    variables=["temperatura", "humedad"],
    limit=10
)

# Obtener alertas
alertas = client.alertas.obtener_activas()

# Generar reporte
reporte = client.reportes.generar(
    tipo="diario",
    formato="pdf"
)
```

### JavaScript SDK

```javascript
// Instalar SDK
npm install metgo3d-sdk

// Usar SDK
import { METGO3DClient } from 'metgo3d-sdk';

const client = new METGO3DClient({
    baseUrl: 'http://localhost:5000/api/v1',
    token: 'tu-jwt-token'
});

// Obtener datos meteorológicos
const datos = await client.meteorologia.obtenerDatos({
    fechaInicio: '2025-01-01T00:00:00Z',
    variables: ['temperatura', 'humedad'],
    limit: 10
});

// Obtener alertas
const alertas = await client.alertas.obtenerActivas();

// Generar reporte
const reporte = await client.reportes.generar({
    tipo: 'diario',
    formato: 'pdf'
});
```

### Postman Collection

```json
{
  "info": {
    "name": "METGO 3D API",
    "description": "Colección de APIs para METGO 3D",
    "version": "2.0"
  },
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{jwt_token}}",
        "type": "string"
      }
    ]
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:5000/api/v1"
    }
  ]
}
```

---

## 📞 Soporte de API

### Recursos de Ayuda

- **Documentación**: `docs/guia_api.md`
- **Postman Collection**: `docs/postman_collection.json`
- **SDKs**: `sdk/`
- **Ejemplos**: `examples/`

### Contacto

- **Email**: api@metgo3d.cl
- **GitHub Issues**: https://github.com/tu-usuario/metgo3d/issues
- **Documentación**: https://metgo3d.readthedocs.io

### Rate Limiting

- **Límite**: 1000 requests por hora por IP
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- **Excedido**: HTTP 429 con `Retry-After` header

---

## 🎉 ¡API Lista para Usar!

**METGO 3D API está completamente documentada y lista para usar**

### Próximos Pasos

1. **Obtener token**: `POST /api/v1/auth/login`
2. **Explorar endpoints**: Comenzar con `/api/v1/health`
3. **Integrar SDK**: Usar Python o JavaScript SDK
4. **Configurar monitoreo**: Usar `/api/v1/monitoreo`
5. **Implementar alertas**: Usar `/api/v1/alertas`

### Enlaces Útiles

- **Guía de Usuario**: [docs/guia_usuario.md](docs/guia_usuario.md)
- **Guía de Instalación**: [docs/guia_instalacion.md](docs/guia_instalacion.md)
- **Configuración**: [docs/guia_configuracion.md](docs/guia_configuracion.md)
- **Troubleshooting**: [docs/troubleshooting.md](docs/troubleshooting.md)

---

**Sistema Meteorológico Agrícola Quillota - API v2.0**

*Documentación completa de la API* ✅
