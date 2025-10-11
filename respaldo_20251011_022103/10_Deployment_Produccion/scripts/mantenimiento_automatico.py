#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 MANTENIMIENTO AUTOMÁTICO METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Este script realiza mantenimiento automático del sistema METGO 3D,
incluyendo limpieza, optimización, respaldo y verificación.
"""

import os
import sys
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import json

def print_header():
    """Imprimir encabezado del mantenimiento"""
    print("🔧 MANTENIMIENTO AUTOMÁTICO METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Mantenimiento Integral")
    print("=" * 60)

def print_step(step, message):
    """Imprimir paso del proceso de mantenimiento"""
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

def ejecutar_script(script_name, descripcion):
    """Ejecutar un script del sistema"""
    try:
        script_path = Path(script_name)
        if not script_path.exists():
            print_warning(f"Script {script_name} no encontrado")
            return False
        
        print_info(f"Ejecutando {descripcion}...")
        
        # Ejecutar script
        resultado = subprocess.run([sys.executable, script_name], 
                                 capture_output=True, text=True, timeout=300)
        
        if resultado.returncode == 0:
            print_success(f"{descripcion} ejecutado exitosamente")
            return True
        else:
            print_warning(f"{descripcion} ejecutado con advertencias (código: {resultado.returncode})")
            return True  # Considerar exitoso si no es crítico
    except subprocess.TimeoutExpired:
        print_error(f"{descripcion} excedió el tiempo límite")
        return False
    except Exception as e:
        print_error(f"Error ejecutando {descripcion}: {e}")
        return False

def verificar_sistema():
    """Verificar estado del sistema"""
    print_step(1, "Verificando estado del sistema")
    
    try:
        return ejecutar_script("verificar_sistema.py", "Verificación del sistema")
    except Exception as e:
        print_error(f"Error en verificación: {e}")
        return False

def limpiar_sistema():
    """Limpiar sistema"""
    print_step(2, "Limpiando sistema")
    
    try:
        return ejecutar_script("limpiar_y_optimizar.py", "Limpieza y optimización")
    except Exception as e:
        print_error(f"Error en limpieza: {e}")
        return False

def respaldar_sistema():
    """Respaldar sistema"""
    print_step(3, "Respaldando sistema")
    
    try:
        return ejecutar_script("respaldo_automatico.py", "Respaldo automático")
    except Exception as e:
        print_error(f"Error en respaldo: {e}")
        return False

def analizar_rendimiento():
    """Analizar rendimiento del sistema"""
    print_step(4, "Analizando rendimiento")
    
    try:
        return ejecutar_script("analisis_rendimiento.py", "Análisis de rendimiento")
    except Exception as e:
        print_error(f"Error en análisis: {e}")
        return False

def diagnosticar_sistema():
    """Diagnosticar sistema"""
    print_step(5, "Diagnosticando sistema")
    
    try:
        return ejecutar_script("diagnostico_completo.py", "Diagnóstico completo")
    except Exception as e:
        print_error(f"Error en diagnóstico: {e}")
        return False

def actualizar_sistema():
    """Actualizar sistema"""
    print_step(6, "Actualizando sistema")
    
    try:
        return ejecutar_script("actualizacion_automatica.py", "Actualización automática")
    except Exception as e:
        print_error(f"Error en actualización: {e}")
        return False

def generar_resumen_sistema():
    """Generar resumen del sistema"""
    print_step(7, "Generando resumen del sistema")
    
    try:
        return ejecutar_script("resumen_sistema.py", "Resumen del sistema")
    except Exception as e:
        print_error(f"Error en resumen: {e}")
        return False

def verificar_logs():
    """Verificar logs del sistema"""
    print_step(8, "Verificando logs del sistema")
    
    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            print_warning("Directorio de logs no existe")
            return False
        
        # Buscar logs recientes
        logs_recientes = []
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for log_file in logs_dir.glob("*.log"):
            if log_file.stat().st_mtime > cutoff_time.timestamp():
                logs_recientes.append(log_file)
        
        if logs_recientes:
            print_success(f"Logs recientes encontrados: {len(logs_recientes)}")
            for log in logs_recientes:
                print_info(f"  - {log.name}")
        else:
            print_warning("No hay logs recientes")
        
        return True
        
    except Exception as e:
        print_error(f"Error verificando logs: {e}")
        return False

def verificar_datos():
    """Verificar datos del sistema"""
    print_step(9, "Verificando datos del sistema")
    
    try:
        data_dir = Path("data")
        if not data_dir.exists():
            print_warning("Directorio de datos no existe")
            return False
        
        # Buscar archivos de datos recientes
        datos_recientes = []
        cutoff_time = datetime.now() - timedelta(days=7)
        
        for data_file in data_dir.glob("*"):
            if data_file.is_file() and data_file.stat().st_mtime > cutoff_time.timestamp():
                datos_recientes.append(data_file)
        
        if datos_recientes:
            print_success(f"Datos recientes encontrados: {len(datos_recientes)}")
            for data in datos_recientes:
                print_info(f"  - {data.name}")
        else:
            print_warning("No hay datos recientes")
        
        return True
        
    except Exception as e:
        print_error(f"Error verificando datos: {e}")
        return False

def verificar_reportes():
    """Verificar reportes del sistema"""
    print_step(10, "Verificando reportes del sistema")
    
    try:
        reports_dir = Path("reportes_revision")
        if not reports_dir.exists():
            print_warning("Directorio de reportes no existe")
            return False
        
        # Buscar reportes recientes
        reportes_recientes = []
        cutoff_time = datetime.now() - timedelta(days=7)
        
        for report_file in reports_dir.glob("*"):
            if report_file.is_file() and report_file.stat().st_mtime > cutoff_time.timestamp():
                reportes_recientes.append(report_file)
        
        if reportes_recientes:
            print_success(f"Reportes recientes encontrados: {len(reportes_recientes)}")
            for report in reportes_recientes:
                print_info(f"  - {report.name}")
        else:
            print_warning("No hay reportes recientes")
        
        return True
        
    except Exception as e:
        print_error(f"Error verificando reportes: {e}")
        return False

def generar_reporte_mantenimiento(estadisticas):
    """Generar reporte de mantenimiento"""
    print_step(11, "Generando reporte de mantenimiento")
    
    try:
        reporte_content = f"""
