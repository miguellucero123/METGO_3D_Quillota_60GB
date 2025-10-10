#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico Completo del Sistema para Plotly - METGO_3D
Verifica todas las dependencias y configuraciones necesarias
"""

import sys
import os
import subprocess
import importlib

def diagnostico_completo_sistema():
    """Diagnóstico completo del sistema para Plotly"""
    
    print('=' * 80)
    print('DIAGNOSTICO COMPLETO DEL SISTEMA PARA PLOTLY - METGO_3D')
    print('=' * 80)
    print()
    
    # 1. Verificar versión de Python
    print('1. INFORMACION DE PYTHON:')
    print('-' * 40)
    print(f'Version de Python: {sys.version}')
    print(f'Version info: {sys.version_info}')
    print(f'Plataforma: {sys.platform}')
    print(f'Ejecutable: {sys.executable}')
    print()
    
    # 2. Verificar paquetes críticos
    print('2. PAQUETES CRITICOS PARA PLOTLY:')
    print('-' * 40)
    
    paquetes_criticos = [
        'streamlit',
        'plotly',
        'pandas',
        'numpy',
        'sqlite3',
        'requests',
        'scipy',
        'sklearn'
    ]
    
    for paquete in paquetes_criticos:
        try:
            if paquete == 'sqlite3':
                import sqlite3
                version = sqlite3.sqlite_version
                print(f'✓ {paquete}: {version}')
            else:
                modulo = importlib.import_module(paquete)
                version = getattr(modulo, '__version__', 'Sin versión')
                print(f'✓ {paquete}: {version}')
        except ImportError as e:
            print(f'✗ {paquete}: NO INSTALADO - {e}')
        except Exception as e:
            print(f'? {paquete}: ERROR - {e}')
    
    print()
    
    # 3. Verificar dependencias específicas de Plotly
    print('3. DEPENDENCIAS ESPECIFICAS DE PLOTLY:')
    print('-' * 40)
    
    dependencias_plotly = [
        'plotly.graph_objects',
        'plotly.express',
        'plotly.subplots',
        'plotly.io',
        'plotly.offline',
        'plotly.utils'
    ]
    
    for dep in dependencias_plotly:
        try:
            importlib.import_module(dep)
            print(f'✓ {dep}: Disponible')
        except ImportError as e:
            print(f'✗ {dep}: NO DISPONIBLE - {e}')
        except Exception as e:
            print(f'? {dep}: ERROR - {e}')
    
    print()
    
    # 4. Verificar configuración de Streamlit
    print('4. CONFIGURACION DE STREAMLIT:')
    print('-' * 40)
    
    try:
        import streamlit as st
        print(f'✓ Streamlit: {st.__version__}')
        
        # Verificar configuración
        config_file = os.path.expanduser('~/.streamlit/config.toml')
        if os.path.exists(config_file):
            print(f'✓ Archivo de configuración encontrado: {config_file}')
            with open(config_file, 'r') as f:
                print(f'Contenido: {f.read()[:200]}...')
        else:
            print('⚠ Archivo de configuración no encontrado')
            
    except Exception as e:
        print(f'✗ Error con Streamlit: {e}')
    
    print()
    
    # 5. Verificar variables de entorno
    print('5. VARIABLES DE ENTORNO:')
    print('-' * 40)
    
    variables_importantes = [
        'PATH',
        'PYTHONPATH',
        'STREAMLIT_SERVER_PORT',
        'STREAMLIT_BROWSER_GATHER_USAGE_STATS',
        'PLOTLY_RENDERER'
    ]
    
    for var in variables_importantes:
        valor = os.environ.get(var, 'No definida')
        if len(valor) > 100:
            valor = valor[:100] + '...'
        print(f'{var}: {valor}')
    
    print()
    
    # 6. Verificar archivos de configuración del proyecto
    print('6. ARCHIVOS DE CONFIGURACION DEL PROYECTO:')
    print('-' * 40)
    
    archivos_config = [
        'requirements.txt',
        'setup.py',
        'pyproject.toml',
        'environment.yml',
        'conda.yml'
    ]
    
    for archivo in archivos_config:
        if os.path.exists(archivo):
            print(f'✓ {archivo}: Encontrado')
            try:
                with open(archivo, 'r') as f:
                    contenido = f.read()[:300]
                    print(f'  Contenido: {contenido}...')
            except Exception as e:
                print(f'  Error leyendo: {e}')
        else:
            print(f'✗ {archivo}: No encontrado')
    
    print()
    
    # 7. Verificar permisos y acceso a archivos
    print('7. PERMISOS Y ACCESO:')
    print('-' * 40)
    
    directorio_actual = os.getcwd()
    print(f'Directorio actual: {directorio_actual}')
    print(f'Permisos de escritura: {os.access(directorio_actual, os.W_OK)}')
    print(f'Permisos de lectura: {os.access(directorio_actual, os.R_OK)}')
    print(f'Permisos de ejecución: {os.access(directorio_actual, os.X_OK)}')
    
    # Verificar archivos de dashboards
    dashboards = [f for f in os.listdir('.') if f.startswith('dashboard_') and f.endswith('.py')]
    print(f'Dashboards encontrados: {len(dashboards)}')
    
    for dashboard in dashboards[:5]:  # Solo primeros 5
        perm_lectura = os.access(dashboard, os.R_OK)
        perm_escritura = os.access(dashboard, os.W_OK)
        print(f'  {dashboard}: R={perm_lectura}, W={perm_escritura}')
    
    print()
    
    # 8. Verificar conectividad de red
    print('8. CONECTIVIDAD DE RED:')
    print('-' * 40)
    
    try:
        import requests
        response = requests.get('https://api.open-meteo.com/v1/forecast', timeout=5)
        print(f'✓ API OpenMeteo: Accesible (Status: {response.status_code})')
    except Exception as e:
        print(f'✗ API OpenMeteo: No accesible - {e}')
    
    try:
        response = requests.get('https://plotly.com', timeout=5)
        print(f'✓ Plotly.com: Accesible (Status: {response.status_code})')
    except Exception as e:
        print(f'✗ Plotly.com: No accesible - {e}')
    
    print()
    
    # 9. Verificar memoria y recursos del sistema
    print('9. RECURSOS DEL SISTEMA:')
    print('-' * 40)
    
    try:
        import psutil
        memoria = psutil.virtual_memory()
        print(f'Memoria total: {memoria.total / (1024**3):.1f} GB')
        print(f'Memoria disponible: {memoria.available / (1024**3):.1f} GB')
        print(f'Uso de memoria: {memoria.percent}%')
        
        cpu = psutil.cpu_percent(interval=1)
        print(f'Uso de CPU: {cpu}%')
        
    except ImportError:
        print('⚠ psutil no instalado - no se puede verificar recursos')
    except Exception as e:
        print(f'⚠ Error verificando recursos: {e}')
    
    print()
    
    # 10. Recomendaciones
    print('10. RECOMENDACIONES:')
    print('-' * 40)
    
    print('Para resolver problemas de Plotly:')
    print('1. Verificar que todas las dependencias estén instaladas')
    print('2. Actualizar pip: python -m pip install --upgrade pip')
    print('3. Reinstalar Plotly: pip uninstall plotly && pip install plotly')
    print('4. Reinstalar Streamlit: pip uninstall streamlit && pip install streamlit')
    print('5. Limpiar cache: pip cache purge')
    print('6. Verificar configuración de Streamlit')
    print('7. Verificar permisos de archivos')
    print('8. Verificar conectividad de red')
    
    print()
    print('=' * 80)

def instalar_dependencias_faltantes():
    """Instala dependencias faltantes"""
    print('INSTALANDO DEPENDENCIAS FALTANTES...')
    print('-' * 40)
    
    paquetes_requeridos = [
        'streamlit>=1.28.0',
        'plotly>=5.15.0',
        'pandas>=1.5.0',
        'numpy>=1.24.0',
        'requests>=2.28.0',
        'scipy>=1.10.0',
        'scikit-learn>=1.3.0'
    ]
    
    for paquete in paquetes_requeridos:
        try:
            print(f'Instalando {paquete}...')
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', paquete], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f'✓ {paquete} instalado correctamente')
            else:
                print(f'✗ Error instalando {paquete}: {result.stderr}')
        except Exception as e:
            print(f'✗ Error instalando {paquete}: {e}')

if __name__ == "__main__":
    diagnostico_completo_sistema()
    
    print()
    respuesta = input('¿Deseas instalar dependencias faltantes? (s/n): ')
    if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        instalar_dependencias_faltantes()

