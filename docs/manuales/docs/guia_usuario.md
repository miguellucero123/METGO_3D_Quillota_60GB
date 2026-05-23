# 📚 Guía de Usuario - METGO 3D

## 🌾 Sistema Meteorológico Agrícola Quillota

### 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Configuración Inicial](#configuración-inicial)
4. [Uso del Sistema](#uso-del-sistema)
5. [Módulos Principales](#módulos-principales)
6. [Dashboard Interactivo](#dashboard-interactivo)
7. [Monitoreo y Alertas](#monitoreo-y-alertas)
8. [Respaldos](#respaldos)
9. [Solución de Problemas](#solución-de-problemas)
10. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## 🚀 Introducción

**METGO 3D** es un sistema meteorológico agrícola avanzado diseñado específicamente para la región de Quillota, Chile. El sistema proporciona:

- **Análisis meteorológico** en tiempo real
- **Predicciones agrícolas** basadas en IA
- **Alertas automáticas** para condiciones críticas
- **Visualizaciones interactivas** en 3D
- **Monitoreo continuo** del sistema
- **Respaldos automáticos** de datos

### 🎯 Características Principales

- ✅ **Score de calidad**: 90+/100
- ✅ **Manejo robusto de errores** en todas las APIs
- ✅ **Validación completa de datos** meteorológicos
- ✅ **Pipeline de ML optimizado** con validación cruzada
- ✅ **Sistema de logging** estructurado
- ✅ **Configuración centralizada**
- ✅ **Monitoreo avanzado** con alertas
- ✅ **Respaldos automáticos**

---

## 📦 Instalación

### Requisitos del Sistema

- **Python**: 3.8 o superior
- **Sistema Operativo**: Windows, Linux, macOS
- **Memoria RAM**: Mínimo 4GB, recomendado 8GB
- **Espacio en disco**: Mínimo 2GB libres
- **Conexión a Internet**: Para APIs meteorológicas

### Instalación Automática

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/metgo3d.git
cd metgo3d

# Ejecutar instalación automática
python instalar_sistema.py
```

### Instalación Manual

```bash
# 1. Crear entorno virtual
python -m venv venv_metgo3d
source venv_metgo3d/bin/activate  # Linux/macOS
# o
venv_metgo3d\Scripts\activate     # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Verificar instalación
python verificar_sistema.py
```

### Instalación con Docker

```bash
# Construir imagen
docker build -t metgo3d:latest .

# Ejecutar con Docker Compose
docker-compose up -d
```

---

## ⚙️ Configuración Inicial

### 1. Configuración Básica

Edita el archivo `config/config.yaml`:

```yaml
sistema:
  nombre: "METGO 3D"
  version: "2.0"
  entorno: "produccion"

quillota:
  coordenadas:
    latitud: -32.8833
    longitud: -71.2333
    altitud: 127
  zona_horaria: "America/Santiago"

meteorologia:
  variables:
    - temperatura
    - precipitacion
    - viento_velocidad
    - viento_direccion
    - humedad
    - presion
    - radiacion_solar
    - punto_rocio
```

### 2. Configuración de APIs

```yaml
apis:
  openmeteo:
    habilitado: true
    url: "https://api.open-meteo.com/v1/forecast"
    timeout: 30
    reintentos: 3
  
  notificaciones:
    email:
      habilitado: true
      smtp_server: "smtp.gmail.com"
      smtp_port: 587
      usuario: "tu-email@gmail.com"
      password: "tu-password"
```

### 3. Configuración de Base de Datos

```yaml
base_datos:
  tipo: "sqlite"
  archivo: "data/metgo3d.db"
  backup_automatico: true
  retencion_dias: 365
```

---

## 🎮 Uso del Sistema

### Inicio Rápido

```bash
# Ejecutar sistema completo
python orquestador_metgo_avanzado.py

# O ejecutar notebooks individuales
jupyter notebook 00_Sistema_Principal_MIP_Quillota.ipynb
```

### Comandos Principales

```bash
# Verificar estado del sistema
python verificar_sistema.py

# Ejecutar tests
python tests/runner_tests.py --categoria todos

# Generar reportes
python resumen_sistema.py

# Limpiar sistema
python limpiar_y_optimizar.py

# Monitoreo en tiempo real
python monitoreo_avanzado_metgo.py

# Dashboard interactivo
python dashboard_unificado_metgo.py --servidor
```

---

## 🔧 Módulos Principales

### 1. Sistema Principal (`00_Sistema_Principal_MIP_Quillota.ipynb`)

**Función**: Orquestador principal del sistema

**Características**:
- Coordinación de todos los módulos
- Generación de datos meteorológicos
- Evaluación de alertas
- Integración de resultados

**Uso**:
```python
# Ejecutar sistema completo
python orquestador_metgo_avanzado.py
```

### 2. Configuración e Imports (`01_Configuracion_e_imports.ipynb`)

**Función**: Configuración centralizada y imports

**Características**:
- Carga de configuración YAML
- Configuración de logging
- Imports de todas las librerías
- Configuración de pandas y matplotlib

### 3. Carga y Procesamiento de Datos (`02_Carga_y_Procesamiento_Datos.ipynb`)

**Función**: Procesamiento de datos meteorológicos

**Características**:
- Carga de datos desde APIs
- Validación de datos
- Corrección automática de errores
- Cálculo de índices agrícolas

### 4. Análisis Meteorológico (`03_Analisis_Meteorologico.ipynb`)

**Función**: Análisis avanzado de datos meteorológicos

**Características**:
- Análisis de temperaturas
- Análisis de precipitación
- Análisis de viento y humedad
- Generación de alertas

### 5. Visualizaciones (`04_Visualizaciones.ipynb`)

**Función**: Creación de visualizaciones

**Características**:
- Dashboards interactivos
- Gráficos 3D
- Visualizaciones con Plotly
- Exportación de gráficos

### 6. Modelos de Machine Learning (`05_Modelos_ML.ipynb`)

**Función**: Modelos de predicción

**Características**:
- Random Forest
- Linear Regression
- Validación cruzada
- Optimización de hiperparámetros

---

## 📊 Dashboard Interactivo

### Acceso al Dashboard

```bash
# Ejecutar dashboard
python dashboard_unificado_metgo.py --servidor

# Acceder desde navegador
http://localhost:8050
```

### Características del Dashboard

1. **Métricas en Tiempo Real**
   - Temperatura actual
   - Precipitación
   - Viento
   - Humedad

2. **Gráficos Interactivos**
   - Series temporales
   - Distribuciones
   - Correlaciones
   - Visualizaciones 3D

3. **Alertas**
   - Alertas activas
   - Historial de alertas
   - Configuración de umbrales

4. **Predicciones ML**
   - Predicciones de temperatura
   - Predicciones de precipitación
   - Confianza de las predicciones

### Navegación del Dashboard

- **Página Principal**: Resumen general del sistema
- **Meteorología**: Datos meteorológicos en tiempo real
- **Análisis**: Análisis estadísticos y tendencias
- **Predicciones**: Modelos de machine learning
- **Alertas**: Sistema de alertas y notificaciones
- **Configuración**: Ajustes del sistema

---

## 📈 Monitoreo y Alertas

### Sistema de Monitoreo

```bash
# Ejecutar monitoreo
python monitoreo_avanzado_metgo.py

# Dashboard de monitoreo
python dashboard_monitoreo_metgo.py --servidor
# Acceder a: http://localhost:8051
```

### Métricas Monitoreadas

1. **Sistema**
   - Uso de CPU
   - Uso de memoria
   - Uso de disco
   - Tráfico de red

2. **Aplicación**
   - Memoria Python
   - Objetos en memoria
   - Hilos activos

3. **Servicios**
   - APIs del sistema
   - Base de datos
   - Servicios externos

### Configuración de Alertas

```yaml
alertas:
  umbrales:
    cpu_uso:
      warning: 70
      critical: 90
    memoria_uso:
      warning: 80
      critical: 95
    temperatura:
      warning: 35
      critical: 40
    humedad:
      warning: 90
      critical: 95
```

### Notificaciones

- **Email**: Notificaciones por correo electrónico
- **Slack**: Integración con Slack (opcional)
- **Webhook**: Notificaciones HTTP (opcional)

---

## 💾 Respaldos

### Sistema de Respaldos Automáticos

```bash
# Ejecutar respaldo manual
python respaldos_automaticos_metgo.py

# Iniciar respaldos automáticos
python -c "from respaldos_automaticos_metgo import RespaldosAutomaticosMETGO; r = RespaldosAutomaticosMETGO(); r.iniciar_respaldos_automaticos()"
```

### Tipos de Respaldo

1. **Completos**
   - Frecuencia: Domingos a las 2:00 AM
   - Retención: 30 días
   - Incluye: Todos los datos del sistema

2. **Incrementales**
   - Frecuencia: Lunes a Sábado a las 3:00 AM
   - Retención: 7 días
   - Incluye: Solo cambios desde el último respaldo

### Restauración de Respaldos

```bash
# Listar respaldos disponibles
python -c "from respaldos_automaticos_metgo import RespaldosAutomaticosMETGO; r = RespaldosAutomaticosMETGO(); print(r.obtener_estadisticas())"

# Restaurar respaldo específico
python -c "from respaldos_automaticos_metgo import RespaldosAutomaticosMETGO; r = RespaldosAutomaticosMETGO(); r.restaurar_respaldo('respaldo_id')"
```

---

## 🔧 Solución de Problemas

### Problemas Comunes

#### 1. Error de Importación

**Síntoma**: `ModuleNotFoundError`

**Solución**:
```bash
# Verificar instalación de dependencias
pip install -r requirements.txt

# Verificar entorno virtual
source venv_metgo3d/bin/activate
```

#### 2. Error de Conexión a API

**Síntoma**: `ConnectionError` o `TimeoutError`

**Solución**:
```bash
# Verificar conexión a internet
ping api.open-meteo.com

# Verificar configuración de proxy
# Editar config/config.yaml
```

#### 3. Error de Base de Datos

**Síntoma**: `sqlite3.OperationalError`

**Solución**:
```bash
# Verificar permisos de directorio
chmod 755 data/

# Recrear base de datos
rm data/metgo3d.db
python 00_Sistema_Principal_MIP_Quillota.ipynb
```

#### 4. Error de Memoria

**Síntoma**: `MemoryError`

**Solución**:
```bash
# Reducir tamaño de datos
# Editar config/config.yaml
meteorologia:
  max_registros: 1000

# Aumentar memoria virtual
# Configurar swap en Linux
```

### Logs del Sistema

```bash
# Ver logs del sistema
tail -f logs/metgo3d.log

# Ver logs de monitoreo
tail -f logs/monitoreo/monitoreo_avanzado.log

# Ver logs de respaldos
tail -f logs/backups/respaldos_automaticos.log
```

### Diagnóstico Completo

```bash
# Ejecutar diagnóstico
python diagnostico_completo.py

# Generar reporte de diagnóstico
python analisis_rendimiento.py
```

---

## ❓ Preguntas Frecuentes

### P: ¿Cómo actualizo el sistema?

**R**: 
```bash
# Actualizar código
git pull origin main

# Actualizar dependencias
pip install -r requirements.txt --upgrade

# Verificar sistema
python verificar_sistema.py
```

### P: ¿Cómo cambio la ubicación geográfica?

**R**: Edita `config/config.yaml`:
```yaml
quillota:
  coordenadas:
    latitud: -33.4489  # Nueva latitud
    longitud: -70.6693  # Nueva longitud
    altitud: 520       # Nueva altitud
```

### P: ¿Cómo personalizo las alertas?

**R**: Edita `config/config.yaml`:
```yaml
alertas:
  umbrales:
    temperatura:
      warning: 30    # Tu umbral de advertencia
      critical: 35   # Tu umbral crítico
```

### P: ¿Cómo ejecuto el sistema en segundo plano?

**R**: 
```bash
# Con nohup (Linux/macOS)
nohup python orquestador_metgo_avanzado.py &

# Con screen
screen -S metgo3d
python orquestador_metgo_avanzado.py
# Ctrl+A, D para detach

# Con systemd (Linux)
sudo systemctl start metgo3d
sudo systemctl enable metgo3d
```

### P: ¿Cómo respaldo manualmente los datos?

**R**: 
```bash
# Respaldo completo
python respaldos_automaticos_metgo.py

# Respaldo específico
python -c "from respaldos_automaticos_metgo import RespaldosAutomaticosMETGO; r = RespaldosAutomaticosMETGO(); r.crear_respaldo(r.respaldos_configurados[0])"
```

### P: ¿Cómo monitoreo el rendimiento?

**R**: 
```bash
# Dashboard de monitoreo
python dashboard_monitoreo_metgo.py --servidor
# Acceder a: http://localhost:8051

# Análisis de rendimiento
python analisis_rendimiento.py
```

### P: ¿Cómo configuro notificaciones por email?

**R**: Edita `config/config.yaml`:
```yaml
notificaciones:
  email:
    habilitado: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    usuario: "tu-email@gmail.com"
    password: "tu-password-app"
    destinatarios:
      - "admin@metgo3d.cl"
      - "operador@metgo3d.cl"
```

---

## 📞 Soporte

### Recursos de Ayuda

- **Documentación**: `docs/`
- **Logs**: `logs/`
- **Configuración**: `config/`
- **Tests**: `tests/`

### Contacto

- **Email**: soporte@metgo3d.cl
- **GitHub**: https://github.com/tu-usuario/metgo3d
- **Documentación**: https://metgo3d.readthedocs.io

### Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 🎉 ¡Gracias por usar METGO 3D!

**Sistema Meteorológico Agrícola Quillota - Versión 2.0**

*Desarrollado con ❤️ para la agricultura de Quillota, Chile*
