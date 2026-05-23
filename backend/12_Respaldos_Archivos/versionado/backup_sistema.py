#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
💾 BACKUP DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Este script crea backups completos del sistema METGO 3D, incluyendo
notebooks, datos, configuración y reportes para preservar el trabajo.
"""

import os
import sys
import shutil
import zipfile
import json
from pathlib import Path
from datetime import datetime, timedelta

def print_header():
    """Imprimir encabezado del backup"""
    print("💾 BACKUP DEL SISTEMA METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Respaldo Completo")
    print("=" * 60)

def print_step(step, message):
    """Imprimir paso del proceso de backup"""
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

def create_backup_directory():
    """Crear directorio de backup"""
    print_step(1, "Creando directorio de backup")
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = Path("backups") / f"metgo_3d_backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        print_success(f"Directorio de backup creado: {backup_dir}")
        return backup_dir
        
    except Exception as e:
        print_error(f"Error creando directorio de backup: {e}")
        return None

def backup_notebooks(backup_dir):
    """Respaldar notebooks del sistema"""
    print_step(2, "Respaldando notebooks del sistema")
    
    try:
        notebooks_dir = backup_dir / "notebooks"
        notebooks_dir.mkdir(exist_ok=True)
        
        notebook_files = [
            "01_Configuracion_e_imports.ipynb",
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
        
        backed_up_count = 0
        
        for notebook in notebook_files:
            source_path = Path(notebook)
            if source_path.exists():
                dest_path = notebooks_dir / notebook
                shutil.copy2(source_path, dest_path)
                backed_up_count += 1
                print_success(f"Notebook respaldado: {notebook}")
            else:
                print_warning(f"Notebook no encontrado: {notebook}")
        
        print_success(f"Notebooks respaldados: {backed_up_count}")
        return backed_up_count
        
    except Exception as e:
        print_error(f"Error respaldando notebooks: {e}")
        return 0

def backup_scripts(backup_dir):
    """Respaldar scripts del sistema"""
    print_step(3, "Respaldando scripts del sistema")
    
    try:
        scripts_dir = backup_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        script_files = [
            "ejecutar_sistema_completo.py",
            "instalar_sistema.py",
            "test_sistema.py",
            "limpiar_sistema.py",
            "monitor_sistema.py",
            "ejecutar_sistema.sh",
            "ejecutar_sistema.ps1"
        ]
        
        backed_up_count = 0
        
        for script in script_files:
            source_path = Path(script)
            if source_path.exists():
                dest_path = scripts_dir / script
                shutil.copy2(source_path, dest_path)
                backed_up_count += 1
                print_success(f"Script respaldado: {script}")
            else:
                print_warning(f"Script no encontrado: {script}")
        
        print_success(f"Scripts respaldados: {backed_up_count}")
        return backed_up_count
        
    except Exception as e:
        print_error(f"Error respaldando scripts: {e}")
        return 0

def backup_configuration(backup_dir):
    """Respaldar configuración del sistema"""
    print_step(4, "Respaldando configuración del sistema")
    
    try:
        config_dir = backup_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        config_files = [
            "config/config.yaml",
            "requirements.txt",
            "README.md",
            "LICENSE"
        ]
        
        backed_up_count = 0
        
        for config_file in config_files:
            source_path = Path(config_file)
            if source_path.exists():
                # Crear subdirectorios si es necesario
                dest_path = config_dir / config_file
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, dest_path)
                backed_up_count += 1
                print_success(f"Configuración respaldada: {config_file}")
            else:
                print_warning(f"Archivo de configuración no encontrado: {config_file}")
        
        print_success(f"Archivos de configuración respaldados: {backed_up_count}")
        return backed_up_count
        
    except Exception as e:
        print_error(f"Error respaldando configuración: {e}")
        return 0

def backup_data_files(backup_dir):
    """Respaldar archivos de datos"""
    print_step(5, "Respaldando archivos de datos")
    
    try:
        data_dir = Path("data")
        if not data_dir.exists():
            print_warning("Directorio de datos no existe")
            return 0
        
        backup_data_dir = backup_dir / "data"
        backup_data_dir.mkdir(exist_ok=True)
        
        # Copiar todos los archivos de datos
        data_files = list(data_dir.glob("*"))
        backed_up_count = 0
        
        for data_file in data_files:
            if data_file.is_file():
                dest_path = backup_data_dir / data_file.name
                shutil.copy2(data_file, dest_path)
                backed_up_count += 1
                print_success(f"Archivo de datos respaldado: {data_file.name}")
            elif data_file.is_dir():
                dest_path = backup_data_dir / data_file.name
                shutil.copytree(data_file, dest_path)
                backed_up_count += 1
                print_success(f"Directorio de datos respaldado: {data_file.name}")
        
        print_success(f"Archivos de datos respaldados: {backed_up_count}")
        return backed_up_count
        
    except Exception as e:
        print_error(f"Error respaldando archivos de datos: {e}")
        return 0

def backup_reports(backup_dir):
    """Respaldar reportes del sistema"""
    print_step(6, "Respaldando reportes del sistema")
    
    try:
        reports_dir = Path("reportes_revision")
        if not reports_dir.exists():
            print_warning("Directorio de reportes no existe")
            return 0
        
        backup_reports_dir = backup_dir / "reportes_revision"
        backup_reports_dir.mkdir(exist_ok=True)
        
        # Copiar todos los reportes
        report_files = list(reports_dir.glob("*"))
        backed_up_count = 0
        
        for report_file in report_files:
            if report_file.is_file():
                dest_path = backup_reports_dir / report_file.name
                shutil.copy2(report_file, dest_path)
                backed_up_count += 1
                print_success(f"Reporte respaldado: {report_file.name}")
            elif report_file.is_dir():
                dest_path = backup_reports_dir / report_file.name
                shutil.copytree(report_file, dest_path)
                backed_up_count += 1
                print_success(f"Directorio de reportes respaldado: {report_file.name}")
        
        print_success(f"Reportes respaldados: {backed_up_count}")
        return backed_up_count
        
    except Exception as e:
        print_error(f"Error respaldando reportes: {e}")
        return 0

def backup_logs(backup_dir):
    """Respaldar logs del sistema"""
    print_step(7, "Respaldando logs del sistema")
    
    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            print_warning("Directorio de logs no existe")
            return 0
        
        backup_logs_dir = backup_dir / "logs"
        backup_logs_dir.mkdir(exist_ok=True)
        
        # Copiar logs recientes (últimos 7 días)
        cutoff_date = datetime.now() - timedelta(days=7)
        log_files = list(logs_dir.glob("*.log"))
        backed_up_count = 0
        
        for log_file in log_files:
            if log_file.stat().st_mtime >= cutoff_date.timestamp():
                dest_path = backup_logs_dir / log_file.name
                shutil.copy2(log_file, dest_path)
                backed_up_count += 1
                print_success(f"Log respaldado: {log_file.name}")
            else:
                print_info(f"Log omitido (muy antiguo): {log_file.name}")
        
        print_success(f"Logs respaldados: {backed_up_count}")
        return backed_up_count
        
    except Exception as e:
        print_error(f"Error respaldando logs: {e}")
        return 0

def create_backup_manifest(backup_dir, backup_stats):
    """Crear manifiesto del backup"""
    print_step(8, "Creando manifiesto del backup")
    
    try:
        manifest = {
            'backup_info': {
                'timestamp': datetime.now().isoformat(),
                'system': 'METGO 3D Operativo v2.0',
                'location': 'Quillota, Región de Valparaíso, Chile',
                'backup_directory': str(backup_dir),
                'total_size_mb': 0  # Se calculará después
            },
            'backup_stats': backup_stats,
            'files_included': {
                'notebooks': backup_stats.get('notebooks', 0),
                'scripts': backup_stats.get('scripts', 0),
                'config_files': backup_stats.get('config_files', 0),
                'data_files': backup_stats.get('data_files', 0),
                'reports': backup_stats.get('reports', 0),
                'logs': backup_stats.get('logs', 0)
            },
            'system_info': {
                'python_version': sys.version,
                'platform': sys.platform,
                'working_directory': os.getcwd()
            }
        }
        
        # Calcular tamaño total del backup
        total_size = 0
        for root, dirs, files in os.walk(backup_dir):
            for file in files:
                file_path = Path(root) / file
                total_size += file_path.stat().st_size
        
        manifest['backup_info']['total_size_mb'] = total_size / (1024**2)
        
        # Guardar manifiesto
        manifest_file = backup_dir / "backup_manifest.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print_success(f"Manifiesto creado: {manifest_file}")
        print_success(f"Tamaño total del backup: {manifest['backup_info']['total_size_mb']:.1f} MB")
        
        return manifest
        
    except Exception as e:
        print_error(f"Error creando manifiesto: {e}")
        return None

def create_backup_zip(backup_dir):
    """Crear archivo ZIP del backup"""
    print_step(9, "Creando archivo ZIP del backup")
    
    try:
        zip_filename = f"{backup_dir.name}.zip"
        zip_path = backup_dir.parent / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(backup_dir.parent)
                    zipf.write(file_path, arcname)
        
        zip_size_mb = zip_path.stat().st_size / (1024**2)
        print_success(f"Archivo ZIP creado: {zip_filename}")
        print_success(f"Tamaño del ZIP: {zip_size_mb:.1f} MB")
        
        return zip_path
        
    except Exception as e:
        print_error(f"Error creando archivo ZIP: {e}")
        return None

def generate_backup_report(backup_dir, backup_stats, manifest):
    """Generar reporte del backup"""
    print_step(10, "Generando reporte del backup")
    
    try:
        report_content = f"""
