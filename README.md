# Dashboard METGO - Sistema Integrado de Monitoreo Meteorológico y Agrícola

Dashboard integrado para monitoreo meteorológico y agrícola en Quillota, Chile. El proyecto combina visualización en Streamlit, análisis de datos, modelos de ML y módulos especializados.

## Estado del repositorio (actualización 2026-05-05)

Este repositorio incorporó mejoras de seguridad, rendimiento y mantenibilidad:

- **Seguridad**: credenciales movidas a variables de entorno (`METGO_PASSWORD_{ADMIN,USER,METGO}`) y soporte de `.env` mediante `python-dotenv`.
- **Rendimiento**: caching con TTL para llamadas a APIs meteorológicas (en Streamlit) para reducir latencia y cuotas.
- **Higiene del repo**: exclusión de respaldos pesados (`respaldo_*/`) desde git y `.env` ignorado.
- **Dependencias**: `requirements.txt` actualizado para reflejar imports reales (ML/visualización + dotenv).
- **CI/DX**: workflow de GitHub Actions con smoke test de imports y chequeo de sintaxis; `Makefile` con comandos comunes.

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

# 4) Ejecutar (ejemplo)
streamlit run sistema_auth_dashboard_principal_metgo.py
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

## Estructura del proyecto (referencia)

```text
METGO_3D_Quillota_60GB/
├── sistema_auth_dashboard_principal_metgo.py
├── 01_Sistema_Meteorologico/
├── 02_Sistema_Agricola/
├── requirements.txt
├── .github/workflows/
└── README.md
```

## CI

El workflow en `.github/workflows/ci.yml` ejecuta validaciones básicas en cada push/PR (smoke test de imports + chequeo de sintaxis).

## Licencia

MIT. Ver `LICENSE`.

## Soporte

- Email: miguel.lucero@metgo3d.com
- Issues: https://github.com/miguellucero123/METGO_3D_Quillota_60GB/issues
