#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 DIAGNÓSTICO COMPLETO METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Este script realiza un diagnóstico completo del sistema METGO 3D,
identificando problemas y proporcionando soluciones.
"""

import os
import sys
import time
import psutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import json
import importlib.util

def print_header():
    """Imprimir encabezado del diagnóstico"""
    print("🔍 DIAGNÓSTICO COMPLETO METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Diagnóstico Integral")
    print("=" * 60)

def print_step(step, message):
    """Imprimir paso del proceso de diagnóstico"""
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

def diagnosticar_sistema_operativo():
    """Diagnosticar sistema operativo"""
    print_step(1, "Diagnosticando sistema operativo")
    
    try:
        sistema_info = {
            'sistema': os.name,
            'plataforma': sys.platform,
            'version': sys.version,
            'arquitectura': os.uname().machine if hasattr(os, 'uname') else 'Unknown',
            'usuario': os.getenv('USER', 'Unknown'),
            'directorio_actual': os.getcwd()
        }
        
        print_success(f"Sistema operativo: {sistema_info['sistema']}")
        print_success(f"Plataforma: {sistema_info['plataforma']}")
        print_success(f"Usuario: {sistema_info['usuario']}")
        print_success(f"Directorio actual: {sistema_info['directorio_actual']}")
        
        return sistema_info
        
    except Exception as e:
        print_error(f"Error diagnosticando sistema operativo: {e}")
        return None

def diagnosticar_python():
    """Diagnosticar instalación de Python"""
    print_step(2, "Diagnosticando instalación de Python")
    
    try:
        python_info = {
            'version': sys.version,
            'version_info': sys.version_info,
            'ejecutable': sys.executable,
            'path': sys.path,
            'modulos_cargados': list(sys.modules.keys())
        }
        
        print_success(f"Versión de Python: {python_info['version']}")
        print_success(f"Ejecutable: {python_info['ejecutable']}")
        print_success(f"Módulos cargados: {len(python_info['modulos_cargados'])}")
        
        return python_info
        
    except Exception as e:
        print_error(f"Error diagnosticando Python: {e}")
        return None

def diagnosticar_dependencias():
    """Diagnosticar dependencias del sistema"""
    print_step(3, "Diagnosticando dependencias")
    
    try:
        dependencias_requeridas = [
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'requests',
            'yaml', 'psutil', 'sklearn', 'plotly', 'streamlit'
        ]
        
        dependencias_info = {}
        
        for dep in dependencias_requeridas:
            try:
                spec = importlib.util.find_spec(dep)
                if spec is not None:
                    dependencias_info[dep] = {
                        'instalada': True,
                        'ubicacion': spec.origin,
                        'version': getattr(__import__(dep), '__version__', 'Unknown')
                    }
                    print_success(f"Dependencia {dep}: Instalada (v{dependencias_info[dep]['version']})")
                else:
                    dependencias_info[dep] = {
                        'instalada': False,
                        'ubicacion': None,
                        'version': None
                    }
                    print_warning(f"Dependencia {dep}: No instalada")
            except Exception as e:
                dependencias_info[dep] = {
                    'instalada': False,
                    'ubicacion': None,
                    'version': None,
                    'error': str(e)
                }
                print_error(f"Dependencia {dep}: Error - {e}")
        
        return dependencias_info
        
    except Exception as e:
        print_error(f"Error diagnosticando dependencias: {e}")
        return None

def diagnosticar_archivos_sistema():
    """Diagnosticar archivos del sistema"""
    print_step(4, "Diagnosticando archivos del sistema")
    
    try:
        archivos_criticos = [
            'ejecutar_notebooks_maestro.py',
            'instalar_y_configurar.py',
            'verificar_sistema.py',
            'inicio_rapido.py',
            'resumen_sistema.py',
            'limpiar_y_optimizar.py',
            'monitoreo_tiempo_real.py',
            'respaldo_automatico.py',
            'analisis_rendimiento.py',
            'requirements.txt',
            'README.md',
            'LICENSE'
        ]
        
        archivos_info = {}
        
        for archivo in archivos_criticos:
            archivo_path = Path(archivo)
            if archivo_path.exists():
                stat = archivo_path.stat()
                archivos_info[archivo] = {
                    'existe': True,
                    'tamaño': stat.st_size,
                    'modificado': datetime.fromtimestamp(stat.st_mtime),
                    'permisos': oct(stat.st_mode)[-3:]
                }
                print_success(f"Archivo {archivo}: Presente ({stat.st_size} bytes)")
            else:
                archivos_info[archivo] = {
                    'existe': False,
                    'tamaño': 0,
                    'modificado': None,
                    'permisos': None
                }
                print_warning(f"Archivo {archivo}: No encontrado")
        
        return archivos_info
        
    except Exception as e:
        print_error(f"Error diagnosticando archivos: {e}")
        return None

def diagnosticar_directorios_sistema():
    """Diagnosticar directorios del sistema"""
    print_step(5, "Diagnosticando directorios del sistema")
    
    try:
        directorios_criticos = [
            'logs', 'data', 'reportes_revision', 'test_results',
            'tests', 'app', 'static', 'templates', 'backups', 'config'
        ]
        
        directorios_info = {}
        
        for directorio in directorios_criticos:
            dir_path = Path(directorio)
            if dir_path.exists():
                archivos_en_dir = list(dir_path.rglob('*'))
                archivos_count = len([f for f in archivos_en_dir if f.is_file()])
                tamaño_total = sum(f.stat().st_size for f in archivos_en_dir if f.is_file())
                
                directorios_info[directorio] = {
                    'existe': True,
                    'archivos': archivos_count,
                    'tamaño_total': tamaño_total,
                    'permisos': oct(dir_path.stat().st_mode)[-3:]
                }
                print_success(f"Directorio {directorio}: Presente ({archivos_count} archivos)")
            else:
                directorios_info[directorio] = {
                    'existe': False,
                    'archivos': 0,
                    'tamaño_total': 0,
                    'permisos': None
                }
                print_warning(f"Directorio {directorio}: No encontrado")
        
        return directorios_info
        
    except Exception as e:
        print_error(f"Error diagnosticando directorios: {e}")
        return None

def diagnosticar_notebooks():
    """Diagnosticar notebooks de Jupyter"""
    print_step(6, "Diagnosticando notebooks de Jupyter")
    
    try:
        notebooks = list(Path(".").glob("*.ipynb"))
        
        notebooks_info = {}
        
        for notebook in notebooks:
            try:
                stat = notebook.stat()
                notebooks_info[notebook.name] = {
                    'existe': True,
                    'tamaño': stat.st_size,
                    'modificado': datetime.fromtimestamp(stat.st_mtime),
                    'permisos': oct(stat.st_mode)[-3:]
                }
                print_success(f"Notebook {notebook.name}: Presente ({stat.st_size} bytes)")
            except Exception as e:
                notebooks_info[notebook.name] = {
                    'existe': False,
                    'tamaño': 0,
                    'modificado': None,
                    'permisos': None,
                    'error': str(e)
                }
                print_error(f"Notebook {notebook.name}: Error - {e}")
        
        return notebooks_info
        
    except Exception as e:
        print_error(f"Error diagnosticando notebooks: {e}")
        return None

def diagnosticar_configuraciones():
    """Diagnosticar configuraciones del sistema"""
    print_step(7, "Diagnosticando configuraciones")
    
    try:
        configuraciones_criticas = [
            'config/config.yaml',
            'metgo.env',
            '.gitignore',
            'Dockerfile',
            'docker-compose.yml'
        ]
        
        configuraciones_info = {}
        
        for config in configuraciones_criticas:
            config_path = Path(config)
            if config_path.exists():
                stat = config_path.stat()
                configuraciones_info[config] = {
                    'existe': True,
                    'tamaño': stat.st_size,
                    'modificado': datetime.fromtimestamp(stat.st_mtime),
                    'permisos': oct(stat.st_mode)[-3:]
                }
                print_success(f"Configuración {config}: Presente ({stat.st_size} bytes)")
            else:
                configuraciones_info[config] = {
                    'existe': False,
                    'tamaño': 0,
                    'modificado': None,
                    'permisos': None
                }
                print_warning(f"Configuración {config}: No encontrada")
        
        return configuraciones_info
        
    except Exception as e:
        print_error(f"Error diagnosticando configuraciones: {e}")
        return None

def diagnosticar_recursos_sistema():
    """Diagnosticar recursos del sistema"""
    print_step(8, "Diagnosticando recursos del sistema")
    
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memoria
        memoria = psutil.virtual_memory()
        
        # Disco
        disco = psutil.disk_usage('/')
        
        # Red
        red = psutil.net_io_counters()
        
        recursos_info = {
            'cpu': {
                'porcentaje': cpu_percent,
                'nucleos': cpu_count
            },
            'memoria': {
                'porcentaje': memoria.percent,
                'total_gb': memoria.total / (1024**3),
                'usada_gb': memoria.used / (1024**3),
                'disponible_gb': memoria.available / (1024**3)
            },
            'disco': {
                'porcentaje': disco.percent,
                'total_gb': disco.total / (1024**3),
                'usado_gb': disco.used / (1024**3),
                'libre_gb': disco.free / (1024**3)
            },
            'red': {
                'bytes_enviados_mb': red.bytes_sent / (1024**2),
                'bytes_recibidos_mb': red.bytes_recv / (1024**2)
            }
        }
        
        print_success(f"CPU: {cpu_percent:.1f}% ({cpu_count} núcleos)")
        print_success(f"Memoria: {memoria.percent:.1f}% ({memoria.used / (1024**3):.1f} GB usados)")
        print_success(f"Disco: {disco.percent:.1f}% ({disco.used / (1024**3):.1f} GB usados)")
        print_success(f"Red: {red.bytes_sent / (1024**2):.1f} MB enviados")
        
        return recursos_info
        
    except Exception as e:
        print_error(f"Error diagnosticando recursos: {e}")
        return None

def diagnosticar_procesos():
    """Diagnosticar procesos del sistema"""
    print_step(9, "Diagnosticando procesos del sistema")
    
    try:
        procesos_python = []
        procesos_sistema = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    procesos_python.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_percent': proc.info['memory_percent'],
                        'status': proc.info['status']
                    })
                else:
                    procesos_sistema.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_percent': proc.info['memory_percent'],
                        'status': proc.info['status']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        procesos_info = {
            'python': procesos_python,
            'sistema': procesos_sistema,
            'total_python': len(procesos_python),
            'total_sistema': len(procesos_sistema)
        }
        
        print_success(f"Procesos Python: {len(procesos_python)}")
        print_success(f"Procesos Sistema: {len(procesos_sistema)}")
        
        return procesos_info
        
    except Exception as e:
        print_error(f"Error diagnosticando procesos: {e}")
        return None

def diagnosticar_logs():
    """Diagnosticar logs del sistema"""
    print_step(10, "Diagnosticando logs del sistema")
    
    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            print_warning("Directorio de logs no existe")
            return {'existe': False, 'archivos': 0, 'tamaño_total': 0}
        
        logs_archivos = list(logs_dir.glob("*.log"))
        logs_info = {
            'existe': True,
            'archivos': len(logs_archivos),
            'tamaño_total': sum(log.stat().st_size for log in logs_archivos),
            'detalles': []
        }
        
        for log_file in logs_archivos:
            stat = log_file.stat()
            logs_info['detalles'].append({
                'nombre': log_file.name,
                'tamaño': stat.st_size,
                'modificado': datetime.fromtimestamp(stat.st_mtime)
            })
            print_success(f"Log {log_file.name}: {stat.st_size} bytes")
        
        print_success(f"Total de logs: {len(logs_archivos)} archivos")
        print_success(f"Tamaño total: {logs_info['tamaño_total']} bytes")
        
        return logs_info
        
    except Exception as e:
        print_error(f"Error diagnosticando logs: {e}")
        return None

def generar_reporte_diagnostico(diagnostico):
    """Generar reporte de diagnóstico"""
    print_step(11, "Generando reporte de diagnóstico")
    
    try:
        reporte_content = f"""
