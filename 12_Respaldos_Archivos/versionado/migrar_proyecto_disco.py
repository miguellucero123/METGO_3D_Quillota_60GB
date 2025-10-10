#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRADOR DE PROYECTO - METGO 3D
Migracion del proyecto a otro disco o ubicacion
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
import logging

class MigradorProyecto:
    """Migrador del proyecto METGO 3D"""
    
    def __init__(self):
        self.logger = logging.getLogger('MIGRADOR')
        self.proyecto_actual = Path.cwd()
        self.nombre_proyecto = "METGO_3D_Quillota"
        
    def crear_paquete_migracion(self, destino=None):
        """Crear paquete completo para migracion"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_paquete = f"{self.nombre_proyecto}_migracion_{timestamp}.zip"
            
            if destino:
                ruta_paquete = Path(destino) / nombre_paquete
            else:
                ruta_paquete = self.proyecto_actual.parent / nombre_paquete
            
            self.logger.info(f"Creando paquete de migracion: {ruta_paquete}")
            
            # Archivos y directorios a incluir
            incluir = [
                '*.py',           # Archivos Python
                '*.ipynb',        # Notebooks
                '*.md',           # Documentacion
                '*.txt',          # Archivos de texto
                '*.yaml',         # Configuraciones
                '*.yml',          # Configuraciones
                '*.json',         # Archivos JSON
                '*.html',         # Dashboards HTML
                '*.css',          # Estilos
                '*.js',           # JavaScript
                'config/',        # Directorio de configuracion
                'docs/',          # Documentacion
                'modelos_ml_quillota/',  # Modelos ML
                'data/',          # Datos (si existe)
                'tests/',         # Tests
                'requirements.txt',
                'README.md',
                'LICENSE'
            ]
            
            # Excluir archivos temporales
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
                '.env'
            ]
            
            with zipfile.ZipFile(ruta_paquete, 'w', zipfile.ZIP_DEFLATED) as zipf:
                archivos_incluidos = 0
                
                for patron in incluir:
                    for archivo in self.proyecto_actual.glob(patron):
                        if archivo.is_file():
                            # Verificar si debe ser excluido
                            excluir_archivo = False
                            for excluir_patron in excluir:
                                if excluir_patron.replace('*', '') in str(archivo):
                                    excluir_archivo = True
                                    break
                            
                            if not excluir_archivo:
                                try:
                                    # Agregar archivo al ZIP
                                    arcname = archivo.relative_to(self.proyecto_actual)
                                    zipf.write(archivo, arcname)
                                    archivos_incluidos += 1
                                    self.logger.info(f"Incluido: {arcname}")
                                except Exception as e:
                                    self.logger.warning(f"Error incluyendo {archivo}: {e}")
                        
                        elif archivo.is_dir():
                            # Procesar directorio recursivamente
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
                                        except Exception as e:
                                            self.logger.warning(f"Error incluyendo {subarchivo}: {e}")
            
            # Crear archivo de informacion de migracion
            info_migracion = {
                'fecha_migracion': datetime.now().isoformat(),
                'proyecto': self.nombre_proyecto,
                'version': '2.0',
                'archivos_incluidos': archivos_incluidos,
                'tamaño_paquete': ruta_paquete.stat().st_size,
                'directorio_origen': str(self.proyecto_actual),
                'instrucciones': [
                    "1. Extraer el archivo ZIP en la nueva ubicacion",
                    "2. Instalar dependencias: pip install -r requirements.txt",
                    "3. Configurar variables de entorno si es necesario",
                    "4. Ejecutar: python optimizar_sistema_completo.py",
                    "5. Iniciar dashboard: python -m streamlit run sistema_unificado_con_conectores.py"
                ]
            }
            
            # Guardar informacion de migracion
            import json
            info_path = ruta_paquete.with_suffix('.json')
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(info_migracion, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Paquete creado exitosamente: {archivos_incluidos} archivos")
            return {
                'ruta_paquete': str(ruta_paquete),
                'ruta_info': str(info_path),
                'archivos_incluidos': archivos_incluidos,
                'tamaño_mb': ruta_paquete.stat().st_size / (1024**2)
            }
            
        except Exception as e:
            self.logger.error(f"Error creando paquete de migracion: {e}")
            return {'error': str(e)}
    
    def migrar_a_disco(self, ruta_destino):
        """Migrar proyecto a otro disco local"""
        try:
            destino = Path(ruta_destino) / self.nombre_proyecto
            
            if destino.exists():
                self.logger.warning(f"El directorio {destino} ya existe")
                return {'error': 'Directorio destino ya existe'}
            
            self.logger.info(f"Migrando proyecto a: {destino}")
            
            # Crear directorio destino
            destino.mkdir(parents=True, exist_ok=True)
            
            # Copiar archivos importantes
            archivos_copiar = [
                '*.py',
                '*.ipynb', 
                '*.md',
                '*.txt',
                '*.yaml',
                '*.yml',
                '*.json',
                '*.html',
                'config/',
                'docs/',
                'modelos_ml_quillota/',
                'tests/',
                'requirements.txt',
                'README.md',
                'LICENSE'
            ]
            
            archivos_copiados = 0
            
            for patron in archivos_copiar:
                for archivo in self.proyecto_actual.glob(patron):
                    if archivo.is_file():
                        try:
                            destino_archivo = destino / archivo.name
                            shutil.copy2(archivo, destino_archivo)
                            archivos_copiados += 1
                            self.logger.info(f"Copiado: {archivo.name}")
                        except Exception as e:
                            self.logger.warning(f"Error copiando {archivo}: {e}")
                    
                    elif archivo.is_dir():
                        try:
                            destino_dir = destino / archivo.name
                            shutil.copytree(archivo, destino_dir, dirs_exist_ok=True)
                            archivos_copiados += 1
                            self.logger.info(f"Copiado directorio: {archivo.name}")
                        except Exception as e:
                            self.logger.warning(f"Error copiando directorio {archivo}: {e}")
            
            # Crear script de instalacion en destino
            script_instalacion = destino / 'instalar_en_nuevo_disco.py'
            with open(script_instalacion, 'w', encoding='utf-8') as f:
                f.write('''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INSTALADOR EN NUEVO DISCO - METGO 3D
Script para instalar el proyecto en la nueva ubicacion
"""

