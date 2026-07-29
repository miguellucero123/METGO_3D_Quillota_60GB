# Desarrollo local METGO

Guía rápida para levantar el stack en PC (Windows/Linux). Producción: Vue en Netlify, API en Render, Streamlit Cloud.

## Requisitos

- Python **3.10+** (recomendado: Anaconda del proyecto)
- Node.js **18+** y `npm` (solo Vue)
- `pip install -r requirements.txt` en la raíz del repo

## Arranque recomendado (Windows)

### 1. API REST (puerto 8080)

```powershell
cd D:\METGO_3D_Quillota_60GB
$env:METGO_ML_AUTO_TRAIN='0'
D:\Miguel\Anaconda_AIEP\python.exe backend\10_Deployment_Produccion\scripts\iniciar_api_rest.py
```

O un clic:

- `backend\10_Deployment_Produccion\scripts\iniciar_metgo_desarrollo.bat` — API + Vue (con `METGO_ML_AUTO_TRAIN=0`)
- `backend\10_Deployment_Produccion\scripts\iniciar_stack_local.bat` — API + Vue + Streamlit 8502, 8503, 8505, 8506 y 8508

Health: http://127.0.0.1:8080/api/health

### 2. Frontend Vue (puerto 5173)

```powershell
cd frontend\vue
npm install
npm run dev
```

Abrir **http://127.0.0.1:5173** (no usar el iframe de Cursor para login; usar Chrome/Edge).

> **Solo desarrollo local / no producción.** Credenciales demo: `admin` / `admin123` (ver tabla abajo). En Render no hay fallbacks: use `METGO_PASSWORD_*`.

### 3. Streamlit principal (opcional, 8501)

```powershell
streamlit run streamlit_app.py
```

## Puertos locales

| Puerto | Servicio | Comando / ruta |
|--------|----------|----------------|
| **8080** | API Flask + JWT | `iniciar_api_rest.py` |
| **5173** | Vue 3 (uso diario) | `frontend/vue` → `npm run dev` |
| **8501** | Streamlit Cloud entry (`streamlit_app.py`) | raíz repo |
| **8502** | Análisis meteorológico profesional (Plotly) | `frontend/dashboards/dashboard_meteorologico_profesional.py` |
| **8503** | Gestión agrícola inteligente | `frontend/dashboards/dashboard_agricola_inteligente.py` |
| **8504** | Monitoreo (API o simulación IoT) | `frontend/dashboards/dashboard_monitoreo_tiempo_real.py` |
| **8506** | Visualizaciones avanzadas | `frontend/dashboards/dashboard_visualizaciones_avanzadas.py` |
| **8507** | Métricas globales (KPIs API + series ilustrativas) | `frontend/dashboards/dashboard_global_metricas.py` |
| **8505** | ML / MLOps (registry + demo) | `frontend/dashboards/dashboard_ia_ml_avanzado.py` |
| **8508** | Agricultura de precisión (API + ilustrativo) | `frontend/dashboards/dashboard_agricultura_precision.py` |
| **8509** | Análisis comparativo (API valle + ilustrativo) | `frontend/dashboards/dashboard_analisis_comparativo.py` |
| **8510** | Alertas automáticas (API + demo) | `frontend/dashboards/dashboard_alertas_automaticas.py` |
| **8511** | Dashboard simple (API OpenMeteo por defecto) | `frontend/dashboards/dashboard_simple_optimizado.py` |
| **8512** | Dashboard unificado (API valle o demo) | `frontend/dashboards/dashboard_unificado_diferenciado.py` |
| **8513** | Dashboard móvil (API + histórico 7d) | `frontend/dashboards/dashboard_mobile_optimizado.py` |

> **No** abrir :8080 como interfaz web; es solo REST. La UI operativa es **5173**.

### Dashboards Streamlit legacy (ejemplos)