# 🔍 REPORTE DE DIAGNÓSTICO METGO 3D
Sistema Meteorológico Agrícola Quillota

## 📅 Información de Diagnóstico
- **Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Sistema**: METGO 3D Operativo v2.0
- **Ubicación**: Quillota, Región de Valparaíso, Chile

## 🖥️ Sistema Operativo
- **Sistema**: {diagnostico['sistema']['sistema']}
- **Plataforma**: {diagnostico['sistema']['plataforma']}
- **Usuario**: {diagnostico['sistema']['usuario']}
- **Directorio**: {diagnostico['sistema']['directorio_actual']}

## 🐍 Python
- **Versión**: {diagnostico['python']['version']}
- **Ejecutable**: {diagnostico['python']['ejecutable']}
- **Módulos**: {len(diagnostico['python']['modulos_cargados'])}

## 📦 Dependencias
"""
        
        for dep, info in diagnostico['dependencias'].items():
            if info['instalada']:
                reporte_content += f"- **{dep}**: ✅ Instalada (v{info['version']})\n"
            else:
                reporte_content += f"- **{dep}**: ❌ No instalada\n"
        
        reporte_content += f"""
## 📁 Archivos del Sistema
"""
        
        for archivo, info in diagnostico['archivos'].items():
            if info['existe']:
                reporte_content += f"- **{archivo}**: ✅ Presente ({info['tamaño']} bytes)\n"
            else:
                reporte_content += f"- **{archivo}**: ❌ No encontrado\n"
        
        reporte_content += f"""
