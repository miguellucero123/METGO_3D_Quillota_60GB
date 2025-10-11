#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚡ ANÁLISIS DE RENDIMIENTO METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Este script analiza el rendimiento del sistema METGO 3D,
identificando cuellos de botella y optimizaciones.
"""

import os
import sys
import time
import psutil
import threading
from datetime import datetime, timedelta
from pathlib import Path
import json
import subprocess

def print_header():
    """Imprimir encabezado del analizador"""
    print("⚡ ANÁLISIS DE RENDIMIENTO METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Análisis de Performance")
    print("=" * 60)

def print_step(step, message):
    """Imprimir paso del proceso de análisis"""
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

def medir_tiempo_ejecucion(func, *args, **kwargs):
    """Medir tiempo de ejecución de una función"""
    inicio = time.time()
    try:
        resultado = func(*args, **kwargs)
        fin = time.time()
        tiempo_ejecucion = fin - inicio
        return resultado, tiempo_ejecucion, None
    except Exception as e:
        fin = time.time()
        tiempo_ejecucion = fin - inicio
        return None, tiempo_ejecucion, str(e)

def analizar_rendimiento_cpu():
    """Analizar rendimiento de CPU"""
    print_step(1, "Analizando rendimiento de CPU")
    
    try:
        # Obtener métricas de CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Análisis de carga
        if cpu_percent < 25:
            estado_cpu = "ÓPTIMO"
            recomendacion_cpu = "CPU funcionando eficientemente"
        elif cpu_percent < 50:
            estado_cpu = "BUENO"
            recomendacion_cpu = "CPU con carga moderada"
        elif cpu_percent < 75:
            estado_cpu = "MODERADO"
            recomendacion_cpu = "CPU con carga alta, monitorear"
        else:
            estado_cpu = "CRÍTICO"
            recomendacion_cpu = "CPU sobrecargado, optimizar procesos"
        
        return {
            'porcentaje': cpu_percent,
            'nucleos': cpu_count,
            'frecuencia': cpu_freq.current if cpu_freq else None,
            'estado': estado_cpu,
            'recomendacion': recomendacion_cpu
        }
        
    except Exception as e:
        print_error(f"Error analizando CPU: {e}")
        return None

def analizar_rendimiento_memoria():
    """Analizar rendimiento de memoria"""
    print_step(2, "Analizando rendimiento de memoria")
    
    try:
        # Obtener métricas de memoria
        memoria = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Análisis de uso de memoria
        if memoria.percent < 50:
            estado_memoria = "ÓPTIMO"
            recomendacion_memoria = "Memoria funcionando eficientemente"
        elif memoria.percent < 75:
            estado_memoria = "BUENO"
            recomendacion_memoria = "Memoria con uso moderado"
        elif memoria.percent < 90:
            estado_memoria = "MODERADO"
            recomendacion_memoria = "Memoria con uso alto, monitorear"
        else:
            estado_memoria = "CRÍTICO"
            recomendacion_memoria = "Memoria casi agotada, liberar recursos"
        
        return {
            'porcentaje': memoria.percent,
            'total_gb': memoria.total / (1024**3),
            'usada_gb': memoria.used / (1024**3),
            'disponible_gb': memoria.available / (1024**3),
            'swap_percent': swap.percent,
            'estado': estado_memoria,
            'recomendacion': recomendacion_memoria
        }
        
    except Exception as e:
        print_error(f"Error analizando memoria: {e}")
        return None

def analizar_rendimiento_disco():
    """Analizar rendimiento de disco"""
    print_step(3, "Analizando rendimiento de disco")
    
    try:
        # Obtener métricas de disco
        disco = psutil.disk_usage('/')
        
        # Análisis de uso de disco
        if disco.percent < 50:
            estado_disco = "ÓPTIMO"
            recomendacion_disco = "Disco con espacio suficiente"
        elif disco.percent < 75:
            estado_disco = "BUENO"
            recomendacion_disco = "Disco con uso moderado"
        elif disco.percent < 90:
            estado_disco = "MODERADO"
            recomendacion_disco = "Disco con uso alto, considerar limpieza"
        else:
            estado_disco = "CRÍTICO"
            recomendacion_disco = "Disco casi lleno, liberar espacio urgentemente"
        
        return {
            'porcentaje': disco.percent,
            'total_gb': disco.total / (1024**3),
            'usado_gb': disco.used / (1024**3),
            'libre_gb': disco.free / (1024**3),
            'estado': estado_disco,
            'recomendacion': recomendacion_disco
        }
        
    except Exception as e:
        print_error(f"Error analizando disco: {e}")
        return None

def analizar_rendimiento_red():
    """Analizar rendimiento de red"""
    print_step(4, "Analizando rendimiento de red")
    
    try:
        # Obtener métricas de red
        red = psutil.net_io_counters()
        
        # Calcular velocidades (aproximadas)
        bytes_enviados_mb = red.bytes_sent / (1024**2)
        bytes_recibidos_mb = red.bytes_recv / (1024**2)
        
        # Análisis de uso de red
        if bytes_enviados_mb < 100 and bytes_recibidos_mb < 100:
            estado_red = "ÓPTIMO"
            recomendacion_red = "Red con uso mínimo"
        elif bytes_enviados_mb < 500 and bytes_recibidos_mb < 500:
            estado_red = "BUENO"
            recomendacion_red = "Red con uso moderado"
        elif bytes_enviados_mb < 1000 and bytes_recibidos_mb < 1000:
            estado_red = "MODERADO"
            recomendacion_red = "Red con uso alto, monitorear"
        else:
            estado_red = "CRÍTICO"
            recomendacion_red = "Red con uso muy alto, optimizar transferencias"
        
        return {
            'bytes_enviados_mb': bytes_enviados_mb,
            'bytes_recibidos_mb': bytes_recibidos_mb,
            'paquetes_enviados': red.packets_sent,
            'paquetes_recibidos': red.packets_recv,
            'estado': estado_red,
            'recomendacion': recomendacion_red
        }
        
    except Exception as e:
        print_error(f"Error analizando red: {e}")
        return None

def analizar_rendimiento_procesos():
    """Analizar rendimiento de procesos"""
    print_step(5, "Analizando rendimiento de procesos")
    
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
        
        # Análisis de procesos
        total_procesos = len(procesos_python) + len(procesos_sistema)
        
        if total_procesos < 50:
            estado_procesos = "ÓPTIMO"
            recomendacion_procesos = "Sistema con pocos procesos activos"
        elif total_procesos < 100:
            estado_procesos = "BUENO"
            recomendacion_procesos = "Sistema con cantidad moderada de procesos"
        elif total_procesos < 200:
            estado_procesos = "MODERADO"
            recomendacion_procesos = "Sistema con muchos procesos, monitorear"
        else:
            estado_procesos = "CRÍTICO"
            recomendacion_procesos = "Sistema sobrecargado con procesos"
        
        return {
            'total_procesos': total_procesos,
            'procesos_python': len(procesos_python),
            'procesos_sistema': len(procesos_sistema),
            'estado': estado_procesos,
            'recomendacion': recomendacion_procesos,
            'detalles_python': procesos_python[:5],  # Solo los primeros 5
            'detalles_sistema': procesos_sistema[:5]  # Solo los primeros 5
        }
        
    except Exception as e:
        print_error(f"Error analizando procesos: {e}")
        return None

def analizar_rendimiento_archivos():
    """Analizar rendimiento de archivos"""
    print_step(6, "Analizando rendimiento de archivos")
    
    try:
        # Analizar archivos del sistema METGO
        archivos_importantes = [
            'ejecutar_notebooks_maestro.py',
            'instalar_y_configurar.py',
            'verificar_sistema.py',
            'inicio_rapido.py',
            'resumen_sistema.py',
            'limpiar_y_optimizar.py',
            'monitoreo_tiempo_real.py',
            'respaldo_automatico.py'
        ]
        
        archivos_analizados = []
        total_tamaño = 0
        
        for archivo in archivos_importantes:
            archivo_path = Path(archivo)
            if archivo_path.exists():
                tamaño = archivo_path.stat().st_size
                total_tamaño += tamaño
                archivos_analizados.append({
                    'nombre': archivo,
                    'tamaño_bytes': tamaño,
                    'tamaño_kb': tamaño / 1024,
                    'existe': True
                })
            else:
                archivos_analizados.append({
                    'nombre': archivo,
                    'tamaño_bytes': 0,
                    'tamaño_kb': 0,
                    'existe': False
                })
        
        # Análisis de archivos
        archivos_presentes = sum(1 for archivo in archivos_analizados if archivo['existe'])
        total_archivos = len(archivos_analizados)
        
        if archivos_presentes == total_archivos:
            estado_archivos = "ÓPTIMO"
            recomendacion_archivos = "Todos los archivos del sistema están presentes"
        elif archivos_presentes >= total_archivos * 0.8:
            estado_archivos = "BUENO"
            recomendacion_archivos = "La mayoría de archivos del sistema están presentes"
        elif archivos_presentes >= total_archivos * 0.5:
            estado_archivos = "MODERADO"
            recomendacion_archivos = "Algunos archivos del sistema faltan"
        else:
            estado_archivos = "CRÍTICO"
            recomendacion_archivos = "Muchos archivos del sistema faltan"
        
        return {
            'total_archivos': total_archivos,
            'archivos_presentes': archivos_presentes,
            'total_tamaño_kb': total_tamaño / 1024,
            'estado': estado_archivos,
            'recomendacion': recomendacion_archivos,
            'detalles': archivos_analizados
        }
        
    except Exception as e:
        print_error(f"Error analizando archivos: {e}")
        return None

def analizar_rendimiento_directorios():
    """Analizar rendimiento de directorios"""
    print_step(7, "Analizando rendimiento de directorios")
    
    try:
        # Analizar directorios del sistema METGO
        directorios_importantes = [
            'logs', 'data', 'reportes_revision', 'test_results',
            'tests', 'app', 'static', 'templates', 'backups', 'config'
        ]
        
        directorios_analizados = []
        total_archivos = 0
        total_tamaño = 0
        
        for directorio in directorios_importantes:
            dir_path = Path(directorio)
            if dir_path.exists():
                archivos_en_dir = list(dir_path.rglob('*'))
                archivos_count = len([f for f in archivos_en_dir if f.is_file()])
                tamaño_dir = sum(f.stat().st_size for f in archivos_en_dir if f.is_file())
                
                total_archivos += archivos_count
                total_tamaño += tamaño_dir
                
                directorios_analizados.append({
                    'nombre': directorio,
                    'existe': True,
                    'archivos': archivos_count,
                    'tamaño_bytes': tamaño_dir,
                    'tamaño_kb': tamaño_dir / 1024
                })
            else:
                directorios_analizados.append({
                    'nombre': directorio,
                    'existe': False,
                    'archivos': 0,
                    'tamaño_bytes': 0,
                    'tamaño_kb': 0
                })
        
        # Análisis de directorios
        directorios_presentes = sum(1 for dir_info in directorios_analizados if dir_info['existe'])
        total_directorios = len(directorios_analizados)
        
        if directorios_presentes == total_directorios:
            estado_directorios = "ÓPTIMO"
            recomendacion_directorios = "Todos los directorios del sistema están presentes"
        elif directorios_presentes >= total_directorios * 0.8:
            estado_directorios = "BUENO"
            recomendacion_directorios = "La mayoría de directorios del sistema están presentes"
        elif directorios_presentes >= total_directorios * 0.5:
            estado_directorios = "MODERADO"
            recomendacion_directorios = "Algunos directorios del sistema faltan"
        else:
            estado_directorios = "CRÍTICO"
            recomendacion_directorios = "Muchos directorios del sistema faltan"
        
        return {
            'total_directorios': total_directorios,
            'directorios_presentes': directorios_presentes,
            'total_archivos': total_archivos,
            'total_tamaño_kb': total_tamaño / 1024,
            'estado': estado_directorios,
            'recomendacion': recomendacion_directorios,
            'detalles': directorios_analizados
        }
        
    except Exception as e:
        print_error(f"Error analizando directorios: {e}")
        return None

def generar_reporte_rendimiento(metricas):
    """Generar reporte de rendimiento"""
    print_step(8, "Generando reporte de rendimiento")
    
    try:
        reporte_content = f"""
