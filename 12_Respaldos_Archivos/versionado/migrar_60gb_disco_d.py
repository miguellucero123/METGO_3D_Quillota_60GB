#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRADOR 60GB AL DISCO D: - METGO 3D
Migra toda la carpeta del proyecto (60+ GB) al disco D:
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import platform

def verificar_espacio():
    """Verificar espacio disponible en disco D:"""
    print("VERIFICANDO ESPACIO EN DISCO D:")
    print("="*50)
    
    disco_d = Path("D:")
    if not disco_d.exists():
        print("ERROR: El disco D: no está disponible")
        return False, 0
    
    total, usado, libre = shutil.disk_usage(disco_d)
    libre_gb = libre // (1024**3)
    
    print(f"OK: Disco D: disponible")
    print(f"Espacio libre: {libre_gb} GB")
    
    if libre_gb < 70:  # Necesitamos al menos 70GB para 60GB + overhead
        print(f"ADVERTENCIA: Solo {libre_gb} GB libres, se recomiendan 70+ GB")
        respuesta = input("¿Continuar de todas formas? (s/n): ").strip().lower()
        if respuesta != 's':
            return False, 0
    
    return True, libre_gb

def migrar_todo():
    """Migrar toda la carpeta del proyecto"""
    print("\nMIGRANDO CARPETA COMPLETA (60+ GB)")
    print("="*50)
    
    proyecto_actual = Path.cwd()
    disco_destino = Path("D:")
    ruta_destino = disco_destino / "METGO_3D_Quillota_60GB"
    
    print(f"Origen: {proyecto_actual}")
    print(f"Destino: {ruta_destino}")
    
    # Verificar si el destino ya existe
    if ruta_destino.exists():
        print(f"ADVERTENCIA: El directorio {ruta_destino} ya existe")
        respuesta = input("¿Sobrescribir? (s/n): ").strip().lower()
        if respuesta == 's':
            print("Eliminando directorio anterior...")
            shutil.rmtree(ruta_destino)
        else:
            # Crear con timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            ruta_destino = disco_destino / f"METGO_3D_Quillota_60GB_{timestamp}"
            print(f"Nuevo directorio: {ruta_destino}")
    
    try:
        print("\nIniciando migración completa...")
        print("Esto puede tomar 30-60 minutos dependiendo de la velocidad del disco...")
        print("Por favor, no interrumpa el proceso...")
        
        # Crear directorio padre
        ruta_destino.parent.mkdir(parents=True, exist_ok=True)
        
        # Copiar todo el árbol de directorios
        print("Copiando estructura completa...")
        shutil.copytree(proyecto_actual, ruta_destino)
        
        print("OK: Migración completada exitosamente")
        
        # Contar archivos copiados
        archivos_copiados = 0
        for archivo in ruta_destino.rglob('*'):
            if archivo.is_file():
                archivos_copiados += 1
        
        print(f"Archivos copiados: {archivos_copiados}")
        
        return ruta_destino, archivos_copiados
        
    except Exception as e:
        print(f"ERROR en migración: {e}")
        return None, 0

def crear_script_instalacion(ruta_destino):
    """Crear script de instalación simple"""
    print(f"\nCREANDO SCRIPT DE INSTALACION")
    print("-"*40)
    
    script_path = ruta_destino / 'instalar_metgo_60gb.py'
    
    script_content = '''#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

print("INSTALADOR METGO 3D - VERSION 60GB")
print("="*40)

# Instalar dependencias
try:
    print("Instalando dependencias...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
    print("OK: Dependencias instaladas")
except Exception as e:
    print(f"ERROR: {e}")

# Crear directorios
directorios = ['data', 'logs', 'config', 'modelos_ml_quillota', 'backups']
for directorio in directorios:
    Path(directorio).mkdir(exist_ok=True)

# Crear .env
env_file = Path('.env')
if not env_file.exists():
    with open(env_file, 'w') as f:
        f.write("# Configuracion METGO 3D\\n")
        f.write("OPENWEATHER_API_KEY=tu_clave_aqui\\n")
        f.write("NASA_API_KEY=tu_clave_aqui\\n")
        f.write("GOOGLE_MAPS_API_KEY=tu_clave_aqui\\n")
        f.write("DEBUG=False\\n")
        f.write("LOG_LEVEL=INFO\\n")
    print("OK: Archivo .env creado")

print("\\nOK: INSTALACION COMPLETADA")
print("\\nPara iniciar:")
print("python -m streamlit run sistema_unificado_con_conectores.py")
print("\\nURL: http://localhost:8501")
print("Usuario: admin")
print("Contrasena: admin123")
'''
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"OK: Script creado: {script_path}")