## 📂 Directorios del Sistema
"""
        
        for directorio, info in diagnostico['directorios'].items():
            if info['existe']:
                reporte_content += f"- **{directorio}**: ✅ Presente ({info['archivos']} archivos)\n"
            else:
                reporte_content += f"- **{directorio}**: ❌ No encontrado\n"
        
        reporte_content += f"""
## 📓 Notebooks
"""
        
        for notebook, info in diagnostico['notebooks'].items():
            if info['existe']:
                reporte_content += f"- **{notebook}**: ✅ Presente ({info['tamaño']} bytes)\n"
            else:
                reporte_content += f"- **{notebook}**: ❌ No encontrado\n"
        
        reporte_content += f"""
## ⚙️ Configuraciones
"""
        
        for config, info in diagnostico['configuraciones'].items():
            if info['existe']:
                reporte_content += f"- **{config}**: ✅ Presente ({info['tamaño']} bytes)\n"
            else:
                reporte_content += f"- **{config}**: ❌ No encontrada\n"
        
        reporte_content += f"""
## 🖥️ Recursos del Sistema
- **CPU**: {diagnostico['recursos']['cpu']['porcentaje']:.1f}% ({diagnostico['recursos']['cpu']['nucleos']} núcleos)
- **Memoria**: {diagnostico['recursos']['memoria']['porcentaje']:.1f}% ({diagnostico['recursos']['memoria']['usada_gb']:.1f} GB usados)
- **Disco**: {diagnostico['recursos']['disco']['porcentaje']:.1f}% ({diagnostico['recursos']['disco']['usado_gb']:.1f} GB usados)
- **Red**: {diagnostico['recursos']['red']['bytes_enviados_mb']:.1f} MB enviados

