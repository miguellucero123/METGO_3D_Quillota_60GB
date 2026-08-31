# 🌾 METGO 3D - Script de Deployment PowerShell
# Sistema Meteorológico Agrícola Quillota - Despliegue Automático

param(
    [Parameter(Position=0)]
    [ValidateSet("deploy", "update", "cleanup", "tests", "build", "health", "info", "help")]
    [string]$Action = "deploy",
    
    [switch]$Help
)

# Función para imprimir mensajes
function Write-Message {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ⚠️ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ❌ $Message" -ForegroundColor Red
}

# Función para verificar si un comando existe
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Función para verificar dependencias
function Test-Dependencies {
    Write-Message "Verificando dependencias..."
    
    $missingDeps = @()
    
    if (-not (Test-Command "docker")) {
        $missingDeps += "docker"
    }
    
    if (-not (Test-Command "docker-compose")) {
        $missingDeps += "docker-compose"
    }
    
    if (-not (Test-Command "git")) {
        $missingDeps += "git"
    }
    
    if ($missingDeps.Count -gt 0) {
        Write-Error "Dependencias faltantes: $($missingDeps -join ', ')"
        Write-Message "Por favor instala las dependencias faltantes y vuelve a intentar."
        exit 1
    }
    
    Write-Success "Todas las dependencias están instaladas"
}

# Función para verificar Docker
function Test-Docker {
    Write-Message "Verificando Docker..."
    
    try {
        docker info | Out-Null
        Write-Success "Docker está ejecutándose"
    }
    catch {
        Write-Error "Docker no está ejecutándose"
        Write-Message "Por favor inicia Docker y vuelve a intentar."
        exit 1
    }
}

# Función para crear directorios necesarios
function New-Directories {
    Write-Message "Creando directorios necesarios..."
    
    $dirs = @(
        "data",
        "logs",
        "config",
        "reportes",
        "graficos",
        "dashboard_html",
        "temp",
        "resultados",
        "backups",
        "config\nginx",
        "config\postgres",
        "config\ssl"
    )
    
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Message "Directorio creado: $dir"
        }
    }
    
    Write-Success "Directorios creados correctamente"
}

# Función para configurar permisos
function Set-Permissions {
    Write-Message "Configurando permisos..."
    
    # Dar permisos de ejecución a scripts
    Get-ChildItem -Path "scripts\*.ps1" -ErrorAction SilentlyContinue | ForEach-Object {
        Unblock-File $_.FullName
    }
    
    # Configurar permisos de directorios
    $dirs = @("data", "logs", "config", "reportes", "graficos", "dashboard_html", "temp", "resultados", "backups")
    foreach ($dir in $dirs) {
        if (Test-Path $dir) {
            icacls $dir /grant Everyone:F /T | Out-Null
        }
    }
    
    Write-Success "Permisos configurados correctamente"
}

# Función para generar archivos de configuración
function New-ConfigFiles {
    Write-Message "Generando archivos de configuración..."
    
    # Generar archivo .env si no existe
    if (-not (Test-Path ".env")) {
        $envContent = @"
# 🌾 METGO 3D - Variables de Entorno
# Sistema Meteorológico Agrícola Quillota

# Entorno
METGO_ENV=production
METGO_DEBUG=False
METGO_LOG_LEVEL=INFO

# Base de datos — rellenar en servidor / Render
POSTGRES_DB=metgo3d
POSTGRES_USER=metgo3d
POSTGRES_PASSWORD=CHANGE_ME_STRONG_PASSWORD
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# APIs
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=False

# Dashboard
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8050
DASHBOARD_DEBUG=False

# Seguridad — generar: python -c "import secrets; print(secrets.token_urlsafe(48))"
SECRET_KEY=CHANGE_ME_GENERATE_SECRET
JWT_SECRET_KEY=CHANGE_ME_GENERATE_JWT_SECRET
METGO_JWT_SECRET=CHANGE_ME_GENERATE_JWT_SECRET
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Monitoreo
MONITORING_ENABLED=True
MONITORING_INTERVAL=60

# Respaldos
BACKUP_ENABLED=True
BACKUP_SCHEDULE=0 3 * * *
BACKUP_RETENTION_DAYS=30

# Performance
CACHE_ENABLED=True
CACHE_TTL=3600
PARALLEL_PROCESSING=True
MAX_WORKERS=4
"@
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Message "Archivo .env creado (placeholders — rellenar antes de producción)"
    }
    
    # Verificar archivos de configuración
    if (-not (Test-Path "config\nginx\nginx.conf")) {
        Write-Warning "Archivo nginx.conf no encontrado, usando configuración por defecto"
    }
    
    if (-not (Test-Path "config\postgres\init.sql")) {
        Write-Warning "Archivo init.sql no encontrado, usando configuración por defecto"
    }
    
    Write-Success "Archivos de configuración generados"
}

