#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 INSTALADOR Y CONFIGURADOR METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Este script instala y configura automáticamente el sistema METGO 3D.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Imprimir encabezado del instalador"""
    print("🌾 INSTALADOR Y CONFIGURADOR METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0")
    print("=" * 70)

def print_step(step, message):
    """Imprimir paso del proceso de instalación"""
    print(f"\n[{step}] {message}")
    print("-" * 50)

def print_success(message):
    """Imprimir mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message):
    """Imprimir mensaje de error"""
    print(f"❌ {message}")

def print_warning(message):
    """Imprimir mensaje de advertencia"""
    print(f"⚠️ {message}")

def print_info(message):
    """Imprimir mensaje informativo"""
    print(f"ℹ️ {message}")

def verificar_python():
    """Verificar versión de Python"""
    try:
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print_error("Se requiere Python 3.8 o superior")
            return False
        
        print_success(f"Python {version.major}.{version.minor}.{version.micro} detectado")
        return True
    except Exception as e:
        print_error(f"Error verificando Python: {e}")
        return False

def instalar_dependencias():
    """Instalar dependencias del sistema"""
    try:
        print_info("Instalando dependencias de Python...")
        
        # Lista de dependencias
        dependencias = [
            "jupyter",
            "nbconvert",
            "pandas",
            "numpy",
            "matplotlib",
            "seaborn",
            "plotly",
            "scikit-learn",
            "requests",
            "pyyaml",
            "streamlit",
            "openpyxl",
            "xlsxwriter"
        ]
        
        # Instalar cada dependencia
        for dep in dependencias:
            try:
                print_info(f"Instalando {dep}...")
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                             check=True, capture_output=True)
                print_success(f"{dep} instalado exitosamente")
            except subprocess.CalledProcessError as e:
                print_warning(f"Error instalando {dep}: {e}")
                continue
        
        print_success("Dependencias instaladas exitosamente")
        return True
        
    except Exception as e:
        print_error(f"Error instalando dependencias: {e}")
        return False

def crear_estructura_directorios():
    """Crear estructura de directorios del sistema"""
    try:
        print_info("Creando estructura de directorios...")
        
        directorios = [
            "logs",
            "data",
            "backups",
            "reportes",
            "modelos",
            "config",
            "src",
            "tests",
            "docs",
            "static",
            "templates"
        ]
        
        for directorio in directorios:
            Path(directorio).mkdir(exist_ok=True)
            print_success(f"Directorio {directorio}/ creado")
        
        print_success("Estructura de directorios creada exitosamente")
        return True
        
    except Exception as e:
        print_error(f"Error creando directorios: {e}")
        return False

def crear_archivo_configuracion():
    """Crear archivo de configuración del sistema"""
    try:
        print_info("Creando archivo de configuración...")
        
        config_content = """# Configuración del Sistema METGO 3D
# Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

# Configuración de Quillota
QUILLOTA:
  nombre: "Quillota"
  region: "Valparaíso"
  pais: "Chile"
  coordenadas:
    latitud: -32.8833
    longitud: -71.2500
  elevacion: 462  # metros sobre el nivel del mar

# Configuración del sistema
SISTEMA:
  version: "2.0.0"
  entorno: "desarrollo"
  debug: true
  logging_level: "INFO"
  max_dias_datos: 365
  timeout_api: 30
  retry_attempts: 3

# Configuración de APIs
APIS:
  openmeteo:
    url: "https://api.open-meteo.com/v1/forecast"
    timeout: 30
    retry_attempts: 3
  backup:
    habilitado: true
    datos_sinteticos: true

# Configuración de alertas
ALERTAS:
  temperatura_minima: -2.0
  temperatura_maxima: 35.0
  precipitacion_minima: 0.1
  humedad_minima: 20.0
  viento_maximo: 50.0

# Configuración de ML
ML:
  random_state: 42
  cv_folds: 5
  test_size: 0.2
  n_jobs: -1

# Configuración de visualización
VISUALIZACION:
  figsize: [14, 8]
  dpi: 100
  style: "default"
  colormap: "viridis"
"""
        
        config_file = Path("config/config.yaml")
        config_file.write_text(config_content, encoding='utf-8')
        print_success("Archivo de configuración creado: config/config.yaml")
        return True
        
    except Exception as e:
        print_error(f"Error creando configuración: {e}")
        return False

def crear_archivo_requirements():
    """Crear archivo requirements.txt"""
    try:
        print_info("Creando archivo requirements.txt...")
        
        requirements_content = """# Dependencias del Sistema METGO 3D
# Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

# Core dependencies
jupyter>=1.0.0
nbconvert>=6.0.0
pandas>=1.5.0
numpy>=1.21.0
matplotlib>=3.5.0
seaborn>=0.11.0
plotly>=5.0.0

# Machine Learning
scikit-learn>=1.1.0

# APIs y conectividad
requests>=2.28.0
urllib3>=1.26.0

# Configuración
pyyaml>=6.0

# Dashboard
streamlit>=1.20.0

# Procesamiento de datos
openpyxl>=3.0.0
xlsxwriter>=3.0.0