# ⚡ REPORTE DE RENDIMIENTO METGO 3D
Sistema Meteorológico Agrícola Quillota

## 📅 Información de Análisis
- **Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Sistema**: METGO 3D Operativo v2.0
- **Ubicación**: Quillota, Región de Valparaíso, Chile

## 🖥️ Análisis de CPU
- **Uso**: {metricas['cpu']['porcentaje']:.1f}%
- **Núcleos**: {metricas['cpu']['nucleos']}
- **Frecuencia**: {metricas['cpu']['frecuencia']:.1f} MHz
- **Estado**: {metricas['cpu']['estado']}
- **Recomendación**: {metricas['cpu']['recomendacion']}

## 🧠 Análisis de Memoria
- **Uso**: {metricas['memoria']['porcentaje']:.1f}%
- **Total**: {metricas['memoria']['total_gb']:.1f} GB
- **Usada**: {metricas['memoria']['usada_gb']:.1f} GB
- **Disponible**: {metricas['memoria']['disponible_gb']:.1f} GB
- **Swap**: {metricas['memoria']['swap_percent']:.1f}%
- **Estado**: {metricas['memoria']['estado']}
- **Recomendación**: {metricas['memoria']['recomendacion']}

## 💾 Análisis de Disco
- **Uso**: {metricas['disco']['porcentaje']:.1f}%
- **Total**: {metricas['disco']['total_gb']:.1f} GB
- **Usado**: {metricas['disco']['usado_gb']:.1f} GB
- **Libre**: {metricas['disco']['libre_gb']:.1f} GB
- **Estado**: {metricas['disco']['estado']}
- **Recomendación**: {metricas['disco']['recomendacion']}

