# 🚀 Guía de Deployment en Producción - METGO 3D

## 📋 Descripción
Guía completa para el deployment del sistema METGO 3D en un entorno de producción.

## 🎯 Objetivos
- Desplegar el sistema METGO 3D en producción
- Configurar servicios y monitoreo
- Verificar funcionamiento correcto
- Generar reportes de deployment

## 📋 Prerequisitos

### Sistema Operativo
- **Linux**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **Windows**: Windows Server 2019+ / Windows 10+
- **macOS**: macOS 10.15+

### Software Requerido
- **Python**: 3.8 o superior
- **pip**: Gestor de paquetes de Python
- **Docker**: 20.10+ (opcional pero recomendado)
- **Docker Compose**: 2.0+ (opcional pero recomendado)
- **Git**: 2.30+ (opcional)

### Recursos del Sistema
- **CPU**: Mínimo 4 cores, recomendado 8+ cores
- **RAM**: Mínimo 8GB, recomendado 16GB+
- **Disco**: Mínimo 50GB, recomendado 100GB+
- **Red**: Conexión estable a internet

## 🔧 Instalación

### 1. Preparación del Entorno

```bash
# Crear directorio del proyecto
mkdir -p /opt/metgo3d
cd /opt/metgo3d

# Clonar repositorio (si aplica)
git clone https://github.com/tu-usuario/metgo3d.git .

# O copiar archivos del proyecto
cp -r /ruta/al/proyecto/* .
```

### 2. Instalación de Dependencias

```bash
# Instalar dependencias de Python
pip install -r requirements.txt

# Verificar instalación
python --version
pip list
```

### 3. Configuración del Sistema

```bash
# Copiar archivo de configuración
cp config/config.yaml.example config/config.yaml

# Editar configuración
nano config/config.yaml
```

### 4. Configuración de Variables de Entorno

```bash
# Crear archivo de entorno
cp metgo.env.example metgo.env

# Editar variables de entorno
nano metgo.env
```

## 🚀 Deployment

### Método 1: Deployment Automático

```bash
# Ejecutar deployment automático
python deployment_produccion_completo.py
```

### Método 2: Deployment Manual

#### Paso 1: Verificar Prerequisitos
```bash
# Verificar Python
python --version

# Verificar pip
pip --version

# Verificar Docker (opcional)
docker --version
docker-compose --version
```

#### Paso 2: Instalar Dependencias
```bash
# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
pip list | grep -E "(numpy|pandas|scikit-learn|dash|plotly)"
```

#### Paso 3: Ejecutar Pruebas
```bash
# Ejecutar pruebas del sistema
python pruebas_finales_metgo.py

# Verificar resultados
cat reportes/pruebas_finales_*.json
```

#### Paso 4: Construir Artefactos
```bash
# Crear directorio de artefactos
mkdir -p artefactos

# Construir imagen Docker (opcional)
docker build -t metgo3d:latest .

# Verificar imagen
docker images | grep metgo3d
```

#### Paso 5: Configurar Entorno
```bash
# Crear directorios necesarios
mkdir -p data logs reportes backups

# Configurar permisos
chmod 755 data logs reportes backups

# Crear archivo de entorno
echo "ENVIRONMENT=production" > metgo.env
echo "VERSION=2.0" >> metgo.env
echo "DEBUG=False" >> metgo.env
```

#### Paso 6: Desplegar Servicios
```bash
# Desplegar con Docker Compose (opcional)
docker-compose up -d

# Verificar servicios
docker-compose ps

# O desplegar servicios Python directamente
python monitoreo_avanzado_metgo.py &
python dashboard_unificado_metgo.py &
python apis_avanzadas_metgo.py &
```

#### Paso 7: Verificar Deployment
```bash
# Verificar contenedores Docker
docker ps

# Verificar logs
tail -f logs/deployment/deployment_completo.log

# Verificar servicios
curl http://localhost:5000/health
curl http://localhost:8051/health
```

#### Paso 8: Generar Reporte
```bash
# El reporte se genera automáticamente
ls -la reportes/deployment_*

# Verificar contenido
cat reportes/deployment_produccion_*.json
```

## 🔍 Verificación

### 1. Verificar Servicios
```bash
# Verificar procesos Python
ps aux | grep python

# Verificar puertos
netstat -tlnp | grep -E "(5000|8051|6379|5432)"

# Verificar contenedores Docker
docker ps
```