## 🔄 Procesos
- **Procesos Python**: {diagnostico['procesos']['total_python']}
- **Procesos Sistema**: {diagnostico['procesos']['total_sistema']}

## 📋 Logs
- **Archivos de Log**: {diagnostico['logs']['archivos']}
- **Tamaño Total**: {diagnostico['logs']['tamaño_total']} bytes

## 🎯 Resumen del Diagnóstico
"""
        
        # Evaluar estado general
        archivos_faltantes = sum(1 for info in diagnostico['archivos'].values() if not info['existe'])
        directorios_faltantes = sum(1 for info in diagnostico['directorios'].values() if not info['existe'])
        dependencias_faltantes = sum(1 for info in diagnostico['dependencias'].values() if not info['instalada'])
        configuraciones_faltantes = sum(1 for info in diagnostico['configuraciones'].values() if not info['existe'])
        
        total_problemas = archivos_faltantes + directorios_faltantes + dependencias_faltantes + configuraciones_faltantes
        
        if total_problemas == 0:
            reporte_content += """
✅ **SISTEMA COMPLETO**: Todos los componentes están presentes y funcionando
🌾 **LISTO PARA USO**: El sistema METGO 3D está operativo
🚀 **RECOMENDACIÓN**: Ejecutar el sistema completo
"""
        elif total_problemas <= 3:
            reporte_content += """
