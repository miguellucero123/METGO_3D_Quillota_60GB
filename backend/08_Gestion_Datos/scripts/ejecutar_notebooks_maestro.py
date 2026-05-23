#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 SCRIPT MAESTRO METGO 3D - EJECUTOR DE NOTEBOOKS
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Este script ejecuta todos los notebooks del proyecto METGO 3D
secuencialmente y automáticamente.
"""

import os
import sys
import time
import subprocess
import json
from datetime import datetime
from pathlib import Path

def print_header():
    """Imprimir encabezado del script maestro"""
    print("🌾 SCRIPT MAESTRO METGO 3D - EJECUTOR DE NOTEBOOKS")
    print("Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0")
    print("=" * 70)

def print_step(step, message):
    """Imprimir paso del proceso de ejecución"""
    print(f"\n[{step}] {message}")
    print("-" * 50)

def print_success(message):
    """Imprimir mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message):
    """Imprimir mensaje de error")
    print(f"❌ {message}")

def print_warning(message):
    """Imprimir mensaje de advertencia"""
    print(f"⚠️ {message}")

def print_info(message):
    """Imprimir mensaje informativo"""
    print(f"ℹ️ {message}")

def verificar_dependencias():
    """Verificar que las dependencias estén instaladas"""
    try:
        print_info("Verificando dependencias...")
        
        # Verificar Python
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print_error("Se requiere Python 3.8 o superior")
            return False
        
        print_success(f"Python {python_version.major}.{python_version.minor}.{python_version.micro} detectado")
        
        # Verificar jupyter
        try:
            import jupyter
            print_success("Jupyter instalado")
        except ImportError:
            print_error("Jupyter no está instalado. Ejecutar: pip install jupyter")
            return False
        
        # Verificar nbconvert
        try:
            import nbconvert
            print_success("nbconvert instalado")
        except ImportError:
            print_error("nbconvert no está instalado. Ejecutar: pip install nbconvert")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Error verificando dependencias: {e}")
        return False

def obtener_lista_notebooks():
    """Obtener lista de notebooks a ejecutar"""
    notebooks = [
        {
            "archivo": "01_Configuracion_e_Imports.ipynb",
            "descripcion": "Configuración e Imports del Sistema",
            "dependencias": [],
            "tiempo_estimado": 30
        },
        {
            "archivo": "02_Carga_y_Procesamiento_Datos.ipynb",
            "descripcion": "Carga y Procesamiento de Datos",
            "dependencias": ["01_Configuracion_e_Imports.ipynb"],
            "tiempo_estimado": 60
        },
        {
            "archivo": "03_Analisis_Meteorologico.ipynb",
            "descripcion": "Análisis Meteorológico Avanzado",
            "dependencias": ["01_Configuracion_e_Imports.ipynb", "02_Carga_y_Procesamiento_Datos.ipynb"],
            "tiempo_estimado": 90
        },
        {
            "archivo": "04_Visualizaciones.ipynb",
            "descripcion": "Visualizaciones Avanzadas e Interactivas",
            "dependencias": ["01_Configuracion_e_Imports.ipynb", "02_Carga_y_Procesamiento_Datos.ipynb", "03_Analisis_Meteorologico.ipynb"],
            "tiempo_estimado": 120
        },
        {
            "archivo": "05_Modelos_ML.ipynb",
            "descripcion": "Modelos de Machine Learning Optimizados",
            "dependencias": ["01_Configuracion_e_Imports.ipynb", "02_Carga_y_Procesamiento_Datos.ipynb", "03_Analisis_Meteorologico.ipynb", "04_Visualizaciones.ipynb"],
            "tiempo_estimado": 180
        },
        {
            "archivo": "06_Dashboard_Interactivo.ipynb",
            "descripcion": "Dashboard Interactivo",
            "dependencias": ["01_Configuracion_e_Imports.ipynb", "02_Carga_y_Procesamiento_Datos.ipynb", "03_Analisis_Meteorologico.ipynb", "04_Visualizaciones.ipynb", "05_Modelos_ML.ipynb"],
            "tiempo_estimado": 90
        },
        {
            "archivo": "07_Reportes_Automaticos.ipynb",
            "descripcion": "Reportes Automáticos",
            "dependencias": ["01_Configuracion_e_Imports.ipynb", "02_Carga_y_Procesamiento_Datos.ipynb", "03_Analisis_Meteorologico.ipynb", "04_Visualizaciones.ipynb", "05_Modelos_ML.ipynb", "06_Dashboard_Interactivo.ipynb"],
            "tiempo_estimado": 60
        },
        {
            "archivo": "08_APIs_Externas.ipynb",
            "descripcion": "APIs Externas e Integraciones",
            "dependencias": ["01_Configuracion_e_Imports.ipynb", "02_Carga_y_Procesamiento_Datos.ipynb"],
            "tiempo_estimado": 45
        },
        {
            "archivo": "09_Testing_Validacion.ipynb",
            "descripcion": "Testing y Validación del Sistema",
            "dependencias": ["01_Configuracion_e_Imports.ipynb", "02_Carga_y_Procesamiento_Datos.ipynb", "03_Analisis_Meteorologico.ipynb", "04_Visualizaciones.ipynb", "05_Modelos_ML.ipynb"],
            "tiempo_estimado": 75
        },
        {
            "archivo": "10_Deployment_Produccion.ipynb",
            "descripcion": "Deployment y Producción",
            "dependencias": ["01_Configuracion_e_Imports.ipynb", "02_Carga_y_Procesamiento_Datos.ipynb", "03_Analisis_Meteorologico.ipynb", "04_Visualizaciones.ipynb", "05_Modelos_ML.ipynb", "06_Dashboard_Interactivo.ipynb", "07_Reportes_Automaticos.ipynb", "08_APIs_Externas.ipynb", "09_Testing_Validacion.ipynb"],
            "tiempo_estimado": 120
        }
    ]
    
    return notebooks

def verificar_notebooks(notebooks):
    """Verificar que todos los notebooks existan"""
    print_info("Verificando existencia de notebooks...")
    
    notebooks_existentes = []
    notebooks_faltantes = []
    
    for notebook in notebooks:
        archivo = Path(notebook["archivo"])
        if archivo.exists():
            notebooks_existentes.append(notebook)
            print_success(f"✅ {notebook['archivo']} - {notebook['descripcion']}")
        else:
            notebooks_faltantes.append(notebook)
            print_error(f"❌ {notebook['archivo']} - {notebook['descripcion']} (NO ENCONTRADO)")
    
    if notebooks_faltantes:
        print_warning(f"⚠️ {len(notebooks_faltantes)} notebooks no encontrados")
        print_info("Se ejecutarán solo los notebooks existentes")
    
    return notebooks_existentes

def ejecutar_notebook(notebook, timeout=600):
    """Ejecutar un notebook individual"""
    try:
        archivo = notebook["archivo"]
        descripcion = notebook["descripcion"]
        tiempo_estimado = notebook["tiempo_estimado"]
        
        print_info(f"Ejecutando: {archivo}")
        print_info(f"Descripción: {descripcion}")
        print_info(f"Tiempo estimado: {tiempo_estimado} segundos")
        
        # Comando para ejecutar el notebook
        comando = [
            "jupyter", "nbconvert",
            "--to", "notebook",
            "--execute",
            "--inplace",
            "--ExecutePreprocessor.timeout=" + str(timeout),
            "--ExecutePreprocessor.kernel_name=python3",
            str(archivo)
        ]
        
        # Ejecutar el comando
        inicio = time.time()
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        fin = time.time()
        tiempo_ejecucion = fin - inicio
        
        if resultado.returncode == 0:
            print_success(f"✅ {archivo} ejecutado exitosamente en {tiempo_ejecucion:.1f} segundos")
            return True, tiempo_ejecucion, None
        else:
            error_msg = f"Error ejecutando {archivo}: {resultado.stderr}"
            print_error(error_msg)
            return False, tiempo_ejecucion, error_msg
            
    except subprocess.TimeoutExpired:
        error_msg = f"Timeout ejecutando {archivo} (>{timeout} segundos)"
        print_error(error_msg)
        return False, timeout, error_msg
    except Exception as e:
        error_msg = f"Error inesperado ejecutando {archivo}: {str(e)}"
        print_error(error_msg)
        return False, 0, error_msg

def ejecutar_notebooks_secuencialmente(notebooks):
    """Ejecutar todos los notebooks secuencialmente"""
    print_info("Iniciando ejecución secuencial de notebooks...")
    
    resultados = []
    tiempo_total_inicio = time.time()
    
    for i, notebook in enumerate(notebooks, 1):
        print_step(f"{i}/{len(notebooks)}", f"Ejecutando {notebook['archivo']}")
        
        # Ejecutar notebook
        exito, tiempo_ejecucion, error = ejecutar_notebook(notebook)
        
        # Guardar resultado
        resultado = {
            "notebook": notebook["archivo"],
            "descripcion": notebook["descripcion"],
            "exito": exito,
            "tiempo_ejecucion": tiempo_ejecucion,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        resultados.append(resultado)
        
        if not exito:
            print_warning(f"⚠️ Error en {notebook['archivo']}, continuando con el siguiente...")
            # Continuar con el siguiente notebook en caso de error
        
        # Pausa entre notebooks
        if i < len(notebooks):
            print_info("Pausa de 5 segundos antes del siguiente notebook...")
            time.sleep(5)
    
    tiempo_total_fin = time.time()
    tiempo_total = tiempo_total_fin - tiempo_total_inicio
    
    return resultados, tiempo_total

def generar_reporte_ejecucion(resultados, tiempo_total):
    """Generar reporte de ejecución"""
    try:
        # Crear directorio de reportes si no existe
        reportes_dir = Path("reportes_ejecucion")
        reportes_dir.mkdir(exist_ok=True)
        
        # Estadísticas
        total_notebooks = len(resultados)
        notebooks_exitosos = sum(1 for r in resultados if r["exito"])
        notebooks_fallidos = total_notebooks - notebooks_exitosos
        tiempo_promedio = sum(r["tiempo_ejecucion"] for r in resultados) / total_notebooks if total_notebooks > 0 else 0
        
        # Generar reporte
        reporte_content = f"""