## 🌐 Análisis de Red
- **Bytes Enviados**: {metricas['red']['bytes_enviados_mb']:.1f} MB
- **Bytes Recibidos**: {metricas['red']['bytes_recibidos_mb']:.1f} MB
- **Paquetes Enviados**: {metricas['red']['paquetes_enviados']:,}
- **Paquetes Recibidos**: {metricas['red']['paquetes_recibidos']:,}
- **Estado**: {metricas['red']['estado']}
- **Recomendación**: {metricas['red']['recomendacion']}

## 🔄 Análisis de Procesos
- **Total de Procesos**: {metricas['procesos']['total_procesos']}
- **Procesos Python**: {metricas['procesos']['procesos_python']}
- **Procesos Sistema**: {metricas['procesos']['procesos_sistema']}
- **Estado**: {metricas['procesos']['estado']}
- **Recomendación**: {metricas['procesos']['recomendacion']}

## 📁 Análisis de Archivos
- **Total de Archivos**: {metricas['archivos']['total_archivos']}
- **Archivos Presentes**: {metricas['archivos']['archivos_presentes']}
- **Tamaño Total**: {metricas['archivos']['total_tamaño_kb']:.1f} KB
- **Estado**: {metricas['archivos']['estado']}
- **Recomendación**: {metricas['archivos']['recomendacion']}

