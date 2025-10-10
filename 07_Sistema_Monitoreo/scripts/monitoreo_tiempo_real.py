#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 MONITOREO EN TIEMPO REAL METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Este script monitorea el sistema METGO 3D en tiempo real,
mostrando métricas de rendimiento y estado del sistema.
"""

import os
import sys
import time
import psutil
import threading
from datetime import datetime, timedelta
from pathlib import Path
import json

def print_header():
    """Imprimir encabezado del monitor"""
    print("📊 MONITOREO EN TIEMPO REAL METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Monitor de Sistema")
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

def obtener_metricas_sistema():
    """Obtener métricas del sistema"""
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memoria
        memoria = psutil.virtual_memory()
        memoria_percent = memoria.percent
        memoria_total = memoria.total / (1024**3)  # GB
        memoria_usada = memoria.used / (1024**3)  # GB
        
        # Disco
        disco = psutil.disk_usage('/')
        disco_percent = disco.percent
        disco_total = disco.total / (1024**3)  # GB
        disco_usado = disco.used / (1024**3)  # GB
        
        # Red
        red = psutil.net_io_counters()
        bytes_enviados = red.bytes_sent / (1024**2)  # MB
        bytes_recibidos = red.bytes_recv / (1024**2)  # MB
        
        return {
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count
            },
            'memoria': {
                'percent': memoria_percent,
                'total_gb': memoria_total,
                'usada_gb': memoria_usada
            },
            'disco': {
                'percent': disco_percent,
                'total_gb': disco_total,
                'usado_gb': disco_usado
            },
            'red': {
                'bytes_enviados_mb': bytes_enviados,
                'bytes_recibidos_mb': bytes_recibidos
            },
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print_error(f"Error obteniendo métricas: {e}")
        return None

def verificar_procesos_python():
    """Verificar procesos Python relacionados con METGO"""
    try:
        procesos_metgo = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if any(keyword in cmdline.lower() for keyword in [
                        'metgo', 'quillota', 'notebook', 'jupyter'
                    ]):
                        procesos_metgo.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline,
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_percent': proc.info['memory_percent']
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return procesos_metgo
    except Exception as e:
        print_error(f"Error verificando procesos: {e}")
        return []

def verificar_archivos_sistema():
    """Verificar archivos del sistema METGO"""
    try:
        archivos_importantes = [
            'ejecutar_notebooks_maestro.py',
            'instalar_y_configurar.py',
            'verificar_sistema.py',
            'inicio_rapido.py',
            'resumen_sistema.py',
            'limpiar_y_optimizar.py',
            'config/config.yaml',
            'requirements.txt',
            'README.md'
        ]
        
        estado_archivos = {}
        for archivo in archivos_importantes:
            archivo_path = Path(archivo)
            estado_archivos[archivo] = {
                'existe': archivo_path.exists(),
                'tamaño': archivo_path.stat().st_size if archivo_path.exists() else 0,
                'modificado': datetime.fromtimestamp(archivo_path.stat().st_mtime).isoformat() if archivo_path.exists() else None
            }
        
        return estado_archivos
    except Exception as e:
        print_error(f"Error verificando archivos: {e}")
        return {}

def verificar_directorios_sistema():
    """Verificar directorios del sistema METGO"""
    try:
        directorios_importantes = [
            'logs', 'data', 'reportes_revision', 'test_results',
            'tests', 'app', 'static', 'templates', 'backups', 'config'
        ]
        
        estado_directorios = {}
        for directorio in directorios_importantes:
            dir_path = Path(directorio)
            estado_directorios[directorio] = {
                'existe': dir_path.exists(),
                'archivos': len(list(dir_path.glob('*'))) if dir_path.exists() else 0,
                'tamaño_total': sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file()) if dir_path.exists() else 0
            }
        
        return estado_directorios
    except Exception as e:
        print_error(f"Error verificando directorios: {e}")
        return {}

def verificar_logs_recientes():
    """Verificar logs recientes"""
    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return []
        
        logs_recientes = []
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for log_file in logs_dir.glob("*.log"):
            if log_file.stat().st_mtime > cutoff_time.timestamp():
                logs_recientes.append({
                    'archivo': log_file.name,
                    'tamaño': log_file.stat().st_size,
                    'modificado': datetime.fromtimestamp(log_file.stat().st_mtime).isoformat(),
                    'lineas': sum(1 for _ in log_file.open('r', encoding='utf-8', errors='ignore'))
                })
        
        return logs_recientes
    except Exception as e:
        print_error(f"Error verificando logs: {e}")
        return []

def generar_reporte_monitoreo(metricas, procesos, archivos, directorios, logs):
    """Generar reporte de monitoreo"""
    try:
        reporte_content = f"""
# 📊 REPORTE DE MONITOREO METGO 3D
Sistema Meteorológico Agrícola Quillota

## 📅 Información de Monitoreo
- **Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Sistema**: METGO 3D Operativo v2.0
- **Ubicación**: Quillota, Región de Valparaíso, Chile

