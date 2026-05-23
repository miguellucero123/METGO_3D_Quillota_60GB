# ⚙️ Guía de Configuración - METGO 3D

## 🌾 Sistema Meteorológico Agrícola Quillota

### 📋 Tabla de Contenidos

1. [Configuración Básica](#configuración-básica)
2. [Configuración Meteorológica](#configuración-meteorológica)
3. [Configuración de APIs](#configuración-de-apis)
4. [Configuración de Base de Datos](#configuración-de-base-de-datos)
5. [Configuración de Alertas](#configuración-de-alertas)
6. [Configuración de Monitoreo](#configuración-de-monitoreo)
7. [Configuración de Respaldos](#configuración-de-respaldos)
8. [Configuración de Logging](#configuración-de-logging)
9. [Variables de Entorno](#variables-de-entorno)
10. [Configuración Avanzada](#configuración-avanzada)

---

## 🔧 Configuración Básica

### Archivo Principal: `config/config.yaml`

```yaml
# Configuración principal del sistema
sistema:
  nombre: "METGO 3D"
  version: "2.0"
  entorno: "produccion"  # desarrollo, testing, produccion
  debug: false
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Configuración de Quillota
quillota:
  coordenadas:
    latitud: -32.8833
    longitud: -71.2333
    altitud: 127
  zona_horaria: "America/Santiago"
  region: "Valparaíso"
  pais: "Chile"
```

### Configuración de Directorios

```yaml
directorios:
  datos: "data"
  logs: "logs"
  config: "config"
  respaldos: "backups"
  graficos: "graficos"
  reportes: "reportes"
  modelos: "modelos_ml_quillota"
  temp: "temp"
```

---

## 🌤️ Configuración Meteorológica

### Variables Meteorológicas

```yaml
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
  
  unidades:
    temperatura: "°C"
    precipitacion: "mm"
    viento_velocidad: "m/s"
    viento_direccion: "°"
    humedad: "%"
    presion: "hPa"
    radiacion_solar: "W/m²"
    punto_rocio: "°C"
  
  rangos_validos:
    temperatura:
      min: -10
      max: 50
    humedad:
      min: 0
      max: 100
    precipitacion:
      min: 0
      max: 200
    viento_velocidad:
      min: 0
      max: 50
```

### Configuración de APIs Meteorológicas

```yaml
apis_meteorologicas:
  openmeteo:
    habilitado: true
    url: "https://api.open-meteo.com/v1/forecast"
    timeout: 30
    reintentos: 3
    intervalo_actualizacion: 3600  # segundos
  
  backup:
    habilitado: true
    tipo: "sintetico"
    calidad: 0.85
```

---

## 🔌 Configuración de APIs

### API Principal

```yaml
api_principal:
  puerto: 5000
  host: "0.0.0.0"
  debug: false
  cors:
    habilitado: true
    origenes: ["*"]
  rate_limiting:
    habilitado: true
    requests_por_hora: 1000
```

### APIs Especializadas

```yaml
apis_especializadas:
  meteorologia:
    puerto: 5001
    host: "0.0.0.0"
  
  agricola:
    puerto: 5002
    host: "0.0.0.0"
  
  alertas:
    puerto: 5003
    host: "0.0.0.0"
  
  iot:
    puerto: 5004
    host: "0.0.0.0"
  
  ml:
    puerto: 5005
    host: "0.0.0.0"
  
  visualizacion:
    puerto: 5006
    host: "0.0.0.0"
  
  reportes:
    puerto: 5007
    host: "0.0.0.0"
  
  configuracion:
    puerto: 5008
    host: "0.0.0.0"
  
  monitoreo:
    puerto: 5009
    host: "0.0.0.0"
```

### Dashboard

```yaml
dashboard:
  puerto: 8050
  host: "0.0.0.0"
  debug: false
  actualizacion_automatica: true
  intervalo_actualizacion: 30  # segundos
```

---

## 🗄️ Configuración de Base de Datos

### SQLite (Por Defecto)

```yaml
base_datos:
  tipo: "sqlite"
  archivo: "data/metgo3d.db"
  backup_automatico: true
  retencion_dias: 365
  compresion: true
  cifrado: false
```

### PostgreSQL (Opcional)

```yaml
base_datos:
  tipo: "postgresql"
  host: "localhost"
  puerto: 5432
  nombre: "metgo3d"
  usuario: "metgo3d"
  password: "metgo3d_2024_secure"
  ssl: false
  pool_size: 10
  max_overflow: 20
```

### Redis (Cache)

```yaml
redis:
  habilitado: true
  host: "localhost"
  puerto: 6379
  password: ""
  db: 0
  timeout: 5
  max_connections: 10
```

---

## 🚨 Configuración de Alertas

### Umbrales de Alertas

```yaml
alertas:
  umbrales:
    temperatura:
      warning: 35.0
      critical: 40.0
    humedad:
      warning: 90.0
      critical: 95.0
    precipitacion:
      warning: 50.0
      critical: 100.0
    viento_velocidad:
      warning: 20.0
      critical: 30.0
    presion:
      warning: 980.0
      critical: 950.0
  
  evaluacion:
    intervalo: 300  # segundos
    retencion_dias: 30
    auto_resolucion: true
    tiempo_resolucion: 3600  # segundos
```

### Notificaciones

```yaml
notificaciones:
  email:
    habilitado: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    usuario: "metgo3d@example.com"
    password: "password"
    destinatarios:
      - "admin@metgo3d.cl"
      - "operador@metgo3d.cl"
    asunto: "METGO 3D - Alerta {nivel}"
  
  slack:
    habilitado: false
    webhook_url: "https://hooks.slack.com/services/..."
    canal: "#metgo3d-alerts"
  
  webhook:
    habilitado: false
    url: "https://api.example.com/webhook"
    headers:
      Authorization: "Bearer token"
```

---

## 📊 Configuración de Monitoreo

### Métricas del Sistema

```yaml
monitoreo:
  metricas:
    intervalo: 30  # segundos
    retencion_dias: 7
    umbrales:
      cpu_uso:
        warning: 70
        critical: 90
      memoria_uso:
        warning: 80
        critical: 95
      disco_uso:
        warning: 85
        critical: 95
  
  servicios:
    intervalo: 60  # segundos
    timeout: 30
    max_reintentos: 3
  
  alertas:
    intervalo: 10  # segundos
    habilitado: true
```

### Dashboard de Monitoreo

```yaml
dashboard_monitoreo:
  puerto: 8051
  host: "0.0.0.0"
  actualizacion_automatica: true
  intervalo_actualizacion: 30  # segundos
  graficos:
    metricas_sistema: true
    estado_servicios: true
    distribucion_metricas: true
    tendencias: true
```

---

## 💾 Configuración de Respaldos

### Respaldos Automáticos

```yaml
respaldos:
  habilitado: true
  tipos:
    completo:
      frecuencia: "0 2 * * 0"  # Domingos a las 2 AM
      retencion_dias: 30
      compresion: true
      cifrado: false
    
    incremental:
      frecuencia: "0 3 * * 1-6"  # Lunes a Sábado a las 3 AM
      retencion_dias: 7
      compresion: true
      cifrado: false
  
  directorios:
    - "data"
    - "config"
    - "logs"
    - "reportes"
    - "graficos"
    - "modelos_ml_quillota"
  
  exclusiones:
    - "*.tmp"
    - "*.log"
    - "*.cache"
    - "temp/*"
    - "backups/*"
  
  verificacion:
    integridad: true
    checksum: "sha256"
  
  notificaciones:
    email: true
    webhook: false
```

### Destinos de Respaldo

```yaml
destinos_respaldo:
  local:
    habilitado: true
    directorio: "backups"
  
  nube:
    habilitado: false
    tipo: "aws_s3"  # aws_s3, google_cloud, azure_blob
    bucket: "metgo3d-backups"
    region: "us-east-1"
    credenciales:
      access_key: ""
      secret_key: ""
```

---

## 📝 Configuración de Logging

### Logging Principal

```yaml
logging:
  nivel: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  formato: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  archivo: "logs/metgo3d.log"
  max_bytes: 10485760  # 10MB
  backup_count: 5
  encoding: "utf-8"
  
  handlers:
    archivo: true
    consola: true
    syslog: false
  
  rotacion:
    habilitada: true
    cuando: "midnight"
    intervalo: 1
    backup_count: 30
```

### Logging Especializado

```yaml
logging_especializado:
  monitoreo:
    archivo: "logs/monitoreo/monitoreo_avanzado.log"
    nivel: "INFO"
  
  respaldos:
    archivo: "logs/backups/respaldos_automaticos.log"
    nivel: "INFO"
  
  errores:
    archivo: "logs/errores/error.log"
    nivel: "ERROR"
  
  auditoria:
    archivo: "logs/auditoria/audit.log"
    nivel: "INFO"
```

---

## 🌍 Variables de Entorno

### Archivo: `.env`

```bash
# Configuración del sistema
METGO3D_ENV=produccion
METGO3D_DEBUG=false
METGO3D_LOG_LEVEL=INFO

# Base de datos
DATABASE_URL=sqlite:///data/metgo3d.db
# Para PostgreSQL:
# DATABASE_URL=postgresql://metgo3d:password@localhost:5432/metgo3d

# Redis
REDIS_URL=redis://localhost:6379/0

# APIs
OPENMETEO_API_URL=https://api.open-meteo.com/v1/forecast
OPENMETEO_TIMEOUT=30

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=metgo3d@example.com
SMTP_PASSWORD=password

# Seguridad
JWT_SECRET_KEY=tu-clave-secreta-muy-segura
JWT_EXPIRATION_HOURS=24

# Monitoreo
MONITORING_ENABLED=true
MONITORING_INTERVAL=30

# Respaldos
BACKUP_ENABLED=true
BACKUP_RETENTION_DAYS=30
```

### Cargar Variables de Entorno

```python
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Usar variables
DEBUG = os.getenv('METGO3D_DEBUG', 'false').lower() == 'true'
LOG_LEVEL = os.getenv('METGO3D_LOG_LEVEL', 'INFO')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/metgo3d.db')
```

---

## 🔧 Configuración Avanzada

### Machine Learning

```yaml
ml:
  modelos:
    lstm:
      habilitado: true
      epochs: 100
      batch_size: 32
      learning_rate: 0.001
      validation_split: 0.2
    
    random_forest:
      habilitado: true
      n_estimators: 100
      max_depth: 10
      random_state: 42
    
    linear_regression:
      habilitado: true
      fit_intercept: true
  
  entrenamiento:
    intervalo: 86400  # 24 horas
    datos_minimos: 1000
    validacion_cruzada: true
    k_folds: 5
  
  predicciones:
    horizonte_maximo: 168  # 7 días
    confianza_minima: 0.7
    actualizacion_automatica: true
```

### IoT y Sensores

```yaml
iot:
  sensores:
    habilitado: true
    simulacion: true
    total_sensores: 10
    tipos:
      - temperatura
      - humedad
      - presion
      - viento
      - radiacion
  
  gateway:
    habilitado: true
    protocolo: "mqtt"
    broker: "localhost"
    puerto: 1883
    topic: "metgo3d/sensores"
  
  comunicacion:
    intervalo: 60  # segundos
    timeout: 30
    max_reintentos: 3
    calidad_servicio: 1
```

### Visualizaciones

```yaml
visualizaciones:
  graficos:
    habilitados: true
    tipos:
      - line
      - bar
      - scatter
      - heatmap
      - 3d
    
    configuracion:
      tema: "plotly_white"
      colores: "quillota"
      animaciones: true
      interactividad: true
  
  dashboards:
    habilitados: true
    actualizacion_automatica: true
    intervalo: 30  # segundos
    exportacion:
      html: true
      png: true
      pdf: true
```

### Seguridad

```yaml
seguridad:
  autenticacion:
    tipo: "jwt"
    expiracion_horas: 24
    algoritmo: "HS256"
    clave_secreta: "cambiar-en-produccion"
  
  autorizacion:
    roles:
      - admin
      - operador
      - usuario
      - solo_lectura
    
    permisos:
      admin: ["*"]
      operador: ["read", "write", "monitor"]
      usuario: ["read"]
      solo_lectura: ["read"]
  
  rate_limiting:
    habilitado: true
    requests_por_hora: 1000
    burst_limit: 100
  
  cors:
    habilitado: true
    origenes: ["*"]
    metodos: ["GET", "POST", "PUT", "DELETE"]
    headers: ["Content-Type", "Authorization"]
```

---

## 🔄 Configuración de Actualizaciones

### Actualizaciones Automáticas

```yaml
actualizaciones:
  habilitadas: true
  tipo: "git"
  repositorio: "https://github.com/tu-usuario/metgo3d.git"
  rama: "main"
  intervalo: 86400  # 24 horas
  
  backup_pre_actualizacion: true
  rollback_automatico: true
  notificaciones: true
  
  exclusiones:
    - "config/config.yaml"
    - "data/*.db"
    - "logs/*"
    - "backups/*"
```

### Mantenimiento

```yaml
mantenimiento:
  limpieza_automatica: true
  intervalo: 86400  # 24 horas
  
  limpieza:
    logs_antiguos: true
    datos_temporales: true
    cache: true
    respaldos_antiguos: true
  
  optimizacion:
    base_datos: true
    indices: true
    estadisticas: true
    vacio: true
```

---

## 📋 Validación de Configuración

### Script de Validación

```python
import yaml
import os
from pathlib import Path

def validar_configuracion():
    """Validar configuración del sistema"""
    try:
        # Cargar configuración
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Validar estructura básica
        assert 'sistema' in config
        assert 'quillota' in config
        assert 'meteorologia' in config
        
        # Validar coordenadas
        coords = config['quillota']['coordenadas']
        assert -90 <= coords['latitud'] <= 90
        assert -180 <= coords['longitud'] <= 180
        
        # Validar directorios
        for dir_name, dir_path in config['directorios'].items():
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        print("✅ Configuración válida")
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

if __name__ == "__main__":
    validar_configuracion()
```

### Comando de Validación

```bash
# Validar configuración
python -c "from configuracion_unificada_metgo import ConfiguracionUnificadaMETGO; c = ConfiguracionUnificadaMETGO(); c.validar_configuracion()"

# O usar script dedicado
python scripts/validar_configuracion.py
```

---

## 🎯 Configuración por Entorno

### Desarrollo

```yaml
# config/config_dev.yaml
sistema:
  entorno: "desarrollo"
  debug: true
  log_level: "DEBUG"

api_principal:
  debug: true

base_datos:
  archivo: "data/metgo3d_dev.db"

logging:
  nivel: "DEBUG"
  consola: true
```

### Testing

```yaml
# config/config_test.yaml
sistema:
  entorno: "testing"
  debug: false
  log_level: "WARNING"

base_datos:
  archivo: "data/metgo3d_test.db"

apis_meteorologicas:
  openmeteo:
    habilitado: false
  backup:
    habilitado: true
    tipo: "sintetico"
```

### Producción

```yaml
# config/config_prod.yaml
sistema:
  entorno: "produccion"
  debug: false
  log_level: "INFO"

base_datos:
  tipo: "postgresql"
  host: "db.metgo3d.cl"
  ssl: true

seguridad:
  autenticacion:
    clave_secreta: "clave-super-secreta-produccion"

notificaciones:
  email:
    habilitado: true
    smtp_server: "smtp.metgo3d.cl"
```

---

## 📞 Soporte de Configuración

### Recursos de Ayuda

- **Documentación**: `docs/guia_configuracion.md`
- **Ejemplos**: `config/examples/`
- **Validación**: `scripts/validar_configuracion.py`
- **Logs**: `logs/configuracion.log`

### Contacto

- **Email**: config@metgo3d.cl
- **GitHub Issues**: https://github.com/tu-usuario/metgo3d/issues
- **Documentación**: https://metgo3d.readthedocs.io

---

## 🎉 ¡Configuración Completada!

**METGO 3D está configurado y listo para usar**

### Próximos Pasos

1. **Validar configuración**: `python scripts/validar_configuracion.py`
2. **Iniciar sistema**: `python orquestador_metgo_avanzado.py`
3. **Verificar servicios**: `python verificar_sistema.py`
4. **Configurar monitoreo**: `python monitoreo_avanzado_metgo.py`
5. **Configurar respaldos**: `python respaldos_automaticos_metgo.py`

### Enlaces Útiles

- **Guía de Usuario**: [docs/guia_usuario.md](docs/guia_usuario.md)
- **Guía de Instalación**: [docs/guia_instalacion.md](docs/guia_instalacion.md)
- **Guía de API**: [docs/guia_api.md](docs/guia_api.md)
- **Troubleshooting**: [docs/troubleshooting.md](docs/troubleshooting.md)

---

**Sistema Meteorológico Agrícola Quillota - Configuración v2.0**

*Configuración completada exitosamente* ✅
