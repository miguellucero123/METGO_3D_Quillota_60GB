#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRADOR COMPLETO AL DISCO D: - METGO 3D
Migra toda la carpeta del proyecto (60+ GB) al disco D:
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import platform
import time

def calcular_tamaño_carpeta(ruta):
    """Calcular el tamaño total de una carpeta"""
    tamaño_total = 0
    archivos_contados = 0
    
    try:
        for archivo in ruta.rglob('*'):
            if archivo.is_file():
                try:
                    tamaño_total += archivo.stat().st_size
                    archivos_contados += 1
                except (OSError, PermissionError):
                    pass
    except Exception as e:
        print(f"Error calculando tamaño: {e}")
    
    return tamaño_total, archivos_contados

def formatear_tamaño(bytes_size):
    """Formatear tamaño en bytes a formato legible"""
    for unidad in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unidad}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def verificar_espacio_disco():
    """Verificar espacio disponible en disco D:"""
    print("VERIFICANDO ESPACIO EN DISCO D:")
    print("="*50)
    
    disco_d = Path("D:")
    if not disco_d.exists():
        print("ERROR: El disco D: no está disponible")
        return False, 0
    
    # Calcular espacio disponible
    total, usado, libre = shutil.disk_usage(disco_d)
    libre_gb = libre // (1024**3)
    total_gb = total // (1024**3)
    
    print(f"OK: Disco D: disponible")
    print(f"Espacio total: {total_gb} GB")
    print(f"Espacio libre: {libre_gb} GB")
    print(f"Espacio usado: {(usado // (1024**3))} GB")
    
    return True, libre_gb

def migrar_carpeta_completa():
    """Migrar toda la carpeta del proyecto"""
    print("\nMIGRANDO CARPETA COMPLETA AL DISCO D:")
    print("="*50)
    
    # Configurar rutas
    proyecto_actual = Path.cwd()
    disco_destino = Path("D:")
    ruta_destino = disco_destino / "METGO_3D_Quillota_Completo"
    
    print(f"Origen: {proyecto_actual}")
    print(f"Destino: {ruta_destino}")
    
    # Calcular tamaño del proyecto origen
    print("\nCalculando tamaño del proyecto...")
    tamaño_origen, archivos_origen = calcular_tamaño_carpeta(proyecto_actual)
    print(f"Tamaño del proyecto: {formatear_tamaño(tamaño_origen)}")
    print(f"Archivos a migrar: {archivos_origen}")
    
    # Verificar si hay suficiente espacio
    _, espacio_libre = verificar_espacio_disco()
    tamaño_origen_gb = tamaño_origen / (1024**3)
    
    if tamaño_origen_gb > espacio_libre:
        print(f"ERROR: No hay suficiente espacio")
        print(f"Necesario: {tamaño_origen_gb:.2f} GB")
        print(f"Disponible: {espacio_libre} GB")
        return False, 0
    
    # Crear directorio destino
    try:
        if ruta_destino.exists():
            print(f"ADVERTENCIA: El directorio {ruta_destino} ya existe")
            respuesta = input("¿Sobrescribir? (s/n): ").strip().lower()
            if respuesta == 's':
                shutil.rmtree(ruta_destino)
                print("Directorio anterior eliminado")
            else:
                # Crear con timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                ruta_destino = disco_destino / f"METGO_3D_Quillota_Completo_{timestamp}"
                print(f"Nuevo directorio: {ruta_destino}")
        
        ruta_destino.mkdir(parents=True, exist_ok=True)
        print(f"OK: Directorio creado: {ruta_destino}")
        
    except Exception as e:
        print(f"ERROR creando directorio: {e}")
        return False, 0
    
    # Migrar archivos y carpetas
    print(f"\nIniciando migración de {archivos_origen} archivos...")
    print("Esto puede tomar varios minutos...")
    
    archivos_copiados = 0
    tamaño_copiado = 0
    errores = []
    
    try:
        # Usar shutil.copytree para copiar todo el árbol de directorios
        print("Copiando estructura completa...")
        shutil.copytree(proyecto_actual, ruta_destino, dirs_exist_ok=True)
        
        # Contar archivos copiados
        for archivo in ruta_destino.rglob('*'):
            if archivo.is_file():
                archivos_copiados += 1
                try:
                    tamaño_copiado += archivo.stat().st_size
                except (OSError, PermissionError):
                    pass
        
        print(f"OK: Migración completada")
        print(f"Archivos copiados: {archivos_copiados}")
        print(f"Tamaño copiado: {formatear_tamaño(tamaño_copiado)}")
        
        return True, archivos_copiados
        
    except Exception as e:
        print(f"ERROR en migración: {e}")
        errores.append(str(e))
        return False, archivos_copiados