## 🖥️ Métricas del Sistema
### CPU
- **Uso**: {metricas['cpu']['percent']:.1f}%
- **Núcleos**: {metricas['cpu']['count']}

### Memoria
- **Uso**: {metricas['memoria']['percent']:.1f}%
- **Total**: {metricas['memoria']['total_gb']:.1f} GB
- **Usada**: {metricas['memoria']['usada_gb']:.1f} GB

### Disco
- **Uso**: {metricas['disco']['percent']:.1f}%
- **Total**: {metricas['disco']['total_gb']:.1f} GB
- **Usado**: {metricas['disco']['usado_gb']:.1f} GB

### Red
- **Bytes Enviados**: {metricas['red']['bytes_enviados_mb']:.1f} MB
- **Bytes Recibidos**: {metricas['red']['bytes_recibidos_mb']:.1f} MB

## 🔄 Procesos Python Activos
"""
        
        if procesos:
            for proc in procesos:
                reporte_content += f"""
### Proceso {proc['pid']}
- **Comando**: {proc['cmdline']}
- **CPU**: {proc['cpu_percent']:.1f}%
- **Memoria**: {proc['memory_percent']:.1f}%
"""
        else:
            reporte_content += "\nNo hay procesos Python relacionados con METGO activos.\n"
        
        reporte_content += f"""
## 📁 Estado de Archivos
"""
        
        for archivo, estado in archivos.items():
            status = "✅ EXISTE" if estado['existe'] else "❌ NO EXISTE"
            reporte_content += f"- **{archivo}**: {status}\n"
        
        reporte_content += f"""
## 📂 Estado de Directorios
"""
        
        for directorio, estado in directorios.items():
            status = "✅ EXISTE" if estado['existe'] else "❌ NO EXISTE"
            reporte_content += f"- **{directorio}**: {status} ({estado['archivos']} archivos)\n"
        
        reporte_content += f"""
## 📋 Logs Recientes (24h)
"""
        
        if logs:
            for log in logs:
                reporte_content += f"- **{log['archivo']}**: {log['lineas']} líneas ({log['tamaño']} bytes)\n"
        else:
            reporte_content += "\nNo hay logs recientes.\n"
        
        reporte_content += f"""
## 🎯 Estado General del Sistema
"""
        
        # Evaluar estado general
        archivos_faltantes = sum(1 for estado in archivos.values() if not estado['existe'])
        directorios_faltantes = sum(1 for estado in directorios.values() if not estado['existe'])
        
        if archivos_faltantes == 0 and directorios_faltantes == 0:
            reporte_content += """
✅ **SISTEMA COMPLETO**: Todos los archivos y directorios están presentes
🌾 **LISTO PARA USO**: El sistema METGO 3D está operativo
🚀 **RECOMENDACIÓN**: Ejecutar el sistema completo
"""
        elif archivos_faltantes <= 2 and directorios_faltantes <= 2:
            reporte_content += """
⚠️ **SISTEMA PARCIALMENTE COMPLETO**: Algunos archivos/directorios faltan
🔧 **ACCIÓN REQUERIDA**: Revisar archivos faltantes
📚 **RECOMENDACIÓN**: Ejecutar instalación/configuración
"""
        else:
            reporte_content += """
❌ **SISTEMA INCOMPLETO**: Muchos archivos/directorios faltan
🔧 **ACCIÓN CRÍTICA**: Reinstalar sistema completo
📞 **RECOMENDACIÓN**: Ejecutar instalación desde cero
"""
        
        reporte_content += f"""
