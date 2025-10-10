# 🌾 Dashboard METGO - Sistema Integrado de Monitoreo Meteorológico y Agrícola

## 📋 Descripción
Dashboard principal integrado para monitoreo meteorológico y agrícola en Quillota, Chile. Sistema completo que combina análisis meteorológico, gestión agrícola, alertas ML y navegación a todos los módulos del sistema METGO.

## ✨ Características Principales

### 🔐 Sistema de Autenticación
- Login seguro con usuario y contraseña
- Acceso controlado al sistema

### 🌤️ Monitoreo Meteorológico
- Datos en tiempo real para Quillota y estaciones cercanas
- Gráficos interactivos con Plotly
- Pronósticos y análisis comparativo
- Alertas meteorológicas automáticas

### 🌱 Análisis Agrícola
- Datos de cultivos específicos de la región
- Recomendaciones agrícolas basadas en ML
- Análisis de riesgo agrícola
- Predicción de producción

### 🤖 Inteligencia Artificial
- Sistema de alertas ML
- Recomendaciones automáticas
- Predicción de riesgos
- Análisis de confort climático

### 🚀 Navegación Integrada
- Acceso a todos los dashboards del sistema METGO
- 12 módulos especializados
- Navegación centralizada

## 🛠️ Instalación Local

### Prerrequisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación
```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/dashboard-metgo.git
cd dashboard-metgo

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar el dashboard
streamlit run sistema_auth_dashboard_principal_metgo.py
```

## 🌐 Acceso

### Local
- **URL:** http://localhost:8501
- **Red Local:** http://192.168.1.7:8501

### Streamlit Cloud (Público)
- **URL:** https://tu-usuario-dashboard-metgo.streamlit.app
- **Accesible desde cualquier lugar del mundo**

## 📊 Módulos del Sistema

| Módulo | Puerto | Descripción |
|--------|--------|-------------|
| 🏠 Principal | 8501 | Dashboard principal integrado |
| 🌤️ Meteorológico | 8503 | Análisis meteorológico avanzado |
| 🌾 Agrícola | 8504 | Gestión agrícola completa |
| 🏠 Unificado | 8502 | Vista integral del sistema |
| 📊 Simple | 8505 | Interfaz simplificada |

## 🎯 Estaciones Meteorológicas Soportadas

- **Quillota** (Principal)
- **Los Nogales**
- **Hijuelas**
- **Limache**
- **Olmue**

## 📈 Funcionalidades Avanzadas

### Panel de Control
- Selector de estación meteorológica
- Botón de actualización de datos
- Selector de período de análisis
- Generación de reportes

### Análisis Temporal
- **Histórico:** Análisis de datos pasados
- **Pronóstico:** Proyecciones futuras
- **Comparativo:** Comparación entre períodos

### Sistema de Alertas
- Alertas de heladas
- Alertas de calor extremo
- Alertas de precipitación intensa
- Alertas de viento fuerte
- Alertas de humedad baja

## 🔧 Configuración

### Variables de Entorno
```bash
# Configuración del servidor
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
```

### Archivo de Configuración
El archivo `.streamlit/config.toml` contiene la configuración personalizada del dashboard.

## 📁 Estructura del Proyecto

```
dashboard-metgo/
├── sistema_auth_dashboard_principal_metgo.py  # Dashboard principal
├── dashboard_meteorologico_metgo.py           # Dashboard meteorológico
├── dashboard_agricola_metgo.py                # Dashboard agrícola
├── dashboard_unificado_metgo.py               # Dashboard unificado
├── dashboard_simple_metgo.py                  # Dashboard simple
├── requirements.txt                           # Dependencias
├── .streamlit/config.toml                     # Configuración
└── README.md                                  # Este archivo
```

## 🚀 Despliegue

### Streamlit Cloud (Recomendado)
1. Subir código a GitHub
2. Conectar repositorio en https://share.streamlit.io
3. Seleccionar archivo principal: `sistema_auth_dashboard_principal_metgo.py`

### Local con Acceso Externo
```bash
# Usando ngrok
python dashboard_web_publico.py

# Configurando router
configurar_router.bat
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Autores

- **Sistema METGO** - *Desarrollo inicial* - [GitHub](https://github.com/metgo)
- **Equipo Quillota** - *Implementación regional*

## 🙏 Agradecimientos

- OpenMeteo
- Desarrolladores de Streamlit y Plotly

## 📞 Soporte

Para soporte técnico o consultas:
- **Email:** soporte@metgo.cl
- **GitHub Issues:** [Crear issue](https://github.com/tu-usuario/dashboard-metgo/issues)

---

**Dashboard METGO - Sistema Integrado de Monitoreo Meteorológico y Agrícola para Quillota** 🌾