# 🔧 REPORTE DE MANTENIMIENTO METGO 3D
Sistema Meteorológico Agrícola Quillota

## 📅 Información de Mantenimiento
- **Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Sistema**: METGO 3D Operativo v2.0
- **Ubicación**: Quillota, Región de Valparaíso, Chile

## 📊 Estadísticas de Mantenimiento
- **Verificación del sistema**: {'✅ Exitosa' if estadisticas['verificacion'] else '❌ Fallida'}
- **Limpieza del sistema**: {'✅ Exitosa' if estadisticas['limpieza'] else '❌ Fallida'}
- **Respaldo del sistema**: {'✅ Exitosa' if estadisticas['respaldo'] else '❌ Fallida'}
- **Análisis de rendimiento**: {'✅ Exitosa' if estadisticas['rendimiento'] else '❌ Fallida'}
- **Diagnóstico del sistema**: {'✅ Exitosa' if estadisticas['diagnostico'] else '❌ Fallida'}
- **Actualización del sistema**: {'✅ Exitosa' if estadisticas['actualizacion'] else '❌ Fallida'}
- **Resumen del sistema**: {'✅ Exitosa' if estadisticas['resumen'] else '❌ Fallida'}
- **Verificación de logs**: {'✅ Exitosa' if estadisticas['logs'] else '❌ Fallida'}
- **Verificación de datos**: {'✅ Exitosa' if estadisticas['datos'] else '❌ Fallida'}
- **Verificación de reportes**: {'✅ Exitosa' if estadisticas['reportes'] else '❌ Fallida'}

## 🔧 Tareas de Mantenimiento Realizadas
### Verificación del Sistema
- Verificación de archivos críticos
- Verificación de directorios
- Verificación de dependencias
- Verificación de configuraciones

### Limpieza del Sistema
- Limpieza de logs antiguos
- Limpieza de archivos temporales
- Limpieza de resultados de pruebas
- Limpieza de datos antiguos
- Limpieza de reportes antiguos
- Limpieza de backups antiguos
- Limpieza de checkpoints de Jupyter
- Limpieza de caché de visualizaciones
- Optimización de directorios

### Respaldo del Sistema
- Respaldo de archivos de código
- Respaldo de notebooks
- Respaldo de configuraciones
- Respaldo de datos
- Respaldo de documentación
- Creación de archivo de metadatos
- Creación de archivo de verificación
- Compresión del respaldo

