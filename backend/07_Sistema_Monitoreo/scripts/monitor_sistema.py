#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 MONITOR DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Este script monitorea el estado del sistema METGO 3D, verificando
el funcionamiento de componentes críticos y generando reportes de estado.
"""

import os
import sys
import time
import psutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import json

def print_header():
    """Imprimir encabezado del monitor"""
    print("📊 MONITOR DEL SISTEMA METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Monitoreo en Tiempo Real")
    print("=" * 60)

def print_step(step, message):
    """Imprimir paso del proceso de monitoreo"""
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

def monitor_system_resources():
    """Monitorear recursos del sistema"""
    print_step(1, "Monitoreando recursos del sistema")
    
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memoria
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available = memory.available / (1024**3)  # GB
        
        # Disco
        disk = psutil.disk_usage('.')
        disk_percent = disk.percent
        disk_free = disk.free / (1024**3)  # GB
        
        # Procesos Python
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if 'python' in proc.info['name'].lower():
                    python_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        print_success("Recursos del sistema monitoreados")
        print(f"   🖥️ CPU: {cpu_percent}% (de {cpu_count} núcleos)")
        print(f"   💾 Memoria: {memory_percent}% ({memory_available:.1f} GB disponibles)")
        print(f"   💿 Disco: {disk_percent}% ({disk_free:.1f} GB libres)")
        print(f"   🐍 Procesos Python: {len(python_processes)}")
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'disk_percent': disk_percent,
            'python_processes': len(python_processes)
        }
        
    except Exception as e:
        print_error(f"Error monitoreando recursos: {e}")
        return None

def monitor_file_system():
    """Monitorear sistema de archivos"""
    print_step(2, "Monitoreando sistema de archivos")
    
    try:
        # Verificar directorios críticos
        critical_dirs = [
            "logs", "data", "reportes_revision", "test_results",
            "tests", "app", "static", "templates", "backups", "config"
        ]
        
        dir_status = {}
        total_size = 0
        
        for dir_name in critical_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                # Calcular tamaño del directorio
                dir_size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
                dir_size_mb = dir_size / (1024**2)
                total_size += dir_size_mb
                
                # Contar archivos
                file_count = len(list(dir_path.rglob('*')))
                
                dir_status[dir_name] = {
                    'exists': True,
                    'size_mb': dir_size_mb,
                    'file_count': file_count
                }
                
                print_success(f"Directorio {dir_name}: {dir_size_mb:.1f} MB, {file_count} archivos")
            else:
                dir_status[dir_name] = {
                    'exists': False,
                    'size_mb': 0,
                    'file_count': 0
                }
                print_warning(f"Directorio {dir_name}: No existe")
        
        print_success(f"Tamaño total del proyecto: {total_size:.1f} MB")
        
        return {
            'directories': dir_status,
            'total_size_mb': total_size
        }
        
    except Exception as e:
        print_error(f"Error monitoreando sistema de archivos: {e}")
        return None

def monitor_dependencies():
    """Monitorear dependencias del sistema"""
    print_step(3, "Monitoreando dependencias del sistema")
    
    critical_packages = [
        "pandas", "numpy", "matplotlib", "seaborn", 
        "sklearn", "requests", "plotly", "streamlit", "yaml"
    ]
    
    package_status = {}
    
    for package in critical_packages:
        try:
            if package == "yaml":
                import yaml
                version = yaml.__version__
            elif package == "sklearn":
                import sklearn
                version = sklearn.__version__
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'Unknown')
            
            package_status[package] = {
                'available': True,
                'version': version
            }
            print_success(f"{package}: {version}")
            
        except ImportError:
            package_status[package] = {
                'available': False,
                'version': None
            }
            print_error(f"{package}: No disponible")
    
    available_count = sum(1 for status in package_status.values() if status['available'])
    print_success(f"Dependencias disponibles: {available_count}/{len(critical_packages)}")
    
    return package_status

def monitor_notebooks():
    """Monitorear notebooks del sistema"""
    print_step(4, "Monitoreando notebooks del sistema")
    
    expected_notebooks = [
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
    
    notebook_status = {}
    
    for notebook in expected_notebooks:
        notebook_path = Path(notebook)
        if notebook_path.exists():
            # Obtener información del archivo
            stat = notebook_path.stat()
            size_mb = stat.st_size / (1024**2)
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            
            notebook_status[notebook] = {
                'exists': True,
                'size_mb': size_mb,
                'modified': modified_time.strftime('%Y-%m-%d %H:%M:%S'),
                'age_days': (datetime.now() - modified_time).days
            }
            
            print_success(f"{notebook}: {size_mb:.1f} MB, modificado {modified_time.strftime('%d/%m/%Y')}")
        else:
            notebook_status[notebook] = {
                'exists': False,
                'size_mb': 0,
                'modified': None,
                'age_days': None
            }
            print_error(f"{notebook}: No encontrado")
    
    existing_count = sum(1 for status in notebook_status.values() if status['exists'])
    print_success(f"Notebooks encontrados: {existing_count}/{len(expected_notebooks)}")
    
    return notebook_status

def monitor_logs():
    """Monitorear logs del sistema"""
    print_step(5, "Monitoreando logs del sistema")
    
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print_warning("Directorio de logs no existe")
        return None
    
    try:
        log_files = list(logs_dir.glob("*.log"))
        log_status = {}
        
        total_log_size = 0
        recent_logs = 0
        
        for log_file in log_files:
            stat = log_file.stat()
            size_mb = stat.st_size / (1024**2)
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            age_hours = (datetime.now() - modified_time).total_seconds() / 3600
            
            total_log_size += size_mb
            
            if age_hours < 24:  # Logs de las últimas 24 horas
                recent_logs += 1
            
            log_status[log_file.name] = {
                'size_mb': size_mb,
                'modified': modified_time.strftime('%Y-%m-%d %H:%M:%S'),
                'age_hours': age_hours
            }
            
            print_success(f"{log_file.name}: {size_mb:.1f} MB, {age_hours:.1f} horas")
        
        print_success(f"Total logs: {len(log_files)} archivos, {total_log_size:.1f} MB")
        print_success(f"Logs recientes (24h): {recent_logs}")
        
        return {
            'log_files': log_status,
            'total_size_mb': total_log_size,
            'recent_logs': recent_logs
        }
        
    except Exception as e:
        print_error(f"Error monitoreando logs: {e}")
        return None

def monitor_data_files():
    """Monitorear archivos de datos"""
    print_step(6, "Monitoreando archivos de datos")
    
    data_dir = Path("data")
    if not data_dir.exists():
        print_warning("Directorio de datos no existe")
        return None
    
    try:
        data_files = list(data_dir.glob("*"))
        data_status = {}
        
        total_data_size = 0
        recent_data = 0
        
        for data_file in data_files:
            if data_file.is_file():
                stat = data_file.stat()
                size_mb = stat.st_size / (1024**2)
                modified_time = datetime.fromtimestamp(stat.st_mtime)
                age_hours = (datetime.now() - modified_time).total_seconds() / 3600
                
                total_data_size += size_mb
                
                if age_hours < 24:  # Datos de las últimas 24 horas
                    recent_data += 1
                
                data_status[data_file.name] = {
                    'size_mb': size_mb,
                    'modified': modified_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'age_hours': age_hours
                }
                
                print_success(f"{data_file.name}: {size_mb:.1f} MB, {age_hours:.1f} horas")
        
        print_success(f"Total archivos de datos: {len(data_files)}, {total_data_size:.1f} MB")
        print_success(f"Datos recientes (24h): {recent_data}")
        
        return {
            'data_files': data_status,
            'total_size_mb': total_data_size,
            'recent_data': recent_data
        }
        
    except Exception as e:
        print_error(f"Error monitoreando datos: {e}")
        return None

def monitor_system_health():
    """Monitorear salud general del sistema"""
    print_step(7, "Monitoreando salud general del sistema")
    
    health_checks = {
        'python_version': sys.version.split()[0],
        'platform': sys.platform,
        'working_directory': os.getcwd(),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Verificar scripts ejecutables
    scripts = ["ejecutar_sistema_completo.py", "instalar_sistema.py", "test_sistema.py"]
    executable_scripts = []
    
    for script in scripts:
        if Path(script).exists():
            executable_scripts.append(script)
            print_success(f"Script disponible: {script}")
        else:
            print_warning(f"Script faltante: {script}")
    
    health_checks['executable_scripts'] = executable_scripts
    
    # Verificar configuración
    config_file = Path("config/config.yaml")
    if config_file.exists():
        health_checks['config_exists'] = True
        print_success("Archivo de configuración encontrado")
    else:
        health_checks['config_exists'] = False
        print_warning("Archivo de configuración faltante")
    
    print_success("Salud del sistema monitoreada")
    
    return health_checks

def generate_monitoring_report(monitoring_data):
    """Generar reporte de monitoreo"""
    print_step(8, "Generando reporte de monitoreo")
    
    try:
        report_content = f"""