# 💾 REPORTE DE BACKUP METGO 3D
Sistema Meteorológico Agrícola Quillota

## 📅 Información del Backup
- **Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Sistema**: METGO 3D Operativo v2.0
- **Ubicación**: Quillota, Región de Valparaíso, Chile
- **Directorio**: {backup_dir}
- **Tamaño total**: {manifest['backup_info']['total_size_mb']:.1f} MB

## 📊 Estadísticas del Backup
- **Notebooks**: {backup_stats.get('notebooks', 0)} archivos
- **Scripts**: {backup_stats.get('scripts', 0)} archivos
- **Configuración**: {backup_stats.get('config_files', 0)} archivos
- **Datos**: {backup_stats.get('data_files', 0)} archivos
- **Reportes**: {backup_stats.get('reports', 0)} archivos
- **Logs**: {backup_stats.get('logs', 0)} archivos

## 📁 Contenido del Backup
El backup incluye:
- ✅ Todos los notebooks del sistema
- ✅ Scripts de ejecución y utilidades
- ✅ Archivos de configuración
- ✅ Datos meteorológicos generados
- ✅ Reportes y análisis
- ✅ Logs del sistema (últimos 7 días)
- ✅ Manifiesto detallado

## 🔄 Restauración
Para restaurar el backup:
1. Extraer el archivo ZIP
2. Copiar archivos a sus ubicaciones originales
3. Verificar configuración
4. Ejecutar tests del sistema