def crear_script_inicio(ruta_destino):
    """Crear script de inicio para Windows"""
    print(f"\nCREANDO SCRIPT DE INICIO")
    print("-"*40)
    
    script_path = ruta_destino / 'iniciar_metgo_60gb.bat'
    
    script_content = '''@echo off
echo Iniciando METGO 3D - Version 60GB
echo ==================================
echo.
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no encontrado
    pause
    exit /b 1
)
echo Iniciando dashboard...
echo URL: http://localhost:8501
echo Usuario: admin
echo Contrasena: admin123
echo.
python -m streamlit run sistema_unificado_con_conectores.py --server.port 8501 --server.headless true
pause
'''
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"OK: Script de inicio creado: {script_path}")

def crear_reporte(ruta_destino, archivos_copiados):
    """Crear reporte de migración"""
    print(f"\nCREANDO REPORTE")
    print("-"*30)
    
    reporte_path = ruta_destino / 'REPORTE_MIGRACION_60GB.md'
    
    reporte_content = f"""# REPORTE DE MIGRACION 60GB - METGO 3D

**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Sistema**: {platform.system()}
**Destino**: {ruta_destino}
**Archivos migrados**: {archivos_copiados}
**Tamaño estimado**: 60+ GB

## Instrucciones

1. **Instalar dependencias**:
   ```bash
   python instalar_metgo_60gb.py
   ```

2. **Iniciar el sistema**:
   ```bash
   python -m streamlit run sistema_unificado_con_conectores.py
   ```

3. **O usar el script de inicio**:
   ```bash
   iniciar_metgo_60gb.bat
   ```

4. **Acceder al dashboard**:
   - URL: http://localhost:8501
   - Usuario: admin
   - Contrasena: admin123

## Contenido Migrado
- Todos los archivos Python
- Todos los notebooks Jupyter
- Todos los datos y respaldos
- Todas las configuraciones
- Toda la documentacion
- Todos los modelos ML
- Todos los logs y reportes

## Caracteristicas
- Sistema meteorologico agricola completo
- Dashboard interactivo
- Machine Learning
- APIs integradas
- Sistema de alertas
- Datos historicos completos

---
Generado automaticamente
"""
    
    with open(reporte_path, 'w', encoding='utf-8') as f:
        f.write(reporte_content)
    
    print(f"OK: Reporte creado: {reporte_path}")

def main():
    """Función principal"""
    print("MIGRADOR 60GB AL DISCO D: - METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Version Completa")
    print("="*70)
    
    # 1. Verificar espacio
    print("\n1. Verificando espacio en disco D:...")
    espacio_ok, espacio_libre = verificar_espacio()
    
    if not espacio_ok:
        print("ERROR: No se puede continuar")
        return False
    
    # 2. Migrar todo
    print("\n2. Migrando carpeta completa (60+ GB)...")
    ruta_destino, archivos_copiados = migrar_todo()
    
    if not ruta_destino or archivos_copiados == 0:
        print("ERROR: Migración falló")
        return False
    
    # 3. Crear scripts
    print("\n3. Creando scripts de instalación...")
    crear_script_instalacion(ruta_destino)
    crear_script_inicio(ruta_destino)
    crear_reporte(ruta_destino, archivos_copiados)
    
    # 4. Resumen final
    print("\n" + "="*70)
    print("OK: MIGRACION 60GB COMPLETADA EXITOSAMENTE")
    print("="*70)
    print(f"Proyecto migrado a: {ruta_destino}")
    print(f"Archivos migrados: {archivos_copiados}")
    print(f"Tamaño: 60+ GB")
    
    print(f"\nPROXIMOS PASOS:")
    print(f"1. cd {ruta_destino}")
    print(f"2. python instalar_metgo_60gb.py")
    print(f"3. python -m streamlit run sistema_unificado_con_conectores.py")
    print(f"4. O ejecutar: iniciar_metgo_60gb.bat")
    print(f"5. Acceder a: http://localhost:8501")
    
    return True

if __name__ == "__main__":
    main()
