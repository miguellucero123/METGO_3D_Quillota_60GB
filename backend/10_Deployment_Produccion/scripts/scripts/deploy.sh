#!/bin/bash

# 🌾 METGO 3D - Script de Deployment
# Sistema Meteorológico Agrícola Quillota - Despliegue Automático

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_message() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Función para verificar dependencias
check_dependencies() {
    print_message "Verificando dependencias..."
    
    local missing_deps=()
    
    if ! command_exists docker; then
        missing_deps+=("docker")
    fi
    
    if ! command_exists docker-compose; then
        missing_deps+=("docker-compose")
    fi
    
    if ! command_exists git; then
        missing_deps+=("git")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Dependencias faltantes: ${missing_deps[*]}"
        print_message "Por favor instala las dependencias faltantes y vuelve a intentar."
        exit 1
    fi
    
    print_success "Todas las dependencias están instaladas"
}

# Función para verificar Docker
check_docker() {
    print_message "Verificando Docker..."
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker no está ejecutándose"
        print_message "Por favor inicia Docker y vuelve a intentar."
        exit 1
    fi
    
    print_success "Docker está ejecutándose"
}

# Función para crear directorios necesarios
create_directories() {
    print_message "Creando directorios necesarios..."
    
    local dirs=(
        "data"
        "logs"
        "config"
        "reportes"
        "graficos"
        "dashboard_html"
        "temp"
        "resultados"
        "backups"
        "config/nginx"
        "config/postgres"
        "config/ssl"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_message "Directorio creado: $dir"
        fi
    done
    
    print_success "Directorios creados correctamente"
}

# Función para configurar permisos
setup_permissions() {
    print_message "Configurando permisos..."
    
    # Dar permisos de ejecución a scripts
    chmod +x scripts/*.sh 2>/dev/null || true
    chmod +x *.py 2>/dev/null || true
    
    # Configurar permisos de directorios
    chmod 755 data logs config reportes graficos dashboard_html temp resultados backups
    
    print_success "Permisos configurados correctamente"
}

# Función para generar archivos de configuración
generate_config_files() {
    print_message "Generando archivos de configuración..."
    
    # Generar archivo .env si no existe
    if [ ! -f .env ]; then
        cat > .env << EOF
# 🌾 METGO 3D - Variables de Entorno
# Sistema Meteorológico Agrícola Quillota

# Entorno
METGO_ENV=production
METGO_DEBUG=False
METGO_LOG_LEVEL=INFO

# Base de datos
POSTGRES_DB=metgo3d
POSTGRES_USER=metgo3d
POSTGRES_PASSWORD=metgo3d_2024_secure
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

# Seguridad
SECRET_KEY=metgo3d_secret_key_2024_secure
JWT_SECRET_KEY=metgo3d_jwt_secret_2024_secure
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
EOF
        print_message "Archivo .env creado"
    fi
    
    # Generar archivo de configuración de Nginx si no existe
    if [ ! -f config/nginx/nginx.conf ]; then
        print_warning "Archivo nginx.conf no encontrado, usando configuración por defecto"
    fi
    
    # Generar archivo de inicialización de PostgreSQL si no existe
    if [ ! -f config/postgres/init.sql ]; then
        print_warning "Archivo init.sql no encontrado, usando configuración por defecto"
    fi
    
    print_success "Archivos de configuración generados"
}

# Función para construir imágenes Docker
build_images() {
    print_message "Construyendo imágenes Docker..."
    
    # Construir imagen principal
    docker build -t metgo3d:latest .
    
    if [ $? -eq 0 ]; then
        print_success "Imagen principal construida correctamente"
    else
        print_error "Error construyendo imagen principal"
        exit 1
    fi
    
    # Construir imagen de monitoreo
    docker build -t metgo3d:monitoring .
    
    if [ $? -eq 0 ]; then
        print_success "Imagen de monitoreo construida correctamente"
    else
        print_error "Error construyendo imagen de monitoreo"
        exit 1
    fi
    
    # Construir imagen de respaldos
    docker build -t metgo3d:backup .
    
    if [ $? -eq 0 ]; then
        print_success "Imagen de respaldos construida correctamente"
    else
        print_error "Error construyendo imagen de respaldos"
        exit 1
    fi
    
    # Construir imagen de tests
    docker build -t metgo3d:tests .
    
    if [ $? -eq 0 ]; then
        print_success "Imagen de tests construida correctamente"
    else
        print_error "Error construyendo imagen de tests"
        exit 1
    fi
}

# Función para ejecutar tests
run_tests() {
    print_message "Ejecutando tests..."
    
    # Ejecutar tests en contenedor
    docker run --rm \
        --network metgo3d_metgo3d_network \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/config:/app/config" \
        -v "$(pwd)/tests:/app/tests" \
        metgo3d:tests
    
    if [ $? -eq 0 ]; then
        print_success "Tests ejecutados correctamente"
    else
        print_error "Algunos tests fallaron"
        print_warning "Continuando con el deployment..."
    fi
}

# Función para desplegar servicios
deploy_services() {
    print_message "Desplegando servicios..."
    
    # Detener servicios existentes
    docker-compose down 2>/dev/null || true
    
    # Iniciar servicios
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        print_success "Servicios desplegados correctamente"
    else
        print_error "Error desplegando servicios"
        exit 1
    fi
    
    # Esperar a que los servicios estén listos
    print_message "Esperando a que los servicios estén listos..."
    sleep 30
    
    # Verificar estado de los servicios
    check_services_health
}

# Función para verificar salud de los servicios
check_services_health() {
    print_message "Verificando salud de los servicios..."
    
    local services=(
        "metgo3d_principal"
        "metgo3d_postgres"
        "metgo3d_redis"
        "metgo3d_nginx"
        "metgo3d_monitoring"
        "metgo3d_backup"
    )
    
    local healthy_services=0
    local total_services=${#services[@]}
    
    for service in "${services[@]}"; do
        if docker ps --filter "name=$service" --filter "status=running" | grep -q "$service"; then
            print_success "Servicio $service está ejecutándose"
            ((healthy_services++))
        else
            print_error "Servicio $service no está ejecutándose"
        fi
    done
    
    if [ $healthy_services -eq $total_services ]; then
        print_success "Todos los servicios están ejecutándose correctamente"
    else
        print_warning "$healthy_services de $total_services servicios están ejecutándose"
    fi
}

# Función para mostrar información del deployment
show_deployment_info() {
    print_message "Información del deployment:"
    
    echo ""
    echo "🌾 METGO 3D - Sistema Meteorológico Agrícola Quillota"
    echo "=================================================="
    echo ""
    echo "📊 Servicios desplegados:"
    echo "  - Sistema principal: http://localhost:5000"
    echo "  - Dashboard: http://localhost:8050"
    echo "  - API meteorología: http://localhost:5001"
    echo "  - API agrícola: http://localhost:5002"
    echo "  - API alertas: http://localhost:5003"
    echo "  - API IoT: http://localhost:5004"
    echo "  - API ML: http://localhost:5005"
    echo "  - API visualización: http://localhost:5006"
    echo "  - API reportes: http://localhost:5007"
    echo "  - API configuración: http://localhost:5008"
    echo "  - API monitoreo: http://localhost:5009"
    echo ""
    echo "🗄️ Base de datos:"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis: localhost:6379"
    echo ""
    echo "🌐 Proxy reverso:"
    echo "  - HTTP: http://localhost"
    echo "  - HTTPS: https://localhost (si está configurado)"
    echo ""
    echo "📁 Directorios:"
    echo "  - Datos: ./data"
    echo "  - Logs: ./logs"
    echo "  - Configuración: ./config"
    echo "  - Reportes: ./reportes"
    echo "  - Gráficos: ./graficos"
    echo "  - Respaldos: ./backups"
    echo ""
    echo "🔧 Comandos útiles:"
    echo "  - Ver logs: docker-compose logs -f"
    echo "  - Reiniciar: docker-compose restart"
    echo "  - Detener: docker-compose down"
    echo "  - Actualizar: ./scripts/deploy.sh --update"
    echo ""
    echo "📋 Monitoreo:"
    echo "  - Estado de servicios: docker-compose ps"
    echo "  - Uso de recursos: docker stats"
    echo "  - Logs del sistema: tail -f logs/metgo3d.log"
    echo ""
}

# Función para actualizar deployment
update_deployment() {
    print_message "Actualizando deployment..."
    
    # Obtener cambios del repositorio
    git pull origin main
    
    # Reconstruir imágenes
    build_images
    
    # Reiniciar servicios
    docker-compose restart
    
    print_success "Deployment actualizado correctamente"
}

# Función para limpiar deployment
cleanup_deployment() {
    print_message "Limpiando deployment..."
    
    # Detener servicios
    docker-compose down
    
    # Eliminar imágenes
    docker rmi metgo3d:latest metgo3d:monitoring metgo3d:backup metgo3d:tests 2>/dev/null || true
    
    # Limpiar volúmenes
    docker volume prune -f
    
    # Limpiar contenedores
    docker container prune -f
    
    print_success "Deployment limpiado correctamente"
}

# Función para mostrar ayuda
show_help() {
    echo "🌾 METGO 3D - Script de Deployment"
    echo "Sistema Meteorológico Agrícola Quillota"
    echo ""
    echo "Uso: $0 [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  --help, -h          Mostrar esta ayuda"
    echo "  --update, -u        Actualizar deployment existente"
    echo "  --cleanup, -c       Limpiar deployment"
    echo "  --tests, -t         Ejecutar solo tests"
    echo "  --build, -b         Solo construir imágenes"
    echo "  --deploy, -d        Solo desplegar servicios"
    echo "  --health, -H        Verificar salud de servicios"
    echo "  --info, -i          Mostrar información del deployment"
    echo ""
    echo "Ejemplos:"
    echo "  $0                  # Deployment completo"
    echo "  $0 --update         # Actualizar deployment"
    echo "  $0 --tests          # Ejecutar tests"
    echo "  $0 --cleanup        # Limpiar todo"
    echo ""
}

# Función principal
main() {
    local action="deploy"
    
    # Procesar argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --update|-u)
                action="update"
                shift
                ;;
            --cleanup|-c)
                action="cleanup"
                shift
                ;;
            --tests|-t)
                action="tests"
                shift
                ;;
            --build|-b)
                action="build"
                shift
                ;;
            --deploy|-d)
                action="deploy"
                shift
                ;;
            --health|-H)
                action="health"
                shift
                ;;
            --info|-i)
                action="info"
                shift
                ;;
            *)
                print_error "Opción desconocida: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Ejecutar acción correspondiente
    case $action in
        "deploy")
            print_message "Iniciando deployment completo..."
            check_dependencies
            check_docker
            create_directories
            setup_permissions
            generate_config_files
            build_images
            run_tests
            deploy_services
            show_deployment_info
            ;;
        "update")
            print_message "Actualizando deployment..."
            check_dependencies
            check_docker
            update_deployment
            show_deployment_info
            ;;
        "cleanup")
            print_message "Limpiando deployment..."
            cleanup_deployment
            ;;
        "tests")
            print_message "Ejecutando tests..."
            check_dependencies
            check_docker
            build_images
            run_tests
            ;;
        "build")
            print_message "Construyendo imágenes..."
            check_dependencies
            check_docker
            build_images
            ;;
        "deploy")
            print_message "Desplegando servicios..."
            check_dependencies
            check_docker
            deploy_services
            ;;
        "health")
            print_message "Verificando salud de servicios..."
            check_services_health
            ;;
        "info")
            show_deployment_info
            ;;
        *)
            print_error "Acción desconocida: $action"
            exit 1
            ;;
    esac
    
    print_success "Operación completada exitosamente"
}

# Ejecutar función principal
main "$@"
