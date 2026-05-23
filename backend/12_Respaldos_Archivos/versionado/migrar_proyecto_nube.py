#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRADOR A LA NUBE - METGO 3D
Migracion del proyecto a servicios en la nube
"""

import os
import zipfile
from pathlib import Path
from datetime import datetime
import logging

class MigradorNube:
    """Migrador del proyecto METGO 3D a la nube"""
    
    def __init__(self):
        self.logger = logging.getLogger('MIGRADOR_NUBE')
        self.proyecto_actual = Path.cwd()
        self.nombre_proyecto = "METGO_3D_Quillota"
        
    def crear_paquete_nube(self):
        """Crear paquete optimizado para la nube"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_paquete = f"{self.nombre_proyecto}_nube_{timestamp}.zip"
            ruta_paquete = self.proyecto_actual.parent / nombre_paquete
            
            self.logger.info(f"Creando paquete para nube: {ruta_paquete}")
            
            # Archivos esenciales para la nube
            archivos_esenciales = [
                'sistema_unificado_con_conectores.py',
                'auth_module.py',
                'integrador_modulos.py',
                'conector_iot_satelital.py',
                'conector_monitoreo_respaldos.py',
                'conector_apis_avanzadas.py',
                'optimizar_sistema_completo.py',
                'fix_ml_models.py',
                '*.ipynb',  # Notebooks principales
                'config/',
                'modelos_ml_quillota/',
                'requirements.txt',
                'README.md',
                'LICENSE'
            ]
            
            # Excluir archivos pesados y temporales
            excluir = [
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
                'data/respaldos/',  # Excluir respaldos pesados
                '*.csv',  # Excluir archivos de datos grandes
                '*.xlsx',
                '*.png',  # Excluir imagenes generadas
                '*.jpg',
                '*.jpeg'
            ]
            
            with zipfile.ZipFile(ruta_paquete, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                archivos_incluidos = 0
                tamaño_total = 0
                
                for patron in archivos_esenciales:
                    for archivo in self.proyecto_actual.glob(patron):
                        if archivo.is_file():
                            # Verificar exclusiones
                            excluir_archivo = False
                            for excluir_patron in excluir:
                                if excluir_patron.replace('*', '') in str(archivo):
                                    excluir_archivo = True
                                    break
                            
                            if not excluir_archivo:
                                try:
                                    arcname = archivo.relative_to(self.proyecto_actual)
                                    zipf.write(archivo, arcname)
                                    archivos_incluidos += 1
                                    tamaño_total += archivo.stat().st_size
                                    self.logger.info(f"Incluido: {arcname}")
                                except Exception as e:
                                    self.logger.warning(f"Error incluyendo {archivo}: {e}")
                        
                        elif archivo.is_dir():
                            # Procesar directorio
                            for subarchivo in archivo.rglob('*'):
                                if subarchivo.is_file():
                                    excluir_archivo = False
                                    for excluir_patron in excluir:
                                        if excluir_patron.replace('*', '') in str(subarchivo):
                                            excluir_archivo = True
                                            break
                                    
                                    if not excluir_archivo:
                                        try:
                                            arcname = subarchivo.relative_to(self.proyecto_actual)
                                            zipf.write(subarchivo, arcname)
                                            archivos_incluidos += 1
                                            tamaño_total += subarchivo.stat().st_size
                                        except Exception as e:
                                            self.logger.warning(f"Error incluyendo {subarchivo}: {e}")
            
            # Crear guia de migracion a la nube
            guia_migracion = f"""# GUIA DE MIGRACION A LA NUBE - METGO 3D

## INFORMACION DEL PAQUETE
- Fecha de creacion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Archivos incluidos: {archivos_incluidos}
- Tamaño original: {tamaño_total / (1024**2):.2f} MB
- Tamaño comprimido: {ruta_paquete.stat().st_size / (1024**2):.2f} MB

## OPCIONES DE MIGRACION A LA NUBE

### 1. GOOGLE DRIVE
1. Subir el archivo ZIP a Google Drive
2. Crear una carpeta compartida para el proyecto
3. Descargar en el nuevo servidor
4. Extraer y seguir las instrucciones de instalacion

### 2. MICROSOFT ONEDRIVE
1. Subir el archivo ZIP a OneDrive
2. Compartir con los usuarios necesarios
3. Sincronizar en el nuevo servidor
4. Extraer y configurar

### 3. DROPBOX
1. Subir el archivo ZIP a Dropbox
2. Crear enlace compartido
3. Descargar en el nuevo servidor
4. Instalar y configurar

### 4. AMAZON S3 / AZURE BLOB
1. Subir el archivo ZIP al servicio de almacenamiento
2. Generar URL de descarga
3. Descargar en el nuevo servidor
4. Extraer y configurar

### 5. GITHUB (Recomendado para desarrollo)
1. Crear repositorio privado en GitHub
2. Subir archivos (excluyendo datos sensibles)
3. Clonar en el nuevo servidor
4. Configurar variables de entorno

## INSTRUCCIONES DE INSTALACION

### Requisitos del servidor:
- Python 3.8 o superior
- 4GB RAM minimo
- 10GB espacio en disco
- Conexion a internet

### Pasos de instalacion:
1. Extraer el archivo ZIP
2. Instalar dependencias: pip install -r requirements.txt
3. Configurar variables de entorno
4. Ejecutar optimizacion: python optimizar_sistema_completo.py
5. Iniciar dashboard: python -m streamlit run sistema_unificado_con_conectores.py

### Variables de entorno necesarias:
```
OPENWEATHER_API_KEY=tu_clave_openweather
NASA_API_KEY=tu_clave_nasa
GOOGLE_MAPS_API_KEY=tu_clave_google_maps
```

### Configuracion de base de datos:
- SQLite (por defecto) - No requiere configuracion adicional
- PostgreSQL (opcional) - Requiere instalacion y configuracion

## NOTAS IMPORTANTES
- Los datos sensibles no estan incluidos en este paquete
- Configurar las claves de API antes de usar
- Verificar que todos los puertos esten disponibles
- Configurar firewall si es necesario

## SOPORTE
Para soporte tecnico, contactar al equipo de desarrollo METGO 3D
"""
            
            # Guardar guia
            guia_path = ruta_paquete.with_suffix('.md')
            with open(guia_path, 'w', encoding='utf-8') as f:
                f.write(guia_migracion)
            
            return {
                'ruta_paquete': str(ruta_paquete),
                'ruta_guia': str(guia_path),
                'archivos_incluidos': archivos_incluidos,
                'tamaño_original_mb': tamaño_total / (1024**2),
                'tamaño_comprimido_mb': ruta_paquete.stat().st_size / (1024**2),
                'compresion_porcentaje': (1 - ruta_paquete.stat().st_size / tamaño_total) * 100 if tamaño_total > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error creando paquete para nube: {e}")
            return {'error': str(e)}
    
    def crear_script_instalacion_nube(self):
        """Crear script de instalacion para la nube"""
        script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INSTALADOR EN LA NUBE - METGO 3D
Script para instalar el proyecto en servidor en la nube
"""

import subprocess
import sys
import os
from pathlib import Path
import platform

def verificar_sistema():
    """Verificar sistema operativo y requisitos"""
    print("Verificando sistema...")
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("Error: Se requiere Python 3.8 o superior")
        return False
    
    print(f"Python version: {sys.version}")
    print(f"Sistema operativo: {platform.system()} {platform.release()}")
    
    # Verificar espacio en disco
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_gb = free // (1024**3)
        print(f"Espacio libre: {free_gb} GB")
        
        if free_gb < 5:
            print("Advertencia: Menos de 5GB de espacio libre")
    except:
        print("No se pudo verificar espacio en disco")
    
    return True

def instalar_dependencias():
    """Instalar dependencias del proyecto"""
    try:
        print("\\nInstalando dependencias...")
        
        # Actualizar pip
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
        
        # Instalar dependencias
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        
        print("Dependencias instaladas exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error instalando dependencias: {e}")
        return False

def configurar_entorno():
    """Configurar variables de entorno"""
    print("\\nConfigurando entorno...")
    
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
        print("Archivo .env creado - Configure las claves de API")
    
    # Crear directorios necesarios
    directorios = ['data', 'logs', 'config', 'modelos_ml_quillota']
    for directorio in directorios:
        Path(directorio).mkdir(exist_ok=True)
        print(f"Directorio creado: {directorio}")
    
    return True

def verificar_instalacion():
    """Verificar que la instalacion sea correcta"""
    try:
        print("\\nVerificando instalacion...")
        
        # Ejecutar optimizacion
        subprocess.run([sys.executable, 'optimizar_sistema_completo.py'], check=True)
        
        print("Instalacion verificada exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error verificando instalacion: {e}")
        return False

def crear_script_inicio():
    """Crear script de inicio del sistema"""
    script_inicio = '''#!/bin/bash
# Script de inicio para METGO 3D

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
    
    # Hacer ejecutable en sistemas Unix
    if platform.system() != 'Windows':
        os.chmod('iniciar_metgo.sh', 0o755)
    
    print("Script de inicio creado: iniciar_metgo.sh")

def main():
    print("INSTALADOR EN LA NUBE - METGO 3D")
    print("Sistema Meteorologico Agricola Quillota")
    print("=" * 50)
    
    if not verificar_sistema():
        print("\\nError: Sistema no compatible")
        return False
    
    if not instalar_dependencias():
        print("\\nError: No se pudieron instalar las dependencias")
        return False
    
    if not configurar_entorno():
        print("\\nError: No se pudo configurar el entorno")
        return False
    
    if not verificar_instalacion():
        print("\\nError: La instalacion no es correcta")
        return False
    
    crear_script_inicio()
    
    print("\\n" + "=" * 50)
    print("INSTALACION COMPLETADA EXITOSAMENTE")
    print("=" * 50)
    print("\\nPara iniciar el sistema:")
    print("1. Configure las claves de API en el archivo .env")
    print("2. Ejecute: python -m streamlit run sistema_unificado_con_conectores.py")
    print("3. O ejecute: ./iniciar_metgo.sh (en sistemas Unix)")
    print("\\nEl dashboard estara disponible en: http://localhost:8501")
    print("Usuario: admin")
    print("Contraseña: admin123")
    
    return True

if __name__ == "__main__":
    main()
'''
        
        with open('instalar_en_nube.py', 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return 'instalar_en_nube.py'

def main():
    """Funcion principal para migracion a la nube"""
    print("MIGRADOR A LA NUBE - METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Version 2.0")
    print("=" * 70)
    
    try:
        migrador = MigradorNube()
        
        print("\\nCreando paquete optimizado para la nube...")
        resultado = migrador.crear_paquete_nube()
        
        if 'error' in resultado:
            print(f"Error: {resultado['error']}")
            return False
        
        print(f"\\nPaquete creado exitosamente:")
        print(f"  Archivo: {resultado['ruta_paquete']}")
        print(f"  Guia: {resultado['ruta_guia']}")
        print(f"  Archivos incluidos: {resultado['archivos_incluidos']}")
        print(f"  Tamaño original: {resultado['tamaño_original_mb']:.2f} MB")
        print(f"  Tamaño comprimido: {resultado['tamaño_comprimido_mb']:.2f} MB")
        print(f"  Compresion: {resultado['compresion_porcentaje']:.1f}%")
        
        # Crear script de instalacion
        script_path = migrador.crear_script_instalacion_nube()
        print(f"\\nScript de instalacion creado: {script_path}")
        
        print("\\nOPCIONES DE MIGRACION A LA NUBE:")
        print("1. Google Drive - Subir el archivo ZIP")
        print("2. Microsoft OneDrive - Subir el archivo ZIP")
        print("3. Dropbox - Subir el archivo ZIP")
        print("4. GitHub - Crear repositorio privado")
        print("5. Amazon S3 / Azure Blob - Subir via CLI")
        
        print("\\nMigracion a la nube preparada exitosamente")
        return True
        
    except Exception as e:
        print(f"\\nError en migracion a la nube: {e}")
        return False

if __name__ == "__main__":
    main()