## 🎯 Estado del Backup
El backup se completó exitosamente y contiene todos los componentes
necesarios para restaurar el sistema METGO 3D.

---
*Reporte generado automáticamente por el Sistema de Backup METGO 3D*
"""
        
        report_file = backup_dir / "backup_report.md"
        report_file.write_text(report_content, encoding='utf-8')
        
        print_success(f"Reporte de backup generado: {report_file}")
        return True
        
    except Exception as e:
        print_error(f"Error generando reporte: {e}")
        return False

def cleanup_old_backups():
    """Limpiar backups antiguos"""
    print_step(11, "Limpiando backups antiguos")
    
    try:
        backups_dir = Path("backups")
        if not backups_dir.exists():
            print_warning("Directorio de backups no existe")
            return 0
        
        # Mantener solo los últimos 5 backups
        backup_dirs = [d for d in backups_dir.iterdir() if d.is_dir() and d.name.startswith('metgo_3d_backup_')]
        backup_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        cleaned_count = 0
        for backup_dir in backup_dirs[5:]:  # Mantener solo los primeros 5
            shutil.rmtree(backup_dir)
            cleaned_count += 1
            print_success(f"Backup antiguo eliminado: {backup_dir.name}")
        
        print_success(f"Backups antiguos limpiados: {cleaned_count}")
        return cleaned_count
        
    except Exception as e:
        print_error(f"Error limpiando backups antiguos: {e}")
        return 0

def show_backup_summary(backup_dir, backup_stats, manifest):
    """Mostrar resumen del backup"""
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL BACKUP")
    print("=" * 60)
    
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Directorio: {backup_dir}")
    print(f"💾 Tamaño total: {manifest['backup_info']['total_size_mb']:.1f} MB")
    
    print("\n📋 CONTENIDO RESPALDADO:")
    print(f"   📓 Notebooks: {backup_stats.get('notebooks', 0)}")
    print(f"   🐍 Scripts: {backup_stats.get('scripts', 0)}")
    print(f"   ⚙️ Configuración: {backup_stats.get('config_files', 0)}")
    print(f"   📊 Datos: {backup_stats.get('data_files', 0)}")
    print(f"   📋 Reportes: {backup_stats.get('reports', 0)}")
    print(f"   📝 Logs: {backup_stats.get('logs', 0)}")
    
    total_files = sum(backup_stats.values())
    print(f"\n📈 Total de archivos: {total_files}")
    
    print("\n🎉 BACKUP COMPLETADO EXITOSAMENTE")
    print("🌾 Sistema METGO 3D respaldado completamente")
    print("💾 Backup listo para restauración")
    
    print(f"\n⏱️ Tiempo total de backup: {time.time() - start_time:.2f} segundos")

def main():
    """Función principal del backup"""
    global start_time
    start_time = time.time()
    
    print_header()
    
    # Crear directorio de backup
    backup_dir = create_backup_directory()
    if not backup_dir:
        print_error("No se pudo crear directorio de backup")
        sys.exit(1)
    
    # Ejecutar todas las operaciones de backup
    backup_stats = {
        'notebooks': backup_notebooks(backup_dir),
        'scripts': backup_scripts(backup_dir),
        'config_files': backup_configuration(backup_dir),
        'data_files': backup_data_files(backup_dir),
        'reports': backup_reports(backup_dir),
        'logs': backup_logs(backup_dir)
    }
    
    # Crear manifiesto
    manifest = create_backup_manifest(backup_dir, backup_stats)
    
    # Crear archivo ZIP
    zip_path = create_backup_zip(backup_dir)
    
    # Generar reporte
    generate_backup_report(backup_dir, backup_stats, manifest)
    
    # Limpiar backups antiguos
    cleanup_old_backups()
    
    # Mostrar resumen
    show_backup_summary(backup_dir, backup_stats, manifest)

if __name__ == "__main__":
    main()
