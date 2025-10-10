#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 VERIFICADOR DE SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Este script verifica que el sistema METGO 3D esté correctamente instalado y configurado.
"""

import os
import sys
import importlib
from pathlib import Path
import yaml

def print_header():
    """Imprimir encabezado del verificador"""
    print("🌾 VERIFICADOR DE SISTEMA METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0")
    print("=" * 70)

def print_step(step, message):
    """Imprimir paso del proceso de verificación"""
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

def verificar_dependencias():
    """Verificar dependencias de Python"""
    try:
        print_info("Verificando dependencias de Python...")
        
        dependencias = [
            "jupyter",
            "nbconvert",
            "pandas",
            "numpy",
            "matplotlib",
            "seaborn",
            "plotly",
            "sklearn",
            "requests",
            "yaml"
        ]
        
        dependencias_faltantes = []
        
        for dep in dependencias:
            try:
                if dep == "yaml":
                    importlib.import_module("yaml")
                elif dep == "sklearn":
                    importlib.import_module("sklearn")
                else:
                    importlib.import_module(dep)
                print_success(f"✅ {dep} instalado")
            except ImportError:
                dependencias_faltantes.append(dep)
                print_error(f"❌ {dep} no instalado")
        
        if dependencias_faltantes:
            print_warning(f"⚠️ {len(dependencias_faltantes)} dependencias faltantes: {', '.join(dependencias_faltantes)}")
            return False
        
        print_success("Todas las dependencias están instaladas")
        return True
        
    except Exception as e:
        print_error(f"Error verificando dependencias: {e}")
        return False

def verificar_estructura_directorios():
    """Verificar estructura de directorios"""
    try:
        print_info("Verificando estructura de directorios...")
        
        directorios_requeridos = [
            "logs",
            "data",
            "backups",
            "reportes",
            "modelos",
            "config",
            "src",
            "tests",
            "docs"
        ]
        
        directorios_faltantes = []
        
        for directorio in directorios_requeridos:
            if Path(directorio).exists():
                print_success(f"✅ Directorio {directorio}/ encontrado")
            else:
                directorios_faltantes.append(directorio)
                print_error(f"❌ Directorio {directorio}/ no encontrado")
        
        if directorios_faltantes:
            print_warning(f"⚠️ {len(directorios_faltantes)} directorios faltantes: {', '.join(directorios_faltantes)}")
            return False
        
        print_success("Estructura de directorios correcta")
        return True
        
    except Exception as e:
        print_error(f"Error verificando directorios: {e}")
        return False

def verificar_archivos_configuracion():
    """Verificar archivos de configuración"""
    try:
        print_info("Verificando archivos de configuración...")
        
        archivos_requeridos = [
            "config/config.yaml",
            "requirements.txt",
            "ejecutar_notebooks_maestro.py"
        ]
        
        archivos_faltantes = []
        
        for archivo in archivos_requeridos:
            if Path(archivo).exists():
                print_success(f"✅ {archivo} encontrado")
            else:
                archivos_faltantes.append(archivo)
                print_error(f"❌ {archivo} no encontrado")
        
        if archivos_faltantes:
            print_warning(f"⚠️ {len(archivos_faltantes)} archivos faltantes: {', '.join(archivos_faltantes)}")
            return False
        
        print_success("Archivos de configuración encontrados")
        return True
        
    except Exception as e:
        print_error(f"Error verificando archivos: {e}")
        return False

def verificar_configuracion_yaml():
    """Verificar configuración YAML"""
    try:
        print_info("Verificando configuración YAML...")
        
        config_file = Path("config/config.yaml")
        if not config_file.exists():
            print_error("Archivo config/config.yaml no encontrado")
            return False
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Verificar secciones requeridas
        secciones_requeridas = ["QUILLOTA", "SISTEMA", "APIS", "ALERTAS", "ML", "VISUALIZACION"]
        
        for seccion in secciones_requeridas:
            if seccion in config:
                print_success(f"✅ Sección {seccion} encontrada")
            else:
                print_error(f"❌ Sección {seccion} no encontrada")
                return False
        
        print_success("Configuración YAML válida")
        return True
        
    except Exception as e:
        print_error(f"Error verificando configuración YAML: {e}")
        return False

def verificar_notebooks():
    """Verificar notebooks del sistema"""
    try:
        print_info("Verificando notebooks del sistema...")
        
        notebooks_requeridos = [
            "01_Configuracion_e_Imports.ipynb",
            "02_Carga_y_Procesamiento_Datos.ipynb",
            "03_Analisis_Meteorologico.ipynb",
            "04_Visualizaciones.ipynb",
            "05_Modelos_ML.ipynb"
        ]
        
        notebooks_faltantes = []
        
        for notebook in notebooks_requeridos:
            if Path(notebook).exists():
                print_success(f"✅ {notebook} encontrado")
            else:
                notebooks_faltantes.append(notebook)
                print_error(f"❌ {notebook} no encontrado")
        
        if notebooks_faltantes:
            print_warning(f"⚠️ {len(notebooks_faltantes)} notebooks faltantes: {', '.join(notebooks_faltantes)}")
            return False
        
        print_success("Notebooks del sistema encontrados")
        return True
        
    except Exception as e:
        print_error(f"Error verificando notebooks: {e}")
        return False

def verificar_permisos():
    """Verificar permisos de archivos y directorios"""
    try:
        print_info("Verificando permisos...")
        
        # Verificar permisos de escritura en directorios críticos
        directorios_escritura = ["logs", "data", "backups", "reportes", "modelos"]
        
        for directorio in directorios_escritura:
            if Path(directorio).exists():
                if os.access(directorio, os.W_OK):
                    print_success(f"✅ Permisos de escritura en {directorio}/")
                else:
                    print_error(f"❌ Sin permisos de escritura en {directorio}/")
                    return False
        
        print_success("Permisos correctos")
        return True
        
    except Exception as e:
        print_error(f"Error verificando permisos: {e}")
        return False

def verificar_conectividad():
    """Verificar conectividad de red"""
    try:
        print_info("Verificando conectividad de red...")
        
        import requests
        
        # Verificar conectividad a OpenMeteo API
        try:
            response = requests.get("https://api.open-meteo.com/v1/forecast", timeout=10)
            if response.status_code == 200:
                print_success("✅ Conectividad a OpenMeteo API")
            else:
                print_warning(f"⚠️ OpenMeteo API respondió con código {response.status_code}")
        except Exception as e:
            print_warning(f"⚠️ No se pudo conectar a OpenMeteo API: {e}")
        
        print_success("Verificación de conectividad completada")
        return True
        
    except Exception as e:
        print_error(f"Error verificando conectividad: {e}")
        return False

def generar_reporte_verificacion(resultados):
    """Generar reporte de verificación"""
    try:
        print_info("Generando reporte de verificación...")
        
        # Crear directorio de reportes si no existe
        reportes_dir = Path("reportes")
        reportes_dir.mkdir(exist_ok=True)
        
        # Estadísticas
        total_verificaciones = len(resultados)
        verificaciones_exitosas = sum(1 for r in resultados if r["exito"])
        verificaciones_fallidas = total_verificaciones - verificaciones_exitosas
        
        # Generar reporte
        reporte_content = f"""
