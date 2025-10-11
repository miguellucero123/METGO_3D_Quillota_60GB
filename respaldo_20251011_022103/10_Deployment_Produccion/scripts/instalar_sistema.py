#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 INSTALADOR AUTOMÁTICO METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Este script instala automáticamente todas las dependencias y configura
el sistema METGO 3D para uso inmediato.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Imprimir encabezado del instalador"""
    print("🌾 INSTALADOR AUTOMÁTICO METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0")
    print("=" * 60)

def print_step(step, message):
    """Imprimir paso del proceso de instalación"""
    print(f"\n[{step}] {message}")
    print("-" * 40)

def print_success(message):
    """Imprimir mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message):
    """Imprimir mensaje de error"""
    print(f"❌ {message}")

def print_warning(message):
    """Imprimir mensaje de advertencia"""
    print(f"⚠️ {message}")

def check_python_version():
    """Verificar versión de Python"""
    print_step(1, "Verificando versión de Python")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python {version.major}.{version.minor} no es compatible")
        print_error("Se requiere Python 3.8 o superior")
        return False
    
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detectado")
    return True

def check_pip():
    """Verificar que pip esté disponible"""
    print_step(2, "Verificando pip")
    
    try:
        import pip
        print_success("pip está disponible")
        return True
    except ImportError:
        print_error("pip no está instalado")
        print("Instalar pip desde: https://pip.pypa.io/en/stable/installation/")
        return False

def install_dependencies():
    """Instalar dependencias desde requirements.txt"""
    print_step(3, "Instalando dependencias")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print_error("Archivo requirements.txt no encontrado")
        return False
    
    try:
        print("Instalando paquetes Python...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("Dependencias instaladas correctamente")
            return True
        else:
            print_error("Error instalando dependencias")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"Excepción instalando dependencias: {e}")
        return False

