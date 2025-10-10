#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reorganización Completa del Proyecto METGO_3D
Separa y organiza el proyecto por módulos específicos
"""

import os
import shutil
import glob
from datetime import datetime

def crear_estructura_carpetas():
    """Crea la estructura de carpetas organizadas por proyecto"""
    
    print('=' * 80)
    print('REORGANIZACION COMPLETA DEL PROYECTO METGO_3D')
    print('=' * 80)
    print(f'Fecha de reorganización: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    # Estructura de carpetas propuesta
    estructura = {
        '01_Sistema_Meteorologico': {
            'descripcion': 'Sistema de pronóstico meteorológico y análisis climático',
            'subcarpetas': ['notebooks', 'scripts', 'datos', 'modelos', 'dashboards', 'reportes']
        },
        '02_Sistema_Agricola': {
            'descripcion': 'Sistema de gestión agrícola y recomendaciones de cultivo',
            'subcarpetas': ['notebooks', 'scripts', 'datos', 'modelos', 'dashboards', 'reportes']
        },
        '03_Sistema_IoT_Drones': {
            'descripcion': 'Sistema de monitoreo IoT y drones agrícolas',
            'subcarpetas': ['scripts', 'config', 'datos', 'logs']
        },
        '04_Dashboards_Unificados': {
            'descripcion': 'Dashboards principales y sistemas de visualización',
            'subcarpetas': ['dashboards', 'templates', 'static', 'config']
        },
        '05_APIs_Externas': {
            'descripcion': 'Integración con APIs meteorológicas y servicios externos',
            'subcarpetas': ['scripts', 'config', 'datos', 'logs']
        },
        '06_Modelos_ML_IA': {
            'descripcion': 'Modelos de machine learning e inteligencia artificial',
            'subcarpetas': ['modelos', 'datos', 'scripts', 'notebooks', 'reportes']
        },
        '07_Sistema_Monitoreo': {
            'descripcion': 'Sistema de monitoreo y alertas en tiempo real',
            'subcarpetas': ['scripts', 'config', 'logs', 'alertas']
        },
        '08_Gestion_Datos': {
            'descripcion': 'Gestión, procesamiento y almacenamiento de datos',
            'subcarpetas': ['datos', 'scripts', 'config', 'respaldos']
        },
        '09_Testing_Validacion': {
            'descripcion': 'Pruebas, validación y control de calidad',
            'subcarpetas': ['tests', 'scripts', 'reportes', 'datos_prueba']
        },
        '10_Deployment_Produccion': {
            'descripcion': 'Despliegue, configuración y mantenimiento en producción',
            'subcarpetas': ['scripts', 'config', 'docker', 'logs']
        },
        '11_Documentacion': {
            'descripcion': 'Documentación técnica y manuales del sistema',
            'subcarpetas': ['manuales', 'api_docs', 'diagramas', 'reportes']
        },
        '12_Respaldos_Archivos': {
            'descripcion': 'Archivos de respaldo y versiones anteriores',
            'subcarpetas': ['backups', 'archivos_obsoletos', 'versionado']
        }
    }
    
    print('1. CREANDO ESTRUCTURA DE CARPETAS:')
    print('-' * 50)
    
    for carpeta, info in estructura.items():
        print(f'Creando: {carpeta}')
        print(f'  Descripción: {info["descripcion"]}')
        
        # Crear carpeta principal
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
            print(f'  OK Carpeta principal creada')
        
        # Crear subcarpetas
        for subcarpeta in info['subcarpetas']:
            ruta_subcarpeta = os.path.join(carpeta, subcarpeta)
            if not os.path.exists(ruta_subcarpeta):
                os.makedirs(ruta_subcarpeta)
                print(f'    OK Subcarpeta: {subcarpeta}')
        
        print()
    
    return estructura

def analizar_archivos_actuales():
    """Analiza los archivos actuales para categorizarlos"""
    
    print('2. ANALIZANDO ARCHIVOS ACTUALES:')
    print('-' * 50)
    
    # Patrones de archivos por categoría
    patrones = {
        'meteorologico': ['*meteorologico*', '*meteo*', '*clima*', '*temperatura*', '*precipitacion*'],
        'agricola': ['*agricola*', '*cultivo*', '*riego*', '*suelo*', '*cosecha*'],
        'iot_drones': ['*iot*', '*drones*', '*satelital*', '*sensor*'],
        'dashboards': ['dashboard_*', '*dashboard*'],
        'apis': ['*api*', '*conector*', '*externo*'],
        'ml_ia': ['*ml*', '*ia*', '*modelo*', '*prediccion*', '*deep_learning*'],
        'monitoreo': ['*monitoreo*', '*alertas*', '*log*', '*auditoria*'],
        'datos': ['*datos*', '*procesamiento*', '*etl*', '*base_datos*'],
        'testing': ['*test*', '*prueba*', '*validacion*'],
        'deployment': ['*deployment*', '*produccion*', '*docker*', '*desplegar*'],
        'documentacion': ['*.md', '*.txt', '*.json', 'README*'],
        'config': ['*config*', '*.ini', '*.cfg', '*.env', '*.yml']
    }
    
    archivos_por_categoria = {}
    
    for categoria, patrones_lista in patrones.items():
        archivos_categoria = []
        for patron in patrones_lista:
            archivos_categoria.extend(glob.glob(patron))
        
        # Filtrar solo archivos (no directorios)
        archivos_categoria = [f for f in archivos_categoria if os.path.isfile(f)]
        archivos_por_categoria[categoria] = archivos_categoria
        
        if archivos_categoria:
            print(f'{categoria.upper()}: {len(archivos_categoria)} archivos')
            for archivo in archivos_categoria[:5]:  # Mostrar solo los primeros 5
                print(f'  - {archivo}')
            if len(archivos_categoria) > 5:
                print(f'  ... y {len(archivos_categoria) - 5} más')
            print()
    
    return archivos_por_categoria

def mover_archivos_por_categoria(archivos_por_categoria):
    """Mueve los archivos a sus carpetas correspondientes"""
    
    print('3. MOVIENDO ARCHIVOS A CARPETAS CORRESPONDIENTES:')
    print('-' * 50)
    
    mapeo_carpetas = {
        'meteorologico': '01_Sistema_Meteorologico',
        'agricola': '02_Sistema_Agricola', 
        'iot_drones': '03_Sistema_IoT_Drones',
        'dashboards': '04_Dashboards_Unificados',
        'apis': '05_APIs_Externas',
        'ml_ia': '06_Modelos_ML_IA',
        'monitoreo': '07_Sistema_Monitoreo',
        'datos': '08_Gestion_Datos',
        'testing': '09_Testing_Validacion',
        'deployment': '10_Deployment_Produccion',
        'documentacion': '11_Documentacion',
        'config': '12_Respaldos_Archivos'
    }
    
    archivos_movidos = 0
    errores = []
    
    for categoria, archivos in archivos_por_categoria.items():
        if not archivos:
            continue
            
        carpeta_destino = mapeo_carpetas.get(categoria, '12_Respaldos_Archivos')
        
        print(f'Moviendo archivos de {categoria.upper()} a {carpeta_destino}:')
        
        for archivo in archivos:
            try:
                # Determinar subcarpeta específica
                if categoria == 'dashboards':
                    subcarpeta = 'dashboards'
                elif categoria == 'config':
                    subcarpeta = 'archivos_obsoletos'
                elif categoria in ['meteorologico', 'agricola', 'ml_ia']:
                    subcarpeta = 'scripts'
                elif categoria == 'documentacion':
                    subcarpeta = 'manuales'
                else:
                    subcarpeta = 'scripts'
                
                destino = os.path.join(carpeta_destino, subcarpeta, archivo)
                
                # Crear directorio si no existe
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                
                # Mover archivo
                shutil.move(archivo, destino)
                print(f'  OK {archivo} -> {destino}')
                archivos_movidos += 1
                
            except Exception as e:
                error_msg = f'Error moviendo {archivo}: {e}'
                errores.append(error_msg)
                print(f'  ERROR {error_msg}')
        
        print()
    
    print(f'Total de archivos movidos: {archivos_movidos}')
    if errores:
        print(f'Errores encontrados: {len(errores)}')
        for error in errores:
            print(f'  - {error}')
    
    return archivos_movidos, errores

def crear_documentacion_proyectos(estructura):
    """Crea documentación para cada proyecto"""
    
    print('4. CREANDO DOCUMENTACION DE PROYECTOS:')
    print('-' * 50)
    
    for carpeta, info in estructura.items():
        readme_path = os.path.join(carpeta, 'README.md')
        
        contenido = f"""# {carpeta.replace('_', ' ').title()}