## 📂 Análisis de Directorios
- **Total de Directorios**: {metricas['directorios']['total_directorios']}
- **Directorios Presentes**: {metricas['directorios']['directorios_presentes']}
- **Total de Archivos**: {metricas['directorios']['total_archivos']}
- **Tamaño Total**: {metricas['directorios']['total_tamaño_kb']:.1f} KB
- **Estado**: {metricas['directorios']['estado']}
- **Recomendación**: {metricas['directorios']['recomendacion']}

## 🎯 Resumen de Rendimiento
"""
        
        # Evaluar rendimiento general
        estados = [
            metricas['cpu']['estado'],
            metricas['memoria']['estado'],
            metricas['disco']['estado'],
            metricas['red']['estado'],
            metricas['procesos']['estado'],
            metricas['archivos']['estado'],
            metricas['directorios']['estado']
        ]
        
        optimos = estados.count('ÓPTIMO')
        buenos = estados.count('BUENO')
        moderados = estados.count('MODERADO')
        criticos = estados.count('CRÍTICO')
        
        if criticos == 0 and moderados <= 1:
            estado_general = "EXCELENTE"
            recomendacion_general = "El sistema está funcionando de manera óptima"
        elif criticos == 0 and moderados <= 3:
            estado_general = "BUENO"
            recomendacion_general = "El sistema está funcionando bien con algunas áreas de mejora"
        elif criticos <= 1 and moderados <= 5:
            estado_general = "MODERADO"
            recomendacion_general = "El sistema requiere optimización en algunas áreas"
        else:
            estado_general = "CRÍTICO"
            recomendacion_general = "El sistema requiere atención inmediata"
        
        reporte_content += f"""