# 📊 REPORTE DE MONITOREO METGO 3D
Sistema Meteorológico Agrícola Quillota

## 📅 Información del Monitoreo
- **Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Sistema**: METGO 3D Operativo v2.0
- **Ubicación**: Quillota, Región de Valparaíso, Chile
- **Python**: {monitoring_data.get('system_health', {}).get('python_version', 'Unknown')}
- **Plataforma**: {monitoring_data.get('system_health', {}).get('platform', 'Unknown')}

## 🖥️ Recursos del Sistema
- **CPU**: {monitoring_data.get('system_resources', {}).get('cpu_percent', 'N/A')}%
- **Memoria**: {monitoring_data.get('system_resources', {}).get('memory_percent', 'N/A')}%
- **Disco**: {monitoring_data.get('system_resources', {}).get('disk_percent', 'N/A')}%
- **Procesos Python**: {monitoring_data.get('system_resources', {}).get('python_processes', 'N/A')}

## 📁 Sistema de Archivos
- **Tamaño total**: {monitoring_data.get('file_system', {}).get('total_size_mb', 'N/A')} MB
- **Directorios críticos**: {len([d for d in monitoring_data.get('file_system', {}).get('directories', {}).values() if d.get('exists', False)])} disponibles

## 📦 Dependencias
- **Paquetes disponibles**: {sum(1 for p in monitoring_data.get('dependencies', {}).values() if p.get('available', False))} de {len(monitoring_data.get('dependencies', {}))}