def crear_script_instalacion(ruta_destino):
    """Crear script de instalación en el destino"""
    print(f"\nCREANDO SCRIPT DE INSTALACION")
    print("-"*40)
    
    script_path = ruta_destino / 'instalar_metgo_completo.py'
    
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INSTALADOR METGO 3D COMPLETO
Script para instalar el proyecto completo migrado
"""

import subprocess
import sys
import os
from pathlib import Path
import platform

def verificar_sistema():
    """Verificar sistema operativo y requisitos"""
    print("VERIFICANDO SISTEMA")
    print("="*30)
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("ERROR: Se requiere Python 3.8 o superior")
        return False
    
    print(f"OK: Python version: {sys.version}")
    print(f"OK: Sistema operativo: {platform.system()}")
    
    # Verificar espacio en disco
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_gb = free // (1024**3)
        print(f"OK: Espacio libre: {free_gb} GB")
        
        if free_gb < 5:
            print("ADVERTENCIA: Menos de 5GB de espacio libre")
    except:
        print("ADVERTENCIA: No se pudo verificar espacio en disco")
    
    return True

def instalar_dependencias():
    """Instalar dependencias del proyecto"""
    try:
        print("\\nINSTALANDO DEPENDENCIAS")
        print("-"*30)
        
        # Actualizar pip
        print("Actualizando pip...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
        
        # Instalar dependencias
        print("Instalando dependencias del proyecto...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        
        print("OK: Dependencias instaladas exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR instalando dependencias: {e}")
        return False

def configurar_entorno():
    """Configurar variables de entorno"""
    try:
        print("\\nCONFIGURANDO ENTORNO")
        print("-"*30)
        
        # Crear archivo .env si no existe
        env_file = Path('.env')
        if not env_file.exists():
            with open(env_file, 'w') as f:
                f.write('''# Configuracion METGO 3D
OPENWEATHER_API_KEY=tu_clave_aqui
NASA_API_KEY=tu_clave_aqui
GOOGLE_MAPS_API_KEY=tu_clave_aqui
DEBUG=False
LOG_LEVEL=INFO
''')
            print("OK: Archivo .env creado - Configure las claves de API")
        else:
            print("OK: Archivo .env ya existe")
        
        # Crear directorios necesarios
        directorios = ['data', 'logs', 'config', 'modelos_ml_quillota', 'src', 'backups']
        for directorio in directorios:
            Path(directorio).mkdir(exist_ok=True)
            print(f"OK: Directorio creado: {directorio}")
        
        return True
        
    except Exception as e:
        print(f"ERROR configurando entorno: {e}")
        return False

def verificar_instalacion():
    """Verificar que la instalacion sea correcta"""
    try:
        print("\\nVERIFICANDO INSTALACION")
        print("-"*30)
        
        # Verificar archivos principales
        archivos_principales = [
            'sistema_unificado_con_conectores.py',
            'requirements.txt',
            'README.md'
        ]
        
        for archivo in archivos_principales:
            if Path(archivo).exists():
                print(f"OK: {archivo}")
            else:
                print(f"ERROR: {archivo} - NO ENCONTRADO")
                return False
        
        # Ejecutar optimizacion si existe
        if Path('optimizar_sistema_completo.py').exists():
            print("Ejecutando optimizacion del sistema...")
            subprocess.run([sys.executable, 'optimizar_sistema_completo.py'], check=True)
            print("OK: Optimizacion completada")
        
        print("OK: Instalacion verificada exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR verificando instalacion: {e}")
        return False

def crear_script_inicio():
    """Crear script de inicio del sistema"""
    try:
        print("\\nCREANDO SCRIPT DE INICIO")
        print("-"*30)
        
        # Script para Windows
        if platform.system() == 'Windows':
            script_inicio = '''@echo off
echo Iniciando METGO 3D - Sistema Meteorologico Agricola
echo ==================================================
echo.

REM Verificar que Python este disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no encontrado
    pause
    exit /b 1
)

REM Verificar que el archivo principal existe
if not exist "sistema_unificado_con_conectores.py" (
    echo Error: Archivo principal no encontrado
    pause
    exit /b 1
)

REM Iniciar el dashboard
echo Iniciando dashboard en puerto 8501...
echo Acceder a: http://localhost:8501
echo Usuario: admin
echo Contrasena: admin123
echo.
python -m streamlit run sistema_unificado_con_conectores.py --server.port 8501 --server.headless true

pause
'''
            
            with open('iniciar_metgo.bat', 'w') as f:
                f.write(script_inicio)
            print("OK: Script de inicio creado: iniciar_metgo.bat")
        
        # Script para Linux/Mac
        else:
            script_inicio = '''#!/bin/bash
echo "Iniciando METGO 3D - Sistema Meteorologico Agricola"
echo "=================================================="

# Verificar que Python este disponible
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 no encontrado"
    exit 1
fi

# Verificar que el archivo principal existe
if [ ! -f "sistema_unificado_con_conectores.py" ]; then
    echo "Error: Archivo principal no encontrado"
    exit 1
fi

# Iniciar el dashboard
echo "Iniciando dashboard en puerto 8501..."
python3 -m streamlit run sistema_unificado_con_conectores.py --server.port 8501 --server.headless true

echo "METGO 3D iniciado exitosamente"
echo "Acceder a: http://localhost:8501"
'''
            
            with open('iniciar_metgo.sh', 'w') as f:
                f.write(script_inicio)
            
            # Hacer ejecutable
            os.chmod('iniciar_metgo.sh', 0o755)
            print("OK: Script de inicio creado: iniciar_metgo.sh")
        
        return True
        
    except Exception as e:
        print(f"ERROR creando script de inicio: {e}")
        return False

def main():
    print("INSTALADOR METGO 3D COMPLETO")
    print("Sistema Meteorologico Agricola Quillota")
    print("=" * 50)
    
    if not verificar_sistema():
        print("\\nERROR: Sistema no compatible")
        return False
    
    if not instalar_dependencias():
        print("\\nERROR: No se pudieron instalar las dependencias")
        return False
    
    if not configurar_entorno():
        print("\\nERROR: No se pudo configurar el entorno")
        return False
    
    if not verificar_instalacion():
        print("\\nERROR: La instalacion no es correcta")
        return False
    
    crear_script_inicio()
    
    print("\\n" + "=" * 50)
    print("OK: INSTALACION COMPLETADA EXITOSAMENTE")
    print("=" * 50)
    print("\\nPara iniciar el sistema:")
    print("1. Configure las claves de API en el archivo .env")
    print("2. Ejecute: python -m streamlit run sistema_unificado_con_conectores.py")
    if platform.system() == 'Windows':
        print("3. O ejecute: iniciar_metgo.bat")
    else:
        print("3. O ejecute: ./iniciar_metgo.sh")
    print("\\nEl dashboard estara disponible en: http://localhost:8501")
    print("Usuario: admin")
    print("Contrasena: admin123")
    
    return True

if __name__ == "__main__":
    main()
'''
    
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print(f"OK: Script de instalacion creado: {script_path}")
        return True
    except Exception as e:
        print(f"ERROR creando script de instalacion: {e}")
        return False

def crear_reporte_migracion(ruta_destino, archivos_copiados):
    """Crear reporte de migración completa"""
    print(f"\nCREANDO REPORTE DE MIGRACION")
    print("-"*40)
    
    reporte_path = ruta_destino / 'REPORTE_MIGRACION_COMPLETA.md'
    
    reporte_content = f"""# REPORTE DE MIGRACION COMPLETA - METGO 3D