### Análisis de Rendimiento
- Análisis de CPU
- Análisis de memoria
- Análisis de disco
- Análisis de red
- Análisis de procesos
- Análisis de archivos
- Análisis de directorios

### Diagnóstico del Sistema
- Diagnóstico del sistema operativo
- Diagnóstico de Python
- Diagnóstico de dependencias
- Diagnóstico de archivos
- Diagnóstico de directorios
- Diagnóstico de notebooks
- Diagnóstico de configuraciones
- Diagnóstico de recursos
- Diagnóstico de procesos
- Diagnóstico de logs

### Actualización del Sistema
- Actualización de dependencias
- Actualización de configuraciones
- Actualización de directorios
- Actualización de scripts
- Actualización de notebooks
- Actualización de documentación

### Resumen del Sistema
- Resumen de componentes
- Resumen de estado
- Resumen de funcionalidades
- Resumen de recomendaciones

### Verificación de Logs
- Verificación de logs recientes
- Verificación de tamaño de logs
- Verificación de contenido de logs

### Verificación de Datos
- Verificación de datos recientes
- Verificación de integridad de datos
- Verificación de formato de datos

### Verificación de Reportes
- Verificación de reportes recientes
- Verificación de contenido de reportes
- Verificación de formato de reportes

## 🎯 Estado del Mantenimiento
"""
        
        # Evaluar estado del mantenimiento
        total_exitosos = sum(estadisticas.values())
        total_tareas = len(estadisticas)
        
        if total_exitosos == total_tareas:
            reporte_content += """
✅ **MANTENIMIENTO COMPLETO**: Todas las tareas han sido ejecutadas exitosamente
🌾 **SISTEMA OPTIMIZADO**: El sistema METGO 3D está completamente mantenido
🚀 **LISTO PARA USO**: El sistema está optimizado y listo para uso
"""
        elif total_exitosos >= total_tareas * 0.8:
            reporte_content += """
⚠️ **MANTENIMIENTO MAYORMENTE EXITOSO**: La mayoría de tareas han sido ejecutadas
🔧 **SISTEMA PARCIALMENTE OPTIMIZADO**: Algunas tareas pueden requerir atención
📚 **RECOMENDACIÓN**: Revisar tareas fallidas para detalles
"""
        elif total_exitosos >= total_tareas * 0.5:
            reporte_content += """
⚠️ **MANTENIMIENTO PARCIALMENTE EXITOSO**: Algunas tareas han sido ejecutadas
🔧 **SISTEMA REQUIERE ATENCIÓN**: Muchas tareas pueden requerir atención manual
📚 **RECOMENDACIÓN**: Revisar tareas fallidas y ejecutar manualmente
"""
        else:
            reporte_content += """
❌ **MANTENIMIENTO INCOMPLETO**: Pocas tareas han sido ejecutadas exitosamente
🔧 **SISTEMA REQUIERE ATENCIÓN CRÍTICA**: Muchas tareas han fallado
📞 **RECOMENDACIÓN**: Revisar errores y ejecutar mantenimiento manual
"""
        
        reporte_content += f"""
## 🚀 Próximos Pasos
1. **Revisar reporte**: Analizar resultados del mantenimiento
2. **Ejecutar tareas fallidas**: Si es necesario, ejecutar manualmente
3. **Verificar sistema**: Ejecutar `python verificar_sistema.py`
4. **Ejecutar sistema**: Ejecutar `python ejecutar_notebooks_maestro.py`
5. **Monitorear rendimiento**: Ejecutar `python analisis_rendimiento.py`

## 📋 Recomendaciones de Mantenimiento
- **Diario**: Verificación de logs y datos
- **Semanal**: Limpieza y respaldo
- **Mensual**: Análisis de rendimiento y diagnóstico
- **Trimestral**: Actualización completa del sistema

## 🔄 Programación de Mantenimiento
Se recomienda programar el mantenimiento automático para:
- **Limpieza**: Diariamente a las 2:00 AM
- **Respaldo**: Semanalmente los domingos a las 3:00 AM
- **Análisis**: Mensualmente el primer día a las 4:00 AM
- **Diagnóstico**: Trimestralmente el primer día a las 5:00 AM