# 🌾 REPORTE DE VERIFICACIÓN METGO 3D
Sistema Meteorológico Agrícola Quillota - Verificador de Sistema

## 📅 Información de Verificación
- **Fecha**: {os.popen('date').read().strip()}
- **Sistema**: METGO 3D Operativo v2.0
- **Script**: verificar_sistema.py

## 📊 Estadísticas de Verificación
- **Total verificaciones**: {total_verificaciones}
- **Exitosas**: {verificaciones_exitosas}
- **Fallidas**: {verificaciones_fallidas}
- **Tasa de éxito**: {(verificaciones_exitosas/total_verificaciones*100):.1f}%

## 📋 Resultados por Verificación
"""
        
        for i, resultado in enumerate(resultados, 1):
            estado = "✅ EXITOSO" if resultado["exito"] else "❌ FALLIDO"
            reporte_content += f"""
### {i}. {resultado['nombre']}
- **Estado**: {estado}
- **Descripción**: {resultado['descripcion']}
"""
            
            if not resultado["exito"] and resultado["error"]:
                reporte_content += f"- **Error**: {resultado['error']}\n"
        
        reporte_content += f"""
## 🎯 Resumen Final
- **Sistema**: METGO 3D Operativo v2.0
- **Verificaciones realizadas**: {total_verificaciones}
- **Verificación exitosa**: {verificaciones_exitosas}/{total_verificaciones}
- **Estado general**: {'✅ SISTEMA LISTO' if verificaciones_fallidas == 0 else '⚠️ SISTEMA CON PROBLEMAS'}

## 📁 Archivos Generados
- **Reporte de verificación**: reportes/reporte_verificacion.md
- **Logs del sistema**: logs/
- **Configuración**: config/