⚠️ **SISTEMA PARCIALMENTE COMPLETO**: Algunos componentes faltan
🔧 **ACCIÓN REQUERIDA**: Revisar componentes faltantes
📚 **RECOMENDACIÓN**: Ejecutar instalación/configuración
"""
        else:
            reporte_content += """
❌ **SISTEMA INCOMPLETO**: Muchos componentes faltan
🔧 **ACCIÓN CRÍTICA**: Reinstalar sistema completo
📞 **RECOMENDACIÓN**: Ejecutar instalación desde cero
"""
        
        reporte_content += f"""
## 🚀 Soluciones Recomendadas
"""
        
        if dependencias_faltantes > 0:
            reporte_content += "- **Dependencias**: Ejecutar `pip install -r requirements.txt`\n"
        
        if archivos_faltantes > 0:
            reporte_content += "- **Archivos**: Verificar integridad del sistema y reinstalar componentes faltantes\n"
        
        if directorios_faltantes > 0:
            reporte_content += "- **Directorios**: Crear directorios faltantes y verificar permisos\n"
        
        if configuraciones_faltantes > 0:
            reporte_content += "- **Configuraciones**: Restaurar archivos de configuración desde respaldo\n"
        
        reporte_content += f"""
## 📋 Próximos Pasos
1. **Revisar problemas** identificados en el diagnóstico
2. **Aplicar soluciones** según las recomendaciones
3. **Verificar sistema** después de aplicar correcciones
4. **Ejecutar sistema** completo una vez resueltos los problemas

