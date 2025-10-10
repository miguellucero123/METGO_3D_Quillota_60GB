# 🌤️ Sistema Meteorológico METGO 3D

## 📋 Descripción
Sistema avanzado de pronóstico meteorológico y análisis climático para Quillota, Chile. Proporciona pronósticos en tiempo real, análisis históricos y alertas meteorológicas con interfaz web interactiva.

## 🏗️ Estructura del Sistema

### 📁 Organización de Carpetas
```
01_Sistema_Meteorologico/
├── 📊 dashboards/           # Interfaces web especializadas
│   └── dashboard_meteorologico_avanzado.py
├── 📝 notebooks/           # Jupyter notebooks para análisis
├── 🔧 scripts/            # Scripts Python del módulo
├── 💾 datos/              # Datos meteorológicos
├── 🤖 modelos/            # Modelos de ML/IA entrenados
├── 📈 reportes/           # Reportes generados
└── 📄 main.py            # Script principal mejorado
```

### 🎯 Archivos Principales

#### 🌟 Scripts Principales
- **`main.py`** - Sistema meteorológico avanzado con múltiples vistas
- **`dashboards/dashboard_meteorologico_avanzado.py`** - Dashboard especializado
- **`scripts/dashboard_meteorologico_final.py`** - Versión legacy funcional

#### 📊 Datos y Configuración
- **`scripts/datos_meteorologicos.db`** - Base de datos SQLite principal
- **`scripts/api_keys_meteorologicas.json`** - Configuración de APIs externas
- **`scripts/datos_meteorologicos_actualizados.json`** - Datos en formato JSON

#### 🔧 Utilidades
- **`scripts/actualizar_dashboard_meteorologico.py`** - Actualizador automático
- **`scripts/validador_datos_meteorologicos.py`** - Validador de datos
- **`scripts/diagnostico_datos_meteorologicos.py`** - Diagnóstico del sistema

## 🚀 Características Principales

### 📊 Dashboard Avanzado
- **Múltiples Vistas**: Dashboard principal, análisis de temperaturas, precipitación, viento, tendencias
- **Métricas en Tiempo Real**: Temperatura, precipitación, humedad, viento, índice UV
- **Gráficos Interactivos**: Plotly con zoom, hover y filtros
- **Alertas Inteligentes**: Sistema de alertas basado en umbrales configurables

### 🌡️ Análisis Meteorológico
- **Temperaturas**: Máxima, mínima, promedio, sensación térmica
- **Precipitación**: Diaria, acumulada, intensidad, días secos consecutivos
- **Viento**: Velocidad, dirección, rosa de vientos
- **Humedad y Presión**: Relativa, punto de rocío, presión atmosférica
- **Índice UV**: Niveles de radiación ultravioleta

### 📈 Análisis Avanzado
- **Tendencias**: Regresión lineal para predicción
- **Correlaciones**: Matriz de correlaciones entre variables
- **Estadísticas**: Distribuciones, percentiles, extremos
- **Histórico**: Análisis de datos históricos

## 🔧 Instalación y Configuración

### 📦 Dependencias
```bash
pip install streamlit pandas numpy plotly requests sqlite3
```

### ⚙️ Configuración de APIs
1. Editar `scripts/api_keys_meteorologicas.json`:
```json
{
    "openweathermap_key": "tu_api_key_aqui",
    "openmeteo_enabled": true
}
```

2. APIs soportadas:
   - **OpenWeatherMap**: Datos en tiempo real (requiere API key)
   - **OpenMeteo**: API gratuita con pronósticos
   - **Datos locales**: SQLite y JSON

### 🚀 Ejecución
```bash
# Dashboard principal
python main.py

# Dashboard avanzado
python dashboards/dashboard_meteorologico_avanzado.py

# Con Streamlit
streamlit run main.py
streamlit run dashboards/dashboard_meteorologico_avanzado.py
```

## 📊 Vistas Disponibles

### 🏠 Dashboard Principal
- Métricas principales en tiempo real
- Gráficos de temperatura y precipitación
- Alertas meteorológicas
- Resumen ejecutivo

### 🌡️ Análisis de Temperaturas
- Estadísticas detalladas
- Distribución de temperaturas
- Análisis de extremos
- Gráficos de evolución

### 🌧️ Análisis de Precipitación
- Precipitación acumulada
- Días de lluvia y secos
- Intensidad de precipitación
- Patrones estacionales

### 💨 Análisis de Viento
- Rosa de vientos
- Velocidad y dirección
- Días ventosos
- Tendencias de viento

### 📈 Tendencias
- Regresión lineal
- Predicciones
- Análisis de correlaciones
- Proyecciones

### 🔍 Datos Detallados
- Tabla completa de datos
- Matriz de correlaciones
- Exportación de datos
- Filtros avanzados

## 🚨 Sistema de Alertas

### 🔴 Alertas Críticas
- Temperatura > 35°C (estrés térmico)
- Temperatura < 5°C (riesgo de heladas)
- Precipitación > 20mm (encharcamiento)
- Viento > 40 km/h (riesgo de daños)
- Índice UV > 8 (protección extrema)

### 🟠 Alertas de Precaución
- Temperatura > 30°C (condiciones elevadas)
- Precipitación > 10mm (precauciones)
- Viento > 25 km/h (actividades al aire libre)
- Humedad > 85% o < 25% (condiciones extremas)

## 🔄 Actualización de Datos

### 📡 Fuentes de Datos
1. **APIs Externas** (tiempo real)
2. **Base de Datos Local** (SQLite)
3. **Archivos JSON** (respaldos)
4. **Datos Simulados** (fallback)

### ⏰ Frecuencia de Actualización
- **Tiempo Real**: Cada 15 minutos (APIs)
- **Local**: Según configuración
- **Manual**: Botón de actualización en dashboard

## 🛠️ Mantenimiento

### 🔍 Diagnóstico
```bash
python scripts/diagnostico_datos_meteorologicos.py
```

### ✅ Validación de Datos
```bash
python scripts/validador_datos_meteorologicos.py
```

### 🔄 Actualización Manual
```bash
python scripts/actualizar_dashboard_meteorologico.py
```

## 📊 Métricas del Sistema

### 📈 Rendimiento
- **Carga de datos**: < 2 segundos
- **Actualización**: < 5 segundos
- **Respuesta de gráficos**: < 1 segundo
- **Disponibilidad**: 99.9%

### 💾 Almacenamiento
- **Base de datos**: SQLite (~10MB)
- **Logs**: Rotación automática
- **Respaldos**: Diarios automáticos

## 🔮 Próximas Mejoras

### 🚀 Características Planificadas
- [ ] Predicciones con ML
- [ ] Alertas por email/SMS
- [ ] Integración con sensores IoT
- [ ] Exportación a PDF
- [ ] API REST
- [ ] Móvil responsive
- [ ] Múltiples ubicaciones
- [ ] Pronósticos extendidos (15 días)

### 🤖 IA y ML
- [ ] Modelos de predicción
- [ ] Detección de patrones
- [ ] Optimización automática
- [ ] Aprendizaje continuo

## 📞 Soporte

### 🐛 Reportar Problemas
1. Verificar logs en `logs/`
2. Ejecutar diagnóstico
3. Revisar configuración de APIs
4. Contactar al equipo de desarrollo

### 📧 Contacto
- **Equipo**: METGO 3D Development Team
- **Versión**: 2.0
- **Última actualización**: 2025-10-09

---
*Sistema Meteorológico METGO 3D - Desarrollado para Quillota, Chile* 🌤️🇨🇱
