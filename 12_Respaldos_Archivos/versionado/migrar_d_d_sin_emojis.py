#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRADOR AL DISCO D: - METGO 3D
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import platform

def main():
    print("MIGRADOR AL DISCO D: - METGO 3D")
    print("="*50)
    
    # Verificar disco D:
    disco_d = Path("D:")
    if not disco_d.exists():
        print("ERROR: El disco D: no está disponible")
        return
    
    # Verificar espacio
    total, usado, libre = shutil.disk_usage(disco_d)
    libre_gb = libre // (1024**3)
    print(f"OK: Disco D: disponible ({libre_gb} GB libres)")
    
    # Configurar rutas
    proyecto_actual = Path.cwd()
    ruta_destino = disco_d / "Proyectos" / "METGO_3D_Quillota"
    
    print(f"Origen: {proyecto_actual}")
    print(f"Destino: {ruta_destino}")
    
    # Crear directorio destino
    ruta_destino.mkdir(parents=True, exist_ok=True)
    print("OK: Directorio creado")
    
    # Archivos a migrar
    archivos_copiados = 0
    
    # Copiar archivos Python
    for archivo in proyecto_actual.glob("*.py"):
        try:
            shutil.copy2(archivo, ruta_destino / archivo.name)
            archivos_copiados += 1
            print(f"   OK: {archivo.name}")
        except Exception as e:
            print(f"   ERROR: {archivo.name}: {e}")
    
    # Copiar notebooks
    for archivo in proyecto_actual.glob("*.ipynb"):
        try:
            shutil.copy2(archivo, ruta_destino / archivo.name)
            archivos_copiados += 1
            print(f"   OK: {archivo.name}")
        except Exception as e:
            print(f"   ERROR: {archivo.name}: {e}")
    
    # Copiar archivos de configuración
    archivos_config = ['requirements.txt', 'README.md', 'LICENSE']
    for archivo in archivos_config:
        if (proyecto_actual / archivo).exists():
            try:
                shutil.copy2(proyecto_actual / archivo, ruta_destino / archivo)
                archivos_copiados += 1
                print(f"   OK: {archivo}")
            except Exception as e:
                print(f"   ERROR: {archivo}: {e}")
    
    # Copiar otros archivos
    for patron in ['*.md', '*.txt', '*.yaml', '*.yml', '*.json']:
        for archivo in proyecto_actual.glob(patron):
            try:
                shutil.copy2(archivo, ruta_destino / archivo.name)
                archivos_copiados += 1
                print(f"   OK: {archivo.name}")
            except Exception as e:
                print(f"   ERROR: {archivo.name}: {e}")
    
    # Copiar directorios importantes
    directorios = ['config', 'docs', 'modelos_ml_quillota', 'src', 'tests']
    for directorio in directorios:
        dir_origen = proyecto_actual / directorio
        if dir_origen.exists():
            try:
                dir_destino = ruta_destino / directorio
                shutil.copytree(dir_origen, dir_destino, dirs_exist_ok=True)
                archivos_copiados += 1
                print(f"   OK: {directorio}/")
            except Exception as e:
                print(f"   ERROR: {directorio}: {e}")
    
    # Crear script de instalación
    script_instalar = ruta_destino / 'instalar_metgo.py'
    script_content = '''#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

print("INSTALADOR METGO 3D")
print("="*30)

# Instalar dependencias
try:
    print("Instalando dependencias...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
    print("OK: Dependencias instaladas")
except Exception as e:
    print(f"ERROR: {e}")

# Crear directorios
directorios = ['data', 'logs', 'config', 'modelos_ml_quillota']
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
    
    with open(script_instalar, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Crear script de inicio Windows
    script_inicio = ruta_destino / 'iniciar_metgo.bat'
    script_bat = '''@echo off
echo Iniciando METGO 3D
echo ==================
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
    
    with open(script_inicio, 'w', encoding='utf-8') as f:
        f.write(script_bat)
    
    # Crear reporte
    reporte = ruta_destino / 'REPORTE_MIGRACION.md'
    with open(reporte, 'w', encoding='utf-8') as f:
        f.write(f"""# REPORTE DE MIGRACION - METGO 3D

**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Sistema**: {platform.system()}
**Destino**: {ruta_destino}
**Archivos migrados**: {archivos_copiados}

## Instrucciones

1. **Instalar dependencias**:
   ```bash
   python instalar_metgo.py
   ```

2. **Iniciar el sistema**:
   ```bash
   python -m streamlit run sistema_unificado_con_conectores.py
   ```

3. **O usar el script de inicio**:
   ```bash
   iniciar_metgo.bat
   ```

4. **Acceder al dashboard**:
   - URL: http://localhost:8501
   - Usuario: admin
   - Contrasena: admin123

## Caracteristicas
- Sistema meteorologico agricola completo
- Dashboard interactivo
- Machine Learning
- APIs integradas
- Sistema de alertas

---
Generado automaticamente
""")
    
    # Resumen final
    print(f"\nOK: MIGRACION COMPLETADA")
    print(f"Destino: {ruta_destino}")
    print(f"Archivos: {archivos_copiados}")
    print(f"\nPROXIMOS PASOS:")
    print(f"1. cd {ruta_destino}")
    print(f"2. python instalar_metgo.py")
    print(f"3. python -m streamlit run sistema_unificado_con_conectores.py")
    print(f"4. O ejecutar: iniciar_metgo.bat")

if __name__ == "__main__":
    main()
