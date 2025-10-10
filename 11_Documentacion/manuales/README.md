# 🌾 METGO 3D - Sistema Meteorológico Agrícola Quillota

## 📋 Descripción del Proyecto

**METGO 3D** es un sistema meteorológico agrícola avanzado diseñado específicamente para la región de Quillota, Chile. El sistema proporciona análisis meteorológico detallado, pronósticos agrícolas, alertas inteligentes y recomendaciones para optimizar la producción agrícola.

## 🚀 Características Principales

### ✅ Sistema Completamente Operativo
- **Configuración centralizada** con archivos YAML
- **Manejo robusto de errores** en todas las operaciones
- **Logging estructurado** para monitoreo y debugging
- **Validación automática de datos** con corrección de errores
- **Análisis meteorológico avanzado** con estadísticas robustas
- **Visualizaciones interactivas** con Plotly y Matplotlib
- **Modelos de Machine Learning** para pronósticos
- **Dashboard interactivo** con Streamlit
- **Reportes automáticos** en múltiples formatos
- **APIs externas** con fallback a datos sintéticos
- **Testing completo** con validación de calidad
- **Deployment listo** para producción

### 🌡️ Análisis Meteorológico
- **Temperaturas**: Análisis de extremos térmicos, variabilidad estacional, tendencias mensuales
- **Precipitación**: Estadísticas hidrológicas, eventos extremos, balance hídrico
- **Viento y Humedad**: Patrones direccionales, índices de confort, riesgo de hongos
- **Índices Agrícolas**: Grados-día, confort térmico, necesidad de riego, riesgo de heladas

### 📊 Visualizaciones Avanzadas
- **Dashboards multi-panel** para cada variable meteorológica
- **Gráficos interactivos** con Plotly
- **Visualizaciones estacionales** y de tendencias
- **Exportación** en múltiples formatos (PNG, PDF, HTML)

### 🤖 Machine Learning
- **Modelos de pronóstico** para temperaturas y precipitación
- **Validación cruzada** y optimización de hiperparámetros
- **Métricas de evaluación** robustas
- **Persistencia de modelos** entrenados

## 📁 Estructura del Proyecto

```
PROYECTO_METGO_3D/
├── 📓 notebooks/
│   ├── 01_Configuracion_e_imports.ipynb          # Configuración centralizada
│   ├── 02_Carga_y_Procesamiento_Datos.ipynb       # Carga y validación de datos
│   ├── 03_Analisis_Meteorologico.ipynb             # Análisis meteorológico avanzado
│   ├── 04_Visualizaciones.ipynb                    # Visualizaciones interactivas
│   ├── 05_Modelos_ML.ipynb                         # Modelos de Machine Learning
│   ├── 06_Dashboard_Interactivo.ipynb             # Dashboard con Streamlit
│   ├── 07_Reportes_Automaticos.ipynb               # Generación de reportes
│   ├── 08_APIs_Externas.ipynb                     # Integración con APIs
│   ├── 09_Testing_Validacion.ipynb                 # Testing y validación
│   └── 10_Deployment_Produccion.ipynb              # Deployment y producción
├── 🐍 scripts/
│   ├── ejecutar_sistema_completo.py                # Script maestro Python
│   ├── ejecutar_sistema.sh                        # Script maestro Bash (Linux/macOS)
│   └── ejecutar_sistema.ps1                        # Script maestro PowerShell (Windows)
├── 📁 config/
│   └── config.yaml                                # Configuración centralizada
├── 📁 data/                                        # Datos meteorológicos
├── 📁 logs/                                        # Archivos de log
├── 📁 reportes_revision/                           # Reportes generados
├── 📁 test_results/                                # Resultados de testing
├── 📁 tests/                                        # Tests unitarios
├── 📁 app/                                          # Aplicación Streamlit
├── 📁 static/                                       # Archivos estáticos
├── 📁 templates/                                    # Plantillas HTML
├── 📁 backups/                                      # Backups del sistema
├── 📄 requirements.txt                              # Dependencias Python
├── 📄 README.md                                    # Este archivo
└── 📄 LICENSE                                       # Licencia del proyecto
```

## 🛠️ Instalación y Configuración

### Prerrequisitos
- **Python 3.8+**
- **Jupyter Notebook**
- **pip** (gestor de paquetes Python)

### Instalación Rápida

1. **Clonar o descargar el proyecto**:
   ```bash
   git clone <repository-url>
   cd PROYECTO_METGO_3D
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verificar instalación**:
   ```bash
   python -c "import pandas, numpy, matplotlib, seaborn, sklearn, requests, plotly, streamlit; print('✅ Todas las dependencias instaladas')"
   ```

## 🚀 Ejecución del Sistema

### Método 1: Script Maestro (Recomendado)

#### En Windows (PowerShell):
```powershell
# Ejecutar sistema completo
.\ejecutar_sistema.ps1

# Ejecutar modo rápido
.\ejecutar_sistema.ps1 rapido

# Ejecutar solo análisis
.\ejecutar_sistema.ps1 analisis

# Ver ayuda
.\ejecutar_sistema.ps1 -Help
```

#### En Linux/macOS (Bash):
```bash
# Ejecutar sistema completo
./ejecutar_sistema.sh

# Ejecutar modo rápido
./ejecutar_sistema.sh rapido

# Ejecutar solo análisis
./ejecutar_sistema.sh analisis

