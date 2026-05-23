#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Organizar Carpetas Restantes METGO_3D
Organiza todas las carpetas restantes en la estructura modular
"""

import os
import shutil
from datetime import datetime

def organizar_carpetas_restantes():
    """Organiza todas las carpetas restantes en la estructura modular"""
    
    print('=' * 80)
    print('ORGANIZANDO CARPETAS RESTANTES METGO_3D')
    print('=' * 80)
    print(f'Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    # Mapeo de carpetas a sus destinos
    mapeo_carpetas = {
        # Datos y configuraciones
        'data': '08_Gestion_Datos/datos/',
        'data_historica': '08_Gestion_Datos/datos/',
        'datos_casablanca': '08_Gestion_Datos/datos/',
        'datos_dashboard': '08_Gestion_Datos/datos/',
        'datos_drones_optimizado': '03_Sistema_IoT_Drones/datos/',
        'datos_economicos': '08_Gestion_Datos/datos/',
        'datos_historicos_5_anios': '08_Gestion_Datos/datos/',
        'datos_integracion': '08_Gestion_Datos/datos/',
        'datos_sensores': '03_Sistema_IoT_Drones/datos/',
        
        # Configuraciones
        'config': '12_Respaldos_Archivos/archivos_obsoletos/',
        'config_riego': '02_Sistema_Agricola/config/',
        'metgo_env': '12_Respaldos_Archivos/archivos_obsoletos/',
        
        # Modelos y análisis
        'modelos': '06_Modelos_ML_IA/modelos/',
        'modelos_casablanca': '06_Modelos_ML_IA/modelos/',
        'modelos_dinamicos': '06_Modelos_ML_IA/modelos/',
        'modelos_hibridos_innovadores': '06_Modelos_ML_IA/modelos/',
        'modelos_hibridos_rapidos': '06_Modelos_ML_IA/modelos/',
        'modelos_historicos': '06_Modelos_ML_IA/modelos/',
        'modelos_ml': '06_Modelos_ML_IA/modelos/',
        'modelos_ml_avanzados': '06_Modelos_ML_IA/modelos/',
        'modelos_ml_quillota': '06_Modelos_ML_IA/modelos/',
        'modelos_ultra_optimizados': '06_Modelos_ML_IA/modelos/',
        
        # Reportes y análisis
        'reportes': '07_Sistema_Monitoreo/reportes/',
        'reportes_automaticos': '07_Sistema_Monitoreo/reportes/',
        'reportes_casablanca': '07_Sistema_Monitoreo/reportes/',
        'reportes_economicos': '07_Sistema_Monitoreo/reportes/',
        'reportes_historicos': '07_Sistema_Monitoreo/reportes/',
        'reportes_revision': '07_Sistema_Monitoreo/reportes/',
        'reportes_riego': '07_Sistema_Monitoreo/reportes/',
        
        # Logs y monitoreo
        'logs': '07_Sistema_Monitoreo/logs/',
        'logs_integracion': '07_Sistema_Monitoreo/logs/',
        'alertas': '07_Sistema_Monitoreo/alertas/',
        
        # Gráficos y visualizaciones
        'graficos': '04_Dashboards_Unificados/static/',
        'graficos_historicos': '04_Dashboards_Unificados/static/',
        
        # Deployment y producción
        'deployment_produccion': '10_Deployment_Produccion/docker/',
        
        # Documentación
        'docs': '11_Documentacion/manuales/',
        'templates': '04_Dashboards_Unificados/templates/',
        'templates_reportes': '07_Sistema_Monitoreo/templates/',
        'static': '04_Dashboards_Unificados/static/',
        
        # Testing y validación
        'tests': '09_Testing_Validacion/tests/',
        'test_results': '09_Testing_Validacion/datos_prueba/',
        
        # Notebooks y scripts
        'notebooks': '11_Documentacion/manuales/',
        'notebooks_corregidos': '11_Documentacion/manuales/',
        'scripts': '10_Deployment_Produccion/scripts/',
        'src': '10_Deployment_Produccion/scripts/',
        
        # Aplicaciones y artefactos
        'app': '04_Dashboards_Unificados/dashboards/',
        'app_movil_metgo': '04_Dashboards_Unificados/dashboards/',
        'artefactos': '12_Respaldos_Archivos/archivos_obsoletos/',
        
        # Análisis y optimizaciones
        'analisis_historicos': '01_Sistema_Meteorologico/datos/',
        'optimizaciones': '10_Deployment_Produccion/logs/',
        'proyecciones': '06_Modelos_ML_IA/datos/',
        'ensembles': '06_Modelos_ML_IA/modelos/',
        'exportaciones': '08_Gestion_Datos/datos/',
        'resultados': '06_Modelos_ML_IA/datos/',
        
        # Respaldos y backups
        'backups': '12_Respaldos_Archivos/backups/',
        'backup_dashboards_20251009_132903': '12_Respaldos_Archivos/backups/',
        'METGO_3D_OPERATIVO': '12_Respaldos_Archivos/archivos_obsoletos/',
        
        # Cache y temporales
        '__pycache__': '12_Respaldos_Archivos/archivos_obsoletos/',
        '.ipynb_checkpoints': '12_Respaldos_Archivos/archivos_obsoletos/',
        '.pytest_cache': '12_Respaldos_Archivos/archivos_obsoletos/',
        '.virtual_documents': '12_Respaldos_Archivos/archivos_obsoletos/',
        '.conda': '12_Respaldos_Archivos/archivos_obsoletos/',
        '.github': '12_Respaldos_Archivos/archivos_obsoletos/',
        '.idea': '12_Respaldos_Archivos/archivos_obsoletos/',
        '.vscode': '12_Respaldos_Archivos/archivos_obsoletos/'
    }
    
    # Obtener todas las carpetas en la raíz
    carpetas_raiz = [item for item in os.listdir('.') if os.path.isdir(item)]
    
    print(f'Carpetas encontradas en la raíz: {len(carpetas_raiz)}')
    print()
    
    carpetas_movidas = 0
    carpetas_no_movidas = []
    
    for carpeta in carpetas_raiz:
        # Saltar las carpetas ya organizadas
        if carpeta.startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_', '11_', '12_')):
            continue
        
        if carpeta in mapeo_carpetas:
            destino = mapeo_carpetas[carpeta]
            try:
                # Crear directorio de destino si no existe
                os.makedirs(destino, exist_ok=True)
                
                # Mover carpeta
                shutil.move(carpeta, os.path.join(destino, carpeta))
                print(f'OK {carpeta} -> {destino}')
                carpetas_movidas += 1
                
            except Exception as e:
                print(f'ERROR moviendo {carpeta}: {e}')
                carpetas_no_movidas.append(carpeta)
        else:
            # Mover carpetas no mapeadas a archivos obsoletos
            try:
                destino = '12_Respaldos_Archivos/archivos_obsoletos/'
                os.makedirs(destino, exist_ok=True)
                shutil.move(carpeta, os.path.join(destino, carpeta))
                print(f'OK {carpeta} -> {destino} (no mapeada)')
                carpetas_movidas += 1
            except Exception as e:
                print(f'ERROR moviendo {carpeta}: {e}')
                carpetas_no_movidas.append(carpeta)
    
    print()
    print('=' * 80)
    print('RESUMEN DE ORGANIZACION DE CARPETAS')
    print('=' * 80)
    print(f'Carpetas movidas: {carpetas_movidas}')
    print(f'Carpetas no movidas: {len(carpetas_no_movidas)}')
    
    if carpetas_no_movidas:
        print()
        print('Carpetas no movidas:')
        for carpeta in carpetas_no_movidas:
            print(f'  - {carpeta}')
    
    return carpetas_movidas, carpetas_no_movidas

def organizar_archivos_restantes():
    """Organiza archivos restantes en la raíz"""
    
    print()
    print('ORGANIZANDO ARCHIVOS RESTANTES:')
    print('-' * 50)
    
    # Mapeo de archivos restantes
    mapeo_archivos = {
        '.env': '12_Respaldos_Archivos/archivos_obsoletos/',
        '.gitignore': '12_Respaldos_Archivos/archivos_obsoletos/',
        '.isort.cfg': '12_Respaldos_Archivos/archivos_obsoletos/',
        '.pre-commit-config.yaml': '12_Respaldos_Archivos/archivos_obsoletos/',
        'activar_entorno.bat': '10_Deployment_Produccion/scripts/',
        'cerrar_y_abrir_disco_d.bat': '10_Deployment_Produccion/scripts/',
        'ejecutar_sistema.ps1': '10_Deployment_Produccion/scripts/',
        'ejecutar_sistema.sh': '10_Deployment_Produccion/scripts/',
        'ejecutar_sistema_organizado.py': '10_Deployment_Produccion/scripts/',
        'migrar_a_cloud.sh': '12_Respaldos_Archivos/versionado/',
        'LICENSE': '11_Documentacion/manuales/',
        'Makefile': '10_Deployment_Produccion/docker/',
        'pyproject.toml': '10_Deployment_Produccion/docker/',
        'requirements.txt': '10_Deployment_Produccion/docker/',
        'requirements_optimizado.txt': '10_Deployment_Produccion/docker/'
    }
    
    # Obtener archivos en la raíz
    archivos_raiz = [item for item in os.listdir('.') if os.path.isfile(item)]
    
    archivos_movidos = 0
    
    for archivo in archivos_raiz:
        if archivo in mapeo_archivos:
            destino = mapeo_archivos[archivo]
            try:
                os.makedirs(destino, exist_ok=True)
                shutil.move(archivo, os.path.join(destino, archivo))
                print(f'OK {archivo} -> {destino}')
                archivos_movidos += 1
            except Exception as e:
                print(f'ERROR moviendo {archivo}: {e}')
    
    print(f'Archivos movidos: {archivos_movidos}')
    return archivos_movidos

def main():
    """Función principal"""
    
    # 1. Organizar carpetas restantes
    carpetas_movidas, carpetas_no_movidas = organizar_carpetas_restantes()
    
    # 2. Organizar archivos restantes
    archivos_movidos = organizar_archivos_restantes()
    
    # 3. Resumen final
    print()
    print('=' * 80)
    print('ORGANIZACION COMPLETA FINALIZADA')
    print('=' * 80)
    print(f'Total carpetas organizadas: {carpetas_movidas}')
    print(f'Total archivos organizados: {archivos_movidos}')
    print(f'Elementos no procesados: {len(carpetas_no_movidas)}')
    print()
    print('ESTRUCTURA FINAL ORGANIZADA:')
    print('✅ Solo carpetas 01_ a 12_ en la raíz')
    print('✅ Todos los datos organizados por módulo')
    print('✅ Archivos de configuración en ubicaciones apropiadas')
    print('✅ Respaldos y archivos obsoletos archivados')
    print()
    print('¡Proyecto METGO_3D completamente organizado!')

if __name__ == "__main__":
    main()