# 🌾 REPORTE DE EJECUCIÓN METGO 3D
Sistema Meteorológico Agrícola Quillota - Script Maestro

## 📅 Información de Ejecución
- **Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Sistema**: METGO 3D Operativo v2.0
- **Script**: ejecutar_notebooks_maestro.py

## 📊 Estadísticas de Ejecución
- **Total notebooks**: {total_notebooks}
- **Ejecutados exitosamente**: {notebooks_exitosos}
- **Fallidos**: {notebooks_fallidos}
- **Tasa de éxito**: {(notebooks_exitosos/total_notebooks*100):.1f}%
- **Tiempo total**: {tiempo_total:.1f} segundos ({tiempo_total/60:.1f} minutos)
- **Tiempo promedio por notebook**: {tiempo_promedio:.1f} segundos

## 📋 Resultados por Notebook
"""
        
        for i, resultado in enumerate(resultados, 1):
            estado = "✅ EXITOSO" if resultado["exito"] else "❌ FALLIDO"
            reporte_content += f"""
### {i}. {resultado['notebook']}
- **Descripción**: {resultado['descripcion']}
- **Estado**: {estado}
- **Tiempo de ejecución**: {resultado['tiempo_ejecucion']:.1f} segundos
- **Timestamp**: {resultado['timestamp']}
"""
            
            if not resultado["exito"] and resultado["error"]:
                reporte_content += f"- **Error**: {resultado['error']}\n"
        
        reporte_content += f"""
