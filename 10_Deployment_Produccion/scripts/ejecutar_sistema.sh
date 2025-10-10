#!/bin/bash

# 🚀 EJECUTOR MAESTRO DEL SISTEMA METGO 3D - SCRIPT BASH
# Sistema Meteorológico Agrícola Quillota - Versión Operativa

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con colores
print_header() {
    echo -e "${BLUE}🚀 EJECUTOR MAESTRO DEL SISTEMA METGO 3D${NC}"
    echo -e "${BLUE}Sistema Meteorológico Agrícola Quillota - Versión Operativa${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Función para mostrar ayuda
show_help() {
    echo -e "${CYAN}USO:${NC}"
    echo "    ./ejecutar_sistema.sh [MODO]"
    echo ""
    echo -e "${CYAN}MODOS DISPONIBLES:${NC}"
    echo "    completo     - Ejecutar todos los notebooks (por defecto)"
    echo "    rapido      - Ejecutar solo notebooks esenciales"
    echo "    analisis    - Ejecutar solo notebooks de análisis"
    echo "    testing     - Ejecutar solo notebooks de testing"
    echo "    deployment  - Ejecutar solo notebooks de deployment"
    echo ""
    echo -e "${CYAN}EJEMPLOS:${NC}"
    echo "    ./ejecutar_sistema.sh"
    echo "    ./ejecutar_sistema.sh completo"
    echo "    ./ejecutar_sistema.sh rapido"
    echo "    ./ejecutar_sistema.sh testing"
    echo ""
    echo -e "${CYAN}CARACTERÍSTICAS:${NC}"
    echo "    ✅ Ejecución automática de todos los notebooks"
    echo "    ✅ Manejo robusto de errores"
    echo "    ✅ Logging detallado"
    echo "    ✅ Reportes de ejecución"
    echo "    ✅ Verificación de dependencias"
    echo "    ✅ Múltiples modos de ejecución"
}

# Función para verificar dependencias
check_dependencies() {
    print_message "Verificando dependencias del sistema..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 no está instalado"
        return 1
    fi
    
    # Verificar Jupyter
    if ! command -v jupyter &> /dev/null; then
        print_error "Jupyter Notebook no está instalado"
        print_message "Instalar con: pip install jupyter"
        return 1
    fi
    
    # Verificar nbconvert
    if ! python3 -c "import nbconvert" 2>/dev/null; then
        print_error "nbconvert no está instalado"
        print_message "Instalar con: pip install nbconvert"
        return 1
    fi
    
    print_success "Todas las dependencias están disponibles"
    return 0
}

# Función para crear directorios necesarios
create_directories() {
    print_message "Creando directorios necesarios..."
    
    directories=("logs" "data" "reportes_revision" "test_results" "tests" "app" "static" "templates" "backups")
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_message "Directorio creado: $dir"
        else
            print_message "Directorio ya existe: $dir"
        fi
    done
}

# Función para ejecutar notebook individual
execute_notebook() {
    local notebook="$1"
    local timeout="${2:-300}"
    
    print_message "Ejecutando notebook: $notebook"
    
    if [ ! -f "$notebook" ]; then
        print_error "Notebook no encontrado: $notebook"
        return 1
    fi
    
    # Ejecutar notebook con timeout
    timeout "$timeout" jupyter nbconvert \
        --to notebook \
        --execute \
        --inplace \
        --ExecutePreprocessor.timeout="$timeout" \
        "$notebook" 2>&1
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "Notebook ejecutado exitosamente: $notebook"
        return 0
    elif [ $exit_code -eq 124 ]; then
        print_error "Timeout ejecutando notebook: $notebook"
        return 1
    else
        print_error "Error ejecutando notebook: $notebook"
        return 1
    fi
}

# Función para ejecutar sistema completo
execute_system() {
    local mode="${1:-completo}"
    
    print_header
    print_message "Iniciando ejecución del sistema METGO 3D"
    print_message "Modo: $mode"
    print_message "Fecha: $(date)"
    
    # Verificar dependencias
    if ! check_dependencies; then
        print_error "No se pueden ejecutar los notebooks sin las dependencias necesarias"
        exit 1
    fi
    
    # Crear directorios
    create_directories
    
    # Determinar notebooks a ejecutar según el modo
    case "$mode" in
        "completo")
            notebooks=(
                "01_Configuracion_e_imports.ipynb"
                "02_Carga_y_Procesamiento_Datos.ipynb"
                "03_Analisis_Meteorologico.ipynb"
                "04_Visualizaciones.ipynb"
                "05_Modelos_ML.ipynb"
                "06_Dashboard_Interactivo.ipynb"
                "07_Reportes_Automaticos.ipynb"
                "08_APIs_Externas.ipynb"
                "09_Testing_Validacion.ipynb"
                "10_Deployment_Produccion.ipynb"
            )
            ;;
        "rapido")
            notebooks=(
                "01_Configuracion_e_imports.ipynb"
                "02_Carga_y_Procesamiento_Datos.ipynb"
                "03_Analisis_Meteorologico.ipynb"
                "04_Visualizaciones.ipynb"
                "05_Modelos_ML.ipynb"
            )
            ;;
        "analisis")
            notebooks=(
                "01_Configuracion_e_imports.ipynb"
                "02_Carga_y_Procesamiento_Datos.ipynb"
                "03_Analisis_Meteorologico.ipynb"
                "04_Visualizaciones.ipynb"
            )
            ;;
        "testing")
            notebooks=("09_Testing_Validacion.ipynb")
            ;;
        "deployment")
            notebooks=("10_Deployment_Produccion.ipynb")
            ;;
        *)
            print_error "Modo no válido: $mode"
            show_help
            exit 1
            ;;
    esac
    
    # Ejecutar notebooks
    local start_time=$(date +%s)
    local successful=0
    local failed=0
    
    for i in "${!notebooks[@]}"; do
        local notebook="${notebooks[$i]}"
        local notebook_num=$((i + 1))
        local total_notebooks=${#notebooks[@]}
        
        echo ""
        print_message "Ejecutando notebook $notebook_num/$total_notebooks: $notebook"
        echo "--------------------------------------------------"
        
        if execute_notebook "$notebook"; then
            ((successful++))
        else
            ((failed++))
            if [ "$mode" != "completo" ]; then
                print_error "Deteniendo ejecución por error"
                break
            else
                print_warning "Continuando con el siguiente notebook..."
            fi
        fi
    done
    
    local end_time=$(date +%s)
    local total_time=$((end_time - start_time))
    
    # Reporte final
    echo ""
    echo "============================================================"
    print_message "REPORTE FINAL DE EJECUCIÓN"
    echo "============================================================"
    print_message "Fecha de ejecución: $(date)"
    print_message "Tiempo total: ${total_time} segundos"
    print_message "Notebooks ejecutados: $((successful + failed))"
    print_success "Exitosos: $successful"
    if [ $failed -gt 0 ]; then
        print_error "Con errores: $failed"
    fi
    
    local success_rate=$((successful * 100 / (successful + failed)))
    print_message "Tasa de éxito: ${success_rate}%"
    
    if [ $failed -eq 0 ]; then
        echo ""
        print_success "🎉 ¡SISTEMA METGO 3D EJECUTADO EXITOSAMENTE!"
        print_success "🌾 El sistema está listo para uso agrícola en Quillota"
        exit 0
    else
        echo ""
        print_warning "⚠️ Sistema ejecutado con $failed errores"
        print_message "🔧 Revisar logs para detalles de errores"
        exit 1
    fi
}

# Función principal
main() {
    # Verificar argumentos
    if [ $# -gt 0 ]; then
        case "$1" in
            "-h"|"--help"|"help")
                show_help
                exit 0
                ;;
            *)
                execute_system "$1"
                ;;
        esac
    else
        execute_system "completo"
    fi
}

# Ejecutar función principal
main "$@"
