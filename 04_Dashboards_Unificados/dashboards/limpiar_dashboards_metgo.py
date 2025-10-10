#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limpieza y Organización de Dashboards METGO_3D
Elimina dashboards duplicados y organiza el sistema
"""

import os
import glob
import shutil
from datetime import datetime

def limpiar_dashboards():
    """Limpia y organiza los dashboards del sistema"""
    
    print('=' * 80)
    print('LIMPIEZA Y ORGANIZACION DE DASHBOARDS METGO_3D')
    print('=' * 80)
    print(f'Fecha de limpieza: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    # 1. Identificar todos los dashboards
    print('1. IDENTIFICANDO DASHBOARDS EXISTENTES:')
    print('-' * 50)
    
    dashboards_python = glob.glob('dashboard_*.py')
    dashboards_html = glob.glob('dashboard_*.html')
    
    print(f'Dashboards Python encontrados: {len(dashboards_python)}')
    print(f'Dashboards HTML encontrados: {len(dashboards_html)}')
    
    # 2. Categorizar dashboards
    print()
    print('2. CATEGORIZANDO DASHBOARDS:')
    print('-' * 50)
    
    dashboards_principales = []
    dashboards_duplicados = []
    dashboards_experimentales = []
    dashboards_corregidos = []
    
    for dashboard in dashboards_python:
        nombre = dashboard.lower()
        
        if any(x in nombre for x in ['principal', 'integrado', 'global', 'completo']):
            dashboards_principales.append(dashboard)
        elif any(x in nombre for x in ['corregido', 'sin_plotly', 'limpio', 'moderno']):
            dashboards_corregidos.append(dashboard)
        elif any(x in nombre for x in ['ultra_sofisticado', 'avanzado_completo', 'profesional_mejorado']):
            dashboards_experimentales.append(dashboard)
        else:
            dashboards_duplicados.append(dashboard)
    
    print(f'Dashboards principales: {len(dashboards_principales)}')
    for d in dashboards_principales:
        print(f'  - {d}')
    
    print(f'Dashboards corregidos: {len(dashboards_corregidos)}')
    for d in dashboards_corregidos:
        print(f'  - {d}')
    
    print(f'Dashboards experimentales: {len(dashboards_experimentales)}')
    for d in dashboards_experimentales:
        print(f'  - {d}')
    
    print(f'Dashboards duplicados: {len(dashboards_duplicados)}')
    for d in dashboards_duplicados:
        print(f'  - {d}')
    
    # 3. Crear directorio de respaldo
    print()
    print('3. CREANDO RESPALDO:')
    print('-' * 50)
    
    backup_dir = f'backup_dashboards_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f'Directorio de respaldo creado: {backup_dir}')
    
    # 4. Mover dashboards duplicados a respaldo
    print()
    print('4. MOVIENDO DASHBOARDS DUPLICADOS:')
    print('-' * 50)
    
    dashboards_para_mover = dashboards_duplicados + dashboards_experimentales
    
    for dashboard in dashboards_para_mover:
        try:
            shutil.move(dashboard, os.path.join(backup_dir, dashboard))
            print(f'  Movido: {dashboard} -> {backup_dir}/')
        except Exception as e:
            print(f'  Error moviendo {dashboard}: {e}')
    
    # 5. Identificar dashboards finales recomendados
    print()
    print('5. DASHBOARDS FINALES RECOMENDADOS:')
    print('-' * 50)
    
    dashboards_finales = []
    
    # Dashboard meteorológico (el que funciona)
    if 'dashboard_meteorologico_final.py' in dashboards_python:
        dashboards_finales.append('dashboard_meteorologico_final.py')
    
    # Dashboard agrícola (sin problemas de Plotly)
    if 'dashboard_agricola_sin_plotly_metgo.py' in dashboards_python:
        dashboards_finales.append('dashboard_agricola_sin_plotly_metgo.py')
    
    # Sistema principal
    if 'sistema_auth_dashboard_principal_metgo.py' in glob.glob('sistema_*.py'):
        dashboards_finales.append('sistema_auth_dashboard_principal_metgo.py')
    
    # Dashboard global HTML
    if 'dashboard_global_html.html' in dashboards_html:
        dashboards_finales.append('dashboard_global_html.html')
    
    print('Dashboards recomendados para mantener:')
    for d in dashboards_finales:
        print(f'  ✓ {d}')
    
    # 6. Crear script de ejecución simple
    print()
    print('6. CREANDO SCRIPT DE EJECUCION SIMPLE:')
    print('-' * 50)
    
    script_ejecucion = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Ejecución Simple - METGO_3D
Ejecuta los dashboards principales del sistema
"""

import subprocess
import sys
import time
import webbrowser

def ejecutar_dashboard(dashboard, puerto):
    """Ejecutar un dashboard en un puerto específico"""
    try:
        print(f"Ejecutando {dashboard} en puerto {puerto}...")
        subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', dashboard,
            '--server.port', str(puerto), '--server.headless', 'true'
        ])
        time.sleep(3)
        webbrowser.open(f'http://localhost:{puerto}')
        print(f"✓ {dashboard} ejecutándose en http://localhost:{puerto}")
        return True
    except Exception as e:
        print(f"✗ Error ejecutando {dashboard}: {e}")
        return False

def main():
    print("=" * 60)
    print("METGO_3D - SISTEMA DE DASHBOARDS LIMPIADO")
    print("=" * 60)
    
    dashboards = [
        ('sistema_auth_dashboard_principal_metgo.py', 8501),
        ('dashboard_meteorologico_final.py', 8502),
        ('dashboard_agricola_sin_plotly_metgo.py', 8503)
    ]
    
    print("Ejecutando dashboards principales...")
    for dashboard, puerto in dashboards:
        if os.path.exists(dashboard):
            ejecutar_dashboard(dashboard, puerto)
        else:
            print(f"⚠ {dashboard} no encontrado")
    
    print("\\nSistema METGO_3D ejecutándose correctamente!")
    print("Dashboards disponibles:")
    print("  - Sistema Principal: http://localhost:8501")
    print("  - Dashboard Meteorológico: http://localhost:8502") 
    print("  - Dashboard Agrícola: http://localhost:8503")

if __name__ == "__main__":
    import os
    main()
'''
    
    with open('ejecutar_sistema_limpiado.py', 'w', encoding='utf-8') as f:
        f.write(script_ejecucion)
    
    print('Script de ejecución creado: ejecutar_sistema_limpiado.py')
    
    # 7. Resumen final
    print()
    print('7. RESUMEN DE LIMPIEZA:')
    print('-' * 50)
    
    dashboards_restantes = glob.glob('dashboard_*.py')
    
    print(f'Dashboards antes de limpieza: {len(dashboards_python)}')
    print(f'Dashboards después de limpieza: {len(dashboards_restantes)}')
    print(f'Dashboards movidos a respaldo: {len(dashboards_para_mover)}')
    
    print()
    print('Dashboards principales restantes:')
    for d in dashboards_restantes:
        print(f'  - {d}')
    
    print()
    print('=' * 80)
    print('LIMPIEZA COMPLETADA')
    print('=' * 80)
    print()
    print('RECOMENDACIONES:')
    print('1. Usar ejecutar_sistema_limpiado.py para ejecutar el sistema')
    print('2. Los dashboards duplicados están en backup_dashboards_*')
    print('3. Mantener solo los dashboards principales')
    print('4. Eliminar backups cuando esté seguro de que todo funciona')

if __name__ == "__main__":
    limpiar_dashboards()