### 2. Verificar Logs
```bash
# Ver logs de deployment
tail -f logs/deployment/deployment_completo.log

# Ver logs de monitoreo
tail -f logs/monitoreo/monitoreo_avanzado.log

# Ver logs de dashboard
tail -f logs/dashboard/dashboard_unificado.log
```

### 3. Verificar Base de Datos
```bash
# Verificar archivos de base de datos
ls -la data/*.db

# Verificar tamaño
du -sh data/*.db
```

### 4. Verificar Archivos de Configuración
```bash
# Verificar configuración principal
cat config/config.yaml

# Verificar variables de entorno
cat metgo.env

# Verificar Docker Compose
cat docker-compose.yml
```

## 📊 Monitoreo

### 1. Monitoreo del Sistema
```bash
# Verificar uso de CPU
top -p $(pgrep -f "python.*metgo")

# Verificar uso de memoria
free -h

# Verificar uso de disco
df -h
```

### 2. Monitoreo de Servicios
```bash
# Verificar estado de servicios
systemctl status metgo3d-*

# Verificar logs del sistema
journalctl -u metgo3d-* -f
```

### 3. Monitoreo de Red
```bash
# Verificar conectividad
ping -c 4 8.8.8.8

# Verificar puertos
nmap -p 5000,8051,6379,5432 localhost
```

## 🔧 Mantenimiento

### 1. Actualizaciones
```bash
# Actualizar dependencias
pip install -r requirements.txt --upgrade

# Actualizar imagen Docker
docker pull metgo3d:latest
docker-compose pull
```

### 2. Respaldos
```bash
# Crear respaldo de datos
python respaldos_automaticos_metgo.py

# Verificar respaldos
ls -la backups/
```

### 3. Limpieza
```bash
# Limpiar logs antiguos
find logs/ -name "*.log" -mtime +30 -delete

# Limpiar respaldos antiguos
find backups/ -name "*.tar.gz" -mtime +90 -delete
```

## 🚨 Troubleshooting

### Problemas Comunes

#### 1. Error de Dependencias
```bash
# Solución: Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

#### 2. Error de Permisos
```bash
# Solución: Configurar permisos
chmod 755 data logs reportes backups
chown -R metgo3d:metgo3d /opt/metgo3d
```

#### 3. Error de Puerto en Uso
```bash
# Solución: Verificar y liberar puertos
netstat -tlnp | grep :5000
kill -9 $(lsof -t -i:5000)
```

#### 4. Error de Docker
```bash
# Solución: Reiniciar Docker
sudo systemctl restart docker
docker-compose down
docker-compose up -d
```

### Logs de Diagnóstico
```bash
# Ver logs de error
grep -i error logs/*.log

# Ver logs de warning
grep -i warning logs/*.log

# Ver logs de deployment
cat reportes/deployment_produccion_*.json | jq '.estado.errores'
```

## 📋 Checklist de Deployment

### Pre-Deployment
- [ ] Verificar prerequisitos del sistema
- [ ] Instalar dependencias
- [ ] Configurar archivos de configuración
- [ ] Configurar variables de entorno
- [ ] Ejecutar pruebas del sistema

### Deployment
- [ ] Construir artefactos
- [ ] Configurar entorno de producción
- [ ] Desplegar servicios
- [ ] Verificar deployment
- [ ] Generar reporte

### Post-Deployment
- [ ] Verificar servicios activos
- [ ] Verificar logs del sistema
- [ ] Verificar base de datos
- [ ] Configurar monitoreo
- [ ] Configurar respaldos automáticos

## 🔗 Enlaces Útiles

- [Documentación del Sistema](README.md)
- [Guía de Usuario](guia_usuario.md)
- [Guía de Instalación](guia_instalacion.md)
- [Guía de API](guia_api.md)
- [Troubleshooting](troubleshooting.md)

## 📞 Soporte

Para soporte técnico:
- **Email**: soporte@metgo3d.cl
- **Documentación**: [docs.metgo3d.cl](https://docs.metgo3d.cl)
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/metgo3d/issues)

---

**Versión**: 2.0  
**Fecha**: 2025-01-02  
**Autor**: Equipo METGO 3D