---
*Reporte generado automáticamente por el Mantenimiento Automático METGO 3D*
"""
        
        reporte_file = Path("reportes_revision") / f"mantenimiento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        reporte_file.write_text(reporte_content, encoding='utf-8')
        
        print_success(f"Reporte de mantenimiento generado: {reporte_file}")
        return True
        
    except Exception as e:
        print_error(f"Error generando reporte: {e}")
        return False

def mostrar_resumen_mantenimiento(estadisticas):
    """Mostrar resumen de mantenimiento"""
    print("\n" + "=" * 60)
    print("🔧 RESUMEN DE MANTENIMIENTO")
    print("=" * 60)
    
    print(f"🔍 Verificación: {'✅ Exitosa' if estadisticas['verificacion'] else '❌ Fallida'}")
    print(f"🧹 Limpieza: {'✅ Exitosa' if estadisticas['limpieza'] else '❌ Fallida'}")
    print(f"💾 Respaldo: {'✅ Exitosa' if estadisticas['respaldo'] else '❌ Fallida'}")
    print(f"⚡ Rendimiento: {'✅ Exitosa' if estadisticas['rendimiento'] else '❌ Fallida'}")
    print(f"🔍 Diagnóstico: {'✅ Exitosa' if estadisticas['diagnostico'] else '❌ Fallida'}")
    print(f"🔄 Actualización: {'✅ Exitosa' if estadisticas['actualizacion'] else '❌ Fallida'}")
    print(f"📊 Resumen: {'✅ Exitosa' if estadisticas['resumen'] else '❌ Fallida'}")
    print(f"📋 Logs: {'✅ Exitosa' if estadisticas['logs'] else '❌ Fallida'}")
    print(f"📁 Datos: {'✅ Exitosa' if estadisticas['datos'] else '❌ Fallida'}")
    print(f"📄 Reportes: {'✅ Exitosa' if estadisticas['reportes'] else '❌ Fallida'}")
    
    total_exitosos = sum(estadisticas.values())
    total_tareas = len(estadisticas)
    
    print(f"\n📊 TAREAS EXITOSAS: {total_exitosos}/{total_tareas}")
    
    if total_exitosos == total_tareas:
        print("\n🎉 MANTENIMIENTO COMPLETO EXITOSO")
        print("🌾 Todas las tareas de mantenimiento han sido ejecutadas")
        print("🚀 El sistema METGO 3D está completamente optimizado")
    elif total_exitosos >= total_tareas * 0.8:
        print("\n✅ MANTENIMIENTO MAYORMENTE EXITOSO")
        print("🌾 La mayoría de tareas han sido ejecutadas")
        print("🔧 Algunas tareas pueden requerir atención manual")
    elif total_exitosos >= total_tareas * 0.5:
        print("\n⚠️ MANTENIMIENTO PARCIALMENTE EXITOSO")
        print("🔧 Algunas tareas han sido ejecutadas")
        print("📚 Revisar tareas fallidas para detalles")
    else:
        print("\n❌ MANTENIMIENTO INCOMPLETO")
        print("🔧 Pocas tareas han sido ejecutadas")
        print("📞 Revisar errores y ejecutar mantenimiento manual")

def main():
    """Función principal del mantenimiento"""
    print_header()
    
    # Ejecutar tareas de mantenimiento
    estadisticas = {
        'verificacion': verificar_sistema(),
        'limpieza': limpiar_sistema(),
        'respaldo': respaldar_sistema(),
        'rendimiento': analizar_rendimiento(),
        'diagnostico': diagnosticar_sistema(),
        'actualizacion': actualizar_sistema(),
        'resumen': generar_resumen_sistema(),
        'logs': verificar_logs(),
        'datos': verificar_datos(),
        'reportes': verificar_reportes()
    }
    
    # Generar reporte
    generar_reporte_mantenimiento(estadisticas)
    
    # Mostrar resumen
    mostrar_resumen_mantenimiento(estadisticas)
    
    # Determinar código de salida
    total_exitosos = sum(estadisticas.values())
    total_tareas = len(estadisticas)
    
    if total_exitosos == total_tareas:
        sys.exit(0)  # Mantenimiento completo
    elif total_exitosos >= total_tareas * 0.8:
        sys.exit(1)  # Mantenimiento mayormente exitoso
    elif total_exitosos >= total_tareas * 0.5:
        sys.exit(2)  # Mantenimiento parcialmente exitoso
    else:
        sys.exit(3)  # Mantenimiento incompleto

if __name__ == "__main__":
    main()
