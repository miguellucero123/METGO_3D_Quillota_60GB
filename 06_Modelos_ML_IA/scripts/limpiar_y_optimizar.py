#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧹 LIMPIEZA Y OPTIMIZACIÓN METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Este script limpia, optimiza y mantiene el sistema METGO 3D para
asegurar el mejor rendimiento y organización.
"""

import os
import sys
import shutil
import glob
from pathlib import Path
from datetime import datetime, timedelta

def print_header():
    """Imprimir encabezado del limpiador"""
    print("🧹 LIMPIEZA Y OPTIMIZACIÓN METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Mantenimiento Automático")
    print("=" * 60)

def print_step(step, message):
    """Imprimir paso del proceso de limpieza"""
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

def print_info(message):
    """Imprimir mensaje informativo"""
    print(f"ℹ️ {message}")

def limpiar_logs(dias_retener=7):
    """Limpiar logs antiguos"""
    print_step(1, "Limpiando logs antiguos")
    
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print_warning("Directorio de logs no existe")
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=dias_retener)
    limpiados = 0
    
    for log_file in logs_dir.glob("*.log"):
        if log_file.stat().st_mtime < cutoff_date.timestamp():
            log_file.unlink()
            limpiados += 1
            print_success(f"Log eliminado: {log_file.name}")
    
    print_success(f"Logs limpiados: {limpiados}")
    return limpiados

def limpiar_archivos_temporales():
    """Limpiar archivos temporales"""
    print_step(2, "Limpiando archivos temporales")
    
    patrones_temporales = [
        "*.tmp", "*.temp", "*.pyc", "__pycache__", "*.pyo", "*.pyd",
        ".pytest_cache", "*.egg-info", "*.swp", "*.swo", "*~"
    ]
    
    limpiados = 0
    for patron in patrones_temporales:
        for archivo in glob.glob(patron, recursive=True):
            try:
                if os.path.isfile(archivo):
                    os.remove(archivo)
                    limpiados += 1
                    print_success(f"Archivo temporal eliminado: {archivo}")
                elif os.path.isdir(archivo):
                    shutil.rmtree(archivo)
                    limpiados += 1
                    print_success(f"Directorio temporal eliminado: {archivo}")
            except Exception as e:
                print_warning(f"No se pudo eliminar {archivo}: {e}")
    
    print_success(f"Archivos temporales limpiados: {limpiados}")
    return limpiados

def limpiar_resultados_pruebas():
    """Limpiar resultados de pruebas"""
    print_step(3, "Limpiando resultados de pruebas")
    
    test_dirs = ["test_results", "tests"]
    limpiados = 0
    
    for test_dir in test_dirs:
        test_path = Path(test_dir)
        if not test_path.exists():
            continue
        
        # Eliminar archivos de prueba específicos
        patrones_prueba = [
            "test_*.png", "test_*.jpg", "test_*.pdf", "test_*.csv",
            "test_*.xlsx", "temp_*.json", "debug_*.log"
        ]
        
        for patron in patrones_prueba:
            for archivo in test_path.glob(patron):
                archivo.unlink()
                limpiados += 1
                print_success(f"Archivo de prueba eliminado: {archivo}")
    
    print_success(f"Resultados de pruebas limpiados: {limpiados}")
    return limpiados

def limpiar_datos_antiguos(dias_retener=30):
    """Limpiar datos antiguos"""
    print_step(4, "Limpiando datos antiguos")
    
    data_dir = Path("data")
    if not data_dir.exists():
        print_warning("Directorio de datos no existe")
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=dias_retener)
    limpiados = 0
    
    # Patrones de archivos de datos a limpiar
    patrones_datos = [
        "datos_meteorologicos_*.csv",
        "datos_meteorologicos_*.xlsx",
        "datos_meteorologicos_*.json",
        "backup_*.csv",
        "backup_*.xlsx",
        "temp_*.csv",
        "temp_*.xlsx"
    ]
    
    for patron in patrones_datos:
        for archivo in data_dir.glob(patron):
            if archivo.stat().st_mtime < cutoff_date.timestamp():
                archivo.unlink()
                limpiados += 1
                print_success(f"Archivo de datos eliminado: {archivo.name}")
    
    print_success(f"Archivos de datos limpiados: {limpiados}")
    return limpiados

def limpiar_reportes_antiguos(dias_retener=14):
    """Limpiar reportes antiguos"""
    print_step(5, "Limpiando reportes antiguos")
    
    reports_dir = Path("reportes_revision")
    if not reports_dir.exists():
        print_warning("Directorio de reportes no existe")
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=dias_retener)
    limpiados = 0
    
    # Patrones de reportes a limpiar
    patrones_reportes = [
        "reporte_*.html", "reporte_*.pdf", "reporte_*.xlsx",
        "analisis_*.html", "analisis_*.pdf", "dashboard_*.html",
        "resumen_*.pdf"
    ]
    
    for patron in patrones_reportes:
        for archivo in reports_dir.glob(patron):
            if archivo.stat().st_mtime < cutoff_date.timestamp():
                archivo.unlink()
                limpiados += 1
                print_success(f"Reporte eliminado: {archivo.name}")
    
    print_success(f"Reportes limpiados: {limpiados}")
    return limpiados

def limpiar_backups_antiguos(dias_retener=30):
    """Limpiar backups antiguos"""
    print_step(6, "Limpiando backups antiguos")
    
    backups_dir = Path("backups")
    if not backups_dir.exists():
        print_warning("Directorio de backups no existe")
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=dias_retener)
    limpiados = 0
    
    for backup_file in backups_dir.glob("*"):
        if backup_file.stat().st_mtime < cutoff_date.timestamp():
            if backup_file.is_file():
                backup_file.unlink()
                limpiados += 1
                print_success(f"Backup eliminado: {backup_file.name}")
            elif backup_file.is_dir():
                shutil.rmtree(backup_file)
                limpiados += 1
                print_success(f"Directorio de backup eliminado: {backup_file.name}")
    
    print_success(f"Backups limpiados: {limpiados}")
    return limpiados

def limpiar_checkpoints_jupyter():
    """Limpiar checkpoints de Jupyter"""
    print_step(7, "Limpiando checkpoints de Jupyter")
    
    checkpoint_dirs = []
    
    # Buscar directorios .ipynb_checkpoints
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == ".ipynb_checkpoints":
                checkpoint_dirs.append(os.path.join(root, dir_name))
    
    limpiados = 0
    for checkpoint_dir in checkpoint_dirs:
        shutil.rmtree(checkpoint_dir)
        limpiados += 1
        print_success(f"Checkpoint eliminado: {checkpoint_dir}")
    
    print_success(f"Checkpoints de Jupyter limpiados: {limpiados}")
    return limpiados

def limpiar_cache_visualizaciones():
    """Limpiar caché de visualizaciones"""
    print_step(8, "Limpiando caché de visualizaciones")
    
    patrones_cache = ["*.png", "*.jpg", "*.jpeg", "*.pdf", "*.svg"]
    
    # Directorios donde buscar archivos de visualización
    directorios_busqueda = [".", "static", "app"]
    limpiados = 0
    
    for directorio in directorios_busqueda:
        if not Path(directorio).exists():
            continue
            
        for patron in patrones_cache:
            for archivo in Path(directorio).glob(patron):
                # Solo eliminar archivos que parecen ser temporales
                if any(keyword in archivo.name.lower() for keyword in [
                    "temp", "tmp", "test", "debug", "cache"
                ]):
                    archivo.unlink()
                    limpiados += 1
                    print_success(f"Archivo de visualización eliminado: {archivo}")
    
    print_success(f"Caché de visualizaciones limpiado: {limpiados}")
    return limpiados

def optimizar_directorios():
    """Optimizar estructura de directorios"""
    print_step(9, "Optimizando estructura de directorios")
    
    # Crear directorios si no existen
    directorios_requeridos = [
        "logs", "data", "reportes_revision", "test_results",
        "tests", "app", "static", "templates", "backups", "config"
    ]
    
    creados = 0
    for directorio in directorios_requeridos:
        dir_path = Path(directorio)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            creados += 1
            print_success(f"Directorio creado: {directorio}")
        else:
            print_info(f"Directorio ya existe: {directorio}")
    
    print_success(f"Directorios optimizados: {creados} creados")
    return creados

def generar_reporte_limpieza():
    """Generar reporte de limpieza"""
    print_step(10, "Generando reporte de limpieza")
    
    try:
        reporte_content = f"""
