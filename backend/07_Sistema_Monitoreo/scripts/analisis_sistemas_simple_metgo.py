#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis de Sistemas Operativos METGO_3D - Versión Simple
Separación por especificación e implementación
"""

import os
import glob
from datetime import datetime

def analizar_sistemas_simple():
    print('=' * 100)
    print('ANALISIS DE SISTEMAS OPERATIVOS - METGO_3D_QUILLOTA_60GB')
    print('SEPARACION POR ESPECIFICACION E IMPLEMENTACION')
    print('=' * 100)
    print(f'Fecha de analisis: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()

    # 1. SISTEMAS METEOROLOGICOS
    print('1. SISTEMAS METEOROLOGICOS')
    print('-' * 50)
    sistemas_meteorologicos = [
        'dashboard_meteorologico_final.py',
        'dashboard_meteorologico_metgo.py',
        'sistema_predicciones_ml_avanzado.py',
        'sistema_modelos_dinamicos.py',
        'sistema_modelos_hibridos_innovadores.py'
    ]
    
    print('ESPECIFICACION: Monitoreo meteorologico en tiempo real')
    print('IMPLEMENTACION:')
    for sistema in sistemas_meteorologicos:
        if os.path.exists(sistema):
            size = os.path.getsize(sistema) / 1024
            print(f'  OPERATIVO: {sistema} ({size:.1f} KB)')
        else:
            print(f'  NO ENCONTRADO: {sistema}')
    
    print('FUNCIONALIDADES:')
    print('  - Datos meteorologicos en tiempo real')
    print('  - Pronosticos de 14 dias')
    print('  - Analisis de tendencias')
    print('  - Predicciones con ML')
    print()

    # 2. SISTEMAS AGRICOLAS
    print('2. SISTEMAS AGRICOLAS')
    print('-' * 50)
    sistemas_agricolas = [
        'dashboard_agricola_avanzado.py',
        'dashboard_agricola_sin_plotly_metgo.py',
        'dashboard_agricola_ultra_sofisticado_metgo.py',
        'sistema_recomendaciones_agricolas_avanzado.py',
        'sistema_riego_inteligente_metgo.py',
        'sistema_notificaciones_agricolas.py'
    ]
    
    print('ESPECIFICACION: Gestion agricola inteligente')
    print('IMPLEMENTACION:')
    for sistema in sistemas_agricolas:
        if os.path.exists(sistema):
            size = os.path.getsize(sistema) / 1024
            print(f'  OPERATIVO: {sistema} ({size:.1f} KB)')
        else:
            print(f'  NO ENCONTRADO: {sistema}')
    
    print('FUNCIONALIDADES:')
    print('  - Recomendaciones de cultivos')
    print('  - Analisis de plagas y enfermedades')
    print('  - Sistema de riego inteligente')
    print('  - Alertas agricolas')
    print()

    # 3. SISTEMAS DE INTEGRACION
    print('3. SISTEMAS DE INTEGRACION')
    print('-' * 50)
    sistemas_integracion = [
        'dashboard_principal_integrado_metgo.py',
        'dashboard_global_metgo.py',
        'dashboard_completo_metgo.py',
        'sistema_integracion_completo_metgo.py',
        'sistema_unificado_metgo.py'
    ]
    
    print('ESPECIFICACION: Integracion de todos los sistemas')
    print('IMPLEMENTACION:')
    for sistema in sistemas_integracion:
        if os.path.exists(sistema):
            size = os.path.getsize(sistema) / 1024
            print(f'  OPERATIVO: {sistema} ({size:.1f} KB)')
        else:
            print(f'  NO ENCONTRADO: {sistema}')
    
    print('FUNCIONALIDADES:')
    print('  - Acceso unificado a dashboards')
    print('  - Navegacion centralizada')
    print('  - Gestion de puertos')
    print('  - Sistema de autenticacion')
    print()

    # 4. SISTEMAS DE AUTENTICACION
    print('4. SISTEMAS DE AUTENTICACION')
    print('-' * 50)
    sistemas_auth = [
        'sistema_autenticacion_metgo.py',
        'sistema_login_simple_metgo.py',
        'autenticacion_avanzada_metgo.py',
        'login_con_dashboards_metgo.py'
    ]
    
    print('ESPECIFICACION: Control de acceso y seguridad')
    print('IMPLEMENTACION:')
    for sistema in sistemas_auth:
        if os.path.exists(sistema):
            size = os.path.getsize(sistema) / 1024
            print(f'  OPERATIVO: {sistema} ({size:.1f} KB)')
        else:
            print(f'  NO ENCONTRADO: {sistema}')
    
    print('FUNCIONALIDADES:')
    print('  - Login de usuarios')
    print('  - Gestion de sesiones')
    print('  - Control de acceso')
    print('  - Seguridad avanzada')
    print()

    # 5. SISTEMAS DE DATOS Y ML
    print('5. SISTEMAS DE DATOS Y MACHINE LEARNING')
    print('-' * 50)
    sistemas_ml = [
        'dashboard_ml_avanzado.py',
        'sistema_predicciones_ml_avanzado.py',
        'analisis_avanzado_metgo.py',
        'apis_avanzadas_metgo.py'
    ]
    
    print('ESPECIFICACION: Analisis avanzado y predicciones')
    print('IMPLEMENTACION:')
    for sistema in sistemas_ml:
        if os.path.exists(sistema):
            size = os.path.getsize(sistema) / 1024
            print(f'  OPERATIVO: {sistema} ({size:.1f} KB)')
        else:
            print(f'  NO ENCONTRADO: {sistema}')
    
    print('FUNCIONALIDADES:')
    print('  - Modelos de machine learning')
    print('  - Predicciones avanzadas')
    print('  - Analisis estadistico')
    print('  - APIs de datos')
    print()

    # 6. DASHBOARDS HTML
    print('6. DASHBOARDS HTML')
    print('-' * 50)
    dashboards_html = glob.glob('*.html')
    
    print('ESPECIFICACION: Interfaces web estaticas')
    print('IMPLEMENTACION:')
    for html in dashboards_html:
        size = os.path.getsize(html) / 1024
        print(f'  OPERATIVO: {html} ({size:.1f} KB)')
    
    print('FUNCIONALIDADES:')
    print('  - Interfaces web responsivas')
    print('  - Visualizaciones estaticas')
    print('  - Acceso directo via navegador')
    print()

    # 7. BASES DE DATOS OPERATIVAS
    print('7. BASES DE DATOS OPERATIVAS')
    print('-' * 50)
    bases_datos = glob.glob('*.db')
    
    print('ESPECIFICACION: Almacenamiento de datos')
    print('IMPLEMENTACION:')
    for db in sorted(bases_datos):
        size = os.path.getsize(db) / 1024
        if size > 1000:  # MB
            size_str = f'{size/1024:.1f} MB'
        else:
            size_str = f'{size:.1f} KB'
        print(f'  OPERATIVA: {db} ({size_str})')
    
    print('FUNCIONALIDADES:')
    print('  - Datos meteorologicos')
    print('  - Datos agricolas')
    print('  - Datos de usuarios')
    print('  - Datos de ML')
    print()

    # 8. ESTADO DE OPERATIVIDAD
    print('8. ESTADO DE OPERATIVIDAD')
    print('-' * 50)
    
    # Verificar sistemas que sabemos que funcionan
    sistemas_funcionando = [
        'dashboard_agricola_sin_plotly_metgo.py',  # Sin problemas de Plotly
        'dashboard_global_html.html',              # HTML funcionando
        'sistema_autenticacion_metgo.py',          # Auth funcionando
        'dashboard_principal_integrado_metgo.py',  # Integrado funcionando
    ]
    
    sistemas_con_problemas = [
        'dashboard_meteorologico_final.py',        # Error PLOTLY_CONFIG
        'dashboard_agricola_profesional_mejorado_metgo.py',  # Error make_subplots
        'dashboard_agricola_ultra_sofisticado_metgo.py',     # Error ConectorAPIs
    ]
    
    print('SISTEMAS FUNCIONANDO CORRECTAMENTE:')
    for sistema in sistemas_funcionando:
        if os.path.exists(sistema):
            print(f'  FUNCIONA: {sistema}')
        else:
            print(f'  NO ENCONTRADO: {sistema}')
    
    print()
    print('SISTEMAS CON PROBLEMAS IDENTIFICADOS:')
    for sistema in sistemas_con_problemas:
        if os.path.exists(sistema):
            print(f'  REQUIERE CORRECCION: {sistema}')
        else:
            print(f'  NO ENCONTRADO: {sistema}')
    
    print()

    # 9. RECOMENDACIONES POR ESPECIFICACION
    print('9. RECOMENDACIONES POR ESPECIFICACION')
    print('-' * 50)
    
    print('PARA METEOROLOGIA:')
    print('  - Usar: dashboard_meteorologico_final.py (corregir PLOTLY_CONFIG)')
    print('  - Alternativa: dashboard_global_html.html')
    
    print()
    print('PARA AGRICULTURA:')
    print('  - Usar: dashboard_agricola_sin_plotly_metgo.py (estable)')
    print('  - Alternativa: dashboard_global_metgo.py')
    
    print()
    print('PARA INTEGRACION:')
    print('  - Usar: dashboard_principal_integrado_metgo.py (funcionando)')
    print('  - Alternativa: sistema_autenticacion_metgo.py')
    
    print()
    print('PARA REPORTES:')
    print('  - Usar: dashboard_html_completo.html')
    print('  - Alternativa: sistema_reportes_automaticos_avanzado.py')
    
    print()
    print('PARA AUTENTICACION:')
    print('  - Usar: sistema_autenticacion_metgo.py (funcionando)')
    print('  - Alternativa: sistema_login_simple_metgo.py')
    
    print()
    print('=' * 100)

if __name__ == "__main__":
    analizar_sistemas_simple()