### Estado General: {estado_general}
- **Óptimos**: {optimos}
- **Buenos**: {buenos}
- **Moderados**: {moderados}
- **Críticos**: {criticos}

### Recomendación General: {recomendacion_general}

## 🚀 Optimizaciones Recomendadas
"""
        
        # Generar recomendaciones específicas
        if metricas['cpu']['estado'] in ['MODERADO', 'CRÍTICO']:
            reporte_content += "- **CPU**: Considerar cerrar procesos innecesarios o aumentar recursos\n"
        
        if metricas['memoria']['estado'] in ['MODERADO', 'CRÍTICO']:
            reporte_content += "- **Memoria**: Liberar memoria cerrando aplicaciones no utilizadas\n"
        
        if metricas['disco']['estado'] in ['MODERADO', 'CRÍTICO']:
            reporte_content += "- **Disco**: Ejecutar limpieza de archivos temporales y logs antiguos\n"
        
        if metricas['archivos']['estado'] in ['MODERADO', 'CRÍTICO']:
            reporte_content += "- **Archivos**: Verificar integridad del sistema y reinstalar componentes faltantes\n"
        
        if metricas['directorios']['estado'] in ['MODERADO', 'CRÍTICO']:
            reporte_content += "- **Directorios**: Crear directorios faltantes y verificar permisos\n"
        
        reporte_content += f"""
## 📋 Próximos Pasos
1. **Revisar recomendaciones** específicas para cada componente
2. **Ejecutar optimizaciones** según el estado identificado
3. **Monitorear mejoras** después de aplicar optimizaciones
4. **Repetir análisis** periódicamente para mantener rendimiento

