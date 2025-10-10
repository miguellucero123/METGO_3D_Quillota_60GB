# 📦 Guía de Instalación - METGO 3D

## 🌾 Sistema Meteorológico Agrícola Quillota

### 📋 Tabla de Contenidos

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación en Windows](#instalación-en-windows)
3. [Instalación en Linux](#instalación-en-linux)
4. [Instalación en macOS](#instalación-en-macos)
5. [Instalación con Docker](#instalación-con-docker)
6. [Instalación en la Nube](#instalación-en-la-nube)
7. [Configuración Post-Instalación](#configuración-post-instalación)
8. [Verificación de la Instalación](#verificación-de-la-instalación)
9. [Solución de Problemas](#solución-de-problemas)
10. [Desinstalación](#desinstalación)

---

## 💻 Requisitos del Sistema

### Requisitos Mínimos

- **Sistema Operativo**: Windows 10, Ubuntu 18.04+, macOS 10.14+
- **Python**: 3.8 o superior
- **Memoria RAM**: 4GB mínimo, 8GB recomendado
- **Espacio en disco**: 2GB libres
- **Conexión a Internet**: Para APIs meteorológicas
- **Navegador web**: Chrome, Firefox, Safari, Edge

### Requisitos Recomendados

- **Sistema Operativo**: Windows 11, Ubuntu 20.04+, macOS 12+
- **Python**: 3.9 o superior
- **Memoria RAM**: 16GB
- **Espacio en disco**: 10GB libres
- **CPU**: 4+ núcleos
- **GPU**: Opcional, para visualizaciones 3D

### Dependencias del Sistema

#### Windows
- Microsoft Visual C++ Redistributable
- Git for Windows
- PowerShell 5.1+

#### Linux
- build-essential
- python3-dev
- libssl-dev
- libffi-dev
- git

#### macOS
- Xcode Command Line Tools
- Homebrew (recomendado)
- Git

---

## 🪟 Instalación en Windows

### Método 1: Instalación Automática

```powershell
# 1. Abrir PowerShell como Administrador
# 2. Ejecutar comando de instalación
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/tu-usuario/metgo3d/main/instalar_windows.ps1" -OutFile "instalar_metgo3d.ps1"
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\instalar_metgo3d.ps1
```

### Método 2: Instalación Manual

```powershell
# 1. Instalar Python
# Descargar desde https://python.org
# Marcar "Add Python to PATH"

# 2. Verificar instalación
python --version
pip --version

# 3. Instalar Git
# Descargar desde https://git-scm.com

# 4. Clonar repositorio
git clone https://github.com/tu-usuario/metgo3d.git
cd metgo3d

# 5. Crear entorno virtual
python -m venv venv_metgo3d
venv_metgo3d\Scripts\activate

# 6. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 7. Verificar instalación
python verificar_sistema.py
```

### Método 3: Con Chocolatey

```powershell
# 1. Instalar Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 2. Instalar dependencias
choco install python git -y

# 3. Continuar con instalación manual
```

---

## 🐧 Instalación en Linux

### Ubuntu/Debian

```bash
# 1. Actualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependencias
sudo apt install -y python3 python3-pip python3-venv git build-essential python3-dev libssl-dev libffi-dev

# 3. Clonar repositorio
git clone https://github.com/tu-usuario/metgo3d.git
cd metgo3d

# 4. Crear entorno virtual
python3 -m venv venv_metgo3d
source venv_metgo3d/bin/activate

# 5. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 6. Verificar instalación
python verificar_sistema.py
```

### CentOS/RHEL/Fedora

```bash
# 1. Instalar dependencias
sudo yum install -y python3 python3-pip git gcc python3-devel openssl-devel libffi-devel
# o para Fedora:
sudo dnf install -y python3 python3-pip git gcc python3-devel openssl-devel libffi-devel

# 2. Continuar con pasos 3-6 de Ubuntu
```

### Arch Linux

```bash
# 1. Instalar dependencias
sudo pacman -S python python-pip git base-devel

# 2. Continuar con pasos 3-6 de Ubuntu
```

### Instalación como Servicio (systemd)

```bash
# 1. Crear usuario del sistema
sudo useradd -r -s /bin/false metgo3d

# 2. Crear directorio de instalación
sudo mkdir -p /opt/metgo3d
sudo chown metgo3d:metgo3d /opt/metgo3d

# 3. Copiar archivos
sudo cp -r . /opt/metgo3d/
sudo chown -R metgo3d:metgo3d /opt/metgo3d

# 4. Crear archivo de servicio
sudo tee /etc/systemd/system/metgo3d.service > /dev/null <<EOF
[Unit]
Description=METGO 3D - Sistema Meteorológico Agrícola
After=network.target

[Service]
Type=simple
User=metgo3d
WorkingDirectory=/opt/metgo3d
Environment=PATH=/opt/metgo3d/venv_metgo3d/bin
ExecStart=/opt/metgo3d/venv_metgo3d/bin/python orquestador_metgo_avanzado.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 5. Habilitar y iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable metgo3d
sudo systemctl start metgo3d

# 6. Verificar estado
sudo systemctl status metgo3d
```

---

## 🍎 Instalación en macOS

### Método 1: Con Homebrew

```bash
# 1. Instalar Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Instalar dependencias
brew install python git

# 3. Clonar repositorio
git clone https://github.com/tu-usuario/metgo3d.git
cd metgo3d

# 4. Crear entorno virtual
python3 -m venv venv_metgo3d
source venv_metgo3d/bin/activate

# 5. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 6. Verificar instalación
python verificar_sistema.py
```

### Método 2: Instalación Manual

```bash
# 1. Instalar Xcode Command Line Tools
xcode-select --install

# 2. Instalar Python desde python.org
# 3. Continuar con pasos 3-6 de Homebrew
```

### Método 3: Con MacPorts

```bash
# 1. Instalar MacPorts
# Descargar desde https://macports.org

# 2. Instalar dependencias
sudo port install python39 py39-pip git

# 3. Continuar con pasos 3-6 de Homebrew
```

---

## 🐳 Instalación con Docker

### Docker Compose (Recomendado)

```bash
# 1. Instalar Docker y Docker Compose
# Windows: Docker Desktop
# Linux: docker.io y docker-compose
# macOS: Docker Desktop

# 2. Clonar repositorio
git clone https://github.com/tu-usuario/metgo3d.git
cd metgo3d

# 3. Configurar variables de entorno
cp metgo.env.example .env
# Editar .env con tus configuraciones

# 4. Ejecutar con Docker Compose
docker-compose up -d

# 5. Verificar servicios
docker-compose ps
docker-compose logs -f
```

### Docker Manual

```bash
# 1. Construir imagen
docker build -t metgo3d:latest .

# 2. Ejecutar contenedor
docker run -d \
  --name metgo3d \
  -p 5000:5000 \
  -p 8050:8050 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config:/app/config \
  metgo3d:latest

# 3. Verificar contenedor
docker ps
docker logs metgo3d
```

### Docker con Base de Datos

```bash
# 1. Crear red Docker
docker network create metgo3d-network

# 2. Ejecutar PostgreSQL
docker run -d \
  --name metgo3d-postgres \
  --network metgo3d-network \
  -e POSTGRES_DB=metgo3d \
  -e POSTGRES_USER=metgo3d \
  -e POSTGRES_PASSWORD=metgo3d_2024_secure \
  -v metgo3d-postgres-data:/var/lib/postgresql/data \
  postgres:13

# 3. Ejecutar Redis
docker run -d \
  --name metgo3d-redis \
  --network metgo3d-network \
  -v metgo3d-redis-data:/data \
  redis:6-alpine

# 4. Ejecutar METGO 3D
docker run -d \
  --name metgo3d \
  --network metgo3d-network \
  -p 5000:5000 \
  -p 8050:8050 \
  -e POSTGRES_HOST=metgo3d-postgres \
  -e REDIS_HOST=metgo3d-redis \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config:/app/config \
  metgo3d:latest
```

---

## ☁️ Instalación en la Nube

### AWS EC2

```bash
# 1. Crear instancia EC2 (Ubuntu 20.04 LTS)
# Tipo: t3.medium o superior
# Almacenamiento: 20GB mínimo

# 2. Conectar por SSH
ssh -i tu-key.pem ubuntu@tu-instancia.amazonaws.com

# 3. Instalar dependencias
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git nginx

# 4. Clonar e instalar METGO 3D
git clone https://github.com/tu-usuario/metgo3d.git
cd metgo3d
python3 -m venv venv_metgo3d
source venv_metgo3d/bin/activate
pip install -r requirements.txt

# 5. Configurar Nginx
sudo tee /etc/nginx/sites-available/metgo3d > /dev/null <<EOF
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://localhost:8050;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/metgo3d /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 6. Configurar SSL con Let's Encrypt
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

### Google Cloud Platform

```bash
# 1. Crear instancia Compute Engine
# Tipo: e2-medium o superior
# Sistema: Ubuntu 20.04 LTS

# 2. Conectar por SSH
gcloud compute ssh tu-instancia --zone=tu-zona

# 3. Continuar con pasos 3-6 de AWS
```

### Azure

```bash
# 1. Crear VM en Azure
# Tipo: Standard_B2s o superior
# Sistema: Ubuntu 20.04 LTS

# 2. Conectar por SSH
ssh azureuser@tu-instancia.cloudapp.azure.com

# 3. Continuar con pasos 3-6 de AWS
```

### DigitalOcean

```bash
# 1. Crear Droplet
# Tipo: 2GB RAM o superior
# Sistema: Ubuntu 20.04 LTS

# 2. Conectar por SSH
ssh root@tu-droplet-ip

# 3. Continuar con pasos 3-6 de AWS
```

---

## ⚙️ Configuración Post-Instalación

### 1. Configuración Inicial

```bash
# Ejecutar configuración inicial
python instalar_y_configurar.py

# O manualmente
cp config/config.yaml.example config/config.yaml
# Editar config/config.yaml
```

### 2. Configuración de Base de Datos

```bash
# Inicializar base de datos
python -c "from orquestador_metgo_avanzado import OrquestadorMETGOAvanzado; o = OrquestadorMETGOAvanzado(); o.inicializar_sistema()"
```

### 3. Configuración de Logs

```bash
# Crear directorios de logs
mkdir -p logs/{sistema,monitoreo,backups,errores}

# Configurar rotación de logs
sudo tee /etc/logrotate.d/metgo3d > /dev/null <<EOF
/path/to/metgo3d/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 metgo3d metgo3d
}
EOF
```

### 4. Configuración de Firewall

```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 5000/tcp  # API
sudo ufw allow 8050/tcp  # Dashboard
sudo ufw enable

# CentOS/RHEL/Fedora
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-port=8050/tcp
sudo firewall-cmd --reload
```

### 5. Configuración de Backup

```bash
# Configurar respaldos automáticos
python -c "from respaldos_automaticos_metgo import RespaldosAutomaticosMETGO; r = RespaldosAutomaticosMETGO(); r.iniciar_respaldos_automaticos()"

# Configurar cron para respaldos
crontab -e
# Agregar línea:
# 0 2 * * * /path/to/metgo3d/venv_metgo3d/bin/python /path/to/metgo3d/respaldos_automaticos_metgo.py
```

---

## ✅ Verificación de la Instalación

### 1. Verificación Automática

```bash
# Ejecutar verificación completa
python verificar_sistema.py

# Verificar componentes individuales
python -c "import sys; print('Python:', sys.version)"
python -c "import pandas; print('Pandas:', pandas.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import sklearn; print('Scikit-learn:', sklearn.__version__)"
```

### 2. Verificación Manual

```bash
# Verificar estructura de directorios
ls -la
# Debe mostrar: data/, config/, logs/, notebooks/, tests/, etc.

# Verificar archivos de configuración
ls -la config/
# Debe mostrar: config.yaml, nginx.conf, etc.

# Verificar base de datos
ls -la data/
# Debe mostrar: metgo3d.db (después de la primera ejecución)
```

### 3. Pruebas del Sistema

```bash
# Ejecutar tests unitarios
python tests/runner_tests.py --categoria unitarios

# Ejecutar tests de integración
python tests/runner_tests.py --categoria integracion

# Ejecutar tests de rendimiento
python tests/runner_tests.py --categoria rendimiento

# Ejecutar todos los tests
python tests/runner_tests.py --categoria todos
```

### 4. Pruebas de Funcionalidad

```bash
# Probar sistema principal
python orquestador_metgo_avanzado.py

# Probar dashboard
python dashboard_unificado_metgo.py --servidor
# Acceder a: http://localhost:8050

# Probar monitoreo
python monitoreo_avanzado_metgo.py

# Probar respaldos
python respaldos_automaticos_metgo.py
```

---

## 🔧 Solución de Problemas

### Problemas Comunes

#### 1. Error de Permisos

**Síntoma**: `PermissionError` o `Access Denied`

**Solución**:
```bash
# Linux/macOS
chmod +x scripts/*.sh
sudo chown -R $USER:$USER .

# Windows
# Ejecutar PowerShell como Administrador
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. Error de Dependencias

**Síntoma**: `ModuleNotFoundError` o `ImportError`

**Solución**:
```bash
# Reinstalar dependencias
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Verificar entorno virtual
which python
pip list
```

#### 3. Error de Puerto en Uso

**Síntoma**: `Address already in use`

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

#### 4. Error de Memoria

**Síntoma**: `MemoryError` o `OutOfMemoryError`

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

#### 5. Error de Conexión a API

**Síntoma**: `ConnectionError` o `TimeoutError`

**Solución**:
```bash
# Verificar conexión a internet
ping api.open-meteo.com

# Verificar configuración de proxy
# Editar config/config.yaml
apis:
  openmeteo:
    timeout: 60
    reintentos: 5
```

### Logs de Diagnóstico

```bash
# Ver logs del sistema
tail -f logs/metgo3d.log

# Ver logs de instalación
tail -f logs/instalacion.log

# Ver logs de errores
tail -f logs/errores/error.log

# Generar diagnóstico completo
python diagnostico_completo.py
```

### Comandos de Diagnóstico

```bash
# Verificar estado del sistema
python verificar_sistema.py

# Análisis de rendimiento
python analisis_rendimiento.py

# Diagnóstico completo
python diagnostico_completo.py

# Limpiar sistema
python limpiar_y_optimizar.py
```

---

## 🗑️ Desinstalación

### Desinstalación Completa

```bash
# 1. Detener servicios
sudo systemctl stop metgo3d  # Si está como servicio
docker-compose down          # Si está con Docker

# 2. Eliminar archivos
rm -rf /path/to/metgo3d

# 3. Eliminar entorno virtual
rm -rf venv_metgo3d

# 4. Eliminar base de datos
rm -rf data/metgo3d.db

# 5. Eliminar logs
rm -rf logs/

# 6. Eliminar configuraciones
rm -rf config/

# 7. Eliminar respaldos
rm -rf backups/
```

### Desinstalación con Docker

```bash
# 1. Detener y eliminar contenedores
docker-compose down -v

# 2. Eliminar imágenes
docker rmi metgo3d:latest

# 3. Eliminar volúmenes
docker volume prune

# 4. Eliminar red
docker network rm metgo3d_metgo3d_network
```

### Desinstalación de Servicio (systemd)

```bash
# 1. Detener y deshabilitar servicio
sudo systemctl stop metgo3d
sudo systemctl disable metgo3d

# 2. Eliminar archivo de servicio
sudo rm /etc/systemd/system/metgo3d.service

# 3. Recargar systemd
sudo systemctl daemon-reload

# 4. Eliminar usuario
sudo userdel metgo3d

# 5. Eliminar directorio
sudo rm -rf /opt/metgo3d
```

### Limpieza de Dependencias

```bash
# Desinstalar paquetes Python
pip uninstall -r requirements.txt -y

# Eliminar cache de pip
pip cache purge

# Eliminar paquetes del sistema (Linux)
sudo apt remove python3-pip python3-venv  # Ubuntu/Debian
sudo yum remove python3-pip               # CentOS/RHEL
```

---

## 📞 Soporte de Instalación

### Recursos de Ayuda

- **Documentación**: `docs/`
- **Logs de instalación**: `logs/instalacion.log`
- **Scripts de instalación**: `scripts/`
- **Tests de verificación**: `tests/`

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
print('Sistema:', platform.system())
print('Versión:', platform.version())
print('Arquitectura:', platform.machine())
print('Python:', sys.version)
print('Directorio:', sys.executable)
"
```

---

## 🎉 ¡Instalación Completada!

**METGO 3D está listo para usar**

### Próximos Pasos

1. **Configurar el sistema**: Editar `config/config.yaml`
2. **Ejecutar primera vez**: `python orquestador_metgo_avanzado.py`
3. **Acceder al dashboard**: http://localhost:8050
4. **Configurar monitoreo**: `python monitoreo_avanzado_metgo.py`
5. **Configurar respaldos**: `python respaldos_automaticos_metgo.py`

### Enlaces Útiles

- **Guía de Usuario**: [docs/guia_usuario.md](docs/guia_usuario.md)
- **Guía de API**: [docs/guia_api.md](docs/guia_api.md)
- **Configuración**: [docs/guia_configuracion.md](docs/guia_configuracion.md)
- **Troubleshooting**: [docs/troubleshooting.md](docs/troubleshooting.md)

---

**Sistema Meteorológico Agrícola Quillota - Versión 2.0**

*Instalación completada exitosamente* ✅
