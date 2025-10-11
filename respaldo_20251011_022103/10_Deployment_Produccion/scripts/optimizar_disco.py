#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPTIMIZADOR DE DISCO - METGO 3D
Limpieza y optimizacion del sistema de archivos
"""

import os
import shutil
import glob
from pathlib import Path
from datetime import datetime, timedelta
import logging

class OptimizadorDisco:
    """Optimizador de espacio en disco para METGO 3D"""
    
    def __init__(self):
        self.logger = logging.getLogger('DISK_OPTIMIZER')
        self.directorios_limpiar = [
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.pytest_cache',
            '.coverage',
            'htmlcov',
            '.mypy_cache',
            '.tox',
            'dist',
            'build',
            '*.egg-info'
        ]
        
        self.archivos_temporales = [
            '*.tmp',
            '*.temp',
            '*.log',
            '*.bak',
            '*.swp',
            '*.swo',
            '*~'
        ]
    
    def obtener_uso_disco(self, directorio='.'):
        """Obtener uso de disco de un directorio"""
        try:
            total_size = 0
            archivos = []
            
            for root, dirs, files in os.walk(directorio):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        total_size += size
                        archivos.append((file_path, size))
                    except (OSError, FileNotFoundError):
                        continue
            
            return total_size, archivos
        except Exception as e:
            self.logger.error(f"Error obteniendo uso de disco: {e}")
            return 0, []
    
    def limpiar_cache_python(self):
        """Limpiar archivos de cache de Python"""
        try:
            archivos_eliminados = 0
            espacio_liberado = 0
            
            for patron in self.directorios_limpiar:
                for archivo in glob.glob(patron, recursive=True):
                    try:
                        if os.path.isdir(archivo):
                            size = self._obtener_tamaño_directorio(archivo)
                            shutil.rmtree(archivo)
                            archivos_eliminados += 1
                            espacio_liberado += size
                            self.logger.info(f"Directorio eliminado: {archivo}")
                        elif os.path.isfile(archivo):
                            size = os.path.getsize(archivo)
                            os.remove(archivo)
                            archivos_eliminados += 1
                            espacio_liberado += size
                            self.logger.info(f"Archivo eliminado: {archivo}")
                    except (OSError, FileNotFoundError) as e:
                        self.logger.warning(f"No se pudo eliminar {archivo}: {e}")
            
            return archivos_eliminados, espacio_liberado
            
        except Exception as e:
            self.logger.error(f"Error limpiando cache Python: {e}")
            return 0, 0
    
    def _obtener_tamaño_directorio(self, directorio):
        """Obtener tamaño total de un directorio"""
        try:
            total_size = 0
            for root, dirs, files in os.walk(directorio):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, FileNotFoundError):
                        continue
            return total_size
        except Exception as e:
            self.logger.error(f"Error obteniendo tamaño de {directorio}: {e}")
            return 0
    
    def limpiar_archivos_temporales(self):
        """Limpiar archivos temporales"""
        try:
            archivos_eliminados = 0
            espacio_liberado = 0
            
            for patron in self.archivos_temporales:
                for archivo in glob.glob(patron, recursive=True):
                    try:
                        if os.path.isfile(archivo):
                            size = os.path.getsize(archivo)
                            os.remove(archivo)
                            archivos_eliminados += 1
                            espacio_liberado += size
                            self.logger.info(f"Archivo temporal eliminado: {archivo}")
                    except (OSError, FileNotFoundError) as e:
                        self.logger.warning(f"No se pudo eliminar {archivo}: {e}")
            
            return archivos_eliminados, espacio_liberado
            
        except Exception as e:
            self.logger.error(f"Error limpiando archivos temporales: {e}")
            return 0, 0
    
    def limpiar_logs_antiguos(self, dias_retener=7):
        """Limpiar logs antiguos"""
        try:
            archivos_eliminados = 0
            espacio_liberado = 0
            fecha_limite = datetime.now() - timedelta(days=dias_retener)
            
            # Buscar archivos de log
            patrones_log = ['*.log', 'logs/*.log', '*.out', '*.err']
            
            for patron in patrones_log:
                for archivo in glob.glob(patron, recursive=True):
                    try:
                        if os.path.isfile(archivo):
                            fecha_modificacion = datetime.fromtimestamp(os.path.getmtime(archivo))
                            if fecha_modificacion < fecha_limite:
                                size = os.path.getsize(archivo)
                                os.remove(archivo)
                                archivos_eliminados += 1
                                espacio_liberado += size
                                self.logger.info(f"Log antiguo eliminado: {archivo}")
                    except (OSError, FileNotFoundError) as e:
                        self.logger.warning(f"No se pudo eliminar {archivo}: {e}")
            
            return archivos_eliminados, espacio_liberado
            
        except Exception as e:
            self.logger.error(f"Error limpiando logs antiguos: {e}")
            return 0, 0
    
    def limpiar_respaldos_antiguos(self, dias_retener=30):
        """Limpiar respaldos antiguos"""
        try:
            archivos_eliminados = 0
            espacio_liberado = 0
            fecha_limite = datetime.now() - timedelta(days=dias_retener)
            
            # Buscar respaldos
            directorio_respaldos = Path('data/respaldos')
            if directorio_respaldos.exists():
                for archivo in directorio_respaldos.glob('*.zip'):
                    try:
                        fecha_modificacion = datetime.fromtimestamp(archivo.stat().st_mtime)
                        if fecha_modificacion < fecha_limite:
                            size = archivo.stat().st_size
                            archivo.unlink()
                            archivos_eliminados += 1
                            espacio_liberado += size
                            self.logger.info(f"Respaldo antiguo eliminado: {archivo}")
                            
                            # Eliminar metadatos si existen
                            metadatos = archivo.with_suffix('_metadata.json')
                            if metadatos.exists():
                                metadatos.unlink()
                    except (OSError, FileNotFoundError) as e:
                        self.logger.warning(f"No se pudo eliminar {archivo}: {e}")
            
            return archivos_eliminados, espacio_liberado
            
        except Exception as e:
            self.logger.error(f"Error limpiando respaldos antiguos: {e}")
            return 0, 0
    
    def optimizar_completo(self):
        """Ejecutar optimizacion completa del disco"""
        try:
            self.logger.info("Iniciando optimizacion completa del disco...")
            
            # Obtener uso inicial
            uso_inicial, _ = self.obtener_uso_disco()
            self.logger.info(f"Uso inicial del disco: {uso_inicial / (1024**3):.2f} GB")
            
            total_archivos_eliminados = 0
            total_espacio_liberado = 0
            
            # 1. Limpiar cache de Python
            self.logger.info("Limpiando cache de Python...")
            archivos, espacio = self.limpiar_cache_python()
            total_archivos_eliminados += archivos
            total_espacio_liberado += espacio
            self.logger.info(f"Cache Python: {archivos} archivos, {espacio / (1024**2):.2f} MB")
            
            # 2. Limpiar archivos temporales
            self.logger.info("Limpiando archivos temporales...")
            archivos, espacio = self.limpiar_archivos_temporales()
            total_archivos_eliminados += archivos
            total_espacio_liberado += espacio
            self.logger.info(f"Archivos temporales: {archivos} archivos, {espacio / (1024**2):.2f} MB")
            
            # 3. Limpiar logs antiguos
            self.logger.info("Limpiando logs antiguos...")
            archivos, espacio = self.limpiar_logs_antiguos(7)
            total_archivos_eliminados += archivos
            total_espacio_liberado += espacio
            self.logger.info(f"Logs antiguos: {archivos} archivos, {espacio / (1024**2):.2f} MB")
            
            # 4. Limpiar respaldos antiguos
            self.logger.info("Limpiando respaldos antiguos...")
            archivos, espacio = self.limpiar_respaldos_antiguos(30)
            total_archivos_eliminados += archivos
            total_espacio_liberado += espacio
            self.logger.info(f"Respaldos antiguos: {archivos} archivos, {espacio / (1024**2):.2f} MB")
            
            # Obtener uso final
            uso_final, _ = self.obtener_uso_disco()
            
            return {
                'archivos_eliminados': total_archivos_eliminados,
                'espacio_liberado_bytes': total_espacio_liberado,
                'espacio_liberado_mb': total_espacio_liberado / (1024**2),
                'espacio_liberado_gb': total_espacio_liberado / (1024**3),
                'uso_inicial_gb': uso_inicial / (1024**3),
                'uso_final_gb': uso_final / (1024**3),
                'reduccion_porcentaje': ((uso_inicial - uso_final) / uso_inicial) * 100 if uso_inicial > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error en optimizacion completa: {e}")
            return {'error': str(e)}

def main():
    """Funcion principal para optimizar disco"""
    print("OPTIMIZADOR DE DISCO - METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Version 2.0")
    print("=" * 70)
    
    try:
        # Crear optimizador
        optimizer = OptimizadorDisco()
        
        # Ejecutar optimizacion completa
        print("\n1. Ejecutando optimizacion completa del disco...")
        resultado = optimizer.optimizar_completo()
        
        if 'error' in resultado:
            print(f"   Error: {resultado['error']}")
            return False
        
        print(f"   Archivos eliminados: {resultado['archivos_eliminados']}")
        print(f"   Espacio liberado: {resultado['espacio_liberado_mb']:.2f} MB")
        print(f"   Uso inicial: {resultado['uso_inicial_gb']:.2f} GB")
        print(f"   Uso final: {resultado['uso_final_gb']:.2f} GB")
        print(f"   Reduccion: {resultado['reduccion_porcentaje']:.1f}%")
        
        print("\nOptimizacion de disco completada exitosamente")
        return True
        
    except Exception as e:
        print(f"\nError optimizando disco: {e}")
        return False

if __name__ == "__main__":
    main()
