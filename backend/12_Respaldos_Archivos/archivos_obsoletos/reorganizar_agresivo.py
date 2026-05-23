#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reorganización Agresiva de Archivos METGO_3D
Mueve TODOS los archivos .py y .ipynb a sus carpetas correspondientes
"""

import os
import shutil
import glob

def mover_todos_los_archivos():
    """Mueve todos los archivos .py y .ipynb a carpetas específicas"""
    
    print('=' * 80)
    print('REORGANIZACION AGRESIVA DE ARCHIVOS')
    print('=' * 80)
    
    # Obtener todos los archivos
    archivos_py = glob.glob('*.py')
    archivos_ipynb = glob.glob('*.ipynb')
    
    print(f'Archivos Python encontrados: {len(archivos_py)}')
    print(f'Notebooks encontrados: {len(archivos_ipynb)}')
    
    # Mapeo específico de archivos
    mapeo_especifico = {
        # Sistema Meteorológico
        '00_Sistema_Principal_MIP_Quillota.ipynb': '01_Sistema_Meteorologico/notebooks/',
        'Fix_Open_Meteo.ipynb': '01_Sistema_Meteorologico/notebooks/',
        'Funcion_OpenMeteo.ipynb': '01_Sistema_Meteorologico/notebooks/',
        'validador_datos_meteorologicos.py': '01_Sistema_Meteorologico/scripts/',
        
        # Sistema Agrícola
        'expansion_regional_metgo.py': '02_Sistema_Agricola/scripts/',
        'expansion_regional_casablanca_metgo.py': '02_Sistema_Agricola/scripts/',
        'riego_automatizado_metgo.py': '02_Sistema_Agricola/scripts/',
        
        # IoT y Drones
        'datos_satelitales_metgo.py': '03_Sistema_IoT_Drones/scripts/',
        'sistema_iot_metgo.py': '03_Sistema_IoT_Drones/scripts/',
        
        # Dashboards
        'dashboard_meteorologico_final.py': '04_Dashboards_Unificados/dashboards/',
        'sistema_auth_dashboard_principal_metgo.py': '04_Dashboards_Unificados/dashboards/',
        'ejecutar_todos_dashboards.py': '04_Dashboards_Unificados/dashboards/',
        '04_Visualizaciones.ipynb': '04_Dashboards_Unificados/dashboards/',
        'visualizacion_3d_metgo.py': '04_Dashboards_Unificados/dashboards/',
        'web_responsive_metgo.py': '04_Dashboards_Unificados/dashboards/',
        
        # APIs
        'apis_avanzadas_metgo.py': '05_APIs_Externas/scripts/',
        'conector_apis_avanzadas.py': '05_APIs_Externas/scripts/',
        'conector_apis_meteorologicas_reales.py': '05_APIs_Externas/scripts/',
        '08_APIs_Externas.ipynb': '05_APIs_Externas/scripts/',
        '15_Integracion_APIs_Externas.ipynb': '05_APIs_Externas/scripts/',
        
        # ML/IA
        'deep_learning_avanzado_metgo.py': '06_Modelos_ML_IA/scripts/',
        'ia_avanzada_metgo.py': '06_Modelos_ML_IA/scripts/',
        '05_Modelos_ML.ipynb': '06_Modelos_ML_IA/notebooks/',
        'pipeline_ml_optimizado.py': '06_Modelos_ML_IA/scripts/',
        
        # Monitoreo
        'monitoreo_avanzado_metgo.py': '07_Sistema_Monitoreo/scripts/',
        'monitoreo_continuo.py': '07_Sistema_Monitoreo/scripts/',
        'monitoreo_tiempo_real.py': '07_Sistema_Monitoreo/scripts/',
        'gestion_alertas.py': '07_Sistema_Monitoreo/scripts/',
        'gestion_auditoria.py': '07_Sistema_Monitoreo/scripts/',
        '07_Reportes_Automaticos.ipynb': '07_Sistema_Monitoreo/scripts/',
        '11_Monitoreo_Tiempo_Real.ipynb': '07_Sistema_Monitoreo/scripts/',
        '14_Reportes_Avanzados.ipynb': '07_Sistema_Monitoreo/scripts/',
        'reportes_automaticos_metgo.py': '07_Sistema_Monitoreo/scripts/',
        'sistema_reportes_automaticos_avanzado.py': '07_Sistema_Monitoreo/scripts/',
        
        # Gestión de Datos
        'gestion_datos.py': '08_Gestion_Datos/scripts/',
        '02_Carga_y_Procesamiento_Datos.ipynb': '08_Gestion_Datos/scripts/',
        'actualizacion_automatica.py': '08_Gestion_Datos/scripts/',
        'procesamiento_datos_metgo.py': '08_Gestion_Datos/scripts/',
        
        # Testing
        'gestion_tests.py': '09_Testing_Validacion/scripts/',
        '09_Testing_Validacion.ipynb': '09_Testing_Validacion/scripts/',
        'testing_integracion_metgo.py': '09_Testing_Validacion/scripts/',
        'pruebas_finales_metgo.py': '09_Testing_Validacion/scripts/',
        'Detector_errores.ipynb': '09_Testing_Validacion/scripts/',
        'Detector_error_beta.ipynb': '09_Testing_Validacion/scripts/',
        'Detector_errpres.ipynb': '09_Testing_Validacion/scripts/',
        'MIP_Complete_Auditor.ipynb': '09_Testing_Validacion/scripts/',
        'MIP_Continuous_Monitor.ipynb': '09_Testing_Validacion/scripts/',
        'MIP_Quick_Fixes.ipynb': '09_Testing_Validacion/scripts/',
        'Proyect_Code_Auditor.ipynb': '09_Testing_Validacion/scripts/',
        'Run_Complete_Audit.ipynb': '09_Testing_Validacion/scripts/',
        
        # Deployment
        'deployment_produccion_metgo.py': '10_Deployment_Produccion/scripts/',
        'deployment_produccion_completo.py': '10_Deployment_Produccion/scripts/',
        'desplegar_sistema.py': '10_Deployment_Produccion/scripts/',
        '10_Deployment_Produccion.ipynb': '10_Deployment_Produccion/scripts/',
        '13_Optimizacion_Mantenimiento.ipynb': '10_Deployment_Produccion/scripts/',
        'optimizacion_rendimiento_metgo.py': '10_Deployment_Produccion/scripts/',
        'optimizador_automatico.py': '10_Deployment_Produccion/scripts/',
        'optimizador_rendimiento_avanzado.py': '10_Deployment_Produccion/scripts/',
        'mantenimiento_automatico.py': '10_Deployment_Produccion/scripts/',
        
        # Documentación
        'gestion_documentacion.py': '11_Documentacion/manuales/',
        'generador_documentacion_simple.py': '11_Documentacion/manuales/',
        'generador_documentacion_tecnica.py': '11_Documentacion/manuales/',
        '01_Configuracion_e_imports.ipynb': '11_Documentacion/manuales/',
        
        # Respaldos
        'gestion_respaldos.py': '12_Respaldos_Archivos/versionado/',
        'respaldos_automaticos_metgo.py': '12_Respaldos_Archivos/versionado/',
        'respaldo_automatico.py': '12_Respaldos_Archivos/versionado/',
        'backup_sistema.py': '12_Respaldos_Archivos/versionado/',
        '12_Respaldos_Automaticos.ipynb': '12_Respaldos_Archivos/versionado/',
        
        # Otros archivos del sistema
        'sistema_unificado_metgo.py': '04_Dashboards_Unificados/dashboards/',
        'sistema_unificado_autenticado.py': '04_Dashboards_Unificados/dashboards/',
        'sistema_integracion_completo_metgo.py': '08_Gestion_Datos/scripts/',
        'integracion_sistemas_existentes_metgo.py': '08_Gestion_Datos/scripts/',
        'integrador_modulos.py': '08_Gestion_Datos/scripts/',
        'orquestador_metgo_avanzado.py': '08_Gestion_Datos/scripts/',
        'pipeline_completo_metgo.py': '08_Gestion_Datos/scripts/',
        'sistema_hibrido_cloud_local.py': '08_Gestion_Datos/scripts/',
        'metricas_negocio_metgo.py': '07_Sistema_Monitoreo/scripts/',
        'gestion_completa.py': '08_Gestion_Datos/scripts/',
        'gestion_cicd.py': '10_Deployment_Produccion/scripts/',
        'gestion_seguridad.py': '07_Sistema_Monitoreo/scripts/',
        'gestion_tareas.py': '08_Gestion_Datos/scripts/',
        'gestion_usuarios.py': '07_Sistema_Monitoreo/scripts/',
        'autenticacion_avanzada_metgo.py': '07_Sistema_Monitoreo/scripts/',
        'sistema_autenticacion_metgo.py': '07_Sistema_Monitoreo/scripts/',
        'auth_module.py': '07_Sistema_Monitoreo/scripts/',
        'sistema_notificaciones_avanzado.py': '07_Sistema_Monitoreo/scripts/',
        'probar_sistema_notificaciones.py': '07_Sistema_Monitoreo/scripts/',
        'activar_notificaciones_simple.py': '07_Sistema_Monitoreo/scripts/',
        'app_movil_metgo.py': '04_Dashboards_Unificados/dashboards/',
        'chatbot_metgo.py': '04_Dashboards_Unificados/dashboards/',
        'visualizador_chats.py': '04_Dashboards_Unificados/dashboards/',
        'visualizador_chats_simple.py': '04_Dashboards_Unificados/dashboards/',
        'escalabilidad_metgo.py': '10_Deployment_Produccion/scripts/',
        'analisis_avanzado_metgo.py': '06_Modelos_ML_IA/scripts/',
        'analisis_rendimiento.py': '07_Sistema_Monitoreo/scripts/',
        'analisis_sistemas_operativos_metgo.py': '07_Sistema_Monitoreo/scripts/',
        'analisis_sistemas_simple_metgo.py': '07_Sistema_Monitoreo/scripts/',
        'monitor_sistema.py': '07_Sistema_Monitoreo/scripts/',
        'verificar_sistema.py': '09_Testing_Validacion/scripts/',
        'verificar_sistema_funcionando.py': '09_Testing_Validacion/scripts/',
        'revision_completa_metgo.py': '09_Testing_Validacion/scripts/',
        'revision_simple_metgo.py': '09_Testing_Validacion/scripts/',
        'resumen_final_metgo.py': '11_Documentacion/manuales/',
        'resumen_sistema.py': '11_Documentacion/manuales/',
        'gestionar_sistema_completo_metgo.py': '08_Gestion_Datos/scripts/',
        'inicio_completo.py': '08_Gestion_Datos/scripts/',
        'cierre_sistema.py': '10_Deployment_Produccion/scripts/',
        'ejecutar_sistema_completo.py': '10_Deployment_Produccion/scripts/',
        'ejecutar_sistema_autenticacion.py': '10_Deployment_Produccion/scripts/',
        'ejecutar_notebooks_maestro.py': '08_Gestion_Datos/scripts/',
        'instalar_metgo.py': '10_Deployment_Produccion/scripts/',
        'instalar_metgo_60gb.py': '10_Deployment_Produccion/scripts/',
        'instalar_metgo_operativo.py': '10_Deployment_Produccion/scripts/',
        'instalar_sistema.py': '10_Deployment_Produccion/scripts/',
        'instrucciones_simple.py': '11_Documentacion/manuales/',
        'instrucciones_sistema_completo.py': '11_Documentacion/manuales/',
        'demo_sistema_completo.py': '11_Documentacion/manuales/',
        'demo_sistema_simple.py': '11_Documentacion/manuales/',
        'abrir_sistema_metgo.py': '10_Deployment_Produccion/scripts/',
        'abrir_sistema_completo_metgo.py': '10_Deployment_Produccion/scripts/',
        'abrir_sistema_completo_simple.py': '10_Deployment_Produccion/scripts/',
        'abrir_sistema_auth_metgo.py': '10_Deployment_Produccion/scripts/',
        'abrir_chats.py': '04_Dashboards_Unificados/dashboards/',
        'implementar_mejoras_sin_emojis.py': '10_Deployment_Produccion/scripts/',
        'migrar_60gb_disco_d.py': '12_Respaldos_Archivos/versionado/',
        'migrar_a_disco_d.py': '12_Respaldos_Archivos/versionado/',
        'migrar_completo_disco_d.py': '12_Respaldos_Archivos/versionado/',
        'migrar_disco_d_final.py': '12_Respaldos_Archivos/versionado/',
        'migrar_disco_d_simple.py': '12_Respaldos_Archivos/versionado/',
        'migrar_d_d.py': '12_Respaldos_Archivos/versionado/',
        'migrar_d_d_sin_emojis.py': '12_Respaldos_Archivos/versionado/',
        'migrar_proyecto_disco.py': '12_Respaldos_Archivos/versionado/',
        'migrar_proyecto_gmail.py': '12_Respaldos_Archivos/versionado/',
        'migrar_proyecto_nube.py': '12_Respaldos_Archivos/versionado/',
        'migraciones_simple.py': '12_Respaldos_Archivos/versionado/',
        'extraer_migraciones.py': '12_Respaldos_Archivos/versionado/',
        'ver_migraciones.py': '12_Respaldos_Archivos/versionado/',
        'optimizar_disco.py': '10_Deployment_Produccion/scripts/',
        'optimizar_sistema.py': '10_Deployment_Produccion/scripts/',
        'optimizar_sistema_completo.py': '10_Deployment_Produccion/scripts/',
        'corregir_plotly_definitivo_metgo.py': '04_Dashboards_Unificados/dashboards/',
        'corregir_plotly_simple_metgo.py': '04_Dashboards_Unificados/dashboards/',
        'reorganizar_archivos_manual.py': '12_Respaldos_Archivos/versionado/',
        'reorganizar_proyecto_metgo.py': '12_Respaldos_Archivos/versionado/',
        'ejecutar_sistema_reorganizado.py': '10_Deployment_Produccion/scripts/'
    }
    
    archivos_movidos = 0
    
    print('Moviendo archivos específicos...')
    
    for archivo, destino in mapeo_especifico.items():
        if os.path.exists(archivo):
            try:
                # Crear directorio si no existe
                os.makedirs(destino, exist_ok=True)
                shutil.move(archivo, os.path.join(destino, archivo))
                print(f'OK {archivo} -> {destino}')
                archivos_movidos += 1
            except Exception as e:
                print(f'ERROR moviendo {archivo}: {e}')
    
    print(f'\nTotal archivos movidos: {archivos_movidos}')
    
    # Mover archivos restantes por categoría general
    print('\nMoviendo archivos restantes por categoría...')
    
    todos_archivos = glob.glob('*.py') + glob.glob('*.ipynb')
    archivos_restantes = 0
    
    for archivo in todos_archivos:
        nombre_lower = archivo.lower()
        
        # Determinar categoría por palabras clave
        if any(word in nombre_lower for word in ['meteorologico', 'meteo', 'clima', 'temperatura']):
            destino = '01_Sistema_Meteorologico/scripts/'
        elif any(word in nombre_lower for word in ['agricola', 'cultivo', 'riego', 'suelo']):
            destino = '02_Sistema_Agricola/scripts/'
        elif any(word in nombre_lower for word in ['iot', 'drones', 'satelital']):
            destino = '03_Sistema_IoT_Drones/scripts/'
        elif any(word in nombre_lower for word in ['dashboard', 'visualizacion', 'web']):
            destino = '04_Dashboards_Unificados/dashboards/'
        elif any(word in nombre_lower for word in ['api', 'conector', 'externo']):
            destino = '05_APIs_Externas/scripts/'
        elif any(word in nombre_lower for word in ['ml', 'ia', 'modelo', 'prediccion', 'deep_learning']):
            destino = '06_Modelos_ML_IA/scripts/'
        elif any(word in nombre_lower for word in ['monitoreo', 'alertas', 'log', 'auditoria', 'reportes']):
            destino = '07_Sistema_Monitoreo/scripts/'
        elif any(word in nombre_lower for word in ['datos', 'procesamiento', 'etl', 'base_datos']):
            destino = '08_Gestion_Datos/scripts/'
        elif any(word in nombre_lower for word in ['test', 'prueba', 'validacion']):
            destino = '09_Testing_Validacion/scripts/'
        elif any(word in nombre_lower for word in ['deployment', 'produccion', 'docker', 'desplegar', 'instalar', 'optimizar']):
            destino = '10_Deployment_Produccion/scripts/'
        elif any(word in nombre_lower for word in ['documentacion', 'generador', 'resumen']):
            destino = '11_Documentacion/manuales/'
        else:
            destino = '12_Respaldos_Archivos/archivos_obsoletos/'
        
        try:
            os.makedirs(destino, exist_ok=True)
            shutil.move(archivo, os.path.join(destino, archivo))
            print(f'OK {archivo} -> {destino}')
            archivos_restantes += 1
        except Exception as e:
            print(f'ERROR moviendo {archivo}: {e}')
    
    print(f'\nArchivos restantes movidos: {archivos_restantes}')
    print(f'Total archivos procesados: {archivos_movidos + archivos_restantes}')

def main():
    mover_todos_los_archivos()

if __name__ == "__main__":
    main()