# Ver ayuda
./ejecutar_sistema.sh --help
```

#### En cualquier sistema (Python):
```bash
# Ejecutar sistema completo
python ejecutar_sistema_completo.py

# Ejecutar modo rápido
python ejecutar_sistema_completo.py rapido

# Ejecutar solo análisis
python ejecutar_sistema_completo.py analisis
```

### Método 2: Ejecución Manual de Notebooks

1. **Iniciar Jupyter Notebook**:
   ```bash
   jupyter notebook
   ```

2. **Ejecutar notebooks en orden**:
   - `01_Configuracion_e_imports.ipynb`
   - `02_Carga_y_Procesamiento_Datos.ipynb`
   - `03_Analisis_Meteorologico.ipynb`
   - `04_Visualizaciones.ipynb`
   - `05_Modelos_ML.ipynb`
   - `06_Dashboard_Interactivo.ipynb`
   - `07_Reportes_Automaticos.ipynb`
   - `08_APIs_Externas.ipynb`
   - `09_Testing_Validacion.ipynb`
   - `10_Deployment_Produccion.ipynb`

## 📊 Modos de Ejecución

### 🎯 Modo Completo
Ejecuta todos los notebooks del sistema:
- Configuración e imports
- Carga y procesamiento de datos
- Análisis meteorológico
- Visualizaciones
- Modelos de ML
- Dashboard interactivo
- Reportes automáticos
- APIs externas
- Testing y validación
- Deployment

### ⚡ Modo Rápido
Ejecuta solo los notebooks esenciales:
- Configuración e imports
- Carga y procesamiento de datos
- Análisis meteorológico
- Visualizaciones
- Modelos de ML

### 🔍 Modo Análisis
Ejecuta solo notebooks de análisis:
- Configuración e imports
- Carga y procesamiento de datos
- Análisis meteorológico
- Visualizaciones

### 🧪 Modo Testing
Ejecuta solo notebooks de testing:
- Testing y validación

### 🚀 Modo Deployment
Ejecuta solo notebooks de deployment:
- Deployment y producción

## 📈 Características Técnicas

### 🔧 Configuración Centralizada
- **Archivo YAML** con toda la configuración del sistema
- **Coordenadas de Quillota** predefinidas
- **Umbrales críticos** para alertas meteorológicas
- **Configuración de logging** estructurado

### 📊 Manejo de Datos
- **Carga desde APIs** (OpenMeteo) con fallback a datos sintéticos
- **Validación robusta** de datos meteorológicos
- **Corrección automática** de errores comunes
- **Procesamiento avanzado** con índices agrícolas

### 🌡️ Análisis Meteorológico
- **Estadísticas robustas** para todas las variables
- **Detección de extremos** y eventos críticos
- **Análisis estacional** y de tendencias
- **Cálculo de índices agrícolas** especializados

### 📊 Visualizaciones
- **Dashboards multi-panel** para cada variable
- **Gráficos interactivos** con Plotly
- **Exportación** en múltiples formatos
- **Tema personalizado** para Quillota

### 🤖 Machine Learning
- **Múltiples algoritmos** (Random Forest, Linear Regression, etc.)
- **Validación cruzada** y optimización de hiperparámetros
- **Métricas de evaluación** robustas
- **Persistencia de modelos** entrenados

### 🚨 Sistema de Alertas
- **Alertas inteligentes** basadas en umbrales críticos
- **Recomendaciones agrícolas** específicas
- **Clasificación por severidad** (crítica, advertencia, info)
- **Mensajes descriptivos** con emojis

## 📋 Dependencias Principales

```txt
pandas>=1.3.0
numpy>=1.21.0
matplotlib>=3.4.0
seaborn>=0.11.0
scikit-learn>=1.0.0
requests>=2.25.0
plotly>=5.0.0
streamlit>=1.0.0
pyyaml>=5.4.0
jupyter>=1.0.0
nbconvert>=6.0.0
```

## 🔍 Troubleshooting

### Problemas Comunes

1. **Error: 'jupyter' command not found**
   ```bash
   pip install jupyter
   ```

2. **Error: ModuleNotFoundError**
   ```bash
   pip install -r requirements.txt
   ```

3. **Error: Permission denied (Linux/macOS)**
   ```bash
   chmod +x ejecutar_sistema.sh
   ```

4. **Error: ExecutionPolicy (Windows)**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

### Logs y Debugging

- **Logs del sistema**: `logs/metgo_operativo.log`
- **Logs de ejecución**: `logs/sistema_completo.log`
- **Resultados de testing**: `test_results/`

## 📞 Soporte y Contacto

Para soporte técnico o consultas sobre el sistema METGO 3D:

- **Proyecto**: Sistema Meteorológico Agrícola Quillota
- **Versión**: 2.0 Operativa
- **Fecha**: 2025-01-02
- **Ubicación**: Quillota, Región de Valparaíso, Chile

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.

## 🎉 ¡Sistema Listo!

El sistema METGO 3D está completamente operativo y listo para uso agrícola en Quillota. Todos los notebooks han sido mejorados con:

- ✅ Manejo robusto de errores
- ✅ Configuración centralizada
- ✅ Logging estructurado
- ✅ Validación de datos
- ✅ Análisis avanzado
- ✅ Visualizaciones interactivas
- ✅ Modelos de ML
- ✅ Testing completo
- ✅ Deployment listo

**¡Ejecuta el sistema y comienza a optimizar tu producción agrícola!** 🌾