#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Revisión Simple del Proyecto METGO_3D_QUILLOTA_60GB
"""

import os
import glob
from datetime import datetime

def revision_simple():
    print('=' * 80)
    print('REVISION COMPLETA DEL PROYECTO METGO_3D_QUILLOTA_60GB')
    print('=' * 80)
    print(f'Fecha de revision: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()

    # 1. Analizar estructura de directorios
    print('1. ESTRUCTURA DE DIRECTORIOS:')
    print('-' * 40)
    dirs = [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('.')]
    for d in sorted(dirs):
        try:
            files_count = len([f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))])
            print(f'DIR: {d}/ ({files_count} archivos)')
        except:
            print(f'DIR: {d}/ (error accediendo)')

    print()

    # 2. Analizar archivos Python principales
    print('2. ARCHIVOS PYTHON PRINCIPALES:')
    print('-' * 40)
    python_files = glob.glob('*.py')
    dashboard_files = [f for f in python_files if 'dashboard' in f.lower()]
    sistema_files = [f for f in python_files if 'sistema' in f.lower()]
    otros_files = [f for f in python_files if not any(x in f.lower() for x in ['dashboard', 'sistema'])]

    print(f'DASHBOARDS ({len(dashboard_files)}):')
    for f in sorted(dashboard_files):
        try:
            size = os.path.getsize(f) / 1024  # KB
            print(f'   - {f} ({size:.1f} KB)')
        except:
            print(f'   - {f} (error)')

    print(f'SISTEMAS ({len(sistema_files)}):')
    for f in sorted(sistema_files):
        try:
            size = os.path.getsize(f) / 1024  # KB
            print(f'   - {f} ({size:.1f} KB)')
        except:
            print(f'   - {f} (error)')

    print(f'OTROS PYTHON ({len(otros_files)}):')
    for f in sorted(otros_files)[:15]:  # Solo primeros 15
        try:
            size = os.path.getsize(f) / 1024  # KB
            print(f'   - {f} ({size:.1f} KB)')
        except:
            print(f'   - {f} (error)')

    print()

    # 3. Analizar archivos HTML
    print('3. DASHBOARDS HTML:')
    print('-' * 40)
    html_files = glob.glob('*.html')
    for f in sorted(html_files):
        try:
            size = os.path.getsize(f) / 1024  # KB
            print(f'HTML: {f} ({size:.1f} KB)')
        except:
            print(f'HTML: {f} (error)')

    print()

    # 4. Analizar archivos de datos
    print('4. ARCHIVOS DE DATOS:')
    print('-' * 40)
    data_files = glob.glob('*.csv') + glob.glob('*.xlsx') + glob.glob('*.db')
    for f in sorted(data_files):
        try:
            size = os.path.getsize(f) / 1024  # KB
            print(f'DATA: {f} ({size:.1f} KB)')
        except:
            print(f'DATA: {f} (error)')

    print()

    # 5. Analizar notebooks
    print('5. NOTEBOOKS JUPYTER:')
    print('-' * 40)
    notebook_files = glob.glob('*.ipynb')
    for f in sorted(notebook_files):
        try:
            size = os.path.getsize(f) / 1024  # KB
            print(f'NOTEBOOK: {f} ({size:.1f} KB)')
        except:
            print(f'NOTEBOOK: {f} (error)')

    print()

    # 6. Resumen estadistico
    print('6. RESUMEN ESTADISTICO:')
    print('-' * 40)
    total_python = len(python_files)
    total_html = len(html_files)
    total_data = len(data_files)
    total_dirs = len(dirs)
    total_notebooks = len(notebook_files)

    print(f'Directorios: {total_dirs}')
    print(f'Archivos Python: {total_python}')
    print(f'Dashboards Python: {len(dashboard_files)}')
    print(f'Sistemas Python: {len(sistema_files)}')
    print(f'Dashboards HTML: {total_html}')
    print(f'Archivos de datos: {total_data}')
    print(f'Notebooks: {total_notebooks}')

    print()

    # 7. Análisis de dashboards específicos
    print('7. DASHBOARDS PRINCIPALES IDENTIFICADOS:')
    print('-' * 40)
    
    # Dashboards que parecen principales
    dashboards_principales = [
        'dashboard_meteorologico_final.py',
        'dashboard_principal_integrado_metgo.py',
        'dashboard_agricola_avanzado.py',
        'dashboard_completo_metgo.py',
        'dashboard_global_metgo.py',
        'dashboard_agricola_sin_plotly_metgo.py'
    ]
    
    for dash in dashboards_principales:
        if dash in python_files:
            try:
                size = os.path.getsize(dash) / 1024
                print(f'DISPONIBLE: {dash} ({size:.1f} KB)')
            except:
                print(f'ERROR: {dash}')
        else:
            print(f'NO ENCONTRADO: {dash}')

    print()

    # 8. Recomendaciones
    print('8. RECOMENDACIONES:')
    print('-' * 40)
    print('DASHBOARDS A PROBAR PRIMERO:')
    print('   1. dashboard_meteorologico_final.py - Dashboard meteorologico completo')
    print('   2. dashboard_principal_integrado_metgo.py - Sistema unificado')
    print('   3. dashboard_completo_metgo.py - Dashboard completo')
    print('   4. dashboard_global_metgo.py - Dashboard global')
    print('   5. dashboard_agricola_sin_plotly_metgo.py - Sin problemas de Plotly')
    
    print()
    print('DASHBOARDS HTML DISPONIBLES:')
    for html in html_files:
        print(f'   - {html}')

    print()
    print('=' * 80)

if __name__ == "__main__":
    revision_simple()

