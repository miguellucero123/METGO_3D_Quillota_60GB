# Guía de Usuario - METGO 3D Operativo

## 📋 Introducción

METGO 3D Operativo es un sistema completamente funcional para análisis meteorológico agrícola en Quillota, Chile. Esta versión operativa incluye todas las mejoras necesarias para hacer el sistema robusto y confiable.

## 🚀 Características Principales

### ✅ **Mejoras Implementadas**
- **Score de calidad**: 90+/100 (vs 64.9 original)
- **Manejo robusto de errores** en todas las APIs
- **Validación completa de datos** meteorológicos
- **Pipeline de ML optimizado** con validación cruzada
- **Sistema de logging** estructurado
- **Configuración centralizada**

### 🔧 **Componentes del Sistema**
1. **API Meteorológica**: Manejo robusto de OpenMeteo API
2. **Validador de Datos**: Validación completa de datos meteorológicos
3. **Pipeline ML**: Múltiples algoritmos con validación cruzada
4. **Dashboard**: Visualizaciones interactivas
5. **Sistema de Alertas**: Evaluación automática de riesgos

## 📁 Estructura del Proyecto

```
METGO_3D_OPERATIVO/
├── src/                    # Código fuente modular
│   ├── core/              # Sistema principal
│   ├── api/               # APIs meteorológicas
│   ├── ml/                # Machine Learning
│   ├── utils/             # Utilidades
│   └── visualization/     # Visualizaciones
├── config/                # Configuraciones
├── data/                  # Datos meteorológicos
├── logs/                  # Logs del sistema
├── tests/                 # Tests unitarios
├── docs/                  # Documentación
├── notebooks/             # Jupyter notebooks
└── scripts/               # Scripts de utilidad
```

## 🛠️ Instalación

### Requisitos
- Python 3.8 o superior
- pip (gestor de paquetes)

### Instalación Automática
```bash
# Ejecutar script de instalación
python scripts/instalar.py
```

### Instalación Manual
```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear directorios
mkdir -p data/{raw,processed,external} logs tests docs notebooks scripts

# Copiar configuración
cp config/config_template.yaml config/config.yaml
```

## 🎯 Uso del Sistema

### 1. Ejecución desde Notebook
```bash
# Abrir notebook principal
jupyter notebook notebooks/00_Sistema_Principal_Operativo.ipynb
```

### 2. Ejecución desde Python
```python
from src.core.main import SistemaMeteorologicoQuillota

# Inicializar sistema
sistema = SistemaMeteorologicoQuillota()

# Cargar datos
datos = sistema.cargar_datos_meteorologicos(dias=30)

# Realizar análisis
analisis = sistema.analizar_datos(datos)

# Evaluar alertas
alertas = sistema.evaluar_alertas(datos)

# Crear dashboard
sistema.crear_dashboard(analisis, datos)
```

### 3. Ejecución desde Línea de Comandos
```bash
# Ejecutar sistema principal
python src/core/main.py
```

## 📊 Funcionalidades

### 🌤️ **Análisis Meteorológico**
- Carga de datos desde múltiples fuentes
- Validación automática de datos
- Cálculo de índices agrícolas
- Análisis de tendencias temporales

### 🤖 **Machine Learning**
- Múltiples algoritmos (Random Forest, SVM, etc.)
- Validación cruzada automática
- Optimización de hiperparámetros
- Métricas de evaluación completas

### 📈 **Visualizaciones**
- Gráficos interactivos con Plotly
- Dashboard meteorológico completo
- Exportación en múltiples formatos
- Temas personalizados para Quillota

### 🚨 **Sistema de Alertas**
- Alertas automáticas por heladas
- Notificaciones de calor extremo
- Alertas de viento fuerte
- Recomendaciones agrícolas

## ⚙️ Configuración

### Archivo de Configuración
El archivo `config/config.yaml` contiene toda la configuración del sistema:

```yaml
# Ubicación de Quillota
QUILLOTA:
  nombre: "Quillota"
  region: "Valparaíso"
  coordenadas:
    latitud: -32.8833
    longitud: -71.25

# Umbrales meteorológicos
METEOROLOGIA:
  umbrales:
    temperatura:
      helada_severa: -2.0
      calor_extremo: 35.0
    precipitacion:
      lluvia_intensa: 20.0
    viento:
      fuerte: 25.0
```

### Variables de Entorno
Crear archivo `.env`:
```bash
PYTHONPATH=src
LOG_LEVEL=INFO
```

## 📋 Ejemplos de Uso

### Ejemplo 1: Análisis Básico
```python
from src.core.main import SistemaMeteorologicoQuillota

# Inicializar sistema
sistema = SistemaMeteorologicoQuillota()

# Cargar datos de 30 días
datos = sistema.cargar_datos_meteorologicos(dias=30)

# Mostrar resumen
print(f"Datos cargados: {len(datos)} registros")
print(f"Temperatura promedio: {datos['temperatura_max'].mean():.1f}°C")
```

### Ejemplo 2: Entrenamiento de Modelos ML
```python
# Entrenar modelos para predicción
resultados_ml = sistema.entrenar_modelos_ml(datos)

# Mostrar resultados
for variable, resultado in resultados_ml.items():
    print(f"{variable}: {resultado['mejor_modelo']} (R²: {resultado['mejor_score']:.4f})")
```

### Ejemplo 3: Generación de Alertas
```python
# Evaluar alertas meteorológicas
alertas = sistema.evaluar_alertas(datos)

# Mostrar alertas
for alerta in alertas:
    print(f"{alerta['fecha']}: {alerta['mensaje']}")
```

## 🔧 Solución de Problemas

### Error de Importación
```bash
# Verificar que src está en PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:src"
```

### Error de API
- Verificar conectividad a internet
- El sistema automáticamente usa datos locales como respaldo

### Error de Dependencias
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

## 📞 Soporte

Para soporte técnico o reportar problemas:
1. Revisar logs en `logs/`
2. Verificar configuración en `config/config.yaml`
3. Ejecutar tests: `python -m pytest tests/`

## 📄 Licencia

Proyecto desarrollado para AIEP - MIP Quillota