## 🎯 Resumen Final
- **Sistema**: METGO 3D Operativo v2.0
- **Notebooks procesados**: {total_notebooks}
- **Ejecución exitosa**: {notebooks_exitosos}/{total_notebooks}
- **Tiempo total**: {tiempo_total:.1f} segundos
- **Estado general**: {'✅ COMPLETADO' if notebooks_fallidos == 0 else '⚠️ COMPLETADO CON ERRORES'}

## 📁 Archivos Generados
- **Logs de ejecución**: logs/ejecucion_notebooks.log
- **Reportes individuales**: reportes_ejecucion/
- **Datos procesados**: datos/
- **Visualizaciones**: logs/graficos/
- **Modelos ML**: modelos/

---
*Reporte generado automáticamente por el Script Maestro METGO 3D*
"""
        
        # Guardar reporte
        reporte_file = reportes_dir / f"reporte_ejecucion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        reporte_file.write_text(reporte_content, encoding='utf-8')
        
        # Guardar resultados en JSON
        resultados_file = reportes_dir / f"resultados_ejecucion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(resultados_file, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        print_success(f"Reporte de ejecución generado: {reporte_file}")
        return reporte_file
        
    except Exception as e:
        print_error(f"Error generando reporte: {e}")
        return None

def mostrar_resumen_final(resultados, tiempo_total):
    """Mostrar resumen final de la ejecución"""
    total_notebooks = len(resultados)
    notebooks_exitosos = sum(1 for r in resultados if r["exito"])
    notebooks_fallidos = total_notebooks - notebooks_exitosos
    
    print("\n" + "=" * 70)
    print("🎉 RESUMEN FINAL - EJECUCIÓN DE NOTEBOOKS METGO 3D")
    print("=" * 70)
    
    print(f"\n📊 ESTADÍSTICAS DE EJECUCIÓN:")
    print(f"   Total notebooks: {total_notebooks}")
    print(f"   Ejecutados exitosamente: {notebooks_exitosos}")
    print(f"   Fallidos: {notebooks_fallidos}")
    print(f"   Tasa de éxito: {(notebooks_exitosos/total_notebooks*100):.1f}%")
    print(f"   Tiempo total: {tiempo_total:.1f} segundos ({tiempo_total/60:.1f} minutos)")
    
    print(f"\n📋 RESULTADOS POR NOTEBOOK:")
    for i, resultado in enumerate(resultados, 1):
        estado = "✅" if resultado["exito"] else "❌"
        print(f"   {i:2d}. {estado} {resultado['notebook']} ({resultado['tiempo_ejecucion']:.1f}s)")
    
    if notebooks_fallidos > 0:
        print(f"\n⚠️ NOTEBOOKS CON ERRORES:")
        for resultado in resultados:
            if not resultado["exito"]:
                print(f"   ❌ {resultado['notebook']}: {resultado['error']}")
    
    print(f"\n🎯 ESTADO GENERAL:")
    if notebooks_fallidos == 0:
        print("   ✅ TODOS LOS NOTEBOOKS EJECUTADOS EXITOSAMENTE")
        print("   🌾 Sistema METGO 3D completamente operativo")
    else:
        print(f"   ⚠️ EJECUCIÓN COMPLETADA CON {notebooks_fallidos} ERRORES")
        print("   🔧 Revisar logs para detalles de errores")
    
    print("\n" + "🌾" + "=" * 68 + "🌾")
    print("  ✅ SCRIPT MAESTRO METGO 3D - EJECUCIÓN COMPLETADA ✅")
    print("🌾" + "=" * 68 + "🌾")

def main():
    """Función principal del script maestro"""
    print_header()
    
    # Verificar dependencias
    print_step(1, "Verificando dependencias del sistema")
    if not verificar_dependencias():
        print_error("❌ Dependencias no satisfechas. Instalar dependencias y reintentar.")
        return False
    
    # Obtener lista de notebooks
    print_step(2, "Obteniendo lista de notebooks a ejecutar")
    notebooks = obtener_lista_notebooks()
    print_info(f"Se encontraron {len(notebooks)} notebooks para ejecutar")
    
    # Verificar notebooks
    print_step(3, "Verificando existencia de notebooks")
    notebooks_existentes = verificar_notebooks(notebooks)
    
    if not notebooks_existentes:
        print_error("❌ No se encontraron notebooks para ejecutar")
        return False
    
    print_info(f"Se ejecutarán {len(notebooks_existentes)} notebooks")
    
    # Ejecutar notebooks
    print_step(4, "Ejecutando notebooks secuencialmente")
    resultados, tiempo_total = ejecutar_notebooks_secuencialmente(notebooks_existentes)
    
    # Generar reporte
    print_step(5, "Generando reporte de ejecución")
    reporte_file = generar_reporte_ejecucion(resultados, tiempo_total)
    
    # Mostrar resumen final
    mostrar_resumen_final(resultados, tiempo_total)
    
    print_success("Script maestro completado exitosamente")
    return True

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Ejecución interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)