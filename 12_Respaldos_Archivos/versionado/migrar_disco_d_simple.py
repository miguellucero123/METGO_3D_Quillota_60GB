#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRADOR AL DISCO D: - METGO 3D (Versión Simplificada)
Sistema para migrar el proyecto METGO 3D al disco D:
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import platform

def verificar_disco_d():
    """Verificar disponibilidad del disco D:"""
    print("🔍 VERIFICANDO DISCO D:")
    print("="*50)
    
    disco_d = Path("D:")
    if not disco_d.exists():
        print("❌ El disco D: no está disponible")
        return False
    
    # Verificar espacio disponible
    total, usado, libre = shutil.disk_usage(disco_d)
    libre_gb = libre // (1024**3)
    
    print(f"✅ Disco D: disponible")
    print(f"📊 Espacio libre: {libre_gb} GB")
    
    if libre_gb < 2:
        print("⚠️ Advertencia: Menos de 2GB libres")
        respuesta = input("¿Continuar? (s/n): ").strip().lower()
        if respuesta != 's':
            return False
    
    return True

def migrar_proyecto():
    """Migrar proyecto al disco D:"""
    print("\n📦 MIGRANDO PROYECTO AL DISCO D:")
    print("="*50)
    
    # Configurar rutas
    proyecto_actual = Path.cwd()
    disco_destino = Path("D:")
    ruta_destino = disco_destino / "Proyectos" / "METGO_3D_Quillota"
    
    print(f"Origen: {proyecto_actual}")
    print(f"Destino: {ruta_destino}")
    
    try:
        # Crear directorio destino
        ruta_destino.mkdir(parents=True, exist_ok=True)
        print(f"✅ Directorio creado: {ruta_destino}")
        
        # Archivos a migrar
        archivos_migrar = [
            '*.py',
            '*.ipynb',
            '*.md',
            '*.txt',
            '*.yaml',
            '*.yml',
            '*.json',
            '*.html',
            '*.css',
            '*.js',
            'requirements.txt',
            'README.md',
            'LICENSE'
        ]
        
        # Directorios a migrar
        directorios_migrar = [
            'config',
            'docs',
            'modelos_ml_quillota',
            'src',
            'tests'
        ]
        
        archivos_copiados = 0
        
        # Copiar archivos
        for patron in archivos_migrar:
            for archivo in proyecto_actual.glob(patron):
                if archivo.is_file():
                    try:
                        destino = ruta_destino / archivo.name
                        shutil.copy2(archivo, destino)
                        archivos_copiados += 1
                        print(f"   ✅ {archivo.name}")
                    except Exception as e:
                        print(f"   ❌ Error copiando {archivo.name}: {e}")
        
        # Copiar directorios
        for directorio in directorios_migrar:
            dir_origen = proyecto_actual / directorio
            if dir_origen.exists():
                try:
                    dir_destino = ruta_destino / directorio
                    shutil.copytree(dir_origen, dir_destino, dirs_exist_ok=True)
                    archivos_copiados += 1
                    print(f"   ✅ {directorio}/")
                except Exception as e:
                    print(f"   ❌ Error copiando {directorio}: {e}")
        
        print(f"\n📊 Archivos migrados: {archivos_copiados}")
        return ruta_destino, archivos_copiados
        
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        return None, 0