# 🧹 REPORTE DE LIMPIEZA METGO 3D
Sistema Meteorológico Agrícola Quillota

## 📅 Información de Limpieza
- **Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Sistema**: METGO 3D Operativo v2.0
- **Ubicación**: Quillota, Región de Valparaíso, Chile

## 📊 Resumen de Limpieza
- ✅ Logs antiguos limpiados
- ✅ Archivos temporales eliminados
- ✅ Resultados de pruebas limpiados
- ✅ Archivos de datos antiguos eliminados
- ✅ Reportes antiguos eliminados
- ✅ Backups antiguos eliminados
- ✅ Checkpoints de Jupyter limpiados
- ✅ Caché de visualizaciones limpiado
- ✅ Estructura de directorios optimizada

## 🎯 Estado del Sistema
El sistema METGO 3D ha sido limpiado y optimizado para:
- Mejor rendimiento
- Menor uso de espacio en disco
- Organización mejorada de archivos
- Preparación para nuevas ejecuciones

## 🚀 Próximos Pasos
1. Ejecutar el sistema completo: `python ejecutar_notebooks_maestro.py`
2. O usar scripts específicos del sistema operativo
3. Monitorear logs en el directorio `logs/`
4. Revisar datos generados en `data/`

---
*Reporte generado automáticamente por el Limpiador METGO 3D*
"""
        
        reporte_file = Path("reportes_revision") / f"limpieza_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        reporte_file.write_text(reporte_content, encoding='utf-8')
        
        print_success(f"Reporte de limpieza generado: {reporte_file}")
        return True
        
    except Exception as e:
        print_error(f"Error generando reporte: {e}")
        return False

def mostrar_resumen_limpieza(resultados):
    """Mostrar resumen de limpieza"""
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE LIMPIEZA")
    print("=" * 60)
    
    total_operaciones = len(resultados)
    operaciones_exitosas = sum(resultados.values())
    operaciones_fallidas = total_operaciones - operaciones_exitosas
    
    print(f"📈 Total de operaciones: {total_operaciones}")
    print(f"✅ Operaciones exitosas: {operaciones_exitosas}")
    print(f"❌ Operaciones fallidas: {operaciones_fallidas}")
    
    tasa_exito = (operaciones_exitosas / total_operaciones) * 100
    print(f"📊 Tasa de éxito: {tasa_exito:.1f}%")
    
    print("\n📋 DETALLE DE OPERACIONES:")
    for operacion, resultado in resultados.items():
        status = "✅ EXITOSA" if resultado else "❌ FALLIDA"
        print(f"   {operacion}: {status}")
    
    if tasa_exito >= 80:
        print("\n🎉 SISTEMA METGO 3D LIMPIADO EXITOSAMENTE")
        print("🌾 El sistema está optimizado y listo para uso")
        print("🚀 Puedes ejecutar el sistema completo ahora")
    elif tasa_exito >= 60:
        print("\n⚠️ LIMPIEZA PARCIALMENTE EXITOSA")
        print("🔧 Algunas operaciones pueden requerir atención manual")
        print("📚 Revisar errores para detalles")
    else:
        print("\n❌ LIMPIEZA REQUIERE ATENCIÓN")
        print("🔧 Revisar permisos y estructura de archivos")
        print("📞 Consultar documentación para troubleshooting")

def main():
    """Función principal del limpiador"""
    print_header()
    
    # Ejecutar todas las operaciones de limpieza
    resultados = {
        "Limpieza de logs": limpiar_logs(),
        "Limpieza de archivos temporales": limpiar_archivos_temporales(),
        "Limpieza de resultados de pruebas": limpiar_resultados_pruebas(),
        "Limpieza de datos antiguos": limpiar_datos_antiguos(),
        "Limpieza de reportes antiguos": limpiar_reportes_antiguos(),
        "Limpieza de backups antiguos": limpiar_backups_antiguos(),
        "Limpieza de checkpoints Jupyter": limpiar_checkpoints_jupyter(),
        "Limpieza de caché de visualizaciones": limpiar_cache_visualizaciones(),
        "Optimización de directorios": optimizar_directorios(),
        "Generación de reporte": generar_reporte_limpieza()
    }
    
    # Mostrar resumen
    mostrar_resumen_limpieza(resultados)
    
    # Determinar código de salida
    tasa_exito = (sum(resultados.values()) / len(resultados)) * 100
    if tasa_exito >= 80:
        sys.exit(0)  # Éxito
    elif tasa_exito >= 60:
        sys.exit(1)  # Advertencias
    else:
        sys.exit(2)  # Errores críticos

if __name__ == "__main__":
    main()