def create_directories():
    """Crear directorios necesarios"""
    print_step(4, "Creando directorios del sistema")
    
    directories = [
        "logs", "data", "reportes_revision", "test_results", 
        "tests", "app", "static", "templates", "backups", "config"
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            print_success(f"Directorio creado/verificado: {directory}")
        except Exception as e:
            print_error(f"Error creando directorio {directory}: {e}")
            return False
    
    return True

def verify_installation():
    """Verificar que la instalación fue exitosa"""
    print_step(5, "Verificando instalación")
    
    critical_packages = [
        "pandas", "numpy", "matplotlib", "seaborn", 
        "sklearn", "requests", "plotly", "streamlit", "yaml"
    ]
    
    missing_packages = []
    
    for package in critical_packages:
        try:
            if package == "yaml":
                import yaml
            elif package == "sklearn":
                import sklearn
            else:
                __import__(package)
            print_success(f"{package} disponible")
        except ImportError:
            missing_packages.append(package)
            print_error(f"{package} no disponible")
    
    if missing_packages:
        print_error(f"Paquetes faltantes: {', '.join(missing_packages)}")
        return False
    
    print_success("Todas las dependencias críticas están disponibles")
    return True

def create_config_files():
    """Crear archivos de configuración si no existen"""
    print_step(6, "Verificando archivos de configuración")
    
    config_files = {
        "config/config.yaml": """# Configuración METGO 3D
QUILLOTA:
  nombre: "Quillota"
  region: "Valparaíso"
  coordenadas:
    latitud: -32.8833
    longitud: -71.25

METEOROLOGIA:
  umbrales:
    temperatura:
      helada_severa: -2.0
      calor_extremo: 35.0
    precipitacion:
      lluvia_intensa: 20.0
    viento:
      fuerte: 25.0
    humedad:
      muy_baja: 30.0
      muy_alta: 85.0
""",
        "requirements.txt": """pandas>=1.3.0
numpy>=1.21.0
matplotlib>=3.4.0
seaborn>=0.11.0
scikit-learn>=1.0.0
requests>=2.25.0
plotly>=5.0.0
streamlit>=1.0.0
pyyaml>=5.4.0
jupyter>=1.0.0
nbconvert>=6.0.0
"""
    }
    
    for file_path, content in config_files.items():
        file_obj = Path(file_path)
        if not file_obj.exists():
            try:
                file_obj.parent.mkdir(exist_ok=True)
                file_obj.write_text(content, encoding='utf-8')
                print_success(f"Archivo creado: {file_path}")
            except Exception as e:
                print_error(f"Error creando {file_path}: {e}")
                return False
        else:
            print_success(f"Archivo ya existe: {file_path}")
    
    return True

def make_scripts_executable():
    """Hacer scripts ejecutables (Linux/macOS)"""
    print_step(7, "Configurando scripts ejecutables")
    
    if platform.system() in ["Linux", "Darwin"]:  # Linux o macOS
        scripts = ["ejecutar_sistema.sh"]
        for script in scripts:
            if Path(script).exists():
                try:
                    os.chmod(script, 0o755)
                    print_success(f"Script {script} hecho ejecutable")
                except Exception as e:
                    print_warning(f"No se pudo hacer ejecutable {script}: {e}")
    else:
        print_success("Sistema Windows detectado - scripts PowerShell listos")
    
    return True

def run_initial_test():
    """Ejecutar prueba inicial del sistema"""
    print_step(8, "Ejecutando prueba inicial")
    
    try:
        # Probar importación de módulos principales
        test_code = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
import requests
import plotly.graph_objects as go
import streamlit as st
import yaml

print("✅ Todas las importaciones exitosas")
print(f"📊 Pandas: {pd.__version__}")
print(f"🔢 NumPy: {np.__version__}")
print(f"📈 Matplotlib: {plt.matplotlib.__version__}")
print(f"🎨 Seaborn: {sns.__version__}")
print(f"🤖 Scikit-learn: {sklearn.__version__}")
print(f"🌐 Requests: {requests.__version__}")
print(f"📊 Plotly: {plotly.__version__}")
print(f"🚀 Streamlit: {st.__version__}")
"""
        
        result = subprocess.run([
            sys.executable, "-c", test_code
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("Prueba inicial exitosa")
            print(result.stdout)
            return True
        else:
            print_error("Prueba inicial falló")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"Error en prueba inicial: {e}")
        return False

def show_completion_message():
    """Mostrar mensaje de finalización"""
    print("\n" + "=" * 60)
    print("🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print("🌾 Sistema METGO 3D listo para uso")
    print("📍 Ubicación: Quillota, Región de Valparaíso, Chile")
    print("📅 Versión: 2.0 Operativa")
    print("")
    print("🚀 PRÓXIMOS PASOS:")
    print("1. Ejecutar el sistema completo:")
    if platform.system() == "Windows":
        print("   .\\ejecutar_sistema.ps1")
    else:
        print("   ./ejecutar_sistema.sh")
    print("")
    print("2. O ejecutar con Python:")
    print("   python ejecutar_sistema_completo.py")
    print("")
    print("3. Para modo rápido:")
    if platform.system() == "Windows":
        print("   .\\ejecutar_sistema.ps1 rapido")
    else:
        print("   ./ejecutar_sistema.sh rapido")
    print("")
    print("📚 Ver README.md para más información")
    print("🔧 Logs del sistema en: logs/")
    print("📊 Datos generados en: data/")
    print("")
    print("¡Sistema listo para optimizar tu producción agrícola! 🌾")

def main():
    """Función principal del instalador"""
    print_header()
    
    # Verificar prerrequisitos
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    # Instalar dependencias
    if not install_dependencies():
        print_error("Instalación de dependencias falló")
        sys.exit(1)
    
    # Crear estructura de directorios
    if not create_directories():
        print_error("Creación de directorios falló")
        sys.exit(1)
    
    # Crear archivos de configuración
    if not create_config_files():
        print_error("Creación de archivos de configuración falló")
        sys.exit(1)
    
    # Configurar scripts ejecutables
    if not make_scripts_executable():
        print_warning("Configuración de scripts ejecutables falló (continuando)")
    
    # Verificar instalación
    if not verify_installation():
        print_error("Verificación de instalación falló")
        sys.exit(1)
    
    # Ejecutar prueba inicial
    if not run_initial_test():
        print_warning("Prueba inicial falló (continuando)")
    
    # Mostrar mensaje de finalización
    show_completion_message()

if __name__ == "__main__":
    main()
