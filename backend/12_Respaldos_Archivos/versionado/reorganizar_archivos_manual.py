#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reorganización Manual de Archivos METGO_3D
Mueve archivos .py y .ipynb a sus carpetas correspondientes
"""

import os
import shutil
import glob
from datetime import datetime

def mover_archivos_por_tipo():
    """Mueve archivos por tipo a sus carpetas correspondientes"""
    
    print('=' * 80)
    print('REORGANIZACION MANUAL DE ARCHIVOS METGO_3D')
    print('=' * 80)
    print(f'Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    # Mapeo de patrones a carpetas
    mapeo_archivos = {
        # Notebooks meteorológicos
        '03_Analisis_Meteorologico.ipynb': '01_Sistema_Meteorologico/notebooks/',
        'Fix_Open_Meteo.ipynb': '01_Sistema_Meteorologico/notebooks/',
        'Funcion_OpenMeteo.ipynb': '01_Sistema_Meteorologico/notebooks/',
        
        # Scripts meteorológicos
        '*meteorologico*': '01_Sistema_Meteorologico/scripts/',
        '*meteo*': '01_Sistema_Meteorologico/scripts/',
        '*clima*': '01_Sistema_Meteorologico/scripts/',
        'validador_datos_meteorologicos.py': '01_Sistema_Meteorologico/scripts/',
        
        # Scripts agrícolas
        '*agricola*': '02_Sistema_Agricola/scripts/',
        '*cultivo*': '02_Sistema_Agricola/scripts/',
        '*riego*': '02_Sistema_Agricola/scripts/',
        '*suelo*': '02_Sistema_Agricola/scripts/',
        
        # Scripts IoT y drones
        '*iot*': '03_Sistema_IoT_Drones/scripts/',
        '*drones*': '03_Sistema_IoT_Drones/scripts/',
        '*satelital*': '03_Sistema_IoT_Drones/scripts/',
        
        # Dashboards
        'dashboard_*': '04_Dashboards_Unificados/dashboards/',
        '*dashboard*': '04_Dashboards_Unificados/dashboards/',
        
        # APIs
        '*api*': '05_APIs_Externas/scripts/',
        '*conector*': '05_APIs_Externas/scripts/',
        '*externo*': '05_APIs_Externas/scripts/',
        
        # ML/IA
        '*ml*': '06_Modelos_ML_IA/scripts/',
        '*ia*': '06_Modelos_ML_IA/scripts/',
        '*modelo*': '06_Modelos_ML_IA/scripts/',
        '*prediccion*': '06_Modelos_ML_IA/scripts/',
        '*deep_learning*': '06_Modelos_ML_IA/scripts/',
        
        # Monitoreo
        '*monitoreo*': '07_Sistema_Monitoreo/scripts/',
        '*alertas*': '07_Sistema_Monitoreo/scripts/',
        '*log*': '07_Sistema_Monitoreo/scripts/',
        '*auditoria*': '07_Sistema_Monitoreo/scripts/',
        
        # Gestión de datos
        '*datos*': '08_Gestion_Datos/scripts/',
        '*procesamiento*': '08_Gestion_Datos/scripts/',
        '*etl*': '08_Gestion_Datos/scripts/',
        '*base_datos*': '08_Gestion_Datos/scripts/',
        
        # Testing
        '*test*': '09_Testing_Validacion/scripts/',
        '*prueba*': '09_Testing_Validacion/scripts/',
        '*validacion*': '09_Testing_Validacion/scripts/',
        
        # Deployment
        '*deployment*': '10_Deployment_Produccion/scripts/',
        '*produccion*': '10_Deployment_Produccion/scripts/',
        '*docker*': '10_Deployment_Produccion/scripts/',
        '*desplegar*': '10_Deployment_Produccion/scripts/',
        
        # Configuración
        '*config*': '12_Respaldos_Archivos/archivos_obsoletos/',
        '*.ini': '12_Respaldos_Archivos/archivos_obsoletos/',
        '*.cfg': '12_Respaldos_Archivos/archivos_obsoletos/',
        '*.env': '12_Respaldos_Archivos/archivos_obsoletos/',
        '*.yml': '12_Respaldos_Archivos/archivos_obsoletos/'
    }
    
    # Obtener todos los archivos .py y .ipynb en la raíz
    archivos_py = glob.glob('*.py')
    archivos_ipynb = glob.glob('*.ipynb')
    todos_archivos = archivos_py + archivos_ipynb
    
    print(f'Archivos encontrados: {len(todos_archivos)}')
    print(f'  - Python (.py): {len(archivos_py)}')
    print(f'  - Notebooks (.ipynb): {len(archivos_ipynb)}')
    print()
    
    archivos_movidos = 0
    archivos_no_movidos = []
    
    for archivo in todos_archivos:
        movido = False
        
        # Buscar coincidencia exacta primero
        if archivo in mapeo_archivos:
            destino = mapeo_archivos[archivo]
            try:
                # Crear directorio si no existe
                os.makedirs(destino, exist_ok=True)
                shutil.move(archivo, os.path.join(destino, archivo))
                print(f'OK {archivo} -> {destino}')
                archivos_movidos += 1
                movido = True
            except Exception as e:
                print(f'ERROR moviendo {archivo}: {e}')
        
        # Si no se movió, buscar por patrón
        if not movido:
            for patron, destino in mapeo_archivos.items():
                if patron != archivo and patron.startswith('*'):
                    # Convertir patrón glob a coincidencia simple
                    patron_simple = patron.replace('*', '')
                    if patron_simple.lower() in archivo.lower():
                        try:
                            # Crear directorio si no existe
                            os.makedirs(destino, exist_ok=True)
                            shutil.move(archivo, os.path.join(destino, archivo))
                            print(f'OK {archivo} -> {destino} (patrón: {patron})')
                            archivos_movidos += 1
                            movido = True
                            break
                        except Exception as e:
                            print(f'ERROR moviendo {archivo}: {e}')
        
        if not movido:
            archivos_no_movidos.append(archivo)
    
    print()
    print('=' * 80)
    print('RESUMEN DE REORGANIZACION')
    print('=' * 80)
    print(f'Archivos movidos: {archivos_movidos}')
    print(f'Archivos no movidos: {len(archivos_no_movidos)}')
    
    if archivos_no_movidos:
        print()
        print('Archivos no movidos:')
        for archivo in archivos_no_movidos:
            print(f'  - {archivo}')
    
    return archivos_movidos, archivos_no_movidos

def mover_notebooks_especificos():
    """Mueve notebooks específicos por nombre"""
    
    print()
    print('MOVIENDO NOTEBOOKS ESPECIFICOS:')
    print('-' * 50)
    
    notebooks_especificos = {
        '00_Sistema_Principal_MIP_Quillota.ipynb': '01_Sistema_Meteorologico/notebooks/',
        '01_Configuracion_e_imports.ipynb': '11_Documentacion/manuales/',
        '02_Carga_y_Procesamiento_Datos.ipynb': '08_Gestion_Datos/scripts/',
        '04_Visualizaciones.ipynb': '04_Dashboards_Unificados/dashboards/',
        '05_Modelos_ML.ipynb': '06_Modelos_ML_IA/notebooks/',
        '06_Dashboard_Interactivo.ipynb': '04_Dashboards_Unificados/dashboards/',
        '07_Reportes_Automaticos.ipynb': '07_Sistema_Monitoreo/scripts/',
        '08_APIs_Externas.ipynb': '05_APIs_Externas/scripts/',
        '09_Testing_Validacion.ipynb': '09_Testing_Validacion/scripts/',
        '10_Deployment_Produccion.ipynb': '10_Deployment_Produccion/scripts/',
        '11_Monitoreo_Tiempo_Real.ipynb': '07_Sistema_Monitoreo/scripts/',
        '12_Respaldos_Automaticos.ipynb': '12_Respaldos_Archivos/versionado/',
        '13_Optimizacion_Mantenimiento.ipynb': '10_Deployment_Produccion/scripts/',
        '14_Reportes_Avanzados.ipynb': '07_Sistema_Monitoreo/scripts/',
        '15_Integracion_APIs_Externas.ipynb': '05_APIs_Externas/scripts/'
    }
    
    notebooks_movidos = 0
    
    for notebook, destino in notebooks_especificos.items():
        if os.path.exists(notebook):
            try:
                # Crear directorio si no existe
                os.makedirs(destino, exist_ok=True)
                shutil.move(notebook, os.path.join(destino, notebook))
                print(f'OK {notebook} -> {destino}')
                notebooks_movidos += 1
            except Exception as e:
                print(f'ERROR moviendo {notebook}: {e}')
    
    print(f'Notebooks específicos movidos: {notebooks_movidos}')
    return notebooks_movidos

def main():
    """Función principal"""
    
    # 1. Mover archivos por tipo y patrón
    archivos_movidos, archivos_no_movidos = mover_archivos_por_tipo()
    
    # 2. Mover notebooks específicos
    notebooks_movidos = mover_notebooks_especificos()
    
    # 3. Resumen final
    print()
    print('=' * 80)
    print('REORGANIZACION COMPLETADA')
    print('=' * 80)
    print(f'Total archivos movidos: {archivos_movidos + notebooks_movidos}')
    print(f'Archivos no procesados: {len(archivos_no_movidos)}')
    print()
    print('PRÓXIMOS PASOS:')
    print('1. Verificar que los archivos están en las carpetas correctas')
    print('2. Actualizar las rutas en los scripts si es necesario')
    print('3. Ejecutar el sistema reorganizado')

if __name__ == "__main__":
    main()