---
*Reporte generado automáticamente por el Monitor METGO 3D*
"""
        
        reporte_file = Path("reportes_revision") / f"monitoreo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        reporte_file.write_text(reporte_content, encoding='utf-8')
        
        print_success(f"Reporte de monitoreo generado: {reporte_file}")
        return True
        
    except Exception as e:
        print_error(f"Error generando reporte: {e}")
        return False

def mostrar_metricas_tiempo_real(duracion_minutos=5):
    """Mostrar métricas en tiempo real"""
    print_step(1, f"Monitoreo en tiempo real ({duracion_minutos} minutos)")
    
    inicio = datetime.now()
    fin = inicio + timedelta(minutes=duracion_minutos)
    
    print_info("Presiona Ctrl+C para detener el monitoreo")
    
    try:
        while datetime.now() < fin:
            # Limpiar pantalla (funciona en la mayoría de terminales)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print_header()
            print(f"🕐 Monitoreo activo - Tiempo restante: {fin - datetime.now()}")
            
            # Obtener métricas
            metricas = obtener_metricas_sistema()
            if metricas:
                print(f"\n📊 MÉTRICAS DEL SISTEMA")
                print(f"CPU: {metricas['cpu']['percent']:.1f}% | Memoria: {metricas['memoria']['percent']:.1f}% | Disco: {metricas['disco']['percent']:.1f}%")
            
            # Verificar procesos
            procesos = verificar_procesos_python()
            if procesos:
                print(f"\n🔄 PROCESOS PYTHON ACTIVOS: {len(procesos)}")
                for proc in procesos[:3]:  # Mostrar solo los primeros 3
                    print(f"PID {proc['pid']}: {proc['cmdline'][:50]}...")
            
            # Verificar archivos críticos
            archivos = verificar_archivos_sistema()
            archivos_faltantes = sum(1 for estado in archivos.values() if not estado['existe'])
            print(f"\n📁 ARCHIVOS CRÍTICOS: {len(archivos) - archivos_faltantes}/{len(archivos)} presentes")
            
            # Verificar directorios críticos
            directorios = verificar_directorios_sistema()
            directorios_faltantes = sum(1 for estado in directorios.values() if not estado['existe'])
            print(f"📂 DIRECTORIOS CRÍTICOS: {len(directorios) - directorios_faltantes}/{len(directorios)} presentes")
            
            # Verificar logs recientes
            logs = verificar_logs_recientes()
            print(f"📋 LOGS RECIENTES: {len(logs)} archivos")
            
            # Estado general
            if archivos_faltantes == 0 and directorios_faltantes == 0:
                print(f"\n✅ SISTEMA COMPLETO Y OPERATIVO")
            elif archivos_faltantes <= 2 and directorios_faltantes <= 2:
                print(f"\n⚠️ SISTEMA PARCIALMENTE COMPLETO")
            else:
                print(f"\n❌ SISTEMA INCOMPLETO")
            
            print(f"\n🔄 Actualizando en 10 segundos...")
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Monitoreo detenido por el usuario")
        return True
    except Exception as e:
        print_error(f"Error en monitoreo: {e}")
        return False
    
    print(f"\n⏰ Monitoreo completado")
    return True

def mostrar_resumen_monitoreo():
    """Mostrar resumen de monitoreo"""
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE MONITOREO")
    print("=" * 60)
    
    # Obtener métricas actuales
    metricas = obtener_metricas_sistema()
    procesos = verificar_procesos_python()
    archivos = verificar_archivos_sistema()
    directorios = verificar_directorios_sistema()
    logs = verificar_logs_recientes()
    
    if metricas:
        print(f"🖥️ CPU: {metricas['cpu']['percent']:.1f}% | Memoria: {metricas['memoria']['percent']:.1f}% | Disco: {metricas['disco']['percent']:.1f}%")
    
    print(f"🔄 Procesos Python activos: {len(procesos)}")
    
    archivos_faltantes = sum(1 for estado in archivos.values() if not estado['existe'])
    directorios_faltantes = sum(1 for estado in directorios.values() if not estado['existe'])
    
    print(f"📁 Archivos críticos: {len(archivos) - archivos_faltantes}/{len(archivos)} presentes")
    print(f"📂 Directorios críticos: {len(directorios) - directorios_faltantes}/{len(directorios)} presentes")
    print(f"📋 Logs recientes: {len(logs)} archivos")
    
    # Generar reporte
    if generar_reporte_monitoreo(metricas, procesos, archivos, directorios, logs):
        print_success("Reporte de monitoreo generado exitosamente")
    
    # Estado general
    if archivos_faltantes == 0 and directorios_faltantes == 0:
        print("\n🎉 SISTEMA METGO 3D COMPLETO Y OPERATIVO")
        print("🌾 El sistema está listo para uso")
        print("🚀 Puedes ejecutar el sistema completo ahora")
    elif archivos_faltantes <= 2 and directorios_faltantes <= 2:
        print("\n⚠️ SISTEMA PARCIALMENTE COMPLETO")
        print("🔧 Algunos archivos/directorios pueden requerir atención")
        print("📚 Revisar archivos faltantes para detalles")
    else:
        print("\n❌ SISTEMA INCOMPLETO")
        print("🔧 Muchos archivos/directorios faltan")
        print("📞 Ejecutar instalación completa del sistema")

def main():
    """Función principal del monitor"""
    print_header()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--tiempo-real":
        # Modo tiempo real
        duracion = 5  # minutos por defecto
        if len(sys.argv) > 2:
            try:
                duracion = int(sys.argv[2])
            except ValueError:
                print_warning("Duración inválida, usando 5 minutos por defecto")
        
        mostrar_metricas_tiempo_real(duracion)
    else:
        # Modo resumen
        mostrar_resumen_monitoreo()
    
    # Determinar código de salida
    archivos = verificar_archivos_sistema()
    directorios = verificar_directorios_sistema()
    
    archivos_faltantes = sum(1 for estado in archivos.values() if not estado['existe'])
    directorios_faltantes = sum(1 for estado in directorios.values() if not estado['existe'])
    
    if archivos_faltantes == 0 and directorios_faltantes == 0:
        sys.exit(0)  # Sistema completo
    elif archivos_faltantes <= 2 and directorios_faltantes <= 2:
        sys.exit(1)  # Sistema parcialmente completo
    else:
        sys.exit(2)  # Sistema incompleto

if __name__ == "__main__":
    main()
