#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPTIMIZADOR AUTOMATICO - METGO 3D
Optimiza el rendimiento del sistema automáticamente
"""

import os
import gc
import psutil
import time
from pathlib import Path
import logging

class OptimizadorMetgo:
    def __init__(self):
        self.logger = logging.getLogger('OPTIMIZADOR')
        self.setup_logging()
        
    def setup_logging(self):
        """Configurar logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('optimizacion.log'),
                logging.StreamHandler()
            ]
        )
    
    def limpiar_memoria(self):
        """Limpiar memoria del sistema"""
        try:
            gc.collect()
            memoria_antes = psutil.virtual_memory().percent
            self.logger.info(f"Memoria antes de limpieza: {memoria_antes}%")
            
            # Limpiar caché de Python
            import sys
            if hasattr(sys, 'getsizeof'):
                for obj in gc.get_objects():
                    if hasattr(obj, '__dict__'):
                        del obj.__dict__
            
            gc.collect()
            memoria_despues = psutil.virtual_memory().percent
            self.logger.info(f"Memoria después de limpieza: {memoria_despues}%")
            
            return memoria_antes - memoria_despues
        except Exception as e:
            self.logger.error(f"Error limpiando memoria: {e}")
            return 0
    
    def optimizar_archivos_temporales(self):
        """Optimizar archivos temporales"""
        try:
            temp_files = list(Path('.').glob('*.tmp')) + list(Path('.').glob('*.log'))
            archivos_eliminados = 0
            
            for archivo in temp_files:
                try:
                    archivo.unlink()
                    archivos_eliminados += 1
                except Exception as e:
                    self.logger.warning(f"No se pudo eliminar {archivo}: {e}")
            
            self.logger.info(f"Archivos temporales eliminados: {archivos_eliminados}")
            return archivos_eliminados
            
        except Exception as e:
            self.logger.error(f"Error optimizando archivos: {e}")
            return 0
    
    def verificar_rendimiento(self):
        """Verificar rendimiento del sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memoria_percent = psutil.virtual_memory().percent
            disco_percent = psutil.disk_usage('.').percent
            
            self.logger.info(f"CPU: {cpu_percent}%")
            self.logger.info(f"Memoria: {memoria_percent}%")
            self.logger.info(f"Disco: {disco_percent}%")
            
            return {
                'cpu': cpu_percent,
                'memoria': memoria_percent,
                'disco': disco_percent
            }
        except Exception as e:
            self.logger.error(f"Error verificando rendimiento: {e}")
            return None
    
    def optimizar_sistema(self):
        """Optimizar sistema completo"""
        self.logger.info("Iniciando optimización del sistema...")
        
        # Limpiar memoria
        memoria_liberada = self.limpiar_memoria()
        
        # Optimizar archivos
        archivos_eliminados = self.optimizar_archivos_temporales()
        
        # Verificar rendimiento
        rendimiento = self.verificar_rendimiento()
        
        self.logger.info("Optimización completada")
        return {
            'memoria_liberada': memoria_liberada,
            'archivos_eliminados': archivos_eliminados,
            'rendimiento': rendimiento
        }

if __name__ == "__main__":
    optimizador = OptimizadorMetgo()
    resultado = optimizador.optimizar_sistema()
    print(f"Optimización completada: {resultado}")