## Descripción
{info['descripcion']}

## Estructura de Carpetas
"""
        
        for subcarpeta in info['subcarpetas']:
            contenido += f"- `{subcarpeta}/` - {get_descripcion_subcarpeta(subcarpeta)}\n"
        
        contenido += f"""
## Archivos Principales
- [Lista de archivos principales del proyecto]

## Instalación y Configuración
1. Instalar dependencias: `pip install -r requirements.txt`
2. Configurar variables de entorno
3. Ejecutar script principal

## Uso
[Instrucciones de uso específicas para este módulo]

## Contribución
[Guías de contribución para este módulo]

---
*Generado automáticamente el {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print(f'OK README creado: {readme_path}')

def get_descripcion_subcarpeta(subcarpeta):
    """Retorna descripción de subcarpeta"""
    descripciones = {
        'notebooks': 'Jupyter notebooks para análisis y desarrollo',
        'scripts': 'Scripts Python del módulo',
        'datos': 'Datos específicos del módulo',
        'modelos': 'Modelos de ML/IA entrenados',
        'dashboards': 'Interfaces de usuario y visualizaciones',
        'reportes': 'Reportes generados por el módulo',
        'config': 'Archivos de configuración',
        'logs': 'Archivos de log del sistema',
        'tests': 'Pruebas unitarias e integración',
        'docker': 'Configuración de contenedores',
        'manuales': 'Documentación técnica',
        'api_docs': 'Documentación de APIs',
        'diagramas': 'Diagramas y esquemas',
        'backups': 'Respaldos del módulo',
        'archivos_obsoletos': 'Archivos no utilizados',
        'versionado': 'Control de versiones',
        'alertas': 'Sistema de alertas',
        'respaldos': 'Respaldos automáticos'
    }
    return descripciones.get(subcarpeta, 'Carpeta específica del módulo')

def crear_script_ejecucion_principal():
    """Crea script principal para ejecutar el sistema reorganizado"""
    
    print('5. CREANDO SCRIPT DE EJECUCION PRINCIPAL:')
    print('-' * 50)
    
    script_contenido = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema METGO_3D - Ejecución Principal Reorganizado
Ejecuta el sistema completo desde la estructura organizada
"""

import os
import sys
import subprocess
import webbrowser
import time

def ejecutar_modulo(modulo, puerto):
    """Ejecutar un módulo específico"""
    try:
        print(f"Ejecutando {modulo} en puerto {puerto}...")
        
        # Buscar script principal del módulo
        script_path = None
        posibles_scripts = [
            f"{modulo}/scripts/main.py",
            f"{modulo}/scripts/{modulo.lower()}.py",
            f"{modulo}/dashboards/main_dashboard.py"
        ]
        
        for script in posibles_scripts:
            if os.path.exists(script):
                script_path = script
                break
        
        if script_path:
            subprocess.Popen([
                sys.executable, '-m', 'streamlit', 'run', script_path,
                '--server.port', str(puerto), '--server.headless', 'true'
            ])
            time.sleep(2)
            webbrowser.open(f'http://localhost:{puerto}')
            print(f"OK {modulo} ejecutandose en http://localhost:{puerto}")
            return True
        else:
            print(f"WARNING No se encontro script principal para {modulo}")
            return False
            
    except Exception as e:
        print(f"ERROR ejecutando {modulo}: {e}")
        return False

def main():
    print("=" * 80)
    print("METGO_3D - SISTEMA REORGANIZADO")
    print("=" * 80)
    
    modulos = [
        ('01_Sistema_Meteorologico', 8501),
        ('02_Sistema_Agricola', 8502),
        ('04_Dashboards_Unificados', 8503),
        ('06_Modelos_ML_IA', 8504)
    ]
    
    print("Ejecutando módulos principales...")
    
    modulos_ejecutados = 0
    for modulo, puerto in modulos:
        if os.path.exists(modulo):
            if ejecutar_modulo(modulo, puerto):
                modulos_ejecutados += 1
        else:
            print(f"WARNING Modulo {modulo} no encontrado")
    
    print(f"\\nSistema ejecutado: {modulos_ejecutados}/{len(modulos)} módulos activos")
    
    if modulos_ejecutados > 0:
        print("\\nURLs del Sistema:")
        for modulo, puerto in modulos:
            print(f"  - {modulo}: http://localhost:{puerto}")

if __name__ == "__main__":
    main()
'''
    
    with open('ejecutar_sistema_reorganizado.py', 'w', encoding='utf-8') as f:
        f.write(script_contenido)
    
    print('OK Script principal creado: ejecutar_sistema_reorganizado.py')

def main():
    """Función principal de reorganización"""
    
    # 1. Crear estructura de carpetas
    estructura = crear_estructura_carpetas()
    
    # 2. Analizar archivos actuales
    archivos_por_categoria = analizar_archivos_actuales()
    
    # 3. Mover archivos
    archivos_movidos, errores = mover_archivos_por_categoria(archivos_por_categoria)
    
    # 4. Crear documentación
    crear_documentacion_proyectos(estructura)
    
    # 5. Crear script principal
    crear_script_ejecucion_principal()
    
    # Resumen final
    print('=' * 80)
    print('REORGANIZACION COMPLETADA')
    print('=' * 80)
    print(f'Archivos reorganizados: {archivos_movidos}')
    print(f'Errores encontrados: {len(errores)}')
    print(f'Carpetas creadas: {len(estructura)}')
    print()
    print('PRÓXIMOS PASOS:')
    print('1. Revisar la estructura creada')
    print('2. Ejecutar: python ejecutar_sistema_reorganizado.py')
    print('3. Verificar que todos los módulos funcionan correctamente')
    print('4. Actualizar documentación según sea necesario')

if __name__ == "__main__":
    main()