# Función para construir imágenes Docker
function Build-Images {
    Write-Message "Construyendo imágenes Docker..."
    
    # Construir imagen principal
    try {
        docker build -t metgo3d:latest .
        Write-Success "Imagen principal construida correctamente"
    }
    catch {
        Write-Error "Error construyendo imagen principal"
        exit 1
    }
    
    # Construir imagen de monitoreo
    try {
        docker build -t metgo3d:monitoring .
        Write-Success "Imagen de monitoreo construida correctamente"
    }
    catch {
        Write-Error "Error construyendo imagen de monitoreo"
        exit 1
    }
    
    # Construir imagen de respaldos
    try {
        docker build -t metgo3d:backup .
        Write-Success "Imagen de respaldos construida correctamente"
    }
    catch {
        Write-Error "Error construyendo imagen de respaldos"
        exit 1
    }
    
    # Construir imagen de tests
    try {
        docker build -t metgo3d:tests .
        Write-Success "Imagen de tests construida correctamente"
    }
    catch {
        Write-Error "Error construyendo imagen de tests"
        exit 1
    }
}

# Función para ejecutar tests
function Invoke-Tests {
    Write-Message "Ejecutando tests..."
    
    try {
        # Ejecutar tests en contenedor
        docker run --rm `
            --network metgo3d_metgo3d_network `
            -v "${PWD}\data:/app/data" `
            -v "${PWD}\logs:/app/logs" `
            -v "${PWD}\config:/app/config" `
            -v "${PWD}\tests:/app/tests" `
            metgo3d:tests
        
        Write-Success "Tests ejecutados correctamente"
    }
    catch {
        Write-Error "Algunos tests fallaron"
        Write-Warning "Continuando con el deployment..."
    }
}

# Función para desplegar servicios
function Deploy-Services {
    Write-Message "Desplegando servicios..."
    
    try {
        # Detener servicios existentes
        docker-compose down 2>$null
        
        # Iniciar servicios
        docker-compose up -d
        
        Write-Success "Servicios desplegados correctamente"
    }
    catch {
        Write-Error "Error desplegando servicios"
        exit 1
    }
    
    # Esperar a que los servicios estén listos
    Write-Message "Esperando a que los servicios estén listos..."
    Start-Sleep -Seconds 30
    
    # Verificar estado de los servicios
    Test-ServicesHealth
}

# Función para verificar salud de los servicios
function Test-ServicesHealth {
    Write-Message "Verificando salud de los servicios..."
    
    $services = @(
        "metgo3d_principal",
        "metgo3d_postgres",
        "metgo3d_redis",
        "metgo3d_nginx",
        "metgo3d_monitoring",
        "metgo3d_backup"
    )
    
    $healthyServices = 0
    $totalServices = $services.Count
    
    foreach ($service in $services) {
        $running = docker ps --filter "name=$service" --filter "status=running" | Select-String $service
        if ($running) {
            Write-Success "Servicio $service está ejecutándose"
            $healthyServices++
        }
        else {
            Write-Error "Servicio $service no está ejecutándose"
        }
    }
    
    if ($healthyServices -eq $totalServices) {
        Write-Success "Todos los servicios están ejecutándose correctamente"
    }
    else {
        Write-Warning "$healthyServices de $totalServices servicios están ejecutándose"
    }
}

# Función para mostrar información del deployment
function Show-DeploymentInfo {
    Write-Message "Información del deployment:"
    
    Write-Host ""
    Write-Host "🌾 METGO 3D - Sistema Meteorológico Agrícola Quillota" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📊 Servicios desplegados:" -ForegroundColor Yellow
    Write-Host "  - Sistema principal: http://localhost:5000"
    Write-Host "  - Dashboard: http://localhost:8050"
    Write-Host "  - API meteorología: http://localhost:5001"
    Write-Host "  - API agrícola: http://localhost:5002"
    Write-Host "  - API alertas: http://localhost:5003"
    Write-Host "  - API IoT: http://localhost:5004"
    Write-Host "  - API ML: http://localhost:5005"
    Write-Host "  - API visualización: http://localhost:5006"
    Write-Host "  - API reportes: http://localhost:5007"
    Write-Host "  - API configuración: http://localhost:5008"
    Write-Host "  - API monitoreo: http://localhost:5009"
    Write-Host ""
    Write-Host "🗄️ Base de datos:" -ForegroundColor Yellow
    Write-Host "  - PostgreSQL: localhost:5432"
    Write-Host "  - Redis: localhost:6379"
    Write-Host ""
    Write-Host "🌐 Proxy reverso:" -ForegroundColor Yellow
    Write-Host "  - HTTP: http://localhost"
    Write-Host "  - HTTPS: https://localhost (si está configurado)"
    Write-Host ""
    Write-Host "📁 Directorios:" -ForegroundColor Yellow
    Write-Host "  - Datos: .\data"
    Write-Host "  - Logs: .\logs"
    Write-Host "  - Configuración: .\config"
    Write-Host "  - Reportes: .\reportes"
    Write-Host "  - Gráficos: .\graficos"
    Write-Host "  - Respaldos: .\backups"
    Write-Host ""
    Write-Host "🔧 Comandos útiles:" -ForegroundColor Yellow
    Write-Host "  - Ver logs: docker-compose logs -f"
    Write-Host "  - Reiniciar: docker-compose restart"
    Write-Host "  - Detener: docker-compose down"
    Write-Host "  - Actualizar: .\scripts\deploy.ps1 -Action update"
    Write-Host ""
    Write-Host "📋 Monitoreo:" -ForegroundColor Yellow
    Write-Host "  - Estado de servicios: docker-compose ps"
    Write-Host "  - Uso de recursos: docker stats"
    Write-Host "  - Logs del sistema: Get-Content logs\metgo3d.log -Wait"
    Write-Host ""
}

