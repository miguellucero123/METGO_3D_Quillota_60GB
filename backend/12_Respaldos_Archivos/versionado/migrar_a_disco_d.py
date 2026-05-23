#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRADOR AL DISCO D: - METGO 3D
Sistema para migrar el proyecto METGO 3D al disco D:
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
import logging
import json
import subprocess
import platform

class MigradorDiscoD:
    """Migrador del proyecto METGO 3D al disco D:"""
    
    def __init__(self):
        self.logger = logging.getLogger('MIGRADOR_DISCO_D')
        self.proyecto_actual = Path.cwd()
        self.nombre_proyecto = "METGO_3D_Quillota"
        self.disco_destino = Path("D:")
        self.ruta_destino = self.disco_destino / "Proyectos" / self.nombre_proyecto
        
    def verificar_disco_d(self):
        """Verificar disponibilidad y espacio del disco D:"""
        print("🔍 VERIFICANDO DISCO D:")
        print("="*50)
        
        try:
            # Verificar si el disco D: existe
            if not self.disco_destino.exists():
                print("❌ El disco D: no está disponible")
                return False
            
            # Verificar espacio disponible
            total, usado, libre = shutil.disk_usage(self.disco_destino)
            libre_gb = libre // (1024**3)
            total_gb = total // (1024**3)
            
            print(f"✅ Disco D: disponible")
            print(f"📊 Espacio total: {total_gb} GB")
            print(f"📊 Espacio libre: {libre_gb} GB")
            print(f"📊 Espacio usado: {(usado // (1024**3))} GB")
            
            # Verificar espacio necesario (estimado 2GB)
            espacio_necesario_gb = 2
            if libre_gb < espacio_necesario_gb:
                print(f"⚠️ Advertencia: Solo {libre_gb} GB libres, se recomiendan {espacio_necesario_gb} GB")
                respuesta = input("¿Continuar de todas formas? (s/n): ").strip().lower()
                if respuesta != 's':
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error verificando disco D:: {e}")
            return False
    
    def calcular_tamaño_proyecto(self):
        """Calcular el tamaño del proyecto actual"""
        print("\n📏 CALCULANDO TAMAÑO DEL PROYECTO")
        print("-"*40)
        
        tamaño_total = 0
        archivos_contados = 0
        
        # Archivos a incluir en la migración
        patrones_incluir = [
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
            'config/',
            'docs/',
            'modelos_ml_quillota/',
            'src/',
            'tests/',
            'requirements.txt',
            'README.md',
            'LICENSE'
        ]
        
        # Archivos a excluir
        patrones_excluir = [
            '__pycache__/',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.pytest_cache/',
            '.coverage',
            'htmlcov/',
            '.mypy_cache/',
            '.tox/',
            'dist/',
            'build/',
            '*.egg-info/',
            '*.log',
            '*.tmp',
            '*.temp',
            '*.bak',
            '*.swp',
            '*.swo',
            '*~',
            '.git/',
            '.vscode/',
            '.idea/',
            'node_modules/',
            'venv/',
            'env/',
            '.env',
            'data/respaldos/',
            'backups/',
            'artefactos/',
            'notebooks_corregidos/',
            'reportes_revision/',
            'resultados/',
            'graficos/',
            'static/',
            'templates/',
            'METGO_3D_OPERATIVO/'
        ]
        
        for patron in patrones_incluir:
            for archivo in self.proyecto_actual.glob(patron):
                if archivo.is_file():
                    # Verificar si debe ser excluido
                    excluir_archivo = False
                    for excluir_patron in patrones_excluir:
                        if excluir_patron.replace('*', '') in str(archivo):
                            excluir_archivo = True
                            break
                    
                    if not excluir_archivo:
                        tamaño_total += archivo.stat().st_size
                        archivos_contados += 1
                
                elif archivo.is_dir():
                    # Procesar directorio recursivamente
                    for subarchivo in archivo.rglob('*'):
                        if subarchivo.is_file():
                            excluir_archivo = False
                            for excluir_patron in patrones_excluir:
                                if excluir_patron.replace('*', '') in str(subarchivo):
                                    excluir_archivo = True
                                    break
                            
                            if not excluir_archivo:
                                tamaño_total += subarchivo.stat().st_size
                                archivos_contados += 1
        
        tamaño_mb = tamaño_total / (1024**2)
        print(f"📁 Archivos a migrar: {archivos_contados}")
        print(f"📦 Tamaño estimado: {tamaño_mb:.2f} MB")
        
        return tamaño_total, archivos_contados
    
    def crear_directorio_destino(self):
        """Crear directorio de destino en disco D:"""
        print(f"\n📁 CREANDO DIRECTORIO DESTINO")
        print(f"Ruta: {self.ruta_destino}")
        print("-"*40)
        
        try:
            # Crear directorio padre si no existe
            self.ruta_destino.parent.mkdir(parents=True, exist_ok=True)
            
            # Verificar si el directorio ya existe
            if self.ruta_destino.exists():
                print(f"⚠️ El directorio {self.ruta_destino} ya existe")
                respuesta = input("¿Sobrescribir? (s/n): ").strip().lower()
                if respuesta == 's':
                    shutil.rmtree(self.ruta_destino)
                    print("🗑️ Directorio anterior eliminado")
                else:
                    # Crear con timestamp
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    self.ruta_destino = self.disco_destino / "Proyectos" / f"{self.nombre_proyecto}_{timestamp}"
                    print(f"📁 Nuevo directorio: {self.ruta_destino}")
            
            # Crear directorio destino
            self.ruta_destino.mkdir(parents=True, exist_ok=True)
            print(f"✅ Directorio creado: {self.ruta_destino}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creando directorio: {e}")
            return False
    
    def migrar_archivos(self):
        """Migrar archivos al disco D:"""
        print(f"\n📦 MIGRANDO ARCHIVOS AL DISCO D:")
        print(f"Origen: {self.proyecto_actual}")
        print(f"Destino: {self.ruta_destino}")
        print("-"*50)
        
        try:
            archivos_migrados = 0
            errores = []
            
            # Archivos a migrar
            patrones_incluir = [
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
                'config/',
                'docs/',
                'modelos_ml_quillota/',
                'src/',
                'tests/',
                'requirements.txt',
                'README.md',
                'LICENSE'
            ]
            
            # Archivos a excluir
            patrones_excluir = [
                '__pycache__/',
                '*.pyc',
                '*.pyo',
                '*.pyd',
                '.pytest_cache/',
                '.coverage',
                'htmlcov/',
                '.mypy_cache/',
                '.tox/',
                'dist/',
                'build/',
                '*.egg-info/',
                '*.log',
                '*.tmp',
                '*.temp',
                '*.bak',
                '*.swp',
                '*.swo',
                '*~',
                '.git/',
                '.vscode/',
                '.idea/',
                'node_modules/',
                'venv/',
                'env/',
                '.env',
                'data/respaldos/',
                'backups/',
                'artefactos/',
                'notebooks_corregidos/',
                'reportes_revision/',
                'resultados/',
                'graficos/',
                'static/',
                'templates/',
                'METGO_3D_OPERATIVO/'
            ]
            
            for patron in patrones_incluir:
                for archivo in self.proyecto_actual.glob(patron):
                    if archivo.is_file():
                        # Verificar si debe ser excluido
                        excluir_archivo = False
                        for excluir_patron in patrones_excluir:
                            if excluir_patron.replace('*', '') in str(archivo):
                                excluir_archivo = True
                                break
                        
                        if not excluir_archivo:
                            try:
                                destino_archivo = self.ruta_destino / archivo.name
                                shutil.copy2(archivo, destino_archivo)
                                archivos_migrados += 1
                                print(f"   ✅ {archivo.name}")
                            except Exception as e:
                                error_msg = f"Error copiando {archivo.name}: {e}"
                                errores.append(error_msg)
                                print(f"   ❌ {error_msg}")
                    
                    elif archivo.is_dir():
                        # Procesar directorio
                        try:
                            destino_dir = self.ruta_destino / archivo.name
                            shutil.copytree(archivo, destino_dir, dirs_exist_ok=True)
                            archivos_migrados += 1
                            print(f"   ✅ {archivo.name}/")
                        except Exception as e:
                            error_msg = f"Error copiando directorio {archivo.name}: {e}"
                            errores.append(error_msg)
                            print(f"   ❌ {error_msg}")
            
            print(f"\n📊 RESUMEN DE MIGRACIÓN:")
            print(f"   ✅ Archivos migrados: {archivos_migrados}")
            print(f"   ❌ Errores: {len(errores)}")
            
            if errores:
                print(f"\n⚠️ ERRORES DETECTADOS:")
                for error in errores:
                    print(f"   • {error}")
            
            return archivos_migrados, errores
            
        except Exception as e:
            print(f"❌ Error en migración: {e}")
            return 0, [str(e)]
    
    def crear_script_instalacion(self):
        """Crear script de instalación en disco D:"""
        print(f"\n🔧 CREANDO SCRIPT DE INSTALACIÓN")
        print("-"*40)
        
        try:
            script_path = self.ruta_destino / 'instalar_en_disco_d.py'
            
            script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INSTALADOR EN DISCO D: - METGO 3D