---
*Reporte generado automáticamente por el Verificador de Sistema METGO 3D*
"""
        
        # Guardar reporte
        reporte_file = reportes_dir / "reporte_verificacion.md"
        reporte_file.write_text(reporte_content, encoding='utf-8')
        
        print_success(f"Reporte de verificación generado: {reporte_file}")
        return reporte_file
        
    except Exception as e:
        print_error(f"Error generando reporte: {e}")
        return None

def mostrar_resumen_final(resultados):
    """Mostrar resumen final de la verificación"""
    total_verificaciones = len(resultados)
    verificaciones_exitosas = sum(1 for r in resultados if r["exito"])
    verificaciones_fallidas = total_verificaciones - verificaciones_exitosas
    
    print("\n" + "=" * 70)
    print("🎉 RESUMEN FINAL - VERIFICACIÓN DE SISTEMA METGO 3D")
    print("=" * 70)
    
    print(f"\n📊 ESTADÍSTICAS DE VERIFICACIÓN:")
    print(f"   Total verificaciones: {total_verificaciones}")
    print(f"   Exitosas: {verificaciones_exitosas}")
    print(f"   Fallidas: {verificaciones_fallidas}")
    print(f"   Tasa de éxito: {(verificaciones_exitosas/total_verificaciones*100):.1f}%")
    
    print(f"\n📋 RESULTADOS POR VERIFICACIÓN:")
    for i, resultado in enumerate(resultados, 1):
        estado = "✅" if resultado["exito"] else "❌"
        print(f"   {i:2d}. {estado} {resultado['nombre']}")
    
    if verificaciones_fallidas > 0:
        print(f"\n⚠️ VERIFICACIONES FALLIDAS:")
        for resultado in resultados:
            if not resultado["exito"]:
                print(f"   ❌ {resultado['nombre']}: {resultado['error']}")
    
    print(f"\n🎯 ESTADO GENERAL:")
    if verificaciones_fallidas == 0:
        print("   ✅ SISTEMA COMPLETAMENTE VERIFICADO")
        print("   🌾 METGO 3D listo para usar")
    else:
        print(f"   ⚠️ SISTEMA CON {verificaciones_fallidas} PROBLEMAS")
        print("   🔧 Revisar errores y corregir antes de usar")
    
    print("\n" + "🌾" + "=" * 68 + "🌾")
    print("  ✅ VERIFICADOR DE SISTEMA METGO 3D - COMPLETADO ✅")
    print("🌾" + "=" * 68 + "🌾")

def main():
    """Función principal del verificador"""
    print_header()
    
    # Lista de verificaciones a realizar
    verificaciones = [
        {
            "nombre": "Python",
            "descripcion": "Verificar versión de Python",
            "funcion": verificar_python
        },
        {
            "nombre": "Dependencias",
            "descripcion": "Verificar dependencias de Python",
            "funcion": verificar_dependencias
        },
        {
            "nombre": "Estructura Directorios",
            "descripcion": "Verificar estructura de directorios",
            "funcion": verificar_estructura_directorios
        },
        {
            "nombre": "Archivos Configuración",
            "descripcion": "Verificar archivos de configuración",
            "funcion": verificar_archivos_configuracion
        },
        {
            "nombre": "Configuración YAML",
            "descripcion": "Verificar configuración YAML",
            "funcion": verificar_configuracion_yaml
        },
        {
            "nombre": "Notebooks",
            "descripcion": "Verificar notebooks del sistema",
            "funcion": verificar_notebooks
        },
        {
            "nombre": "Permisos",
            "descripcion": "Verificar permisos de archivos",
            "funcion": verificar_permisos
        },
        {
            "nombre": "Conectividad",
            "descripcion": "Verificar conectividad de red",
            "funcion": verificar_conectividad
        }
    ]
    
    # Ejecutar verificaciones
    resultados = []
    
    for i, verificacion in enumerate(verificaciones, 1):
        print_step(f"{i}/{len(verificaciones)}", verificacion["descripcion"])
        
        try:
            exito = verificacion["funcion"]()
            resultado = {
                "nombre": verificacion["nombre"],
                "descripcion": verificacion["descripcion"],
                "exito": exito,
                "error": None
            }
        except Exception as e:
            resultado = {
                "nombre": verificacion["nombre"],
                "descripcion": verificacion["descripcion"],
                "exito": False,
                "error": str(e)
            }
        
        resultados.append(resultado)
    
    # Generar reporte
    print_step("Final", "Generando reporte de verificación")
    reporte_file = generar_reporte_verificacion(resultados)
    
    # Mostrar resumen final
    mostrar_resumen_final(resultados)
    
    # Retornar éxito si todas las verificaciones pasaron
    verificaciones_exitosas = sum(1 for r in resultados if r["exito"])
    return verificaciones_exitosas == len(verificaciones)

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Verificación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)