```powershell
# Meteorológico profesional (8502) — datos OpenMeteo vía API
streamlit run frontend/dashboards/dashboard_meteorologico_profesional.py --server.port 8502

# Visualizaciones multi-estación (8506)
streamlit run frontend/dashboards/dashboard_visualizaciones_avanzadas.py --server.port 8506

# Comparativo estaciones (8509) — por defecto API METGO
streamlit run frontend/dashboards/dashboard_analisis_comparativo.py --server.port 8509

# Alertas (8510) — por defecto alertas reales de la API
streamlit run frontend/dashboards/dashboard_alertas_automaticas.py --server.port 8510
```

Requieren API en :8080 o acceso directo a OpenMeteo. En sidebar de cada dashboard legacy, elija **API METGO** cuando exista; el modo ilustrativo queda etiquetado como simulación.

## Variables de entorno útiles

| Variable | Uso |
|----------|-----|
| `METGO_ML_AUTO_TRAIN=0` | Arranque rápido de API sin entrenar ML al boot |
| `METGO_ML_ALLOW_SYNTHETIC=1` | Solo CI/tests: permite entrenar con datos sintéticos si no hay histórico |
| `METGO_API_PORT=8080` | Puerto API (default) |
| `METGO_JWT_SECRET` | Copiar desde `.env.example` → `.env` |
| `METGO_CORS_ORIGINS` | Orígenes Vue (`http://127.0.0.1:5173`) |

No commitear `.env` ni `secrets.toml`.

## Opción B — Docker Compose (Fase 2.5)

```bash
docker compose -f docker-compose.dev.yml up --build
```

- API: http://127.0.0.1:8080/api/health
- Vue: http://127.0.0.1:5173

## Usuarios demo (Fase 2 RBAC) — solo local

> **No usar en producción.** En Render defina `METGO_PASSWORD_*` fuertes y `METGO_ALLOW_SELF_REGISTER=0`.

| Usuario   | Contraseña | Rol      |
|-----------|------------|----------|
| admin     | admin123   | admin    |
| agronomo  | agro123    | agronomo |
| operador  | op123      | operador |
| lector    | lec123     | lectura  |
| user      | user123    | operador |
| metgo     | metgo2025  | agronomo |
| copiapo   | copiapo123 | lectura  |
| mantos    | mantos123  | operador |
| paine     | paine123   | lectura  |

## Rutas Vue (Fase 2+)

| Ruta | Contenido |
|------|-----------|
| `/meteo` | Condiciones actuales, pronóstico 7d, histórico 14d (sin fechas futuras) |
| `/meteo/historico` | 30 días, gráficos de línea + tabla |
| `/meteo/comparativo` | Comparación 5 estaciones del valle |
| `/metricas` | KPIs globales + detalle por estación |
| `/alertas/config` | Umbrales (roles operador+) |
| `/agricola` | Riego por cultivo, recomendaciones módulo 02 |
| `/ml` | Registry MLOps, predicciones, cola de entrenamiento |
| `/monitoreo` | Alertas, comparativo del valle, sensores IoT |

Histórico y pronóstico usan zona **America/Santiago**; el backend filtra días futuros en histórico.

## Tests

```powershell
python -m pytest tests/ -q
```

## Solución de problemas

| Síntoma | Acción |
|---------|--------|
| Login 404 en :8000 | Usar API en **8080**, no procesos viejos |
| API tarda minutos | `METGO_ML_AUTO_TRAIN=0` |
| `py` no funciona | Usar ruta completa a `python.exe` (Anaconda) |
| Temperaturas distintas 8502 vs Vue | Reiniciar API; ambos usan OpenMeteo/METGO (no simulación) |
| Histórico con días futuros | Actualizar API + recargar Vue (fix jun-2026) |

## Referencias

- `docs/PROMPT_MVP_METGO.md` · `docs/PROMPT_ESCALAMIENTO_MVP.md`
- `AGENTS.md` · `docs/roadmap/README.md`