Script para instalar el proyecto en el disco D:
"""

import subprocess
import sys
import os
from pathlib import Path
import platform

def verificar_sistema():
    """Verificar sistema operativo y requisitos"""
    print("🔍 VERIFICANDO SISTEMA")
    print("="*30)
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        return False
    
    print(f"✅ Python version: {{sys.version}}")
    print(f"✅ Sistema operativo: {{platform.system()}} {{platform.release()}}")
    
    # Verificar espacio en disco
    try:
        import shutil
        total, used, free = shutil.disk_usage("D:")
        free_gb = free // (1024**3)
        print(f"✅ Espacio libre en D:: {{free_gb}} GB")
        
        if free_gb < 1:
            print("⚠️ Advertencia: Menos de 1GB de espacio libre en D:")
    except:
        print("⚠️ No se pudo verificar espacio en disco D:")
    
    return True

def instalar_dependencias():
    """Instalar dependencias del proyecto"""
    try:
        print("\\n📦 INSTALANDO DEPENDENCIAS")
        print("-"*30)
        
        # Actualizar pip
        print("Actualizando pip...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
        
        # Instalar dependencias
        print("Instalando dependencias del proyecto...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        
        print("✅ Dependencias instaladas exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {{e}}")
        return False

def configurar_entorno():
    """Configurar variables de entorno"""
    try:
        print("\\n⚙️ CONFIGURANDO ENTORNO")
        print("-"*30)
        
        # Crear archivo .env si no existe
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
            print("✅ Archivo .env creado - Configure las claves de API")
        else:
            print("✅ Archivo .env ya existe")
        
        # Crear directorios necesarios
        directorios = ['data', 'logs', 'config', 'modelos_ml_quillota', 'src']
        for directorio in directorios:
            Path(directorio).mkdir(exist_ok=True)
            print(f"✅ Directorio creado: {{directorio}}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando entorno: {{e}}")
        return False

def verificar_instalacion():
    """Verificar que la instalación sea correcta"""
    try:
        print("\\n🔍 VERIFICANDO INSTALACIÓN")
        print("-"*30)
        
        # Verificar archivos principales
        archivos_principales = [
            'sistema_unificado_con_conectores.py',
            'requirements.txt',
            'README.md'
        ]
        
        for archivo in archivos_principales:
            if Path(archivo).exists():
                print(f"✅ {{archivo}}")
            else:
                print(f"❌ {{archivo}} - NO ENCONTRADO")
                return False
        
        # Ejecutar optimización si existe
        if Path('optimizar_sistema_completo.py').exists():
            print("Ejecutando optimización del sistema...")
            subprocess.run([sys.executable, 'optimizar_sistema_completo.py'], check=True)
            print("✅ Optimización completada")
        
        print("✅ Instalación verificada exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error verificando instalación: {{e}}")
        return False

def crear_script_inicio():
    """Crear script de inicio del sistema"""
    try:
        print("\\n🚀 CREANDO SCRIPT DE INICIO")
        print("-"*30)
        
        # Script para Windows
        if platform.system() == 'Windows':
            script_inicio = r'''@echo off
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
            print("✅ Script de inicio creado: iniciar_metgo.bat")
        
        # Script para Linux/Mac
        else:
            script_inicio = r'''#!/bin/bash
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
            print("✅ Script de inicio creado: iniciar_metgo.sh")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando script de inicio: {{e}}")
        return False

def main():
    print("🚀 INSTALADOR EN DISCO D: - METGO 3D")
    print("Sistema Meteorologico Agricola Quillota")
    print("=" * 50)
    
    if not verificar_sistema():
        print("\\n❌ Error: Sistema no compatible")
        return False
    
    if not instalar_dependencias():
        print("\\n❌ Error: No se pudieron instalar las dependencias")
        return False
    
    if not configurar_entorno():
        print("\\n❌ Error: No se pudo configurar el entorno")
        return False
    
    if not verificar_instalacion():
        print("\\n❌ Error: La instalacion no es correcta")
        return False
    
    crear_script_inicio()
    
    print("\\n" + "=" * 50)
    print("✅ INSTALACION COMPLETADA EXITOSAMENTE")
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
    print("Contraseña: admin123")
    
    return True

if __name__ == "__main__":
    main()
'''
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            print(f"✅ Script de instalación creado: {script_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creando script de instalación: {e}")
            return False
    
    def crear_reporte_migracion(self, archivos_migrados, errores):
        """Crear reporte de migración"""
        print(f"\n📄 CREANDO REPORTE DE MIGRACIÓN")
        print("-"*40)
        
        try:
            reporte = {
                'fecha_migracion': datetime.now().isoformat(),
                'proyecto': self.nombre_proyecto,
                'version': '2.0',
                'ruta_origen': str(self.proyecto_actual),
                'ruta_destino': str(self.ruta_destino),
                'archivos_migrados': archivos_migrados,
                'errores': errores,
                'sistema_operativo': platform.system(),
                'python_version': platform.python_version(),
                'estado': 'COMPLETADO' if archivos_migrados > 0 else 'FALLIDO'
            }
            
            # Guardar reporte JSON
            reporte_path = self.ruta_destino / 'reporte_migracion.json'
            with open(reporte_path, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            # Crear reporte legible
            reporte_txt = f"""# REPORTE DE MIGRACIÓN - METGO 3D