def crear_script_instalacion(ruta_destino):
    """Crear script de instalación"""
    print(f"\n🔧 CREANDO SCRIPT DE INSTALACIÓN")
    print("-"*40)
    
    script_path = ruta_destino / 'instalar_metgo.py'
    
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INSTALADOR METGO 3D
Script para instalar el proyecto
"""

import subprocess
import sys
import os
from pathlib import Path

def instalar_dependencias():
    """Instalar dependencias"""
    try:
        print("Instalando dependencias...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencias instaladas")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def configurar_entorno():
    """Configurar entorno"""
    try:
        # Crear .env
        env_file = Path('.env')
        if not env_file.exists():
            with open(env_file, 'w') as f:
                f.write('''# Configuración METGO 3D
OPENWEATHER_API_KEY=tu_clave_aqui
NASA_API_KEY=tu_clave_aqui
GOOGLE_MAPS_API_KEY=tu_clave_aqui
DEBUG=False
LOG_LEVEL=INFO
''')
            print("✅ Archivo .env creado")
        
        # Crear directorios
        directorios = ['data', 'logs', 'config', 'modelos_ml_quillota']
        for directorio in directorios:
            Path(directorio).mkdir(exist_ok=True)
        
        print("✅ Entorno configurado")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 INSTALADOR METGO 3D")
    print("="*30)
    
    if instalar_dependencias() and configurar_entorno():
        print("\\n✅ INSTALACIÓN COMPLETADA")
        print("\\nPara iniciar el sistema:")
        print("python -m streamlit run sistema_unificado_con_conectores.py")
        print("\\nAcceder a: http://localhost:8501")
        print("Usuario: admin")
        print("Contraseña: admin123")
    else:
        print("\\n❌ Error en la instalación")

if __name__ == "__main__":
    main()
'''
    
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print(f"✅ Script creado: {script_path}")
        return True
    except Exception as e:
        print(f"❌ Error creando script: {e}")
        return False

def crear_script_inicio_windows(ruta_destino):
    """Crear script de inicio para Windows"""
    print(f"\n🚀 CREANDO SCRIPT DE INICIO WINDOWS")
    print("-"*40)
    
    script_path = ruta_destino / 'iniciar_metgo.bat'
    
    script_content = '''@echo off
echo Iniciando METGO 3D - Sistema Meteorologico Agricola
echo ==================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no encontrado
    pause
    exit /b 1
)

REM Verificar archivo principal
if not exist "sistema_unificado_con_conectores.py" (
    echo Error: Archivo principal no encontrado
    pause
    exit /b 1
)

REM Iniciar dashboard
echo Iniciando dashboard...
echo URL: http://localhost:8501
echo Usuario: admin
echo Contraseña: admin123
echo.
python -m streamlit run sistema_unificado_con_conectores.py --server.port 8501 --server.headless true

pause
'''
    
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print(f"✅ Script Windows creado: {script_path}")
        return True
    except Exception as e:
        print(f"❌ Error creando script Windows: {e}")
        return False

def crear_reporte(ruta_destino, archivos_copiados):
    """Crear reporte de migración"""
    print(f"\n📄 CREANDO REPORTE")
    print("-"*30)
    
    reporte_path = ruta_destino / 'REPORTE_MIGRACION.md'
    
    reporte_content = f"""# REPORTE DE MIGRACIÓN - METGO 3D

## Información General
- **Proyecto**: METGO 3D Quillota
- **Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Sistema**: {platform.system()}

## Rutas
- **Destino**: {ruta_destino}

## Estadísticas
- **Archivos migrados**: {archivos_copiados}
- **Estado**: COMPLETADO

## Instrucciones de Uso

### 1. Instalar dependencias
```bash
python instalar_metgo.py
```

### 2. Iniciar el sistema
```bash
python -m streamlit run sistema_unificado_con_conectores.py
```

### 3. Acceder al dashboard
- URL: http://localhost:8501
- Usuario: admin
- Contraseña: admin123

## Características
- Sistema meteorológico agrícola completo
- Dashboard interactivo
- Machine Learning
- APIs integradas
- Sistema de alertas

---
Generado automáticamente
"""
    
    try:
        with open(reporte_path, 'w', encoding='utf-8') as f:
            f.write(reporte_content)
        print(f"✅ Reporte creado: {reporte_path}")
        return True
    except Exception as e:
        print(f"❌ Error creando reporte: {e}")
        return False

def main():
    """Función principal"""
    print("💾 MIGRADOR AL DISCO D: - METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota")
    print("="*60)
    
    # 1. Verificar disco D:
    if not verificar_disco_d():
        print("❌ No se puede continuar")
        return False
    
    # 2. Migrar proyecto
    ruta_destino, archivos_copiados = migrar_proyecto()
    
    if not ruta_destino or archivos_copiados == 0:
        print("❌ Migración falló")
        return False
    
    # 3. Crear scripts
    crear_script_instalacion(ruta_destino)
    crear_script_inicio_windows(ruta_destino)
    crear_reporte(ruta_destino, archivos_copiados)
    
    # 4. Resumen final
    print("\n" + "="*60)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("="*60)
    print(f"📁 Proyecto migrado a: {ruta_destino}")
    print(f"📦 Archivos migrados: {archivos_copiados}")
    
    print(f"\n📋 PRÓXIMOS PASOS:")
    print(f"1. Navegar: cd {ruta_destino}")
    print(f"2. Instalar: python instalar_metgo.py")
    print(f"3. Iniciar: python -m streamlit run sistema_unificado_con_conectores.py")
    print(f"4. O ejecutar: iniciar_metgo.bat")
    print(f"5. Acceder a: http://localhost:8501")
    
    return True

if __name__ == "__main__":
    main()