## 📓 Notebooks
- **Notebooks encontrados**: {sum(1 for n in monitoring_data.get('notebooks', {}).values() if n.get('exists', False))} de {len(monitoring_data.get('notebooks', {}))}

## 📋 Logs
- **Archivos de log**: {len(monitoring_data.get('logs', {}).get('log_files', {}))}
- **Tamaño total**: {monitoring_data.get('logs', {}).get('total_size_mb', 'N/A')} MB
- **Logs recientes**: {monitoring_data.get('logs', {}).get('recent_logs', 'N/A')}

## 📊 Datos
- **Archivos de datos**: {len(monitoring_data.get('data_files', {}).get('data_files', {}))}
- **Tamaño total**: {monitoring_data.get('data_files', {}).get('total_size_mb', 'N/A')} MB
- **Datos recientes**: {monitoring_data.get('data_files', {}).get('recent_data', 'N/A')}

## 🎯 Estado General
El sistema METGO 3D está {'✅ OPERATIVO' if monitoring_data.get('overall_status', False) else '⚠️ REQUIERE ATENCIÓN'}

## 🚀 Recomendaciones
- Monitorear recursos del sistema regularmente
- Limpiar logs antiguos periódicamente
- Verificar dependencias antes de ejecutar
- Mantener backups actualizados

---
*Reporte generado automáticamente por el Monitor METGO 3D*
"""
        
        report_file = Path("reportes_revision") / f"monitoreo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_file.parent.mkdir(exist_ok=True)
        report_file.write_text(report_content, encoding='utf-8')
        
        print_success(f"Reporte de monitoreo generado: {report_file}")
        return True
        
    except Exception as e:
        print_error(f"Error generando reporte: {e}")
        return False

def show_monitoring_summary(monitoring_data):
    """Mostrar resumen de monitoreo"""
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE MONITOREO")
    print("=" * 60)
    
    # Recursos del sistema
    resources = monitoring_data.get('system_resources', {})
    if resources:
        print(f"🖥️ CPU: {resources.get('cpu_percent', 'N/A')}%")
        print(f"💾 Memoria: {resources.get('memory_percent', 'N/A')}%")
        print(f"💿 Disco: {resources.get('disk_percent', 'N/A')}%")
        print(f"🐍 Procesos Python: {resources.get('python_processes', 'N/A')}")
    
    # Sistema de archivos
    file_system = monitoring_data.get('file_system', {})
    if file_system:
        print(f"📁 Tamaño total: {file_system.get('total_size_mb', 'N/A')} MB")
    
    # Dependencias
    dependencies = monitoring_data.get('dependencies', {})
    if dependencies:
        available_count = sum(1 for p in dependencies.values() if p.get('available', False))
        total_count = len(dependencies)
        print(f"📦 Dependencias: {available_count}/{total_count} disponibles")
    
    # Notebooks
    notebooks = monitoring_data.get('notebooks', {})
    if notebooks:
        existing_count = sum(1 for n in notebooks.values() if n.get('exists', False))
        total_count = len(notebooks)
        print(f"📓 Notebooks: {existing_count}/{total_count} encontrados")
    
    # Estado general
    overall_status = monitoring_data.get('overall_status', False)
    if overall_status:
        print("\n🎉 SISTEMA METGO 3D OPERATIVO")
        print("🌾 Todas las funcionalidades principales funcionando")
        print("🚀 Sistema listo para ejecución completa")
    else:
        print("\n⚠️ SISTEMA REQUIERE ATENCIÓN")
        print("🔧 Revisar componentes con problemas")
        print("📚 Consultar logs para detalles")
    
    print(f"\n⏱️ Tiempo total de monitoreo: {time.time() - start_time:.2f} segundos")

def main():
    """Función principal del monitor"""
    global start_time
    start_time = time.time()
    
    print_header()
    
    # Ejecutar todas las operaciones de monitoreo
    monitoring_data = {
        'system_resources': monitor_system_resources(),
        'file_system': monitor_file_system(),
        'dependencies': monitor_dependencies(),
        'notebooks': monitor_notebooks(),
        'logs': monitor_logs(),
        'data_files': monitor_data_files(),
        'system_health': monitor_system_health()
    }
    
    # Determinar estado general
    overall_status = (
        monitoring_data['system_resources'] is not None and
        monitoring_data['file_system'] is not None and
        monitoring_data['dependencies'] is not None and
        monitoring_data['notebooks'] is not None
    )
    
    monitoring_data['overall_status'] = overall_status
    
    # Generar reporte
    generate_monitoring_report(monitoring_data)
    
    # Mostrar resumen
    show_monitoring_summary(monitoring_data)

if __name__ == "__main__":
    main()