## Información General
- **Proyecto**: {self.nombre_proyecto}
- **Versión**: 2.0
- **Fecha de migración**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Sistema operativo**: {platform.system()}
- **Python version**: {platform.python_version()}

## Rutas
- **Origen**: {self.proyecto_actual}
- **Destino**: {self.ruta_destino}

## Estadísticas
- **Archivos migrados**: {archivos_migrados}
- **Errores**: {len(errores)}
- **Estado**: {'COMPLETADO' if archivos_migrados > 0 else 'FALLIDO'}

## Errores
"""
            
            if errores:
                for i, error in enumerate(errores, 1):
                    reporte_txt += f"{i}. {error}\n"
            else:
                reporte_txt += "Ningún error detectado.\n"
            
            reporte_txt += f"""
## Instrucciones Post-Migración

### 1. Navegar al directorio
```bash
cd {self.ruta_destino}
```

### 2. Ejecutar instalación
```bash
python instalar_en_disco_d.py
```

### 3. Iniciar el sistema
```bash
python -m streamlit run sistema_unificado_con_conectores.py
```

### 4. Acceder al dashboard
- URL: http://localhost:8501
- Usuario: admin
- Contraseña: admin123

## Características del Sistema
- Sistema meteorológico agrícola completo
- Dashboard interactivo con visualizaciones 3D
- Machine Learning para predicciones
- APIs integradas (OpenWeather, NASA, etc.)
- Sistema de alertas automáticas
- Reportes automáticos

