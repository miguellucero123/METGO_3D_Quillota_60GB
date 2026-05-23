#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 RESUMEN DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Este script genera un resumen completo del sistema METGO 3D.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
import yaml

def print_header():
    """Imprimir encabezado del resumen"""
    print("🌾 RESUMEN DEL SISTEMA METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0")
    print("=" * 70)

def print_section(title):
    """Imprimir sección del resumen"""
    print(f"\n{'=' * 70}")
    print(f"📋 {title}")
    print('=' * 70)

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

def obtener_info_sistema():
    """Obtener información del sistema"""
    try:
        info = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "sistema_operativo": os.name,
            "directorio_actual": str(Path.cwd()),
            "usuario": os.getenv("USER", "desconocido")
        }
        return info
    except Exception as e:
        print_error(f"Error obteniendo información del sistema: {e}")
        return None

def obtener_info_proyecto():
    """Obtener información del proyecto"""
    try:
        info = {
            "nombre": "METGO 3D",
            "descripcion": "Sistema Meteorológico Agrícola Quillota",
            "version": "2.0.0",
            "entorno": "Operativo",
            "fecha_creacion": "2025-01-02",
            "autor": "Sistema METGO 3D",
            "licencia": "MIT"
        }
        return info
    except Exception as e:
        print_error(f"Error obteniendo información del proyecto: {e}")
        return None

def obtener_info_configuracion():
    """Obtener información de configuración"""
    try:
        config_file = Path("config/config.yaml")
        if not config_file.exists():
            print_warning("Archivo de configuración no encontrado")
            return None
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        info = {
            "quillota": config.get("QUILLOTA", {}),
            "sistema": config.get("SISTEMA", {}),
            "apis": config.get("APIS", {}),
            "alertas": config.get("ALERTAS", {}),
            "ml": config.get("ML", {}),
            "visualizacion": config.get("VISUALIZACION", {})
        }
        return info
    except Exception as e:
        print_error(f"Error obteniendo configuración: {e}")
        return None

