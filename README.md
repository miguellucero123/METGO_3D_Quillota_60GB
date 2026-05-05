# Dashboard METGO - Sistema Integrado de Monitoreo Meteorológico y Agrícola

Dashboard integrado para monitoreo meteorológico y agrícola en Quillota, Chile. El proyecto combina visualización en Streamlit, análisis de datos, modelos de ML y módulos especializados.

## Estado del repositorio (actualización 2026-05-05)

Este repositorio incorporó mejoras de seguridad, rendimiento, mantenibilidad y **reorganización de carpetas**:

- **Seguridad**: credenciales movidas a variables de entorno (`METGO_PASSWORD_{ADMIN,USER,METGO}`) y soporte de `.env` mediante `python-dotenv`.
- **Rendimiento**: caching con TTL para llamadas a APIs meteorológicas (en Streamlit) para reducir latencia y cuotas.
- **Higiene del repo**: exclusión de respaldos pesados (`respaldo_*/`) desde git y `.env` ignorado.
- **Dependencias**: `requirements.txt` actualizado para reflejar imports reales (ML/visualización + dotenv).
- **CI/DX**: workflow de GitHub Actions con smoke test de imports y chequeo de sintaxis; `Makefile` con comandos comunes.
- **Organización**: dashboards, scripts y documentación reagrupados en carpetas `dashboards/`, `scripts/` y `docs/`.

## Características principales

### Sistema de autenticación
- Login con usuario y contraseña.
- Acceso controlado por credenciales configurables vía variables de entorno.

### Monitoreo meteorológico
- Datos para Quillota y estaciones cercanas.
- Gráficos interactivos.
- Pronósticos y análisis comparativo.
- Alertas meteorológicas.

### Análisis agrícola
- Recomendaciones agrícolas basadas en modelos.
- Análisis de riesgo y predicción.

### Inteligencia artificial
- Alertas y recomendaciones automáticas.
- Predicción de riesgos y análisis de confort climático.

### Navegación integrada
- Acceso centralizado a módulos del sistema.

## Estructura del proyecto

```text
METGO_3D_Quillota_60GB/
├── sistema_auth_dashboard_principal_metgo.py  ← Punto de entrada principal (Streamlit)
├── datos_reales_openmeteo.py                  ← Módulo compartido de datos Open-Meteo
├── requirements.txt
├── README.md
├── LICENSE
│
├── dashboards/                                ← Todos los dashboards Streamlit
│   ├── dashboard_agricola_inteligente.py
│   ├── dashboard_agricola_metgo.py
│   ├── dashboard_agricultura_precision.py
│   ├── dashboard_alertas_automaticas.py
│   ├── dashboard_analisis_comparativo.py
│   ├── dashboard_global_metricas.py
│   ├── dashboard_ia_ml_avanzado.py
│   ├── dashboard_meteorologico_metgo.py
│   ├── dashboard_meteorologico_profesional.py
│   ├── dashboard_mobile_optimizado.py
│   ├── dashboard_monitoreo_tiempo_real.py
│   ├── dashboard_simple_metgo.py
│   ├── dashboard_simple_optimizado.py
│   ├── dashboard_unificado_diferenciado.py
│   ├── dashboard_unificado_metgo.py
│   ├── dashboard_visualizaciones_avanzadas.py
│   └── dashboard_web_publico.py
│
├── scripts/                                   ← Scripts de gestión y despliegue
│   ├── ejecutar_todos_dashboards.py
│   ├── ejecutar_dashboards_correctos.py
│   ├── iniciar_sistema_automatico.py
│   ├── detener_sistema.py
│   ├── reiniciar_sistema.py
│   ├── monitorear_sistema.py
│   ├── verificar_datos_reales.py
│   ├── deploy_streamlit_cloud.py
│   ├── mobile_config.py
│   ├── notificaciones_mobile.py
│   ├── cache_offline_mobile.py
│   ├── automatizar_sistema.bat          (Windows)
│   ├── iniciar_sistema_permanente.bat   (Windows)
│   └── ...
│
├── docs/                                      ← Documentación adicional
│   ├── INSTRUCCIONES_ACCESO_EXTERNO.md
│   ├── INSTRUCCIONES_AUTOMATIZACION.md
│   ├── INTEGRACION_DATOS_REALES.md
│   └── ...
│
├── 01_Sistema_Meteorologico/                  ← Módulo meteorológico
├── 02_Sistema_Agricola/                       ← Módulo agrícola
├── 03_Sistema_IoT_Drones/                     ← Módulo IoT y drones
├── 04_Dashboards_Unificados/                  ← Dashboards unificados avanzados
├── 05_APIs_Externas/                          ← Integraciones de APIs
├── 06_Modelos_ML_IA/                          ← Modelos de Machine Learning
├── 07_Sistema_Monitoreo/                      ← Sistema de monitoreo
├── 08_Gestion_Datos/                          ← Gestión de base de datos
├── 09_Testing_Validacion/                     ← Tests y validaciones
├── 10_Deployment_Produccion/                  ← Scripts de despliegue
├── 11_Documentacion/                          ← Documentación técnica
└── 12_Respaldos_Archivos/                     ← Respaldos y versiones
```

## Instalación local

### Prerrequisitos
- Python 3.8+
- pip

### Pasos

```bash
# 1) Clonar
git clone https://github.com/miguellucero123/METGO_3D_Quillota_60GB.git
cd METGO_3D_Quillota_60GB

# 2) Instalar dependencias
pip install -r requirements.txt

# 3) (Recomendado) Configurar variables de entorno
cp .env.example .env
# Edita .env y define:
# METGO_PASSWORD_ADMIN=
# METGO_PASSWORD_USER=
# METGO_PASSWORD_METGO=

# 4) Ejecutar dashboard principal
streamlit run sistema_auth_dashboard_principal_metgo.py
```

## Cómo abrir dashboards

### Dashboard principal (puerto 8501)
```bash
streamlit run sistema_auth_dashboard_principal_metgo.py
```

### Dashboard individual (ejemplo)
```bash
streamlit run dashboards/dashboard_meteorologico_profesional.py --server.port 8502
streamlit run dashboards/dashboard_agricola_inteligente.py --server.port 8503
```

### Todos los dashboards a la vez
```bash
python scripts/ejecutar_todos_dashboards.py
```

### Windows (desde la raíz del proyecto)
```bat
scripts\automatizar_sistema.bat
```

## Configuración (credenciales)

Las contraseñas se leen desde variables de entorno:

- `METGO_PASSWORD_ADMIN`
- `METGO_PASSWORD_USER`
- `METGO_PASSWORD_METGO`

Nota: si alguna no está definida, el sistema emite un warning en runtime y puede caer a valores de desarrollo (según implementación).

## Acceso

### Local
- URL: http://localhost:8501

### Streamlit Cloud (público)
- URL: https://metgo-3d-quillota-60gb.streamlit.app
- Credenciales: contactar administrador

## Estaciones meteorológicas soportadas

- Quillota (principal)
- Los Nogales
- Hijuelas
- Limache
- Olmué

## CI

El workflow en `.github/workflows/ci.yml` ejecuta validaciones básicas en cada push/PR (smoke test de imports + chequeo de sintaxis).

## Licencia

MIT. Ver `LICENSE`.

## Soporte

- Email: miguel.lucero@metgo3d.com
- Issues: https://github.com/miguellucero123/METGO_3D_Quillota_60GB/issues
