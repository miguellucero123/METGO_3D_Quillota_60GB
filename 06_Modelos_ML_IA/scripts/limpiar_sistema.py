#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 LIMPIADOR DE SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Este script limpia y optimiza el sistema METGO 3D.
"""

import os
import sys
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta

def print_header():
    """Imprimir encabezado del limpiador"""
    print("🌾 LIMPIADOR DE SISTEMA METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0")
    print("=" * 70)

def print_step(step, message):
    """Imprimir paso del proceso de limpieza"""
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

def limpiar_logs_antiguos():
    """Limpiar logs antiguos del sistema"""
    try:
        print_info("Limpiando logs antiguos...")
        
        logs_dir = Path("logs")
        if not logs_dir.exists():
            print_warning("Directorio de logs no encontrado")
            return False
        
        # Limpiar logs más antiguos de 30 días
        fecha_limite = datetime.now() - timedelta(days=30)
        archivos_eliminados = 0
        espacio_liberado = 0
        
        for archivo in logs_dir.iterdir():
            if archivo.is_file():
                try:
                    fecha_modificacion = datetime.fromtimestamp(archivo.stat().st_mtime)
                    if fecha_modificacion < fecha_limite:
                        tamaño = archivo.stat().st_size
                        archivo.unlink()
                        archivos_eliminados += 1
                        espacio_liberado += tamaño
                        print_success(f"✅ {archivo.name} eliminado")
                except Exception as e:
                    print_warning(f"⚠️ Error eliminando {archivo.name}: {e}")
        
        print_success(f"Logs antiguos limpiados: {archivos_eliminados} archivos")
        print_success(f"Espacio liberado: {espacio_liberado / (1024**2):.1f} MB")
        
        return True
        
    except Exception as e:
        print_error(f"Error limpiando logs: {e}")
        return False

def limpiar_datos_temporales():
    """Limpiar datos temporales del sistema"""
    try:
        print_info("Limpiando datos temporales...")
        
        # Directorios de datos temporales
        directorios_limpiar = [
            "data/temp",
            "data/cache",
            "data/tmp",
            "backups/temp"
        ]
        
        archivos_eliminados = 0
        espacio_liberado = 0
        
        for directorio in directorios_limpiar:
            if Path(directorio).exists():
                for archivo in Path(directorio).rglob("*"):
                    if archivo.is_file():
                        try:
                            tamaño = archivo.stat().st_size
                            archivo.unlink()
                            archivos_eliminados += 1
                            espacio_liberado += tamaño
                        except Exception:
                            continue
        
        print_success(f"Datos temporales limpiados: {archivos_eliminados} archivos")
        print_success(f"Espacio liberado: {espacio_liberado / (1024**2):.1f} MB")
        
        return True
        
    except Exception as e:
        print_error(f"Error limpiando datos temporales: {e}")
        return False

def limpiar_cache_python():
    """Limpiar cache de Python"""
    try:
        print_info("Limpiando cache de Python...")
        
        # Buscar directorios __pycache__
        cache_dirs = list(Path(".").rglob("__pycache__"))
        
        archivos_eliminados = 0
        espacio_liberado = 0
        
        for cache_dir in cache_dirs:
            try:
                for archivo in cache_dir.rglob("*"):
                    if archivo.is_file():
                        tamaño = archivo.stat().st_size
                        archivo.unlink()
                        archivos_eliminados += 1
                        espacio_liberado += tamaño
                
                # Eliminar directorio vacío
                cache_dir.rmdir()
                
            except Exception as e:
                print_warning(f"⚠️ Error limpiando {cache_dir}: {e}")
        
        print_success(f"Cache de Python limpiado: {archivos_eliminados} archivos")
        print_success(f"Espacio liberado: {espacio_liberado / (1024**2):.1f} MB")
        
        return True
        
    except Exception as e:
        print_error(f"Error limpiando cache de Python: {e}")
        return False

def limpiar_checkpoints_jupyter():
    """Limpiar checkpoints de Jupyter"""
    try:
        print_info("Limpiando checkpoints de Jupyter...")
        
        # Buscar directorios .ipynb_checkpoints
        checkpoint_dirs = list(Path(".").rglob(".ipynb_checkpoints"))
        
        archivos_eliminados = 0
        espacio_liberado = 0
        
        for checkpoint_dir in checkpoint_dirs:
            try:
                for archivo in checkpoint_dir.rglob("*"):
                    if archivo.is_file():
                        tamaño = archivo.stat().st_size
                        archivo.unlink()
                        archivos_eliminados += 1
                        espacio_liberado += tamaño
                
                # Eliminar directorio vacío
                checkpoint_dir.rmdir()
                
            except Exception as e:
                print_warning(f"⚠️ Error limpiando {checkpoint_dir}: {e}")
        
        print_success(f"Checkpoints de Jupyter limpiados: {archivos_eliminados} archivos")
        print_success(f"Espacio liberado: {espacio_liberado / (1024**2):.1f} MB")
        
        return True
        
    except Exception as e:
        print_error(f"Error limpiando checkpoints de Jupyter: {e}")
        return False

def limpiar_archivos_duplicados():
    """Limpiar archivos duplicados"""
    try:
        print_info("Limpiando archivos duplicados...")
        
        # Buscar archivos duplicados por nombre
        archivos_por_nombre = {}
        
        for archivo in Path(".").rglob("*"):
            if archivo.is_file() and not archivo.name.startswith('.'):
                nombre = archivo.name
                if nombre not in archivos_por_nombre:
                    archivos_por_nombre[nombre] = []
                archivos_por_nombre[nombre].append(archivo)
        
        archivos_eliminados = 0
        espacio_liberado = 0
        
        for nombre, archivos in archivos_por_nombre.items():
            if len(archivos) > 1:
                # Ordenar por fecha de modificación (más reciente primero)
                archivos.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                # Eliminar duplicados (mantener el más reciente)
                for archivo in archivos[1:]:
                    try:
                        tamaño = archivo.stat().st_size
                        archivo.unlink()
                        archivos_eliminados += 1
                        espacio_liberado += tamaño
                        print_success(f"✅ Duplicado eliminado: {archivo}")
                    except Exception as e:
                        print_warning(f"⚠️ Error eliminando duplicado {archivo}: {e}")
        
        print_success(f"Archivos duplicados eliminados: {archivos_eliminados}")
        print_success(f"Espacio liberado: {espacio_liberado / (1024**2):.1f} MB")
        
        return True
        
    except Exception as e:
        print_error(f"Error limpiando archivos duplicados: {e}")
        return False

def optimizar_estructura_directorios():
    """Optimizar estructura de directorios"""
    try:
        print_info("Optimizando estructura de directorios...")
        
        # Crear directorios necesarios si no existen
        directorios_crear = [
            "logs",
            "data",
            "backups",
            "reportes",
            "modelos",
            "src",
            "tests",
            "docs"
        ]
        
        for directorio in directorios_crear:
            Path(directorio).mkdir(exist_ok=True)
            print_success(f"✅ Directorio {directorio}/ verificado")
        
        # Crear archivos .gitkeep en directorios vacíos
        for directorio in directorios_crear:
            dir_path = Path(directorio)
            if dir_path.exists() and not any(dir_path.iterdir()):
                gitkeep_file = dir_path / ".gitkeep"
                gitkeep_file.touch()
                print_success(f"✅ .gitkeep creado en {directorio}/")
        
        print_success("Estructura de directorios optimizada")
        return True
        
    except Exception as e:
        print_error(f"Error optimizando estructura: {e}")
        return False

def generar_reporte_limpieza(resultados):
    """Generar reporte de limpieza"""
    try:
        print_info("Generando reporte de limpieza...")
        
        # Crear directorio de reportes si no existe
        reportes_dir = Path("reportes")
        reportes_dir.mkdir(exist_ok=True)
        
        # Generar reporte
        reporte = {
            'fecha': datetime.now().isoformat(),
            'limpieza': resultados,
            'resumen': {
                'total_operaciones': len(resultados),
                'operaciones_exitosas': sum(1 for r in resultados.values() if r),
                'operaciones_fallidas': sum(1 for r in resultados.values() if not r)
            }
        }
        
        # Guardar reporte
        reporte_file = reportes_dir / f"reporte_limpieza_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        import json
        with open(reporte_file, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print_success(f"Reporte de limpieza generado: {reporte_file}")
        return reporte_file
        
    except Exception as e:
        print_error(f"Error generando reporte: {e}")
        return None

def main():
    """Función principal del limpiador"""
    print_header()
    
    # Limpiar logs antiguos
    print_step(1, "Limpiando logs antiguos")
    logs_limpiados = limpiar_logs_antiguos()
    
    # Limpiar datos temporales
    print_step(2, "Limpiando datos temporales")
    datos_limpiados = limpiar_datos_temporales()
    
    # Limpiar cache de Python
    print_step(3, "Limpiando cache de Python")
    cache_limpiado = limpiar_cache_python()
    
    # Limpiar checkpoints de Jupyter
    print_step(4, "Limpiando checkpoints de Jupyter")
    checkpoints_limpiados = limpiar_checkpoints_jupyter()
    
    # Limpiar archivos duplicados
    print_step(5, "Limpiando archivos duplicados")
    duplicados_limpiados = limpiar_archivos_duplicados()
    
    # Optimizar estructura de directorios
    print_step(6, "Optimizando estructura de directorios")
    estructura_optimizada = optimizar_estructura_directorios()
    
    # Generar reporte
    print_step(7, "Generando reporte de limpieza")
    resultados = {
        'logs_antiguos': logs_limpiados,
        'datos_temporales': datos_limpiados,
        'cache_python': cache_limpiado,
        'checkpoints_jupyter': checkpoints_limpiados,
        'archivos_duplicados': duplicados_limpiados,
        'estructura_directorios': estructura_optimizada
    }
    
    reporte_file = generar_reporte_limpieza(resultados)
    
    # Mostrar resumen final
    print("\n" + "=" * 70)
    print("🎉 LIMPIEZA COMPLETADA")
    print("=" * 70)
    
    print(f"\n🧹 OPERACIONES DE LIMPIEZA:")
    print(f"   Logs antiguos: {'✅' if logs_limpiados else '❌'}")
    print(f"   Datos temporales: {'✅' if datos_limpiados else '❌'}")
    print(f"   Cache de Python: {'✅' if cache_limpiado else '❌'}")
    print(f"   Checkpoints Jupyter: {'✅' if checkpoints_limpiados else '❌'}")
    print(f"   Archivos duplicados: {'✅' if duplicados_limpiados else '❌'}")
    print(f"   Estructura directorios: {'✅' if estructura_optimizada else '❌'}")
    
    operaciones_exitosas = sum(1 for r in resultados.values() if r)
    total_operaciones = len(resultados)
    
    print(f"\n📊 RESUMEN:")
    print(f"   Operaciones exitosas: {operaciones_exitosas}/{total_operaciones}")
    print(f"   Tasa de éxito: {(operaciones_exitosas/total_operaciones*100):.1f}%")
    
    if reporte_file:
        print(f"\n📋 Reporte generado: {reporte_file}")
    
    print("\n🌾 Sistema METGO 3D limpiado exitosamente")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Limpieza interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)