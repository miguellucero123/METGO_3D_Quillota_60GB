# 🔧 Troubleshooting - METGO 3D

## 🌾 Sistema Meteorológico Agrícola Quillota

### 📋 Tabla de Contenidos

1. [Problemas Comunes](#problemas-comunes)
2. [Errores de Instalación](#errores-de-instalación)
3. [Errores de Configuración](#errores-de-configuración)
4. [Errores de API](#errores-de-api)
5. [Errores de Base de Datos](#errores-de-base-de-datos)
6. [Errores de Monitoreo](#errores-de-monitoreo)
7. [Errores de Respaldos](#errores-de-respaldos)
8. [Problemas de Rendimiento](#problemas-de-rendimiento)
9. [Problemas de Red](#problemas-de-red)
10. [Herramientas de Diagnóstico](#herramientas-de-diagnóstico)

---

## 🚨 Problemas Comunes

### 1. Error de Importación de Módulos

**Síntoma**: `ModuleNotFoundError: No module named 'pandas'`

**Causa**: Dependencias no instaladas o entorno virtual no activado

**Solución**:
```bash
# Verificar entorno virtual
which python
pip list

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall

# Verificar instalación
python -c "import pandas; print('Pandas instalado correctamente')"
```

### 2. Error de Permisos

**Síntoma**: `PermissionError: [Errno 13] Permission denied`

**Causa**: Permisos insuficientes en directorios o archivos

**Solución**:
```bash
# Linux/macOS
chmod +x scripts/*.sh
sudo chown -R $USER:$USER .

# Windows (PowerShell como Administrador)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Error de Puerto en Uso

**Síntoma**: `Address already in use: Port 8050`

**Causa**: Puerto ya está siendo utilizado por otro proceso

**Solución**:
```bash
# Encontrar proceso usando el puerto
lsof -i :8050
# o
netstat -tulpn | grep :8050

# Terminar proceso
kill -9 PID

# O usar puerto diferente
python dashboard_unificado_metgo.py --servidor --puerto 8051
```

### 4. Error de Memoria

**Síntoma**: `MemoryError: Unable to allocate array`

**Causa**: Memoria RAM insuficiente

**Solución**:
```bash
# Reducir tamaño de datos
# Editar config/config.yaml
meteorologia:
  max_registros: 1000

# Aumentar memoria virtual (Linux)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📦 Errores de Instalación

### 1. Error de Python

**Síntoma**: `python: command not found`

**Solución**:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip

# macOS
brew install python

# Windows
# Descargar desde https://python.org
```

### 2. Error de pip

**Síntoma**: `pip: command not found`

**Solución**:
```bash
# Instalar pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

# O usar python -m pip
python -m pip install --upgrade pip
```

### 3. Error de Dependencias del Sistema

**Síntoma**: `Microsoft Visual C++ 14.0 is required`

**Solución**:
```bash
# Windows
# Instalar Microsoft Visual C++ Redistributable

# Linux
sudo apt install build-essential python3-dev

# macOS
xcode-select --install
```

### 4. Error de Git

**Síntoma**: `git: command not found`

**Solución**:
```bash
# Ubuntu/Debian
sudo apt install git

# CentOS/RHEL
sudo yum install git

# macOS
brew install git

# Windows
# Descargar desde https://git-scm.com
```

---

## ⚙️ Errores de Configuración

### 1. Error de Archivo de Configuración

**Síntoma**: `FileNotFoundError: config/config.yaml`

**Solución**:
```bash
# Crear archivo de configuración
cp config/config.yaml.example config/config.yaml

# O generar configuración por defecto
python -c "from configuracion_unificada_metgo import ConfiguracionUnificadaMETGO; c = ConfiguracionUnificadaMETGO(); c.crear_configuracion_default()"
```

### 2. Error de Validación de Configuración

**Síntoma**: `ValidationError: Invalid configuration`

**Solución**:
```bash
# Validar configuración
python scripts/validar_configuracion.py

# Ver errores específicos
python -c "import yaml; print(yaml.safe_load(open('config/config.yaml')))"
```

### 3. Error de Variables de Entorno

**Síntoma**: `KeyError: 'DATABASE_URL'`

**Solución**:
```bash
# Crear archivo .env
cp metgo.env.example .env

# Editar variables
nano .env

# Cargar variables
source .env
```

### 4. Error de Coordenadas

**Síntoma**: `ValueError: Invalid coordinates`

**Solución**:
```yaml
# Verificar coordenadas en config/config.yaml
quillota:
  coordenadas:
    latitud: -32.8833  # Entre -90 y 90
    longitud: -71.2333  # Entre -180 y 180
    altitud: 127  # Positivo
```

---

## 🔌 Errores de API

### 1. Error de Conexión a API

**Síntoma**: `ConnectionError: Failed to connect to API`

**Solución**:
```bash
# Verificar conexión a internet
ping api.open-meteo.com

# Verificar configuración de proxy
# Editar config/config.yaml
apis_meteorologicas:
  openmeteo:
    timeout: 60
    reintentos: 5
```

### 2. Error de Autenticación

**Síntoma**: `401 Unauthorized`

**Solución**:
```bash
# Verificar token JWT
python -c "import jwt; print(jwt.decode('tu-token', verify=False))"

# Renovar token
curl -X POST http://localhost:5000/api/v1/auth/refresh \
  -H "Authorization: Bearer tu-token"
```

### 3. Error de Rate Limiting

**Síntoma**: `429 Too Many Requests`

**Solución**:
```bash
# Verificar límites
curl -I http://localhost:5000/api/v1/health

# Esperar y reintentar
sleep 60
```

### 4. Error de CORS

**Síntoma**: `CORS error: Access to fetch blocked`

**Solución**:
```yaml
# Configurar CORS en config/config.yaml
api_principal:
  cors:
    habilitado: true
    origenes: ["*"]
    metodos: ["GET", "POST", "PUT", "DELETE"]
```

---

## 🗄️ Errores de Base de Datos

### 1. Error de Conexión a SQLite

**Síntoma**: `sqlite3.OperationalError: database is locked`

**Solución**:
```bash
# Verificar procesos usando la base de datos
lsof data/metgo3d.db

# Terminar procesos
kill -9 PID

# Recrear base de datos
rm data/metgo3d.db
python 00_Sistema_Principal_MIP_Quillota.ipynb
```

### 2. Error de Permisos de Base de Datos

**Síntoma**: `sqlite3.OperationalError: unable to open database file`

**Solución**:
```bash
# Verificar permisos
ls -la data/

# Corregir permisos
chmod 755 data/
chmod 644 data/metgo3d.db
```

### 3. Error de PostgreSQL

**Síntoma**: `psycopg2.OperationalError: connection refused`

**Solución**:
```bash
# Verificar servicio PostgreSQL
sudo systemctl status postgresql

# Iniciar servicio
sudo systemctl start postgresql

# Verificar configuración
sudo -u postgres psql -c "SELECT version();"
```

### 4. Error de Redis

**Síntoma**: `redis.ConnectionError: Error connecting to Redis`

**Solución**:
```bash
# Verificar servicio Redis
sudo systemctl status redis

# Iniciar servicio
sudo systemctl start redis

# Verificar conexión
redis-cli ping
```

---

## 📊 Errores de Monitoreo

### 1. Error de Métricas

**Síntoma**: `psutil.NoSuchProcess: process not found`

**Solución**:
```bash
# Verificar procesos del sistema
ps aux | grep python

# Reiniciar monitoreo
python monitoreo_avanzado_metgo.py
```

### 2. Error de Dashboard de Monitoreo

**Síntoma**: `Dash app failed to start`

**Solución**:
```bash
# Verificar puerto
lsof -i :8051

# Usar puerto diferente
python dashboard_monitoreo_metgo.py --servidor --puerto 8052
```

### 3. Error de Alertas

**Síntoma**: `SMTPAuthenticationError: Authentication failed`

**Solución**:
```yaml
# Verificar configuración de email
notificaciones:
  email:
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    usuario: "tu-email@gmail.com"
    password: "tu-password-app"  # Usar contraseña de aplicación
```

### 4. Error de Base de Datos de Monitoreo

**Síntoma**: `sqlite3.OperationalError: no such table: metricas`

**Solución**:
```bash
# Recrear base de datos de monitoreo
rm data/monitoreo/monitoreo_avanzado.db
python monitoreo_avanzado_metgo.py
```

---

## 💾 Errores de Respaldos

### 1. Error de Espacio en Disco

**Síntoma**: `OSError: [Errno 28] No space left on device`

**Solución**:
```bash
# Verificar espacio en disco
df -h

# Limpiar espacio
python limpiar_y_optimizar.py

# Configurar respaldos en ubicación diferente
# Editar config/config.yaml
respaldos:
  destino: "/path/to/external/disk"
```

### 2. Error de Permisos de Respaldo

**Síntoma**: `PermissionError: [Errno 13] Permission denied`

**Solución**:
```bash
# Verificar permisos del directorio de respaldos
ls -la backups/

# Corregir permisos
chmod 755 backups/
chown -R $USER:$USER backups/
```

### 3. Error de Compresión

**Síntoma**: `tarfile.ReadError: file could not be opened successfully`

**Solución**:
```bash
# Verificar integridad del archivo
tar -tzf backup.tar.gz

# Recrear respaldo
python respaldos_automaticos_metgo.py
```

### 4. Error de Verificación de Integridad

**Síntoma**: `Checksum verification failed`

**Solución**:
```bash
# Verificar checksum manualmente
sha256sum backup.tar.gz

# Recrear respaldo
python respaldos_automaticos_metgo.py
```

---

## ⚡ Problemas de Rendimiento

### 1. Sistema Lento

**Síntoma**: Respuestas lentas del sistema

**Solución**:
```bash
# Analizar rendimiento
python analisis_rendimiento.py

# Optimizar base de datos
python -c "from orquestador_metgo_avanzado import OrquestadorMETGOAvanzado; o = OrquestadorMETGOAvanzado(); o.optimizar_base_datos()"

# Limpiar sistema
python limpiar_y_optimizar.py
```

### 2. Alto Uso de CPU

**Síntoma**: CPU al 100%

**Solución**:
```bash
# Identificar procesos
top -p $(pgrep -f python)

# Reducir frecuencia de actualización
# Editar config/config.yaml
monitoreo:
  metricas:
    intervalo: 60  # Aumentar de 30 a 60 segundos
```

### 3. Alto Uso de Memoria

**Síntoma**: Memoria RAM agotada

**Solución**:
```bash
# Verificar uso de memoria
free -h
ps aux --sort=-%mem | head

# Reducir tamaño de datos
# Editar config/config.yaml
meteorologia:
  max_registros: 500  # Reducir de 1000 a 500
```

### 4. Lento Acceso a Base de Datos

**Síntoma**: Consultas lentas

**Solución**:
```bash
# Optimizar base de datos
python -c "from orquestador_metgo_avanzado import OrquestadorMETGOAvanzado; o = OrquestadorMETGOAvanzado(); o.optimizar_base_datos()"

# Crear índices
sqlite3 data/metgo3d.db "CREATE INDEX IF NOT EXISTS idx_timestamp ON datos_meteorologicos(timestamp);"
```

---

## 🌐 Problemas de Red

### 1. Error de Conexión a Internet

**Síntoma**: `ConnectionError: Failed to connect`

**Solución**:
```bash
# Verificar conectividad
ping google.com
curl -I https://api.open-meteo.com

# Verificar DNS
nslookup api.open-meteo.com

# Verificar proxy
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

### 2. Error de Firewall

**Síntoma**: `Connection refused`

**Solución**:
```bash
# Verificar firewall
sudo ufw status
sudo firewall-cmd --list-all

# Abrir puertos necesarios
sudo ufw allow 5000/tcp
sudo ufw allow 8050/tcp
```

### 3. Error de SSL/TLS

**Síntoma**: `SSL: CERTIFICATE_VERIFY_FAILED`

**Solución**:
```bash
# Actualizar certificados
sudo apt update && sudo apt install ca-certificates

# O deshabilitar verificación SSL (no recomendado)
# Editar config/config.yaml
apis_meteorologicas:
  openmeteo:
    verify_ssl: false
```

### 4. Error de Timeout

**Síntoma**: `ReadTimeout: HTTPSConnectionPool`

**Solución**:
```yaml
# Aumentar timeout
apis_meteorologicas:
  openmeteo:
    timeout: 120  # Aumentar de 30 a 120 segundos
    reintentos: 5
```

---

## 🔍 Herramientas de Diagnóstico

### 1. Diagnóstico Completo

```bash
# Ejecutar diagnóstico completo
python diagnostico_completo.py

# Ver reporte
cat reportes/diagnostico_*.json
```

### 2. Verificación del Sistema

```bash
# Verificar estado del sistema
python verificar_sistema.py

# Verificar componentes específicos
python -c "from verificar_sistema import VerificarSistema; v = VerificarSistema(); v.verificar_componentes()"
```

### 3. Análisis de Rendimiento

```bash
# Analizar rendimiento
python analisis_rendimiento.py

# Ver métricas
cat reportes/rendimiento_*.json
```

### 4. Análisis de Logs

```bash
# Ver logs del sistema
tail -f logs/metgo3d.log

# Buscar errores
grep -i error logs/*.log

# Analizar logs de monitoreo
tail -f logs/monitoreo/monitoreo_avanzado.log
```

### 5. Comandos de Diagnóstico

```bash
# Información del sistema
uname -a
python --version
pip list

# Espacio en disco
df -h

# Memoria
free -h

# Procesos
ps aux | grep python

# Puertos
netstat -tulpn | grep python

# Red
ping -c 4 api.open-meteo.com
```

---

## 📞 Soporte

### Recursos de Ayuda

- **Documentación**: `docs/`
- **Logs**: `logs/`
- **Scripts de diagnóstico**: `scripts/`
- **Tests**: `tests/`

### Contacto

- **Email**: soporte@metgo3d.cl
- **GitHub Issues**: https://github.com/tu-usuario/metgo3d/issues
- **Documentación**: https://metgo3d.readthedocs.io

### Información del Sistema

```bash
# Generar información del sistema
python -c "
import platform
import sys
import os
print('Sistema:', platform.system())
print('Versión:', platform.version())
print('Arquitectura:', platform.machine())
print('Python:', sys.version)
print('Directorio:', os.getcwd())
print('Usuario:', os.getenv('USER', 'unknown'))
"
```

---

## 🎯 Soluciones Rápidas

### Reiniciar Sistema

```bash
# Detener todos los procesos
pkill -f python

# Limpiar archivos temporales
rm -rf temp/*

# Reiniciar sistema
python orquestador_metgo_avanzado.py
```

### Restaurar Configuración

```bash
# Restaurar configuración por defecto
cp config/config.yaml.example config/config.yaml

# O generar nueva configuración
python -c "from configuracion_unificada_metgo import ConfiguracionUnificadaMETGO; c = ConfiguracionUnificadaMETGO(); c.crear_configuracion_default()"
```

### Limpiar Sistema

```bash
# Limpiar archivos temporales
python limpiar_y_optimizar.py

# Limpiar logs antiguos
find logs/ -name "*.log" -mtime +30 -delete

# Limpiar respaldos antiguos
find backups/ -name "*.tar.gz" -mtime +30 -delete
```

### Restaurar desde Respaldo

```bash
# Listar respaldos disponibles
ls -la backups/

# Restaurar respaldo específico
python -c "from respaldos_automaticos_metgo import RespaldosAutomaticosMETGO; r = RespaldosAutomaticosMETGO(); r.restaurar_respaldo('respaldo_id')"
```

---

## 🎉 ¡Problema Resuelto!

**METGO 3D está funcionando correctamente**

### Próximos Pasos

1. **Verificar sistema**: `python verificar_sistema.py`
2. **Ejecutar tests**: `python tests/runner_tests.py`
3. **Monitorear sistema**: `python monitoreo_avanzado_metgo.py`
4. **Configurar respaldos**: `python respaldos_automaticos_metgo.py`

### Enlaces Útiles

- **Guía de Usuario**: [docs/guia_usuario.md](docs/guia_usuario.md)
- **Guía de Instalación**: [docs/guia_instalacion.md](docs/guia_instalacion.md)
- **Guía de API**: [docs/guia_api.md](docs/guia_api.md)
- **Guía de Configuración**: [docs/guia_configuracion.md](docs/guia_configuracion.md)

---

**Sistema Meteorológico Agrícola Quillota - Troubleshooting v2.0**

*Problema resuelto exitosamente* ✅
