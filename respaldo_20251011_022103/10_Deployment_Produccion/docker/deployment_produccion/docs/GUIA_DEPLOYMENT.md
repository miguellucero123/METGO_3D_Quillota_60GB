# 🚀 GUÍA DE DEPLOYMENT - METGO 3D QUILLOTA

## 📋 Requisitos Previos

### Sistema Operativo
- Windows 10/11, Linux (Ubuntu 20.04+), o macOS 10.15+
- Python 3.11 o superior
- Docker (opcional, para deployment con contenedores)

### Dependencias
- streamlit
- pandas
- plotly
- scikit-learn
- requests
- sqlite3
- yaml

## 🚀 Deployment Local

### 1. Preparación del Entorno
```bash
# Clonar o copiar el proyecto
cd metgo-3d-quillota

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python -c "import streamlit, pandas, plotly, sklearn; print('Dependencias OK')"
```

### 2. Iniciar Sistema
```bash
# Opción 1: Script automático
python scripts/iniciar_produccion.py

# Opción 2: Script de sistema operativo
# Windows:
scripts/iniciar_produccion.bat

# Linux/Mac:
./scripts/iniciar_produccion.sh
```

### 3. Verificar Estado
```bash
python scripts/verificar_estado.py
```

## 🐳 Deployment con Docker

### 1. Construir Imagen
```bash
docker build -t metgo-quillota .
```

### 2. Iniciar Servicios
```bash
docker-compose up -d
```

### 3. Verificar Servicios
```bash
docker-compose ps
```

## 🌐 Acceso al Sistema

Una vez iniciado, el sistema estará disponible en:

- **Dashboard Principal:** http://localhost:8501
- **Dashboard Agrícola Avanzado:** http://localhost:8510
- **Sistema de Monitoreo:** http://localhost:8502

## 🔧 Configuración

### Variables de Entorno
```bash
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_HEADLESS=true
```

### Archivos de Configuración
- `config/monitoreo_config.json` - Configuración de monitoreo
- `config/backup_config.json` - Configuración de backup
- `configuracion_notificaciones_avanzada.json` - Notificaciones

## 🛠️ Mantenimiento

### Iniciar Sistema
```bash
python scripts/iniciar_produccion.py
```

### Detener Sistema
```bash
python scripts/parar_produccion.py
```

### Reiniciar Sistema
```bash
python scripts/reiniciar_produccion.py
```

### Verificar Estado
```bash
python scripts/verificar_estado.py
```

## 📊 Monitoreo

### Monitoreo Continuo
```bash
python monitoring/monitoreo_produccion.py
```

### Verificar Servicios
```bash
python scripts/verificar_estado.py
```

## 💾 Backup

### Backup Manual
```bash
python backup/backup_automatico.py
```

### Backup Programado
Configurar cron job (Linux/Mac) o Task Scheduler (Windows) para ejecutar:
```bash
python backup/backup_automatico.py
```

## 🚨 Solución de Problemas

### Servicio No Inicia
1. Verificar dependencias: `pip install -r requirements.txt`
2. Verificar puertos: `netstat -an | grep 8501`
3. Revisar logs: `logs/deployment_produccion.log`

### Error de Memoria
1. Verificar uso de memoria: `python scripts/verificar_estado.py`
2. Reiniciar sistema: `python scripts/reiniciar_produccion.py`

### Error de Base de Datos
1. Verificar archivos .db en directorio data/
2. Restaurar backup si es necesario

## 📞 Soporte

Para soporte técnico, contactar:
- Email: admin@metgo.cl
- Logs: Revisar archivos en directorio logs/
- Documentación: Ver directorio docs/

---

*Guía de Deployment - METGO 3D Quillota*
*Sistema Meteorológico Agrícola Avanzado*