def obtener_info_notebooks():
    """Obtener información de notebooks"""
    try:
        notebooks = [
            "01_Configuracion_e_Imports.ipynb",
            "02_Carga_y_Procesamiento_Datos.ipynb",
            "03_Analisis_Meteorologico.ipynb",
            "04_Visualizaciones.ipynb",
            "05_Modelos_ML.ipynb",
            "06_Dashboard_Interactivo.ipynb",
            "07_Reportes_Automaticos.ipynb",
            "08_APIs_Externas.ipynb",
            "09_Testing_Validacion.ipynb",
            "10_Deployment_Produccion.ipynb"
        ]
        
        info = {
            "total": len(notebooks),
            "existentes": 0,
            "faltantes": 0,
            "detalles": []
        }
        
        for notebook in notebooks:
            if Path(notebook).exists():
                info["existentes"] += 1
                info["detalles"].append({
                    "nombre": notebook,
                    "estado": "existe",
                    "tamaño": Path(notebook).stat().st_size,
                    "modificado": datetime.fromtimestamp(Path(notebook).stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
            else:
                info["faltantes"] += 1
                info["detalles"].append({
                    "nombre": notebook,
                    "estado": "faltante",
                    "tamaño": 0,
                    "modificado": "N/A"
                })
        
        return info
    except Exception as e:
        print_error(f"Error obteniendo información de notebooks: {e}")
        return None

def obtener_info_directorios():
    """Obtener información de directorios"""
    try:
        directorios = [
            "config",
            "logs",
            "data",
            "backups",
            "reportes",
            "modelos",
            "src",
            "tests",
            "docs"
        ]
        
        info = {
            "total": len(directorios),
            "existentes": 0,
            "faltantes": 0,
            "detalles": []
        }
        
        for directorio in directorios:
            if Path(directorio).exists():
                info["existentes"] += 1
                archivos = list(Path(directorio).iterdir())
                info["detalles"].append({
                    "nombre": directorio,
                    "estado": "existe",
                    "archivos": len(archivos),
                    "tamaño_total": sum(f.stat().st_size for f in archivos if f.is_file())
                })
            else:
                info["faltantes"] += 1
                info["detalles"].append({
                    "nombre": directorio,
                    "estado": "faltante",
                    "archivos": 0,
                    "tamaño_total": 0
                })
        
        return info
    except Exception as e:
        print_error(f"Error obteniendo información de directorios: {e}")
        return None

def obtener_info_archivos():
    """Obtener información de archivos principales"""
    try:
        archivos = [
            "ejecutar_notebooks_maestro.py",
            "instalar_y_configurar.py",
            "verificar_sistema.py",
            "inicio_rapido.py",
            "requirements.txt",
            "README.md",
            "LICENSE"
        ]
        
        info = {
            "total": len(archivos),
            "existentes": 0,
            "faltantes": 0,
            "detalles": []
        }
        
        for archivo in archivos:
            if Path(archivo).exists():
                info["existentes"] += 1
                info["detalles"].append({
                    "nombre": archivo,
                    "estado": "existe",
                    "tamaño": Path(archivo).stat().st_size,
                    "modificado": datetime.fromtimestamp(Path(archivo).stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
            else:
                info["faltantes"] += 1
                info["detalles"].append({
                    "nombre": archivo,
                    "estado": "faltante",
                    "tamaño": 0,
                    "modificado": "N/A"
                })
        
        return info
    except Exception as e:
        print_error(f"Error obteniendo información de archivos: {e}")
        return None

def obtener_info_dependencias():
    """Obtener información de dependencias"""
    try:
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
        
        info = {
            "total": len(dependencias),
            "instaladas": 0,
            "faltantes": 0,
            "detalles": []
        }
        
        for dep in dependencias:
            try:
                if dep == "yaml":
                    import yaml
                elif dep == "sklearn":
                    import sklearn
                else:
                    __import__(dep)
                
                info["instaladas"] += 1
                info["detalles"].append({
                    "nombre": dep,
                    "estado": "instalada",
                    "version": "N/A"
                })
            except ImportError:
                info["faltantes"] += 1
                info["detalles"].append({
                    "nombre": dep,
                    "estado": "faltante",
                    "version": "N/A"
                })
        
        return info
    except Exception as e:
        print_error(f"Error obteniendo información de dependencias: {e}")
        return None

def generar_resumen_completo():
    """Generar resumen completo del sistema"""
    try:
        print_info("Generando resumen completo del sistema...")
        
        # Obtener información de todas las secciones
        info_sistema = obtener_info_sistema()
        info_proyecto = obtener_info_proyecto()
        info_configuracion = obtener_info_configuracion()
        info_notebooks = obtener_info_notebooks()
        info_directorios = obtener_info_directorios()
        info_archivos = obtener_info_archivos()
        info_dependencias = obtener_info_dependencias()
        
        # Crear resumen completo
        resumen = {
            "fecha_generacion": datetime.now().isoformat(),
            "sistema": info_sistema,
            "proyecto": info_proyecto,
            "configuracion": info_configuracion,
            "notebooks": info_notebooks,
            "directorios": info_directorios,
            "archivos": info_archivos,
            "dependencias": info_dependencias
        }
        
        return resumen
    except Exception as e:
        print_error(f"Error generando resumen: {e}")
        return None

def mostrar_resumen_consola(resumen):
    """Mostrar resumen en consola"""
    try:
        print_header()
        
        # Información del sistema
        print_section("INFORMACIÓN DEL SISTEMA")
        if resumen["sistema"]:
            print(f"📅 Fecha: {resumen['sistema']['fecha']}")
            print(f"🐍 Python: {resumen['sistema']['python_version']}")
            print(f"💻 SO: {resumen['sistema']['sistema_operativo']}")
            print(f"📁 Directorio: {resumen['sistema']['directorio_actual']}")
            print(f"👤 Usuario: {resumen['sistema']['usuario']}")
        
        # Información del proyecto
        print_section("INFORMACIÓN DEL PROYECTO")
        if resumen["proyecto"]:
            print(f"🌾 Nombre: {resumen['proyecto']['nombre']}")
            print(f"📝 Descripción: {resumen['proyecto']['descripcion']}")
            print(f"🔢 Versión: {resumen['proyecto']['version']}")
            print(f"🌍 Entorno: {resumen['proyecto']['entorno']}")
            print(f"📅 Fecha creación: {resumen['proyecto']['fecha_creacion']}")
            print(f"👨‍💻 Autor: {resumen['proyecto']['autor']}")
            print(f"📄 Licencia: {resumen['proyecto']['licencia']}")
        
        # Configuración
        print_section("CONFIGURACIÓN")
        if resumen["configuracion"]:
            if resumen["configuracion"]["quillota"]:
                print(f"📍 Ubicación: {resumen['configuracion']['quillota'].get('nombre', 'N/A')}, {resumen['configuracion']['quillota'].get('region', 'N/A')}")
                print(f"🗺️ Coordenadas: {resumen['configuracion']['quillota'].get('coordenadas', {}).get('latitud', 'N/A')}, {resumen['configuracion']['quillota'].get('coordenadas', {}).get('longitud', 'N/A')}")
                print(f"⛰️ Elevación: {resumen['configuracion']['quillota'].get('elevacion', 'N/A')} m")
            
            if resumen["configuracion"]["sistema"]:
                print(f"🔧 Versión: {resumen['configuracion']['sistema'].get('version', 'N/A')}")
                print(f"🌍 Entorno: {resumen['configuracion']['sistema'].get('entorno', 'N/A')}")
                print(f"🐛 Debug: {resumen['configuracion']['sistema'].get('debug', 'N/A')}")
                print(f"📊 Logging: {resumen['configuracion']['sistema'].get('logging_level', 'N/A')}")
        
        # Notebooks
        print_section("NOTEBOOKS")
        if resumen["notebooks"]:
            print(f"📊 Total: {resumen['notebooks']['total']}")
            print(f"✅ Existentes: {resumen['notebooks']['existentes']}")
            print(f"❌ Faltantes: {resumen['notebooks']['faltantes']}")
            print(f"📈 Tasa de éxito: {(resumen['notebooks']['existentes']/resumen['notebooks']['total']*100):.1f}%")
            
            print("\n📋 Detalles de notebooks:")
            for notebook in resumen["notebooks"]["detalles"]:
                estado = "✅" if notebook["estado"] == "existe" else "❌"
                print(f"   {estado} {notebook['nombre']} ({notebook['tamaño']} bytes)")
        
        # Directorios
        print_section("DIRECTORIOS")
        if resumen["directorios"]:
            print(f"📁 Total: {resumen['directorios']['total']}")
            print(f"✅ Existentes: {resumen['directorios']['existentes']}")
            print(f"❌ Faltantes: {resumen['directorios']['faltantes']}")
            print(f"📈 Tasa de éxito: {(resumen['directorios']['existentes']/resumen['directorios']['total']*100):.1f}%")
            
            print("\n📋 Detalles de directorios:")
            for directorio in resumen["directorios"]["detalles"]:
                estado = "✅" if directorio["estado"] == "existe" else "❌"
                print(f"   {estado} {directorio['nombre']}/ ({directorio['archivos']} archivos, {directorio['tamaño_total']} bytes)")
        
        # Archivos
        print_section("ARCHIVOS PRINCIPALES")
        if resumen["archivos"]:
            print(f"📄 Total: {resumen['archivos']['total']}")
            print(f"✅ Existentes: {resumen['archivos']['existentes']}")
            print(f"❌ Faltantes: {resumen['archivos']['faltantes']}")
            print(f"📈 Tasa de éxito: {(resumen['archivos']['existentes']/resumen['archivos']['total']*100):.1f}%")
            
            print("\n📋 Detalles de archivos:")
            for archivo in resumen["archivos"]["detalles"]:
                estado = "✅" if archivo["estado"] == "existe" else "❌"
                print(f"   {estado} {archivo['nombre']} ({archivo['tamaño']} bytes)")
        
        # Dependencias
        print_section("DEPENDENCIAS")
        if resumen["dependencias"]:
            print(f"📦 Total: {resumen['dependencias']['total']}")
            print(f"✅ Instaladas: {resumen['dependencias']['instaladas']}")
            print(f"❌ Faltantes: {resumen['dependencias']['faltantes']}")
            print(f"📈 Tasa de éxito: {(resumen['dependencias']['instaladas']/resumen['dependencias']['total']*100):.1f}%")
            
            print("\n📋 Detalles de dependencias:")
            for dep in resumen["dependencias"]["detalles"]:
                estado = "✅" if dep["estado"] == "instalada" else "❌"
                print(f"   {estado} {dep['nombre']}")
        
        # Resumen final
        print_section("RESUMEN FINAL")
        total_elementos = (
            resumen["notebooks"]["total"] + 
            resumen["directorios"]["total"] + 
            resumen["archivos"]["total"] + 
            resumen["dependencias"]["total"]
        )
        total_exitosos = (
            resumen["notebooks"]["existentes"] + 
            resumen["directorios"]["existentes"] + 
            resumen["archivos"]["existentes"] + 
            resumen["dependencias"]["instaladas"]
        )
        
        print(f"🎯 Total de elementos verificados: {total_elementos}")
        print(f"✅ Elementos exitosos: {total_exitosos}")
        print(f"❌ Elementos con problemas: {total_elementos - total_exitosos}")
        print(f"📈 Tasa de éxito general: {(total_exitosos/total_elementos*100):.1f}%")
        
        if total_exitosos == total_elementos:
            print_success("🎉 SISTEMA COMPLETAMENTE OPERATIVO")
        elif total_exitosos > total_elementos * 0.8:
            print_warning("⚠️ SISTEMA MAYORMENTE OPERATIVO (algunos problemas menores)")
        else:
            print_error("❌ SISTEMA CON PROBLEMAS SIGNIFICATIVOS")
        
        print("\n" + "🌾" + "=" * 68 + "🌾")
        print("  ✅ RESUMEN DEL SISTEMA METGO 3D - COMPLETADO ✅")
        print("🌾" + "=" * 68 + "🌾")
        
    except Exception as e:
        print_error(f"Error mostrando resumen: {e}")

def guardar_resumen_archivo(resumen):
    """Guardar resumen en archivo"""
    try:
        # Crear directorio de reportes si no existe
        reportes_dir = Path("reportes")
        reportes_dir.mkdir(exist_ok=True)
        
        # Guardar resumen en JSON
        resumen_file = reportes_dir / f"resumen_sistema_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(resumen_file, 'w', encoding='utf-8') as f:
            json.dump(resumen, f, indent=2, ensure_ascii=False)
        
        print_success(f"Resumen guardado en archivo: {resumen_file}")
        return resumen_file
        
    except Exception as e:
        print_error(f"Error guardando resumen: {e}")
        return None

def main():
    """Función principal del resumen"""
    try:
        # Generar resumen completo
        resumen = generar_resumen_completo()
        if not resumen:
            print_error("No se pudo generar el resumen")
            return False
        
        # Mostrar resumen en consola
        mostrar_resumen_consola(resumen)
        
        # Guardar resumen en archivo
        guardar_resumen_archivo(resumen)
        
        print_success("Resumen del sistema completado exitosamente")
        return True
        
    except Exception as e:
        print_error(f"Error generando resumen: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Resumen interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)