import subprocess
import sys
import os
from pathlib import Path

def instalar_dependencias():
    """Instalar dependencias del proyecto"""
    try:
        print("Instalando dependencias...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("Dependencias instaladas exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error instalando dependencias: {e}")
        return False

def verificar_instalacion():
    """Verificar que la instalacion sea correcta"""
    try:
        print("Verificando instalacion...")
        subprocess.run([sys.executable, 'optimizar_sistema_completo.py'], check=True)
        print("Instalacion verificada exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error verificando instalacion: {e}")
        return False

def main():
    print("INSTALADOR EN NUEVO DISCO - METGO 3D")
    print("=" * 50)
    
    if instalar_dependencias() and verificar_instalacion():
        print("\\nProyecto instalado exitosamente en el nuevo disco")
        print("Para iniciar el dashboard ejecute:")
        print("python -m streamlit run sistema_unificado_con_conectores.py")
    else:
        print("\\nError en la instalacion")

if __name__ == "__main__":
    main()
''')
            
            return {
                'ruta_destino': str(destino),
                'archivos_copiados': archivos_copiados,
                'script_instalacion': str(script_instalacion)
            }
            
        except Exception as e:
            self.logger.error(f"Error migrando a disco: {e}")
            return {'error': str(e)}

def main():
    """Funcion principal para migracion"""
    print("MIGRADOR DE PROYECTO - METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Version 2.0")
    print("=" * 70)
    
    try:
        migrador = MigradorProyecto()
        
        print("\\nOpciones de migracion:")
        print("1. Crear paquete ZIP para migracion")
        print("2. Migrar a otro disco local")
        print("3. Ambas opciones")
        
        opcion = input("\\nSeleccione opcion (1-3): ").strip()
        
        if opcion in ['1', '3']:
            print("\\n1. Creando paquete ZIP...")
            resultado_zip = migrador.crear_paquete_migracion()
            
            if 'error' not in resultado_zip:
                print(f"   Paquete creado: {resultado_zip['ruta_paquete']}")
                print(f"   Archivos incluidos: {resultado_zip['archivos_incluidos']}")
                print(f"   Tamaño: {resultado_zip['tamaño_mb']:.2f} MB")
            else:
                print(f"   Error: {resultado_zip['error']}")
        
        if opcion in ['2', '3']:
            print("\\n2. Migrando a otro disco...")
            ruta_destino = input("Ingrese ruta de destino (ej: D:\\\\Proyectos): ").strip()
            
            if ruta_destino:
                resultado_disco = migrador.migrar_a_disco(ruta_destino)
                
                if 'error' not in resultado_disco:
                    print(f"   Proyecto migrado a: {resultado_disco['ruta_destino']}")
                    print(f"   Archivos copiados: {resultado_disco['archivos_copiados']}")
                    print(f"   Script de instalacion: {resultado_disco['script_instalacion']}")
                else:
                    print(f"   Error: {resultado_disco['error']}")
        
        print("\\nMigracion completada")
        
    except Exception as e:
        print(f"\\nError en migracion: {e}")

if __name__ == "__main__":
    main()