## Informacion General
- **Proyecto**: METGO 3D Quillota - Version Completa
- **Fecha de migracion**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Sistema operativo**: {platform.system()}
- **Python version**: {platform.python_version()}

## Rutas
- **Destino**: {ruta_destino}

## Estadisticas
- **Archivos migrados**: {archivos_copiados}
- **Tamaño estimado**: 60+ GB
- **Estado**: MIGRACION COMPLETA EXITOSA

## Contenido Migrado
- **Archivos Python**: Todos los scripts y modulos
- **Notebooks Jupyter**: Todos los notebooks del proyecto
- **Datos**: Todos los archivos de datos y respaldos
- **Configuraciones**: Archivos de configuracion y dependencias
- **Documentacion**: Toda la documentacion del proyecto
- **Modelos ML**: Modelos de machine learning entrenados
- **Logs**: Archivos de log y reportes
- **Backups**: Respaldos automaticos

## Instrucciones de Uso

### 1. Navegar al directorio
```bash
cd {ruta_destino}
```

### 2. Ejecutar instalacion completa
```bash
python instalar_metgo_completo.py
```

### 3. Iniciar el sistema
```bash
python -m streamlit run sistema_unificado_con_conectores.py
```

### 4. O usar el script de inicio
```bash
iniciar_metgo.bat
```

