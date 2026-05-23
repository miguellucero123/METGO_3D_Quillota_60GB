#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 INICIO RÁPIDO METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Este script proporciona un inicio rápido del sistema METGO 3D.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_header():
    """Imprimir encabezado del inicio rápido"""
    print("🌾 INICIO RÁPIDO METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0")
    print("=" * 70)

def print_step(step, message):
    """Imprimir paso del proceso de inicio"""
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

def verificar_sistema():
    """Verificar que el sistema esté listo"""
    try:
        print_info("Verificando sistema...")
        
        # Verificar archivos críticos
        archivos_criticos = [
            "config/config.yaml",
            "ejecutar_notebooks_maestro.py"
        ]
        
        for archivo in archivos_criticos:
            if not Path(archivo).exists():
                print_error(f"Archivo crítico no encontrado: {archivo}")
                return False
        
        print_success("Sistema verificado exitosamente")
        return True
        
    except Exception as e:
        print_error(f"Error verificando sistema: {e}")
        return False

def mostrar_menu():
    """Mostrar menú de opciones"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE OPCIONES - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🚀 Ejecutar sistema completo (recomendado)")
    print("2. 📊 Ejecutar notebooks individuales")
    print("3. 🔧 Verificar sistema")
    print("4. 📋 Ver reportes")
    print("5. 🗂️ Explorar archivos")
    print("6. ❌ Salir")
    
    print("\n" + "=" * 70)

def ejecutar_sistema_completo():
    """Ejecutar el sistema completo"""
    try:
        print_info("Ejecutando sistema completo...")
        
        # Ejecutar script maestro
        resultado = subprocess.run([
            sys.executable, "ejecutar_notebooks_maestro.py"
        ], capture_output=True, text=True)
        
        if resultado.returncode == 0:
            print_success("Sistema ejecutado exitosamente")
            print("\n📊 Salida del sistema:")
            print(resultado.stdout)
        else:
            print_error("Error ejecutando sistema")
            print("\n❌ Error del sistema:")
            print(resultado.stderr)
        
        return resultado.returncode == 0
        
    except Exception as e:
        print_error(f"Error ejecutando sistema: {e}")
        return False

def ejecutar_notebooks_individuales():
    """Ejecutar notebooks individuales"""
    try:
        print_info("Iniciando Jupyter Notebook...")
        
        # Ejecutar Jupyter Notebook
        subprocess.run([sys.executable, "-m", "jupyter", "notebook"])
        
        return True
        
    except Exception as e:
        print_error(f"Error ejecutando Jupyter: {e}")
        return False

def verificar_sistema_detallado():
    """Verificar sistema de manera detallada"""
    try:
        print_info("Ejecutando verificación detallada...")
        
        # Ejecutar script de verificación
        resultado = subprocess.run([
            sys.executable, "verificar_sistema.py"
        ], capture_output=True, text=True)
        
        if resultado.returncode == 0:
            print_success("Verificación completada exitosamente")
            print("\n📊 Resultado de la verificación:")
            print(resultado.stdout)
        else:
            print_error("Error en la verificación")
            print("\n❌ Error de la verificación:")
            print(resultado.stderr)
        
        return resultado.returncode == 0
        
    except Exception as e:
        print_error(f"Error ejecutando verificación: {e}")
        return False

def ver_reportes():
    """Ver reportes generados"""
    try:
        print_info("Mostrando reportes disponibles...")
        
        reportes_dir = Path("reportes")
        if not reportes_dir.exists():
            print_warning("No se encontró directorio de reportes")
            return False
        
        reportes = list(reportes_dir.glob("*.md"))
        if not reportes:
            print_warning("No se encontraron reportes")
            return False
        
        print(f"\n📋 Reportes encontrados ({len(reportes)}):")
        for i, reporte in enumerate(reportes, 1):
            print(f"   {i}. {reporte.name}")
        
        # Mostrar el reporte más reciente
        reporte_mas_reciente = max(reportes, key=lambda x: x.stat().st_mtime)
        print(f"\n📄 Mostrando reporte más reciente: {reporte_mas_reciente.name}")
        
        with open(reporte_mas_reciente, 'r', encoding='utf-8') as f:
            contenido = f.read()
            print("\n" + "=" * 70)
            print(contenido[:1000] + "..." if len(contenido) > 1000 else contenido)
            print("=" * 70)
        
        return True
        
    except Exception as e:
        print_error(f"Error mostrando reportes: {e}")
        return False

def explorar_archivos():
    """Explorar archivos del sistema"""
    try:
        print_info("Explorando archivos del sistema...")
        
        # Mostrar estructura de directorios
        print("\n📁 Estructura de directorios:")
        for directorio in ["config", "logs", "data", "reportes", "modelos", "src"]:
            if Path(directorio).exists():
                archivos = list(Path(directorio).iterdir())
                print(f"\n   📁 {directorio}/ ({len(archivos)} archivos)")
                for archivo in archivos[:5]:  # Mostrar solo los primeros 5
                    print(f"      📄 {archivo.name}")
                if len(archivos) > 5:
                    print(f"      ... y {len(archivos) - 5} archivos más")
            else:
                print(f"\n   📁 {directorio}/ (no existe)")
        
        # Mostrar archivos principales
        print("\n📄 Archivos principales:")
        archivos_principales = [
            "ejecutar_notebooks_maestro.py",
            "instalar_y_configurar.py",
            "verificar_sistema.py",
            "requirements.txt"
        ]
        
        for archivo in archivos_principales:
            if Path(archivo).exists():
                print(f"   ✅ {archivo}")
            else:
                print(f"   ❌ {archivo} (no encontrado)")
        
        return True
        
    except Exception as e:
        print_error(f"Error explorando archivos: {e}")
        return False

def mostrar_ayuda():
    """Mostrar ayuda del sistema"""
    print("\n" + "=" * 70)
    print("📚 AYUDA - METGO 3D")
    print("=" * 70)
    
    print("\n🌾 DESCRIPCIÓN:")
    print("   METGO 3D es un sistema meteorológico agrícola para Quillota, Chile.")
    print("   Proporciona análisis meteorológico, predicciones y recomendaciones agrícolas.")
    
    print("\n🚀 OPCIONES DISPONIBLES:")
    print("   1. Ejecutar sistema completo: Ejecuta todos los notebooks automáticamente")
    print("   2. Ejecutar notebooks individuales: Abre Jupyter Notebook para edición manual")
    print("   3. Verificar sistema: Verifica que todo esté correctamente instalado")
    print("   4. Ver reportes: Muestra los reportes generados por el sistema")
    print("   5. Explorar archivos: Muestra la estructura de archivos del proyecto")
    
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
    
    print("\n🌾 ¡Disfruta usando METGO 3D!")
    print("=" * 70)

def main():
    """Función principal del inicio rápido"""
    print_header()
    
    # Verificar sistema
    if not verificar_sistema():
        print_error("Sistema no está listo. Ejecutar instalar_y_configurar.py primero.")
        return False
    
    print_success("Sistema verificado y listo para usar")
    
    # Mostrar menú principal
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🔢 Selecciona una opción (1-6): ").strip()
            
            if opcion == "1":
                print_step("1", "Ejecutando sistema completo")
                if ejecutar_sistema_completo():
                    print_success("Sistema ejecutado exitosamente")
                else:
                    print_error("Error ejecutando sistema")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "2":
                print_step("2", "Ejecutando notebooks individuales")
                if ejecutar_notebooks_individuales():
                    print_success("Jupyter Notebook iniciado")
                else:
                    print_error("Error iniciando Jupyter")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Verificando sistema")
                if verificar_sistema_detallado():
                    print_success("Verificación completada")
                else:
                    print_error("Error en la verificación")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Mostrando reportes")
                if ver_reportes():
                    print_success("Reportes mostrados")
                else:
                    print_error("Error mostrando reportes")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Explorando archivos")
                if explorar_archivos():
                    print_success("Archivos explorados")
                else:
                    print_error("Error explorando archivos")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_info("Saliendo del sistema...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-6.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Interrumpido por el usuario")
            print_success("¡Hasta luego! 🌾")
            break
        except Exception as e:
            print_error(f"Error inesperado: {e}")
            input("\n⏸️ Presiona Enter para continuar...")
    
    return True

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)