---
*Reporte generado automáticamente por el Analizador de Rendimiento METGO 3D*
"""
        
        reporte_file = Path("reportes_revision") / f"rendimiento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        reporte_file.write_text(reporte_content, encoding='utf-8')
        
        print_success(f"Reporte de rendimiento generado: {reporte_file}")
        return True
        
    except Exception as e:
        print_error(f"Error generando reporte: {e}")
        return False

def mostrar_resumen_rendimiento(metricas):
    """Mostrar resumen de rendimiento"""
    print("\n" + "=" * 60)
    print("⚡ RESUMEN DE RENDIMIENTO")
    print("=" * 60)
    
    print(f"🖥️ CPU: {metricas['cpu']['porcentaje']:.1f}% ({metricas['cpu']['estado']})")
    print(f"🧠 Memoria: {metricas['memoria']['porcentaje']:.1f}% ({metricas['memoria']['estado']})")
    print(f"💾 Disco: {metricas['disco']['porcentaje']:.1f}% ({metricas['disco']['estado']})")
    print(f"🌐 Red: {metricas['red']['estado']}")
    print(f"🔄 Procesos: {metricas['procesos']['total_procesos']} ({metricas['procesos']['estado']})")
    print(f"📁 Archivos: {metricas['archivos']['archivos_presentes']}/{metricas['archivos']['total_archivos']} ({metricas['archivos']['estado']})")
    print(f"📂 Directorios: {metricas['directorios']['directorios_presentes']}/{metricas['directorios']['total_directorios']} ({metricas['directorios']['estado']})")
    
    # Evaluar rendimiento general
    estados = [
        metricas['cpu']['estado'],
        metricas['memoria']['estado'],
        metricas['disco']['estado'],
        metricas['red']['estado'],
        metricas['procesos']['estado'],
        metricas['archivos']['estado'],
        metricas['directorios']['estado']
    ]
    
    optimos = estados.count('ÓPTIMO')
    buenos = estados.count('BUENO')
    moderados = estados.count('MODERADO')
    criticos = estados.count('CRÍTICO')
    
    print(f"\n📊 DISTRIBUCIÓN DE ESTADOS:")
    print(f"   Óptimos: {optimos}")
    print(f"   Buenos: {buenos}")
    print(f"   Moderados: {moderados}")
    print(f"   Críticos: {criticos}")
    
    if criticos == 0 and moderados <= 1:
        print("\n🎉 RENDIMIENTO EXCELENTE")
        print("🌾 El sistema está funcionando de manera óptima")
        print("🚀 No se requieren optimizaciones inmediatas")
    elif criticos == 0 and moderados <= 3:
        print("\n✅ RENDIMIENTO BUENO")
        print("🌾 El sistema está funcionando bien")
        print("🔧 Algunas optimizaciones menores pueden mejorar el rendimiento")
    elif criticos <= 1 and moderados <= 5:
        print("\n⚠️ RENDIMIENTO MODERADO")
        print("🔧 El sistema requiere optimización en algunas áreas")
        print("📚 Revisar recomendaciones específicas para mejoras")
    else:
        print("\n❌ RENDIMIENTO CRÍTICO")
        print("🔧 El sistema requiere atención inmediata")
        print("📞 Ejecutar optimizaciones críticas urgentemente")

def main():
    """Función principal del analizador"""
    print_header()
    
    # Ejecutar análisis de rendimiento
    metricas = {
        'cpu': analizar_rendimiento_cpu(),
        'memoria': analizar_rendimiento_memoria(),
        'disco': analizar_rendimiento_disco(),
        'red': analizar_rendimiento_red(),
        'procesos': analizar_rendimiento_procesos(),
        'archivos': analizar_rendimiento_archivos(),
        'directorios': analizar_rendimiento_directorios()
    }
    
    # Verificar que todas las métricas se obtuvieron
    metricas_validas = all(metricas.values())
    if not metricas_validas:
        print_error("No se pudieron obtener todas las métricas de rendimiento")
        sys.exit(1)
    
    # Generar reporte
    generar_reporte_rendimiento(metricas)
    
    # Mostrar resumen
    mostrar_resumen_rendimiento(metricas)
    
    # Determinar código de salida
    estados = [metricas[key]['estado'] for key in metricas.keys()]
    criticos = estados.count('CRÍTICO')
    moderados = estados.count('MODERADO')
    
    if criticos == 0 and moderados <= 1:
        sys.exit(0)  # Rendimiento excelente
    elif criticos == 0 and moderados <= 3:
        sys.exit(1)  # Rendimiento bueno
    elif criticos <= 1 and moderados <= 5:
        sys.exit(2)  # Rendimiento moderado
    else:
        sys.exit(3)  # Rendimiento crítico

if __name__ == "__main__":
    main()