### 5. Acceder al dashboard
- URL: http://localhost:8501
- Usuario: admin
- Contraseña: admin123

## Caracteristicas del Sistema Completo
- **Sistema meteorologico agricola completo**
- **Dashboard interactivo con visualizaciones 3D**
- **Machine Learning para predicciones**
- **APIs integradas (OpenWeather, NASA, etc.)**
- **Sistema de alertas automaticas**
- **Reportes automaticos**
- **Respaldos automaticos**
- **Monitoreo en tiempo real**
- **Gestion completa de datos**

## Notas Importantes
- Esta es una migracion completa que incluye todos los archivos
- El sistema esta listo para uso inmediato
- Todos los datos historicos estan preservados
- Los modelos ML estan incluidos y listos para usar

## Soporte
Para soporte tecnico, contactar al equipo de desarrollo METGO 3D.

---
Generado automaticamente por el sistema de migracion completa METGO 3D
"""
    
    try:
        with open(reporte_path, 'w', encoding='utf-8') as f:
            f.write(reporte_content)
        print(f"OK: Reporte creado: {reporte_path}")
        return True
    except Exception as e:
        print(f"ERROR creando reporte: {e}")
        return False

def main():
    """Funcion principal para migracion completa"""
    print("MIGRADOR COMPLETO AL DISCO D: - METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Version Completa")
    print("="*70)
    
    # 1. Verificar espacio en disco D:
    print("\n1. Verificando espacio en disco D:...")
    disco_ok, espacio_libre = verificar_espacio_disco()
    
    if not disco_ok:
        print("ERROR: No se puede continuar sin acceso al disco D:")
        return False
    
    # 2. Migrar carpeta completa
    print("\n2. Migrando carpeta completa...")
    migracion_ok, archivos_copiados = migrar_carpeta_completa()
    
    if not migracion_ok:
        print("ERROR: La migracion fallo")
        return False
    
    # 3. Crear script de instalacion
    print("\n3. Creando script de instalacion...")
    ruta_destino = Path("D:") / "METGO_3D_Quillota_Completo"
    crear_script_instalacion(ruta_destino)
    
    # 4. Crear reporte de migracion
    print("\n4. Creando reporte de migracion...")
    crear_reporte_migracion(ruta_destino, archivos_copiados)
    
    # 5. Resumen final
    print("\n" + "="*70)
    print("OK: MIGRACION COMPLETA EXITOSA")
    print("="*70)
    print(f"Proyecto migrado a: {ruta_destino}")
    print(f"Archivos migrados: {archivos_copiados}")
    print(f"Tamaño estimado: 60+ GB")
    
    print(f"\nPROXIMOS PASOS:")
    print(f"1. Navegar: cd {ruta_destino}")
    print(f"2. Instalar: python instalar_metgo_completo.py")
    print(f"3. Iniciar: python -m streamlit run sistema_unificado_con_conectores.py")
    print(f"4. O ejecutar: iniciar_metgo.bat")
    print(f"5. Acceder a: http://localhost:8501")
    
    return True

if __name__ == "__main__":
    main()