---
*Reporte generado automáticamente por el Diagnóstico METGO 3D*
"""
        
        reporte_file = Path("reportes_revision") / f"diagnostico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        reporte_file.write_text(reporte_content, encoding='utf-8')
        
        print_success(f"Reporte de diagnóstico generado: {reporte_file}")
        return True
        
    except Exception as e:
        print_error(f"Error generando reporte: {e}")
        return False

def mostrar_resumen_diagnostico(diagnostico):
    """Mostrar resumen del diagnóstico"""
    print("\n" + "=" * 60)
    print("🔍 RESUMEN DE DIAGNÓSTICO")
    print("=" * 60)
    
    # Evaluar estado general
    archivos_faltantes = sum(1 for info in diagnostico['archivos'].values() if not info['existe'])
    directorios_faltantes = sum(1 for info in diagnostico['directorios'].values() if not info['existe'])
    dependencias_faltantes = sum(1 for info in diagnostico['dependencias'].values() if not info['instalada'])
    configuraciones_faltantes = sum(1 for info in diagnostico['configuraciones'].values() if not info['existe'])
    
    total_problemas = archivos_faltantes + directorios_faltantes + dependencias_faltantes + configuraciones_faltantes
    
    print(f"📁 Archivos faltantes: {archivos_faltantes}")
    print(f"📂 Directorios faltantes: {directorios_faltantes}")
    print(f"📦 Dependencias faltantes: {dependencias_faltantes}")
    print(f"⚙️ Configuraciones faltantes: {configuraciones_faltantes}")
    print(f"📊 Total de problemas: {total_problemas}")
    
    print(f"\n🖥️ RECURSOS DEL SISTEMA:")
    print(f"   CPU: {diagnostico['recursos']['cpu']['porcentaje']:.1f}%")
    print(f"   Memoria: {diagnostico['recursos']['memoria']['porcentaje']:.1f}%")
    print(f"   Disco: {diagnostico['recursos']['disco']['porcentaje']:.1f}%")
    
    print(f"\n🔄 PROCESOS:")
    print(f"   Python: {diagnostico['procesos']['total_python']}")
    print(f"   Sistema: {diagnostico['procesos']['total_sistema']}")
    
    print(f"\n📋 LOGS:")
    print(f"   Archivos: {diagnostico['logs']['archivos']}")
    print(f"   Tamaño: {diagnostico['logs']['tamaño_total']} bytes")
    
    if total_problemas == 0:
        print("\n🎉 SISTEMA COMPLETO Y OPERATIVO")
        print("🌾 Todos los componentes están presentes y funcionando")
        print("🚀 El sistema METGO 3D está listo para uso")
    elif total_problemas <= 3:
        print("\n⚠️ SISTEMA PARCIALMENTE COMPLETO")
        print("🔧 Algunos componentes pueden requerir atención")
        print("📚 Revisar problemas identificados para detalles")
    else:
        print("\n❌ SISTEMA INCOMPLETO")
        print("🔧 Muchos componentes faltan o tienen problemas")
        print("📞 Ejecutar instalación completa del sistema")

def main():
    """Función principal del diagnóstico"""
    print_header()
    
    # Ejecutar diagnóstico completo
    diagnostico = {
        'sistema': diagnosticar_sistema_operativo(),
        'python': diagnosticar_python(),
        'dependencias': diagnosticar_dependencias(),
        'archivos': diagnosticar_archivos_sistema(),
        'directorios': diagnosticar_directorios_sistema(),
        'notebooks': diagnosticar_notebooks(),
        'configuraciones': diagnosticar_configuraciones(),
        'recursos': diagnosticar_recursos_sistema(),
        'procesos': diagnosticar_procesos(),
        'logs': diagnosticar_logs()
    }
    
    # Verificar que todas las métricas se obtuvieron
    diagnostico_valido = all(diagnostico.values())
    if not diagnostico_valido:
        print_error("No se pudieron obtener todas las métricas de diagnóstico")
        sys.exit(1)
    
    # Generar reporte
    generar_reporte_diagnostico(diagnostico)
    
    # Mostrar resumen
    mostrar_resumen_diagnostico(diagnostico)
    
    # Determinar código de salida
    archivos_faltantes = sum(1 for info in diagnostico['archivos'].values() if not info['existe'])
    directorios_faltantes = sum(1 for info in diagnostico['directorios'].values() if not info['existe'])
    dependencias_faltantes = sum(1 for info in diagnostico['dependencias'].values() if not info['instalada'])
    configuraciones_faltantes = sum(1 for info in diagnostico['configuraciones'].values() if not info['existe'])
    
    total_problemas = archivos_faltantes + directorios_faltantes + dependencias_faltantes + configuraciones_faltantes
    
    if total_problemas == 0:
        sys.exit(0)  # Sistema completo
    elif total_problemas <= 3:
        sys.exit(1)  # Sistema parcialmente completo
    else:
        sys.exit(2)  # Sistema incompleto

if __name__ == "__main__":
    main()