# Función para actualizar deployment
function Update-Deployment {
    Write-Message "Actualizando deployment..."
    
    try {
        # Obtener cambios del repositorio
        git pull origin main
        
        # Reconstruir imágenes
        Build-Images
        
        # Reiniciar servicios
        docker-compose restart
        
        Write-Success "Deployment actualizado correctamente"
    }
    catch {
        Write-Error "Error actualizando deployment"
        exit 1
    }
}

# Función para limpiar deployment
function Remove-Deployment {
    Write-Message "Limpiando deployment..."
    
    try {
        # Detener servicios
        docker-compose down
        
        # Eliminar imágenes
        docker rmi metgo3d:latest metgo3d:monitoring metgo3d:backup metgo3d:tests 2>$null
        
        # Limpiar volúmenes
        docker volume prune -f
        
        # Limpiar contenedores
        docker container prune -f
        
        Write-Success "Deployment limpiado correctamente"
    }
    catch {
        Write-Error "Error limpiando deployment"
        exit 1
    }
}

# Función para mostrar ayuda
function Show-Help {
    Write-Host "🌾 METGO 3D - Script de Deployment PowerShell" -ForegroundColor Cyan
    Write-Host "Sistema Meteorológico Agrícola Quillota" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Uso: .\scripts\deploy.ps1 [ACCIÓN]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Acciones:" -ForegroundColor Yellow
    Write-Host "  deploy          Deployment completo (por defecto)"
    Write-Host "  update          Actualizar deployment existente"
    Write-Host "  cleanup         Limpiar deployment"
    Write-Host "  tests           Ejecutar solo tests"
    Write-Host "  build           Solo construir imágenes"
    Write-Host "  health          Verificar salud de servicios"
    Write-Host "  info            Mostrar información del deployment"
    Write-Host "  help            Mostrar esta ayuda"
    Write-Host ""
    Write-Host "Ejemplos:" -ForegroundColor Yellow
    Write-Host "  .\scripts\deploy.ps1                    # Deployment completo"
    Write-Host "  .\scripts\deploy.ps1 -Action update     # Actualizar deployment"
    Write-Host "  .\scripts\deploy.ps1 -Action tests      # Ejecutar tests"
    Write-Host "  .\scripts\deploy.ps1 -Action cleanup    # Limpiar todo"
    Write-Host ""
}

# Función principal
function Main {
    if ($Help) {
        Show-Help
        return
    }
    
    switch ($Action) {
        "deploy" {
            Write-Message "Iniciando deployment completo..."
            Test-Dependencies
            Test-Docker
            New-Directories
            Set-Permissions
            New-ConfigFiles
            Build-Images
            Invoke-Tests
            Deploy-Services
            Show-DeploymentInfo
        }
        "update" {
            Write-Message "Actualizando deployment..."
            Test-Dependencies
            Test-Docker
            Update-Deployment
            Show-DeploymentInfo
        }
        "cleanup" {
            Write-Message "Limpiando deployment..."
            Remove-Deployment
        }
        "tests" {
            Write-Message "Ejecutando tests..."
            Test-Dependencies
            Test-Docker
            Build-Images
            Invoke-Tests
        }
        "build" {
            Write-Message "Construyendo imágenes..."
            Test-Dependencies
            Test-Docker
            Build-Images
        }
        "health" {
            Write-Message "Verificando salud de servicios..."
            Test-ServicesHealth
        }
        "info" {
            Show-DeploymentInfo
        }
        "help" {
            Show-Help
        }
        default {
            Write-Error "Acción desconocida: $Action"
            Show-Help
            exit 1
        }
    }
    
    Write-Success "Operación completada exitosamente"
}

# Ejecutar función principal
Main