# Utilidades
python-dateutil>=2.8.0
pytz>=2022.1
"""
        
        requirements_file = Path("requirements.txt")
        requirements_file.write_text(requirements_content, encoding='utf-8')
        print_success("Archivo requirements.txt creado")
        return True
        
    except Exception as e:
        print_error(f"Error creando requirements.txt: {e}")
        return False

def crear_script_ejecucion():
    """Crear script de ejecución del sistema"""
    try:
        print_info("Creando script de ejecución...")
        
        if platform.system() == "Windows":
            script_content = """@echo off
echo 🌾 METGO 3D - Sistema Meteorológico Agrícola Quillota
echo =====================================================
echo.
echo Iniciando sistema...
python ejecutar_notebooks_maestro.py
pause
"""
            script_file = Path("ejecutar_sistema.bat")
        else:
            script_content = """#!/bin/bash
echo "🌾 METGO 3D - Sistema Meteorológico Agrícola Quillota"
echo "====================================================="
echo ""
echo "Iniciando sistema..."
python3 ejecutar_notebooks_maestro.py
"""
            script_file = Path("ejecutar_sistema.sh")
        
        script_file.write_text(script_content, encoding='utf-8')
        
        if platform.system() != "Windows":
            os.chmod(script_file, 0o755)
        
        print_success(f"Script de ejecución creado: {script_file}")
        return True
        
    except Exception as e:
        print_error(f"Error creando script de ejecución: {e}")
        return False

def verificar_instalacion():
    """Verificar que la instalación sea exitosa"""
    try:
        print_info("Verificando instalación...")
        
        # Verificar archivos críticos
        archivos_criticos = [
            "config/config.yaml",
            "requirements.txt",
            "ejecutar_notebooks_maestro.py"
        ]
        
        for archivo in archivos_criticos:
            if Path(archivo).exists():
                print_success(f"✅ {archivo} encontrado")
            else:
                print_error(f"❌ {archivo} no encontrado")
                return False
        
        # Verificar directorios
        directorios_criticos = [
            "logs",
            "data",
            "config",
            "src"
        ]
        
        for directorio in directorios_criticos:
            if Path(directorio).exists():
                print_success(f"✅ Directorio {directorio}/ encontrado")
            else:
                print_error(f"❌ Directorio {directorio}/ no encontrado")
                return False
        
        print_success("Instalación verificada exitosamente")
        return True
        
    except Exception as e:
        print_error(f"Error verificando instalación: {e}")
        return False

def mostrar_instrucciones_uso():
    """Mostrar instrucciones de uso del sistema"""
    print("\n" + "=" * 70)
    print("🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    
    print("\n📋 INSTRUCCIONES DE USO:")
    print("1. Ejecutar el sistema completo:")
    if platform.system() == "Windows":
        print("   ejecutar_sistema.bat")
    else:
        print("   ./ejecutar_sistema.sh")
    
    print("\n2. Ejecutar notebooks individualmente:")
    print("   jupyter notebook")
    
    print("\n3. Ejecutar script maestro:")
    print("   python ejecutar_notebooks_maestro.py")
    
    print("\n4. Verificar configuración:")
    print("   python verificar_sistema.py")
    
    print("\n📁 ESTRUCTURA DEL PROYECTO:")
    print("   📊 notebooks/     - Notebooks del sistema")
    print("   📁 config/        - Archivos de configuración")
    print("   📁 logs/          - Logs del sistema")
    print("   📁 data/          - Datos meteorológicos")
    print("   📁 modelos/       - Modelos de ML entrenados")
    print("   📁 reportes/      - Reportes generados")
    print("   📁 src/           - Código fuente Python")
    
    print("\n🔧 CONFIGURACIÓN:")
    print("   - Editar config/config.yaml para personalizar")
    print("   - Los logs se guardan en logs/")
    print("   - Los datos se procesan en data/")
    print("   - Los reportes se generan en reportes/")
    
    print("\n🌾 ¡Sistema METGO 3D listo para usar!")
    print("=" * 70)

def main():
    """Función principal del instalador"""
    print_header()
    
    # Verificar Python
    print_step(1, "Verificando Python")
    if not verificar_python():
        return False
    
    # Instalar dependencias
    print_step(2, "Instalando dependencias")
    if not instalar_dependencias():
        return False
    
    # Crear estructura de directorios
    print_step(3, "Creando estructura de directorios")
    if not crear_estructura_directorios():
        return False
    
    # Crear archivo de configuración
    print_step(4, "Creando archivo de configuración")
    if not crear_archivo_configuracion():
        return False
    
    # Crear requirements.txt
    print_step(5, "Creando requirements.txt")
    if not crear_archivo_requirements():
        return False
    
    # Crear script de ejecución
    print_step(6, "Creando script de ejecución")
    if not crear_script_ejecucion():
        return False
    
    # Verificar instalación
    print_step(7, "Verificando instalación")
    if not verificar_instalacion():
        return False
    
    # Mostrar instrucciones
    mostrar_instrucciones_uso()
    
    print_success("Instalación completada exitosamente")
    return True

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Instalación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)