---
Generado automáticamente por el sistema de migración METGO 3D
"""
            
            reporte_txt_path = self.ruta_destino / 'REPORTE_MIGRACION.md'
            with open(reporte_txt_path, 'w', encoding='utf-8') as f:
                f.write(reporte_txt)
            
            print(f"✅ Reporte JSON: {reporte_path}")
            print(f"✅ Reporte MD: {reporte_txt_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creando reporte: {e}")
            return False

def main():
    """Función principal para migración al disco D:"""
    print("💾 MIGRADOR AL DISCO D: - METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Versión 2.0")
    print("="*70)
    
    try:
        migrador = MigradorDiscoD()
        
        # 1. Verificar disco D:
        print("\n1️⃣ Verificando disco D:...")
        if not migrador.verificar_disco_d():
            print("❌ No se puede continuar sin acceso al disco D:")
            return False
        
        # 2. Calcular tamaño del proyecto
        print("\n2️⃣ Calculando tamaño del proyecto...")
        tamaño_total, archivos_contados = migrador.calcular_tamaño_proyecto()
        
        # 3. Crear directorio destino
        print("\n3️⃣ Creando directorio destino...")
        if not migrador.crear_directorio_destino():
            print("❌ No se pudo crear el directorio destino")
            return False
        
        # 4. Migrar archivos
        print("\n4️⃣ Migrando archivos...")
        archivos_migrados, errores = migrador.migrar_archivos()
        
        if archivos_migrados == 0:
            print("❌ No se migraron archivos")
            return False
        
        # 5. Crear script de instalación
        print("\n5️⃣ Creando script de instalación...")
        migrador.crear_script_instalacion()
        
        # 6. Crear reporte de migración
        print("\n6️⃣ Creando reporte de migración...")
        migrador.crear_reporte_migracion(archivos_migrados, errores)
        
        # 7. Resumen final
        print("\n" + "="*70)
        print("✅ MIGRACIÓN AL DISCO D: COMPLETADA EXITOSAMENTE")
        print("="*70)
        print(f"📁 Proyecto migrado a: {migrador.ruta_destino}")
        print(f"📦 Archivos migrados: {archivos_migrados}")
        print(f"❌ Errores: {len(errores)}")
        
        print(f"\n📋 PRÓXIMOS PASOS:")
        print(f"1. Navegar al directorio: cd {migrador.ruta_destino}")
        print(f"2. Ejecutar instalación: python instalar_en_disco_d.py")
        print(f"3. Iniciar sistema: python -m streamlit run sistema_unificado_con_conectores.py")
        print(f"4. Acceder a: http://localhost:8501")
        
        return True
        
    except Exception as e:
        print(f"\n💥 ERROR EN MIGRACIÓN AL DISCO D:: {e}")
        return False

if __name__ == "__main__":
    main()
